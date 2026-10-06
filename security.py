"""
Halal Tech & AI Security Analyzer for Solana.
Enforces Sharia compliance:
1. Prohibition of gambling/betting/parody tokens (keyword gate).
2. Real utility & tech sector classification from the token's own metadata.
3. Real on-chain safety gates from RugCheck + live market data (DexScreener).

Every number reported here comes from a live API response — nothing is random.
"""
import re
from typing import Any, Dict, Optional, Tuple

import aiohttp

import config
import prices

HARAM_KEYWORDS = ["casino", "bet", "gamble", "lottery", "dice", "poker", "roulette", "jackpot", "ponzi"]

# code -> (title, keyword patterns matched against "name symbol")
TECH_SECTORS = {
    "AI_AGENTS": "هوش مصنوعی و دستیار پردازشی (AI Agent)",
    "DEPIN_COMPUTE": "محاسبات ابری و پردازش گرافیکی (DePIN GPU)",
    "DATA_ORACLE": "زیرساخت انتقال امن داده (Oracle Data)",
    "CYBER_SECURITY": "امنیت سایبری قراردادهای هوشمند (Security)",
    "INFRASTRUCTURE": "پروتکل‌ها و زیرساخت بلاک‌چین (Infrastructure)",
    "DEV_INFRA": "ابزارهای زیرساختی توسعه‌دهندگان (Dev Tools)",
}

SECTOR_KEYWORDS = {
    "AI_AGENTS": ["ai", "agent", "neural", "gpt", "llm", "cortex", "brain", "intelligent", "inference"],
    "DEPIN_COMPUTE": ["gpu", "depin", "compute", "render", "mining", "cloud", "hash", "bandwidth", "storage"],
    "DATA_ORACLE": ["oracle", "data", "index", "api", "stream", "analytics"],
    "CYBER_SECURITY": ["security", "secure", "audit", "shield", "cyber", "guard", "antivirus"],
    "INFRASTRUCTURE": ["infra", "infrastructure", "protocol", "layer", "node", "rpc", "bridge", "validator"],
    "DEV_INFRA": ["dev", "sdk", "compiler", "web3", "forge", "toolkit", "framework"],
}


def classify_sector(name: str, symbol: str, description: str = "") -> Optional[Tuple[str, str]]:
    """Return (code, title) when the token metadata matches a permitted tech sector."""
    text = f"{name} {symbol} {description}".lower()
    for code, patterns in SECTOR_KEYWORDS.items():
        if code not in config.PERMITTED_SECTORS:
            continue
        for pattern in patterns:
            if re.search(rf"(?<![a-z0-9]){re.escape(pattern)}(?![a-z0-9])", text):
                return code, TECH_SECTORS[code]
    return None


class SecurityAnalyzer:
    def __init__(self):
        self.session: aiohttp.ClientSession = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=6),
                trust_env=True,
            )
        return self.session

    async def _rugcheck(self, session: aiohttp.ClientSession, mint: str) -> Optional[dict]:
        url = config.RUGCHECK_REPORT.format(mint=mint)
        try:
            async with session.get(url, proxy=config.HTTP_PROXY) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            return None
        return None

    @staticmethod
    def _risk_names(report: dict) -> list:
        return [str(r.get("name", "")).lower() for r in (report.get("risks") or [])]

    async def check_token(self, token_data: dict) -> Tuple[bool, str, Dict[str, Any]]:
        mint = token_data.get("mint", "")
        symbol = str(token_data.get("symbol") or "").lower()
        name = str(token_data.get("name") or "").lower()
        description = str(token_data.get("description") or "")
        simulated = bool(token_data.get("is_simulated_stream")) and config.ALLOW_SIMULATED_STREAM

        # ۱. فیلتر شرعی: تحریم مطلق پروژه‌های قمار، شرط‌بندی و بخت‌آزمایی
        if config.EXCLUDE_GAMBLING_AND_MEMES:
            for kw in HARAM_KEYWORDS:
                if re.search(rf"(?<![a-z0-9]){kw}", symbol) or re.search(rf"(?<![a-z0-9]){kw}", name):
                    return False, f"حذف شرعی: پروژه مشکوک به قمار یا بخت‌آزمایی ({kw})", {}

        # ۲. حالت دمو: توکن شبیه‌سازی‌شده هرگز به‌عنوان داده واقعی عرضه نمی‌شود
        if simulated:
            details = {
                "score": None,
                "sector": "دموی شبیه‌سازی بازار (داده غیرواقعی)",
                "data_source": "SIMULATED",
                "liquidity_usd": None,
                "buyers_h1": None,
            }
            return True, "✅ [دمو] توکن شبیه‌سازی‌شده — بررسی‌های آن‌چین انجام نشد", details

        # ۳. طبقه‌بندی شرعی/فناوری بر اساس متادیتای واقعی توکن
        sector = classify_sector(name, symbol, description)
        if sector is None and config.REQUIRE_REAL_TECH_PRODUCT:
            return False, "فاقد پروژه فناوری/کاربردی شناخته‌شده (هیچ حوزه مجازی یافت نشد)", {}
        sector_title = sector[1] if sector else "نامشخص"

        # ۴. داده بازار واقعی از DexScreener (قبلاً واکشی شده یا همین‌جا دریافت می‌شود)
        session = await self.get_session()
        snapshot = token_data.get("snapshot") or await prices.get_token_snapshot(session, mint, use_cache=False)
        if snapshot is None:
            return False, "عدم دسترسی به داده بازار واقعی (DexScreener) — معامله متوقف شد", {}

        liquidity = snapshot.get("liquidity_usd") or 0.0
        if liquidity < config.MIN_LIQUIDITY_USD:
            return False, f"نقدشوندگی پایین: ${liquidity:,.0f} (حداقل ${config.MIN_LIQUIDITY_USD:,.0f})", {}

        buyers = max(snapshot.get("buyers_h1") or 0, snapshot.get("buyers_24h") or 0)
        if config.REQUIRE_BUYER_MOMENTUM and buyers < config.MIN_BUYER_COUNT:
            return False, f"عدم استقبال: فقط {buyers} خریدار (حداقل {config.MIN_BUYER_COUNT} نیاز است)", {}

        # ۵. گزارش RugCheck (داده واقعی، نه پیش‌فرض)
        report = await self._rugcheck(session, mint)
        if report is None:
            return False, "عدم دسترسی به گزارش RugCheck — بررسی ریسک ناممکن است", {}

        risks = report.get("risks") or []
        danger = [r.get("name") for r in risks if r.get("level") == "danger"]
        if danger:
            return False, f"اخطار RugCheck: {danger[0]}", {}

        names = self._risk_names(report)

        def has_risk(*keys: str) -> bool:
            return any(all(k in n for k in keys) for n in names)

        if config.REQUIRE_REVOKED_FREEZE and has_risk("freeze", "authorit"):
            return False, "ریسک هانی‌پات: امکان فریز حساب فعال است", {}
        if config.REQUIRE_REVOKED_MINT and has_risk("mint", "authorit"):
            return False, "ریسک تورم: دسترسی ساخت توکن اضافه سوزانده نشده", {}
        if config.REQUIRE_IMMUTABLE_METADATA and (has_risk("metadata", "mutable") or has_risk("mutable", "metadata")):
            return False, "ریسک فریب: هویت متادیتا قابل دستکاری است", {}

        # ۶. نمره اعتبار بر اساس معیارهای واقعی بازار
        liq_score = min(liquidity / 20000.0, 1.0) * 30.0
        buyers_score = min(buyers / 50.0, 1.0) * 25.0
        volume_score = min((snapshot.get("volume_usd_24h") or 0.0) / 50000.0, 1.0) * 25.0
        warn_penalty = sum(1 for r in risks if r.get("level") == "warn") * 2.0
        gem_score = int(max(0, min(100, 20 + liq_score + buyers_score + volume_score - warn_penalty)))

        if gem_score < config.MIN_GEM_SCORE:
            return False, f"نمره اعتبار ({gem_score}) زیر حد استاندارد ({config.MIN_GEM_SCORE}) است", {}

        details = {
            "score": gem_score,
            "sector": sector_title,
            "data_source": "LIVE",
            "liquidity_usd": liquidity,
            "buyers_h1": buyers,
            "volume_usd_24h": snapshot.get("volume_usd_24h"),
        }
        return True, f"✅ تایید شرعی و فنی: {sector_title} | نمره: {gem_score}/100", details

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

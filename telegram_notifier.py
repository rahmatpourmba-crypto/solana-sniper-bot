"""
Halal Tech Telegram Notifier with Project Sector, Live Metrics, and Solscan Links.
Messages are tagged when they originate from the simulated (demo) stream.
"""
from typing import Optional

import aiohttp

import config


class TelegramNotifier:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self.enabled = bool(self.bot_token and self.chat_id)
        self.session: Optional[aiohttp.ClientSession] = None

    def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8))
        return self.session

    async def send_message(self, text: str) -> bool:
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        for attempt in range(2):
            try:
                async with self._get_session().post(url, json=payload, proxy=config.HTTP_PROXY) as resp:
                    if resp.status == 200:
                        return True
            except Exception:
                pass
        return False

    async def notify_buy(
        self,
        symbol: str,
        mint: str,
        amount_sol: float,
        score: str,
        sector: str,
        balance_sol: float,
        liquidity_usd: Optional[float] = None,
        buyers: Optional[int] = None,
        simulated: bool = False,
    ):
        dex_link = f"https://dexscreener.com/solana/{mint}"
        solscan_link = f"https://solscan.io/token/{mint}"
        demo_badge = "🧪 <b>[دمو — داده شبیه‌سازی‌شده]</b>\n" if simulated else ""
        liquidity_text = f"${liquidity_usd:,.0f}" if liquidity_usd else "—"
        buyers_text = str(buyers) if buyers is not None else "—"

        text = (
            f"{demo_badge}💎 <b>[خرید موفق پروژه فناوری و هوش مصنوعی]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏷 <b>حوزه کاربردی:</b> {sector}\n"
            f"🪙 <b>نماد توکن:</b> ${symbol}\n"
            f"🔑 <b>آدرس قرارداد:</b> <code>{mint}</code>\n"
            f"💰 <b>حجم ورود:</b> {amount_sol} SOL\n"
            f"💧 <b>نقدشوندگی:</b> {liquidity_text}\n"
            f"🛒 <b>خریداران:</b> {buyers_text}\n"
            f"🌟 <b>نمره اعتبار:</b> {score}\n"
            f"💵 <b>موجودی حساب:</b> {balance_sol:.3f} SOL\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 <a href='{dex_link}'>چارت DexScreener</a> | <a href='{solscan_link}'>کاوشگر Solscan</a>"
        )
        await self.send_message(text)

    async def notify_close(
        self,
        symbol: str,
        mint: str,
        reason: str,
        multiplier: float,
        pnl_sol: float,
        pnl_percent: float,
        balance_sol: float,
        win_rate: float,
        simulated: bool = False,
    ):
        is_profit = pnl_sol > 0
        icon = "🎯" if is_profit else "🛑"
        result_title = "سود محقق شد (حلال)" if is_profit else "خروج اضطراری (Stop Loss)"
        demo_badge = "🧪 <b>[دمو]</b>\n" if simulated else ""
        dex_link = f"https://dexscreener.com/solana/{mint}"

        text = (
            f"{demo_badge}{icon} <b>[{result_title}]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🪙 <b>توکن:</b> ${symbol}\n"
            f"📈 <b>ضریب رشد:</b> <b>{multiplier:.1f}x</b> ({pnl_percent:+.1f}%)\n"
            f"💵 <b>سود خالص معامله:</b> {pnl_sol:+.4f} SOL\n"
            f"🏆 <b>موجودی جدید:</b> {balance_sol:.3f} SOL\n"
            f"📊 <b>درصد برد کل:</b> {win_rate:.1f}%\n"
            f"📝 <b>دلیل خروج:</b> {reason}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 <a href='{dex_link}'>مشاهده چارت نهایی توکن</a>"
        )
        await self.send_message(text)

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

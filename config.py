"""
🎯 HALAL MEME SNIPER — Config (Mega-Prompt Edition)
════════════════════════════════════════════════════
[تکنیک ۱ — Expert Anchoring] پیکربندی ربات شکارچی میم‌کوین حلال
[تکنیک ۹ — Dynamic Variable Injection] تمام پارامترها از .env قابل تنظیم
[تکنیک ۶ — Negative Constraints] هیچ کلید خصوصی در کد نیست — همه از env

استراتژی جدید: HALAL_MEME_SNIPER
- میم‌کوین‌های سالم سولانا ✅
- بدون قمار / ربا / محتوای نامناسب ✅
- هدف رشد ۲۰۰۰٪ در اوج پامپ‌دات‌فان ✅
"""
import os


def _load_dotenv(path: str = None) -> None:
    """Minimal .env loader (no external dependency). Existing env vars win."""
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.isfile(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        pass


_load_dotenv()


# --- MODE SELECTION ---
def _flag(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


SIMULATION_MODE = _flag("SIMULATION_MODE", "true")   # کاغذی: هیچ پول واقعی جابجا نمی‌شود
ALLOW_SIMULATED_STREAM = SIMULATION_MODE              # استریم دمو فقط در حالت کاغذی
LIVE_DRY_RUN = _flag("LIVE_DRY_RUN", "true")         # تراکنش ساخته می‌شود ولی ارسال نمی‌شود

# ═══════════════════════════════════════════════════════════════
# [تکنیک ۷ — Step-Back] استراتژی کلان: HALAL_MEME_SNIPER
# تغییر اساسی از HALAL_UTILITY_AI به سمت میم‌کوین‌های سالم
# ═══════════════════════════════════════════════════════════════
STRATEGY_MODE = "HALAL_MEME_SNIPER"
REQUIRE_REAL_TECH_PRODUCT = False      # ❌ دیگر فناوری الزامی نیست — میم‌کوین مجاز است
EXCLUDE_HARAM_CONTENT = True           # ✅ فیلتر شرعی کامل فعال است

# ═══════════════════════════════════════════════════════════════
# [تکنیک ۹ — Dynamic Variables] سرمایه‌گذاری: از نیم‌دلار شروع می‌شود
# ═══════════════════════════════════════════════════════════════
INITIAL_SIM_SOL      = 2.0
BUY_AMOUNT_SOL       = float(os.getenv("BUY_AMOUNT_SOL", "0.001"))    # ~0.15$ تا 0.20$ (10 تا 20 سنت)
MAX_ACTIVE_POSITIONS = int(os.getenv("MAX_ACTIVE_POSITIONS", "3"))
MIN_SOL_RESERVE      = 0.006          # حداقل ذخیره برای فی‌های تراکنش

# ═══════════════════════════════════════════════════════════════
# [تکنیک ۱۴ — Risk Matrix] ماتریس ریسک: سود هدف ۲۰۰۰٪
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# مرحله ۱: استاپ اولیه ۱۲٪ (محافظت اولیه)
# مرحله ۲: تریلینگ ۱۸٪ پس از رشد ۴۰٪ (محافظت سود)
# مرحله ۳: قفل برک‌ایون پس از ۱۰۰٪ (ضرر صفر)
# مرحله ۴: خروج در ۲۰۰۰٪ (هدف نهایی)
# ═══════════════════════════════════════════════════════════════
ENABLE_TRAILING_STOP         = True
TRAILING_STOP_PERCENT        = 18.0   # ۱۸٪ زیر اوج → خروج
TIER1_TP                     = 40.0   # از اینجا تریلینگ فعال می‌شود
BREAKEVEN_TRIGGER_PERCENT    = 100.0  # پس از ۲ برابر → برک‌ایون قفل
LOCKED_PROFIT_FLOOR_PERCENT  = 50.0   # اگر قفل شد، تا ۵۰٪ نگه می‌دارد
MOONSHOT_TP                  = 2000.0 # ۲۰ برابر → خروج نهایی 🚀
STOP_LOSS_INITIAL            = 12.0   # خروج سریع در -۱۲٪
MAX_HOLD_SECONDS             = 300    # ۵ دقیقه رکود → خروج

# --- WALLET (live mode only) ---
PHANTOM_PRIVATE_KEY = os.getenv("PHANTOM_PRIVATE_KEY", "")
AUTO_CLOSE_ATA_RENT = True

# --- LIVE TRADING (Jupiter Swap API + Solana RPC) ---
JUPITER_BASE          = os.getenv("JUPITER_BASE_URL", "https://lite-api.jup.ag/swap/v1")
SLIPPAGE_BPS          = int(os.getenv("SLIPPAGE_BPS", "500"))        # ۵٪ اسلیپاژ — میم‌کوین نیاز دارد
MAX_PRICE_IMPACT_PCT  = 0.05          # تا ۵٪ price impact برای میم‌کوین
CONFIRM_TIMEOUT_SECONDS = 45
DAILY_LOSS_LIMIT_SOL  = 0.025         # کلید اضطراری روزانه
SELL_RETRY_LIMIT      = 3
ATA_RENT_SOL          = 0.00204       # اجاره ATA (بازیابی در فروش)
TX_FEE_SOL            = 0.000005      # فی یک امضا

# ═══════════════════════════════════════════════════════════════
# [تکنیک ۱۲ — Self-Consistency] معیارهای کیفی on-chain
# اعداد بر اساس تجربه میدانی pump.fun تنظیم شده‌اند
# ═══════════════════════════════════════════════════════════════
MAX_TOP5_HOLDERS       = 16.0   # اگر ۵ نفر بیش از ۱۶٪ داشتند → rug احتمالی
REQUIRE_BUYER_MOMENTUM = True
MIN_BUYER_COUNT        = 4      # حداقل ۴ خریدار واقعی در اول
REQUIRE_REVOKED_MINT   = True   # اختیار ضرب توکن باید لغو شده باشد
REQUIRE_REVOKED_FREEZE = True   # اختیار فریز باید لغو شده باشد
REQUIRE_IMMUTABLE_METADATA = True
REQUIRE_SOCIALS        = False
MIN_GEM_SCORE          = 55     # آستانه پایین‌تر برای میم‌کوین تازه (قبلاً ۷۰)
MIN_LIQUIDITY_USD      = 2000.0 # حداقل نقدشوندگی (قبلاً ۳۰۰۰ — کاهش برای pump.fun)

# --- MARKET DATA APIs ---
PRICE_POLL_SECONDS  = 4
DEXSCREENER_LATEST  = "https://api.dexscreener.com/token-profiles/latest/v1"
DEXSCREENER_TOKEN   = "https://api.dexscreener.com/latest/dex/tokens/{mint}"
DEXSCREENER_PAIR    = "https://api.dexscreener.com/latest/dex/pairs/solana/{pair}"
RUGCHECK_REPORT     = "https://api.rugcheck.xyz/v1/tokens/{mint}/report/summary"

# --- MULTI-RPC FALLBACK POOL ---
RPC_POOL = [
    "https://api.mainnet-beta.solana.com",
    "https://solana-rpc.publicnode.com",
    "https://rpc.ankr.com/solana",
]
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", RPC_POOL[0])

# --- TELEGRAM 24/7 (secrets come from environment only) ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

# --- PROXY (set only if you are behind a filter; empty = direct) ---
HTTP_PROXY = os.getenv("HTTP_PROXY", "") or None

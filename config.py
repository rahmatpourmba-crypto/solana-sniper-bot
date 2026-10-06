"""
Institutional-Grade Configuration for Solana & Pump.fun Moonshot Sniper.
Audited for Maximum Security, MEV-Protection, and Micro-Capital Growth.
"""
import os

# --- MODE SELECTION ---
# True: شبیه‌ساز کاملاً امن و دقیق با شبیه‌سازی اسلیپیج و کارمزد
# False: ترید زنده روی شبکه سولانا
SIMULATION_MODE = True

# --- CAPITAL & POSITION SIZING ---
INITIAL_SIM_SOL = 2.0                 # موجودی فرضی اولیه
BUY_AMOUNT_SOL = 0.0035               # معادل حدود نیم دلار ($0.50) برای معامله خرد
MAX_ACTIVE_POSITIONS = 3              # حداکثر ۳ پوزیشن فعال همزمان جهت مدیریت هوشمند نقدینگی
MIN_SOL_RESERVE = 0.006               # حفظ حداقل موجودی برای کارمزد شبکه

# --- WALLET & AUTOMATIC RENT RECOVERY ---
PHANTOM_PRIVATE_KEY = os.getenv("PHANTOM_PRIVATE_KEY", "")
AUTO_CLOSE_ATA_RENT = True            # بازپس‌گیری خودکار ۰.۰۰۲ سولانا وثیقه حساب پس از هر فروش

# --- ADVANCED MOONSHOT TARGETS & LOSS MITIGATION ---
ENABLE_TRAILING_STOP = True
TRAILING_STOP_PERCENT = 18.0          # خروج هوشمند در صورت ۱۸٪ افت از بالاترین قله قیمت (Peak)
BREAKEVEN_TRIGGER_PERCENT = 100.0     # به محض ۲ برابر شدن، حد ضرر بالای نقطه ورود قفل می‌شود (تضمین صفر شدن باخت)
STOP_LOSS_INITIAL = 12.0              # خروج اضطراری سریع در صورت ریزش اولیه ۱۲٪- (حداکثر ضرر زیر ۴ سنت)

# --- ADVANCED ON-CHAIN SECURITY GATES (فیلترهای نفوذناپذیر ضدکلاهبرداری) ---
MAX_DEV_HOLDING = 5.0                 # سخت‌گیرانه‌ترین حد: سهم سازنده حداکثر ۵٪ (کاهش از ۶٪)
MAX_TOP5_HOLDERS = 16.0               # سهم ۵ هولدر اول زیر ۱۶٪ (جلوگیری از تبانی گروهی)
REQUIRE_BUYER_MOMENTUM = True         # الزام وجود حداقل ۴ خریدار مستقل در ثانیه‌های اول
MIN_BUYER_COUNT = 4
REQUIRE_REVOKED_MINT = True           # الزام سوزانده شدن دسترسی ضرب توکن اضافه
REQUIRE_REVOKED_FREEZE = True         # الزام خاموش بودن دسترسی مسدود کردن کیف‌پول‌ها
REQUIRE_IMMUTABLE_METADATA = True     # جلوگیری از تغییر نام و هویت توکن پس از خرید
MIN_GEM_SCORE = 88                    # نمره قبولی در راگ‌چک حداقل ۸۸ از ۱۰۰

# --- MULTI-RPC FALLBACK POOL (استخر چرخان نودها برای قطعی‌ناپذیری) ---
RPC_POOL = [
    "https://api.mainnet-beta.solana.com",
    "https://solana-rpc.publicnode.com",
    "https://rpc.ankr.com/solana"
]
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", RPC_POOL[0])

# --- TELEGRAM 24/7 NOTIFICATIONS ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8886497499:AAH1crLMaaDDVhbrSPvTCVfhlJWQGKB9pno")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003954902967")

# --- PROXY & EXTERNAL APIS ---
HTTP_PROXY = os.getenv("HTTP_PROXY", "http://127.0.0.1:10809")
DEXSCREENER_LATEST = "https://api.dexscreener.com/token-profiles/latest/v1"
DEXSCREENER_PAIRS = "https://api.dexscreener.com/latest/dex/tokens/"

"""
Halal Tech & Utility Configuration for Solana & DePIN/AI Ecosystem.
Compliant with Islamic ethical finance: targets only utility, AI, and computing tokens.
"""
import os

# --- MODE SELECTION ---
SIMULATION_MODE = True

# --- STRATEGY & SHARIA COMPLIANCE ---
STRATEGY_MODE = "HALAL_UTILITY_AI"   # استراتژی معاملات حلال توکن‌های کاربردی و هوش مصنوعی
EXCLUDE_GAMBLING_AND_MEMES = True    # حذف مطلق توکن‌های قمار، شرط‌بندی و شوخی‌های پوچ
REQUIRE_REAL_TECH_PRODUCT = True     # الزام داشتن محصول فناوری، داکیومنت یا هوش مصنوعی

# دسته‌بندی‌های مجاز و حلال:
PERMITTED_SECTORS = [
    "AI_AGENTS",           # ایجنت‌های هوش مصنوعی
    "DEPIN_COMPUTE",       # اشتراک‌گذاری قدرت پردازش و اینترنت
    "DATA_ORACLE",         # زیرساخت‌های انتقال داده و اوراکل
    "INFRASTRUCTURE",      # پروتکل‌های ابری و بلاک‌چین
    "CYBER_SECURITY"       # ابزارهای امنیت نرم‌افزار
]

# --- CAPITAL SETTINGS ---
INITIAL_SIM_SOL = 2.0
BUY_AMOUNT_SOL = 0.0035              # نیم دلار ($0.50) برای معامله خرد
MAX_ACTIVE_POSITIONS = 3
MIN_SOL_RESERVE = 0.006

# --- PHANTOM WALLET & RENT RECOVERY ---
PHANTOM_PRIVATE_KEY = os.getenv("PHANTOM_PRIVATE_KEY", "")
AUTO_CLOSE_ATA_RENT = True

# --- TARGETS & RISK MITIGATION ---
ENABLE_TRAILING_STOP = True
TRAILING_STOP_PERCENT = 18.0
BREAKEVEN_TRIGGER_PERCENT = 100.0    # قفل بدون باخت پس از ۲ برابر شدن
STOP_LOSS_INITIAL = 12.0             # خروج سریع در ۱۲٪-

# --- ON-CHAIN INTEGRITY ---
MAX_DEV_HOLDING = 5.0
MAX_TOP5_HOLDERS = 16.0
REQUIRE_BUYER_MOMENTUM = True
MIN_BUYER_COUNT = 4
REQUIRE_REVOKED_MINT = True
REQUIRE_REVOKED_FREEZE = True
REQUIRE_IMMUTABLE_METADATA = True
MIN_GEM_SCORE = 88

# --- MULTI-RPC FALLBACK POOL ---
RPC_POOL = [
    "https://api.mainnet-beta.solana.com",
    "https://solana-rpc.publicnode.com",
    "https://rpc.ankr.com/solana"
]
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", RPC_POOL[0])

# --- TELEGRAM 24/7 ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8886497499:AAH1crLMaaDDVhbrSPvTCVfhlJWQGKB9pno")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003954902967")

# --- PROXY ---
HTTP_PROXY = os.getenv("HTTP_PROXY", "http://127.0.0.1:10809")
DEXSCREENER_LATEST = "https://api.dexscreener.com/token-profiles/latest/v1"
DEXSCREENER_PAIRS = "https://api.dexscreener.com/latest/dex/tokens/"

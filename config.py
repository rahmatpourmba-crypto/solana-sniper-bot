"""
Configuration module for Solana Moonshot Sniper Bot & Simulation Engine.
Upgraded with Anti-Loss Guard, Buyer Momentum Verification, and Tight Stop-Loss.
"""
import os

# --- MODE SELECTION ---
SIMULATION_MODE = True

# --- MICRO-CAPITAL SETTINGS ---
INITIAL_SIM_SOL = 2.0
BUY_AMOUNT_SOL = 0.0035               # نیم دلار ($0.50) برای هر ورود
MIN_WALLET_RESERVE_SOL = 0.005

# --- PHANTOM WALLET ---
PHANTOM_PRIVATE_KEY = os.getenv("PHANTOM_PRIVATE_KEY", "")
AUTO_CLOSE_EMPTY_ACCOUNTS = True

# --- ANTI-LOSS PROTECTION (سپر دفاعی ضدضرر جدید) ---
MIN_GEM_SCORE = 88.0                  # افزایش حداقل نمره کیفی جم از ۸۰ به ۸۸
REQUIRE_BUYER_MOMENTUM = True         # الزام وجود حداقل چند خریدار اولیه مستقل
MAX_TOP5_HOLDERS_PERCENT = 18.0       # حداکثر سهم ۵ هولدر برتر زیر ۱۸٪
STOP_LOSS_INITIAL = 12.0              # سفت کردن حد ضرر اولیه از ۲۵٪- به ۱۲٪- (کاهش چشمگیر ضرر)

# --- MOONSHOT TARGETS & EXIT STRATEGY ---
ENABLE_TRAILING_STOP = True
TRAILING_STOP_PERCENT = 18.0          # خروج هوشمند در ۱۸٪ افت از قله
TIER1_TP = 100.0                      # ۲ برابر (ریسک‌فری)
TIER2_TP = 500.0                      # ۵ برابر
MOONSHOT_TP = 2000.0                  # ۲۰ برابر (۲۰۰۰٪)

# --- GEM CRITERIA ---
REQUIRE_SOCIALS = True
MAX_DEV_HOLDING = 6.0                 # کاهش حداکثر سهم سازنده از ۸٪ به ۶٪ (امنیت بیشتر)
MIN_LIQUIDITY_USD = 2000.0

# --- TELEGRAM ALERTS ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8886497499:AAH1crLMaaDDVhbrSPvTCVfhlJWQGKB9pno")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003954902967")

# --- NETWORK & PROXY ---
HTTP_PROXY = os.getenv("HTTP_PROXY", "http://127.0.0.1:10809")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
DEXSCREENER_LATEST = "https://api.dexscreener.com/token-profiles/latest/v1"
DEXSCREENER_PAIRS = "https://api.dexscreener.com/latest/dex/tokens/"

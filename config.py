"""
Configuration module for Solana Sniper Bot & Simulation Engine.
"""
import os

# --- MODE SELECTION ---
# True = Paper Trading (سرمایه مجازی بدون خطر برای تست)
# False = Real Trading (معامله واقعی با ولت)
SIMULATION_MODE = True

# --- SIMULATION SETTINGS ---
INITIAL_SIM_SOL = 2.0        # موجودی مجازی اولیه بر حسب سولانا
BUY_AMOUNT_SOL = 0.05        # حجم هر خرید به ازای هر توکن جدید

# --- PROFIT & LOSS MANAGEMENT ---
TAKE_PROFIT_PERCENT = 40.0   # تارگت سیو سود (مثلاً ۴۰٪ رشد)
STOP_LOSS_PERCENT = 15.0     # حد ضرر خودکار (مثلاً ۱۵٪ ریزش)
MAX_HOLD_SECONDS = 120       # حداکثر زمان نگهداری توکن (ثانیه) در صورت نرسیدن به تارگت

# --- SECURITY / ANTI-RUGPUT CRITERIA ---
CHECK_SECURITY = True
MIN_LIQUIDITY_USD = 1000.0    # حداقل نقدینگی اولیه استخر (دلار)

# --- PROXY SETTING (Local VPN / Proxy for Iran) ---
HTTP_PROXY = os.getenv("HTTP_PROXY", "http://127.0.0.1:10809")

# --- NETWORK & API ENDPOINTS ---
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
DEXSCREENER_LATEST = "https://api.dexscreener.com/token-profiles/latest/v1"
DEXSCREENER_PAIRS = "https://api.dexscreener.com/latest/dex/tokens/"
PUMPFUN_WS_URL = "wss://pumpportal.fun/api/data"

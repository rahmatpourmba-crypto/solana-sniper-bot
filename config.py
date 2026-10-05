"""
Configuration module for Solana Moonshot Sniper Bot & Simulation Engine.
Optimized for hunting 1,000% - 5,000% runners on Pump.fun & Raydium.
"""
import os

# --- MODE SELECTION ---
SIMULATION_MODE = True        # حالت شبیه‌ساز امن (بدون ریسک)

# --- SIMULATION CAPITAL ---
INITIAL_SIM_SOL = 2.0         # موجودی مجازی اولیه
BUY_AMOUNT_SOL = 0.05         # حجم ورود به هر جم مستعد

# --- MOONSHOT TARGETS & EXIT STRATEGY ---
ENABLE_TRAILING_STOP = True   # فعال‌سازی حد ضرر متحرک از سقف قیمت
TRAILING_STOP_PERCENT = 20.0  # خروج در صورت ۲۰٪ افت از بالاترین قله قیمت (Peak)

# خروج پله‌ای برای تضمین سود و شکار سقف‌های چند هزار درصدی:
TIER1_TP = 100.0              # ۲ برابر شدن (برداشت اصل سرمایه)
TIER2_TP = 500.0              # ۵ برابر شدن
MOONSHOT_TP = 2000.0          # ۲۰ برابر شدن (۲۰۰۰ درصد)
STOP_LOSS_INITIAL = 25.0      # حد ضرر اولیه در صورت شکست اولیه

# --- GEM CRITERIA (فیلترهای شناسایی جم‌های چند هزار درصدی) ---
REQUIRE_SOCIALS = True        # الزام داشتن توییتر/تلگرام یا وب‌سایت
MAX_DEV_HOLDING = 8.0         # حداکثر سهم مجاز سازنده (درصد)
MIN_LIQUIDITY_USD = 1500.0    # حداقل نقدینگی اولیه

# --- NETWORK & PROXY ---
HTTP_PROXY = os.getenv("HTTP_PROXY", "http://127.0.0.1:10809")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
DEXSCREENER_LATEST = "https://api.dexscreener.com/token-profiles/latest/v1"
DEXSCREENER_PAIRS = "https://api.dexscreener.com/latest/dex/tokens/"

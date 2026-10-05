"""
Configuration module for Solana Moonshot Sniper Bot & Simulation Engine.
Supports Micro-Budget trades (down to $0.50 / 0.0035 SOL) with direct Phantom Wallet settlement.
"""
import os

# --- MODE SELECTION ---
# True = حالت تستی (آزمایشی شبیه‌ساز)
# False = حالت ترید واقعی با کیف‌پول فانتوم
SIMULATION_MODE = True

# --- MICRO-CAPITAL SETTINGS (معامله با مبالغ خرد) ---
INITIAL_SIM_SOL = 2.0                 # موجودی شبیه‌ساز فعلی
BUY_AMOUNT_SOL = 0.0035               # معادل نیم دلار ($0.50) برای شروع مایکرو
MIN_WALLET_RESERVE_SOL = 0.005        # ذخیره حداقلی در ولت برای کارمزدها

# --- PHANTOM WALLET (برای فاز اجرای واقعی هفته آینده) ---
# در حالت واقعی، کلید خصوصی یک ولت تستی فانتوم اینجا قرار می‌گیرد
PHANTOM_PRIVATE_KEY = os.getenv("PHANTOM_PRIVATE_KEY", "")

# --- ATA RENT RECOVERY (بازگرداندن خودکار وثیقه شبکه به فانتوم) ---
AUTO_CLOSE_EMPTY_ACCOUNTS = True      # پس از فروش توکن، وثیقه شبکه به کیف‌پول بازمی‌گردد

# --- MOONSHOT TARGETS & EXIT STRATEGY ---
ENABLE_TRAILING_STOP = True           # حد ضرر متحرک از سقف
TRAILING_STOP_PERCENT = 20.0          # خروج در ۲۰٪ ریزش از قله
TIER1_TP = 100.0                      # ۲ برابر (برداشت اصل پول)
TIER2_TP = 500.0                      # ۵ برابر
MOONSHOT_TP = 2000.0                  # ۲۰ برابر (۲۰۰۰٪)
STOP_LOSS_INITIAL = 25.0              # حد ضرر اولیه

# --- GEM CRITERIA (فیلترهای شناسایی جم‌های امن) ---
REQUIRE_SOCIALS = True                # داشتن توییتر/تلگرام
MAX_DEV_HOLDING = 8.0                 # سهم سازنده زیر ۸٪
MIN_LIQUIDITY_USD = 1500.0            # حداقل نقدینگی

# --- TELEGRAM ALERTS (کانال شما) ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8886497499:AAH1crLMaaDDVhbrSPvTCVfhlJWQGKB9pno")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003954902967")

# --- NETWORK & PROXY ---
HTTP_PROXY = os.getenv("HTTP_PROXY", "http://127.0.0.1:10809")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
DEXSCREENER_LATEST = "https://api.dexscreener.com/token-profiles/latest/v1"
DEXSCREENER_PAIRS = "https://api.dexscreener.com/latest/dex/tokens/"

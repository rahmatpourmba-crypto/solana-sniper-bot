"""
Halal Tech & Utility Configuration for Solana & DePIN/AI Ecosystem.
Compliant with Islamic ethical finance: targets only utility, AI, and computing tokens.

All secrets are read from environment variables (see .env.example).
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
SIMULATION_MODE = True                      # Paper trading: no real funds are ever used
# Mock token stream is only allowed in simulation mode; never mixed into live feeds.
ALLOW_SIMULATED_STREAM = SIMULATION_MODE

# --- STRATEGY & SHARIA COMPLIANCE ---
STRATEGY_MODE = "HALAL_UTILITY_AI"
EXCLUDE_GAMBLING_AND_MEMES = True
REQUIRE_REAL_TECH_PRODUCT = True            # token must match a known tech/utility sector
PERMITTED_SECTORS = [
    "AI_AGENTS",
    "DEPIN_COMPUTE",
    "DATA_ORACLE",
    "INFRASTRUCTURE",
    "CYBER_SECURITY",
    "DEV_INFRA",
]

# --- CAPITAL SETTINGS ---
INITIAL_SIM_SOL = 2.0
BUY_AMOUNT_SOL = 0.0035
MAX_ACTIVE_POSITIONS = 3
MIN_SOL_RESERVE = 0.006

# --- WALLET (live mode only) ---
PHANTOM_PRIVATE_KEY = os.getenv("PHANTOM_PRIVATE_KEY", "")
AUTO_CLOSE_ATA_RENT = True

# --- TARGETS & RISK MITIGATION ---
ENABLE_TRAILING_STOP = True
TRAILING_STOP_PERCENT = 18.0                # trail 18% below the peak
TIER1_TP = 40.0                             # trailing stop arms after +40%
BREAKEVEN_TRIGGER_PERCENT = 100.0           # lock breakeven after 2x
MOONSHOT_TP = 2000.0                        # exit at +2000% (20x)
STOP_LOSS_INITIAL = 12.0                    # fast exit at -12%
MAX_HOLD_SECONDS = 240                      # stagnant exit after 4 minutes

# --- ON-CHAIN INTEGRITY (real data, checked via RugCheck + DexScreener) ---
MAX_TOP5_HOLDERS = 16.0
REQUIRE_BUYER_MOMENTUM = True
MIN_BUYER_COUNT = 4
REQUIRE_REVOKED_MINT = True
REQUIRE_REVOKED_FREEZE = True
REQUIRE_IMMUTABLE_METADATA = True
REQUIRE_SOCIALS = False
MIN_GEM_SCORE = 70
MIN_LIQUIDITY_USD = 3000.0

# --- MARKET DATA ---
PRICE_POLL_SECONDS = 5
DEXSCREENER_LATEST = "https://api.dexscreener.com/token-profiles/latest/v1"
DEXSCREENER_TOKEN = "https://api.dexscreener.com/latest/dex/tokens/{mint}"
DEXSCREENER_PAIR = "https://api.dexscreener.com/latest/dex/pairs/solana/{pair}"
RUGCHECK_REPORT = "https://api.rugcheck.xyz/v1/tokens/{mint}/report/summary"

# --- MULTI-RPC FALLBACK POOL ---
RPC_POOL = [
    "https://api.mainnet-beta.solana.com",
    "https://solana-rpc.publicnode.com",
    "https://rpc.ankr.com/solana",
]
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", RPC_POOL[0])

# --- TELEGRAM 24/7 (secrets come from environment only) ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# --- PROXY (set only if you are behind a filter; empty = direct) ---
HTTP_PROXY = os.getenv("HTTP_PROXY", "") or None

# ⚡ Solana Sniper Bot (Paper Trading → Live with Safety Gates)

An automated Solana sniping research bot with a **paper-trading engine**, a **live execution layer (Jupiter + Solana RPC)**, real market data from DexScreener, on-chain safety checks via RugCheck, position/risk management, and a live Rich terminal dashboard with Telegram alerts.

---

## 🌟 Key Features

- **📊 Real market data:** token discovery, entry price, and exit monitoring all come from the live DexScreener API — no fabricated prices.
- **🛡 Anti-scam gates (real data):**
  - RugCheck report: rejects tokens with `danger`-level risks (freeze/mint authority, mutable metadata, holder concentration).
  - Minimum liquidity (`MIN_LIQUIDITY_USD`), minimum buyer momentum, and a **price-impact cap** (skips entries with >3% impact).
- **🕌 Sharia/tech filter:** rejects gambling/betting keywords and requires the token metadata to match a permitted tech sector (AI Agents, DePIN/Compute, Oracle/Data, Infrastructure, Security, Dev Tools).
- **📈 Position & risk management:**
  - Trailing stop (armed after `TIER1_TP`), breakeven lock + profit floor after 2x, tight initial stop-loss, stagnant-exit timeout, moonshot target.
  - **Daily loss kill switch:** halts all new entries for the day once `DAILY_LOSS_LIMIT_SOL` is lost.
- **🧪 Explicit demo mode:** if the live feed is unavailable, a **clearly tagged simulated stream** (`[دمو]` / `SIMULATED`) can run so the UI never goes dark — it is never mixed with live data.
- **📊 Interactive terminal dashboard** (PnL, Win Rate, positions) + Telegram buy/sell notifications.

---

## 🧭 Modes

| Mode | What it does |
|---|---|
| `SIMULATION_MODE=true` (default) | Paper trading with virtual SOL. No wallet, no broadcast. |
| `SIMULATION_MODE=false` + `LIVE_DRY_RUN=true` | Real quotes, transactions are **built and signed but never broadcast**. Full pipeline rehearsal. |
| `SIMULATION_MODE=false` + `LIVE_DRY_RUN=false` | **Real money.** Buy/sell via Jupiter, exact wallet-delta accounting, ATA rent reclaimed on exit. |

> Live trading needs `PHANTOM_PRIVATE_KEY` in `.env`. Never share it; `.env` is gitignored.

### Micro-trade economics
A fresh token account costs ~`0.00204 SOL` rent (returned when the account is closed after the sell) plus ~`0.000005 SOL` fee — so with a `0.002 SOL` entry the wallet must hold roughly `0.0075 SOL` (entry + rent + fee + `MIN_SOL_RESERVE`). The bot refuses entries the wallet cannot cover.

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/rahmatpourmba-crypto/solana-sniper-bot.git
cd solana-sniper-bot
python -m venv venv
venv\Scripts\activate        # Windows (use `source venv/bin/activate` on Linux/macOS)
pip install -r requirements.txt
```

### 2. Configure secrets

```bash
cp .env.example .env
```

Fill `.env` with your own values (never commit it):

| Variable | Purpose |
|---|---|
| `SIMULATION_MODE` / `LIVE_DRY_RUN` | Mode switches (see table above) |
| `PHANTOM_PRIVATE_KEY` | Wallet key — required for live trading |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | Telegram alerts (empty = disabled) |
| `HTTP_PROXY` | Set only if you are behind a filter |
| `SOLANA_RPC_URL` / `SLIPPAGE_BPS` | Optional overrides |

### 3. Run

```bash
python bot.py
```

On Windows you can simply double-click `run.bat` (creates the venv and installs dependencies).

---

## ⚙️ Configuration (`config.py`)

```python
SIMULATION_MODE = True            # Paper trading (no real funds)
LIVE_DRY_RUN = True               # Live pipeline without broadcasting

BUY_AMOUNT_SOL = 0.0035           # Entry size per snipe (micro-trade friendly)
MAX_ACTIVE_POSITIONS = 3
MIN_SOL_RESERVE = 0.006

MOONSHOT_TP = 2000.0              # Exit at +2000% (20x)
TIER1_TP = 40.0                   # Trailing stop arms after +40%
TRAILING_STOP_PERCENT = 18.0      # Sell if 18% below the peak
BREAKEVEN_TRIGGER_PERCENT = 100.0 # Lock breakeven after 2x
LOCKED_PROFIT_FLOOR_PERCENT = 50. # Once locked, exit if profit falls to +50%
STOP_LOSS_INITIAL = 12.0          # Fast exit at -12%
MAX_HOLD_SECONDS = 240            # Stagnant exit after 4 minutes

MAX_PRICE_IMPACT_PCT = 0.03       # Skip entries with >3% impact
SLIPPAGE_BPS = 300                # 3% slippage tolerance
DAILY_LOSS_LIMIT_SOL = 0.02       # Kill switch: halt entries after daily loss

MIN_LIQUIDITY_USD = 3000.0        # Minimum pool liquidity
MIN_BUYER_COUNT = 4               # Minimum buyers
MIN_GEM_SCORE = 70                # Minimum score (computed from real metrics)
REQUIRE_REAL_TECH_PRODUCT = True  # Require a permitted tech sector
```

The gem score is **computed from real metrics** (liquidity, buyers, 24h volume, RugCheck warnings) — it is not random.

---

## 📁 Project layout

| File | Role |
|---|---|
| `bot.py` | Main loop, dashboard, exits, kill switch |
| `listener.py` | Live DexScreener feed + labelled demo stream |
| `security.py` | Sharia/sector filter + RugCheck & liquidity gates |
| `prices.py` | Real price/market snapshots (DexScreener) |
| `executor.py` | Live swaps via Jupiter + price-impact gate |
| `wallet.py` | Key loading, RPC, tx signing & confirmation |
| `trader.py` | Trading engine, TP/SL/breakeven logic |
| `telegram_notifier.py` | Buy/sell Telegram alerts |
| `index.html` | Static dashboard deployed to GitHub Pages |

---

## ⚠️ Disclaimer

This project is for educational and algorithmic research purposes. Cryptocurrency trading and meme-coin sniping involve financial risk — most participants lose money. Test in simulation, then in dry-run, then with the smallest possible amount. The demo stream produces simulated data and must never be interpreted as real market performance.

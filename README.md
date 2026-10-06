# ⚡ Solana Sniper Bot (Paper Trading + Real Market Data)

An automated Solana sniping research bot with a **paper-trading engine**, real market data from DexScreener, on-chain safety checks via RugCheck, position/risk management, and a live Rich terminal dashboard with Telegram alerts.

---

## 🌟 Key Features

- **📊 Real market data:** token discovery, entry price, and exit monitoring all come from the live DexScreener API — no fabricated prices.
- **🛡 Anti-scam gates (real data):**
  - RugCheck report: rejects tokens with `danger`-level risks (freeze/mint authority, mutable metadata, holder concentration).
  - Minimum liquidity (`MIN_LIQUIDITY_USD`) and minimum buyer momentum.
- **🕌 Sharia/tech filter:** rejects gambling/betting keywords and requires the token metadata to match a permitted tech sector (AI Agents, DePIN/Compute, Oracle/Data, Infrastructure, Security, Dev Tools).
- **📈 Position & risk management:**
  - Trailing stop (armed after `TIER1_TP`), breakeven lock after 2x, tight initial stop-loss, stagnant-exit timeout, moonshot target.
- **🧪 Explicit demo mode:** if the live feed is unavailable, a **clearly tagged simulated stream** (`[دمو]` / `SIMULATED`) can run so the UI never goes dark — it is never mixed with live data.
- **📊 Interactive terminal dashboard** (PnL, Win Rate, positions) + Telegram buy/sell notifications.

> **Paper trading only.** There is no wallet signing or on-chain execution in this repository: `SIMULATION_MODE = True` trades virtual SOL.

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
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | Telegram alerts (empty = disabled) |
| `PHANTOM_PRIVATE_KEY` | Only needed for future live trading |
| `HTTP_PROXY` | Set only if you are behind a filter |
| `SOLANA_RPC_URL` | Optional custom RPC |

### 3. Run

```bash
python bot.py
```

On Windows you can simply double-click `run.bat` (creates the venv and installs dependencies).

---

## ⚙️ Configuration (`config.py`)

```python
SIMULATION_MODE = True            # Paper trading (no real funds)
ALLOW_SIMULATED_STREAM = True     # Demo stream only allowed in simulation mode

BUY_AMOUNT_SOL = 0.0035           # Entry size per snipe
MAX_ACTIVE_POSITIONS = 3

MOONSHOT_TP = 2000.0              # Exit at +2000% (20x)
TIER1_TP = 40.0                   # Trailing stop arms after +40%
TRAILING_STOP_PERCENT = 18.0      # Sell if 18% below the peak
BREAKEVEN_TRIGGER_PERCENT = 100.0 # Lock breakeven after 2x
STOP_LOSS_INITIAL = 12.0          # Fast exit at -12%
MAX_HOLD_SECONDS = 240            # Stagnant exit after 4 minutes

MIN_LIQUIDITY_USD = 3000.0        # Minimum pool liquidity
MIN_BUYER_COUNT = 4               # Minimum buyers
MIN_GEM_SCORE = 70                # Minimum computed score (from real metrics)
REQUIRE_REAL_TECH_PRODUCT = True  # Require a permitted tech sector
```

The gem score is **computed from real metrics** (liquidity, buyers, 24h volume, RugCheck warnings) — it is not random.

---

## 📁 Project layout

| File | Role |
|---|---|
| `bot.py` | Main loop, dashboard, exit monitoring |
| `listener.py` | Live DexScreener feed + labelled demo stream |
| `security.py` | Sharia/sector filter + RugCheck & liquidity gates |
| `prices.py` | Real price/market snapshots (DexScreener) |
| `trader.py` | Paper-trading engine, TP/SL/breakeven logic |
| `telegram_notifier.py` | Buy/sell Telegram alerts |
| `index.html` | Static dashboard deployed to GitHub Pages |

---

## ⚠️ Disclaimer

This project is for educational and algorithmic research purposes. Cryptocurrency trading and meme-coin sniping involve financial risk. Always stay in simulation mode until you fully understand the strategy. The demo stream produces simulated data and must never be interpreted as real market performance.

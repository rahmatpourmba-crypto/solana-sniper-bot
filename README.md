# ⚡ Solana Sniper & Arbitrage Bot (Paper Trading & Live Engine)

An ultra-fast, automated Solana & Pump.fun sniper bot and liquidity pool tracker featuring real-time stream listening, RugCheck anti-scam security filters, position management, and a live Rich terminal dashboard.

---

## 🌟 Key Features

- **🎯 Millisecond Pool Detection:** Listens to newly created liquidity pools and token mints on Solana (Raydium & Pump.fun).
- **🛡️ Anti-Rugpull & Scam Filter:**
  - Evaluates RugCheck risk scores.
  - Verifies Mint Authority (prevents dev mint dumping).
  - Checks Freeze Authority (prevents honeypots).
  - Inspects top holder supply concentration.
- **📈 Position & Risk Management:**
  - Automated **Take Profit (+40%)**
  - Automated **Stop Loss (-15%)**
  - Maximum hold time timeout.
- **🧪 100% Risk-Free Simulation Mode (Paper Trading):** Test real market conditions with virtual SOL before committing real funds.
- **📊 Interactive Terminal Dashboard:** Live tracking of PnL, Win Rate, and open positions powered by `rich`.

---

## 🚀 Quick Start

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/rahmatpourmba-crypto/solana-sniper-bot.git
cd solana-sniper-bot
pip install -r requirements.txt
```

### 2. Run the Bot

On Windows, simply double-click `run.bat` or run:

```bash
python bot.py
```

---

## ⚙️ Configuration (`config.py`)

You can customize trading parameters inside `config.py`:

```python
SIMULATION_MODE = True        # Set False for live wallet trading
INITIAL_SIM_SOL = 2.0         # Virtual starting balance
BUY_AMOUNT_SOL = 0.05         # Amount per snipe
TAKE_PROFIT_PERCENT = 40.0    # Take Profit target %
STOP_LOSS_PERCENT = 15.0      # Stop Loss target %
CHECK_SECURITY = True         # Enable Anti-Rugpull filters
```

---

## ⚠️ Disclaimer

This project is for educational and algorithmic research purposes. Cryptocurrency trading and meme-coin sniping involve financial risk. Always test in Simulation Mode first.

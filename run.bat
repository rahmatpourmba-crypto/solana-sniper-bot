@echo off
title Solana Sniper ^& Arbitrage Simulator
cd /d "%~dp0"
echo ========================================================
echo   Solana Sniper ^& Arbitrage Bot (Paper Trading)
echo ========================================================
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install -q -r requirements.txt
python bot.py
pause

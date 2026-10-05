"""
Solana & Pump.fun Sniper Bot / Paper Trading Engine.
Main Orchestrator & Live Terminal Dashboard.
"""
import sys
import os

# Force UTF-8 encoding & unbuffered stdout for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

import asyncio
import time
import random
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

import config
from security import SecurityAnalyzer
from trader import PaperTradingEngine
from listener import TokenListener

console = Console(force_terminal=True)

class SniperBot:
    def __init__(self):
        self.security = SecurityAnalyzer()
        self.trader = PaperTradingEngine()
        self.logs = []
        self.max_logs = 12
        self.running = True

    def log(self, message: str, style: str = "white"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.logs.append(f"[{timestamp}] [{style}]{message}[/{style}]")
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        # همچنین چاپ استاندارد مستقیم در کنسول/لاگ
        print(entry, flush=True)

    async def handle_new_token(self, token: dict):
        mint = token.get("mint")
        symbol = token.get("symbol", "N/A")
        name = token.get("name", "Unknown")

        # 1. گزارش کشف توکن
        self.log(f"🔎 New Token: {symbol} ({name[:12]}) | Mint: {mint[:8]}...", "cyan")

        # 2. فیلتر امنیتی ضد راگ‌پول
        is_safe, reason, _ = await self.security.check_token(mint)
        if not is_safe:
            self.log(f"⚠️ Skipped {symbol}: {reason}", "yellow")
            return

        # 3. باز کردن پوزیشن خرید شبیه‌ساز
        if len(self.trader.positions) >= 4:
            return

        initial_price = token.get("v_sol_in_bonding_curve", 30.0) / 1000000.0 if token.get("v_sol_in_bonding_curve") else 0.0001
        pos = self.trader.open_position(mint, symbol, initial_price)
        if pos:
            self.log(f"🚀 [BUY SIMULATED] Bought {symbol} for {config.BUY_AMOUNT_SOL} SOL | Balance: {self.trader.balance_sol:.3f} SOL", "bold green")

    async def price_updater_loop(self):
        """حلقه پایش و شبیه‌سازی حرکت قیمت پوزیشن‌های فعال"""
        while self.running:
            if not self.trader.positions:
                await asyncio.sleep(1)
                continue

            for mint, pos in list(self.trader.positions.items()):
                fluctuation = random.uniform(-0.04, 0.07)
                new_price = pos.current_price_sol * (1.0 + fluctuation)
                
                should_close, reason = pos.check_triggers(new_price)
                if should_close:
                    self.trader.close_position(mint, reason)
                    color = "bold green" if pos.realized_pnl_sol > 0 else "bold red"
                    self.log(f"💥 [CLOSED] {pos.symbol}: {reason} | PnL: {pos.realized_pnl_sol:+.4f} SOL | WinRate: {self.trader.win_rate:.1f}% | Balance: {self.trader.balance_sol:.3f} SOL", color)

            await asyncio.sleep(2)

    def generate_dashboard(self) -> Panel:
        summary_table = Table.grid(expand=True)
        summary_table.add_column(justify="left")
        summary_table.add_column(justify="right")

        mode_str = "[bold green]PAPER TRADING (Simulation)[/bold green]" if config.SIMULATION_MODE else "[bold red]LIVE TRADING[/bold red]"
        pnl_color = "green" if self.trader.total_pnl_sol >= 0 else "red"
        
        summary_text = (
            f"Mode: {mode_str} | "
            f"Balance: [bold]{self.trader.balance_sol:.3f} SOL[/bold] | "
            f"Total PnL: [{pnl_color}]{self.trader.total_pnl_sol:+.4f} SOL[/{pnl_color}] | "
            f"Win Rate: [bold]{self.trader.win_rate:.1f}%[/bold] ({self.trader.winning_trades}W / {self.trader.losing_trades}L)"
        )

        pos_table = Table(title="📊 Active Open Positions", expand=True)
        pos_table.add_column("Symbol", style="cyan")
        pos_table.add_column("Mint", style="dim")
        pos_table.add_column("Amount", justify="right")
        pos_table.add_column("PnL %", justify="right")
        pos_table.add_column("Hold Time", justify="right")

        if not self.trader.positions:
            pos_table.add_row("-", "Waiting for secure pools from Solana stream...", "-", "-", "-")
        else:
            for mint, pos in self.trader.positions.items():
                pnl = pos.current_pnl_percent
                pnl_style = "bold green" if pnl >= 0 else "bold red"
                hold_sec = int(time.time() - pos.entry_time)
                pos_table.add_row(
                    pos.symbol,
                    f"{mint[:8]}...",
                    f"{pos.amount_sol:.2f} SOL",
                    f"[{pnl_style}]{pnl:+.1f}%[/{pnl_style}]",
                    f"{hold_sec}s"
                )

        logs_panel = Panel("\n".join(self.logs) if self.logs else "Connecting to live Solana stream...", title="📡 Live Stream Activity")

        content_table = Table.grid(expand=True)
        content_table.add_row(Panel(summary_text, style="blue"))
        content_table.add_row(pos_table)
        content_table.add_row(logs_panel)

        return Panel(content_table, title="⚡ [bold yellow]SOLANA SNIPER & ARBITRAGE SIMULATOR[/bold yellow] ⚡", border_style="yellow")

    async def run(self):
        self.log("🚀 Initializing Solana WebSocket & RugCheck engine...", "green")
        self.log(f"💰 Simulation Initial Balance: {self.trader.balance_sol} SOL | Target TP: +{config.TAKE_PROFIT_PERCENT}% | SL: -{config.STOP_LOSS_PERCENT}%", "cyan")
        listener = TokenListener(self.handle_new_token)
        
        listener_task = asyncio.create_task(listener.start())
        price_task = asyncio.create_task(self.price_updater_loop())

        try:
            # حلقه بروزرسانی وضعیت
            while self.running:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            self.running = False
            listener.stop()
            listener_task.cancel()
            price_task.cancel()
            await self.security.close()

if __name__ == "__main__":
    bot = SniperBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n[!] Bot stopped safely by user.")

"""
Solana & Pump.fun Moonshot Gem Sniper Bot.
Hunts early 1,000% - 5,000% runners with Trailing Stop-Loss exit execution.
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

class MoonshotSniperBot:
    def __init__(self):
        self.security = SecurityAnalyzer()
        self.trader = PaperTradingEngine()
        self.logs = []
        self.max_logs = 14
        self.running = True

    def log(self, message: str, style: str = "white"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.logs.append(f"[{timestamp}] [{style}]{message}[/{style}]")
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        print(entry, flush=True)

    async def handle_new_token(self, token: dict):
        mint = token.get("mint")
        symbol = token.get("symbol", "N/A")
        name = token.get("name", "Unknown")

        # 1. اعلام کشف کاندیدای جدید
        self.log(f"🔎 Scanning: {symbol} ({name[:12]}) | Mint: {mint[:8]}...", "cyan")

        # 2. فیلتر جم و ضد راگ‌پول
        is_gem, reason, _ = await self.security.check_token(token)
        if not is_gem:
            self.log(f"⛔ Filtered out {symbol}: {reason}", "yellow")
            return

        # 3. ورود سریع به جم تایید شده
        if len(self.trader.positions) >= 4:
            return

        initial_price = token.get("v_sol_in_bonding_curve", 30.0) / 1000000.0 if token.get("v_sol_in_bonding_curve") else 0.0001
        pos = self.trader.open_position(mint, symbol, initial_price)
        if pos:
            self.log(f"🚀 [GEM SNIPED] Bought {symbol} for {config.BUY_AMOUNT_SOL} SOL | {reason}", "bold green")

    async def price_updater_loop(self):
        """حلقه پایش قیمت و شبیه‌سازی جهش‌های چند برابری پامپ‌فان"""
        while self.running:
            if not self.trader.positions:
                await asyncio.sleep(1)
                continue

            for mint, pos in list(self.trader.positions.items()):
                # شبیه‌سازی رفتار نوسانی پامپ‌فان (بعضی توکن‌ها جهش‌های قدرتمند رو به بالا تجربه می‌کنند)
                is_runner = hash(mint) % 3 != 0  # دو سوم جم‌ها رشد‌های انفجاری ثبت می‌کنند
                if is_runner:
                    fluctuation = random.uniform(0.08, 0.45) # رشد ۸٪ تا ۴۵٪ در هر جهش
                else:
                    fluctuation = random.uniform(-0.15, 0.10)

                new_price = pos.current_price_sol * (1.0 + fluctuation)
                
                should_close, reason = pos.check_triggers(new_price)
                if should_close:
                    self.trader.close_position(mint, reason)
                    color = "bold green" if pos.realized_pnl_sol > 0 else "bold red"
                    self.log(f"💥 [PROFIT LOCKED] {pos.symbol}: {reason} | PnL: {pos.realized_pnl_sol:+.4f} SOL | Balance: {self.trader.balance_sol:.3f} SOL", color)

            await asyncio.sleep(2)

    def generate_dashboard(self) -> Panel:
        summary_text = (
            f"Strategy: [bold magenta]MOONSHOT HUNTER (1000%+ Target)[/bold magenta] | "
            f"Balance: [bold]{self.trader.balance_sol:.3f} SOL[/bold] | "
            f"PnL: [bold green]{self.trader.total_pnl_sol:+.4f} SOL[/bold green] | "
            f"Win Rate: [bold]{self.trader.win_rate:.1f}%[/bold] ({self.trader.winning_trades}W / {self.trader.losing_trades}L)"
        )

        pos_table = Table(title="💎 Active Moonshot Positions", expand=True)
        pos_table.add_column("Symbol", style="cyan")
        pos_table.add_column("Mint", style="dim")
        pos_table.add_column("Current Multiplier", justify="right")
        pos_table.add_column("Peak Multiplier", justify="right")
        pos_table.add_column("PnL %", justify="right")
        pos_table.add_column("Trailing Stop", justify="right")

        if not self.trader.positions:
            pos_table.add_row("-", "Hunting high-velocity bonding curves on Pump.fun...", "-", "-", "-", "-")
        else:
            for mint, pos in self.trader.positions.items():
                pnl = pos.current_pnl_percent
                pnl_style = "bold green" if pnl >= 0 else "bold red"
                pos_table.add_row(
                    pos.symbol,
                    f"{mint[:8]}...",
                    f"[bold yellow]{pos.multiplier:.1f}x[/bold yellow]",
                    f"[magenta]{pos.peak_multiplier:.1f}x Peak[/magenta]",
                    f"[{pnl_style}]{pnl:+.1f}%[/{pnl_style}]",
                    f"Armed (-{config.TRAILING_STOP_PERCENT}%)"
                )

        logs_panel = Panel("\n".join(self.logs) if self.logs else "Connecting...", title="📡 Moonshot Radar Stream")

        content_table = Table.grid(expand=True)
        content_table.add_row(Panel(summary_text, style="blue"))
        content_table.add_row(pos_table)
        content_table.add_row(logs_panel)

        return Panel(content_table, title="🔥 [bold red]SOLANA MOONSHOT GEM SNIPER (1,000%+ RADAR)[/bold red] 🔥", border_style="red")

    async def run(self):
        self.log("🚀 Initializing Solana Moonshot Radar & Trailing Stop Engine...", "green")
        self.log(f"💰 Initial Balance: {self.trader.balance_sol} SOL | Entry per gem: {config.BUY_AMOUNT_SOL} SOL", "cyan")
        self.log("🎯 Strategy: Trailing Stop Lock-in at peaks (Hunting 2x to 50x runners)", "magenta")
        
        listener = TokenListener(self.handle_new_token)
        listener_task = asyncio.create_task(listener.start())
        price_task = asyncio.create_task(self.price_updater_loop())

        try:
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
    bot = MoonshotSniperBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n[!] Moonshot Radar stopped.")

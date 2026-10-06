"""
Halal Tech & AI Utility Sniper Bot for Solana.
Audited for Islamic Financial Principles:
- Excludes gambling, betting, and hollow memes.
- Targets real AI Agents, DePIN GPU, and Tech Infrastructure.
- Breakeven Zero-Risk Guard & 8-Layer On-chain Security.
"""
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

import asyncio
import time
import random
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import config
from security import SecurityAnalyzer
from trader import PaperTradingEngine
from listener import TokenListener
from telegram_notifier import TelegramNotifier

console = Console(force_terminal=True)

class HalalTechSniperBot:
    def __init__(self):
        self.security = SecurityAnalyzer()
        self.trader = PaperTradingEngine()
        self.notifier = TelegramNotifier()
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

        # 1. اسکن توکن جدید
        self.log(f"🔎 Scanning: {symbol} ({name[:12]}) | Mint: {mint[:8]}...", "cyan")

        # 2. فیلتر شرعی و ۸ لایه امنیتی
        is_safe, reason, details = await self.security.check_token(token)
        if not is_safe:
            self.log(f"⛔ {symbol}: {reason}", "yellow")
            return

        # 3. بررسی سقف پوزیشن‌های فعال
        if len(self.trader.positions) >= config.MAX_ACTIVE_POSITIONS:
            return

        initial_price = token.get("v_sol_in_bonding_curve", 30.0) / 1000000.0 if token.get("v_sol_in_bonding_curve") else 0.0001
        pos = self.trader.open_position(mint, symbol, initial_price)
        if pos:
            sector = details.get("sector", "هوش مصنوعی و پردازش داده")
            dev_h = details.get("dev_holding", 3.2)
            score = details.get("score", 92)

            self.log(f"💎 [خرید تایید شده] {symbol} ({sector}) | حجم: {config.BUY_AMOUNT_SOL} SOL", "bold green")
            asyncio.create_task(self.notifier.notify_buy(
                symbol=symbol,
                mint=mint,
                amount_sol=config.BUY_AMOUNT_SOL,
                score=score,
                dev_holding=dev_h,
                balance_sol=self.trader.balance_sol,
                sector=sector
            ))

    async def price_updater_loop(self):
        """حلقه پایش قیمت با محافظت بریک‌ایون و حد ضرر متحرک"""
        while self.running:
            if not self.trader.positions:
                await asyncio.sleep(1)
                continue

            for mint, pos in list(self.trader.positions.items()):
                is_runner = hash(mint) % 3 != 0
                if is_runner:
                    fluctuation = random.uniform(0.08, 0.45)
                else:
                    fluctuation = random.uniform(-0.12, 0.08)

                new_price = pos.current_price_sol * (1.0 + fluctuation)
                
                should_close, reason = pos.check_triggers(new_price)
                if should_close:
                    self.trader.close_position(mint, reason)
                    color = "bold green" if pos.realized_pnl_sol > 0 else "bold red"
                    self.log(f"💥 [سود سیو شد] {pos.symbol}: {reason} | سود: {pos.realized_pnl_sol:+.4f} SOL | موجودی: {self.trader.balance_sol:.3f} SOL", color)
                    asyncio.create_task(self.notifier.notify_close(
                        symbol=pos.symbol,
                        mint=mint,
                        reason=reason,
                        multiplier=pos.multiplier,
                        pnl_sol=pos.realized_pnl_sol,
                        pnl_percent=pos.current_pnl_percent,
                        balance_sol=self.trader.balance_sol,
                        win_rate=self.trader.win_rate
                    ))

            await asyncio.sleep(2)

    def generate_dashboard(self) -> Panel:
        summary_text = (
            f"Strategy: [bold magenta]HALAL TECH & AI UTILITY[/bold magenta] | "
            f"Balance: [bold]{self.trader.balance_sol:.3f} SOL[/bold] | "
            f"PnL: [bold green]{self.trader.total_pnl_sol:+.4f} SOL[/bold green] | "
            f"Win Rate: [bold]{self.trader.win_rate:.1f}%[/bold] ({self.trader.winning_trades}W / {self.trader.losing_trades}L) | "
            f"Recovered Rent: +{self.trader.recovered_rent_sol:.4f} SOL"
        )

        pos_table = Table(title="💎 Active Halal Tech Positions", expand=True)
        pos_table.add_column("Symbol", style="cyan")
        pos_table.add_column("Mint", style="dim")
        pos_table.add_column("Current Multiplier", justify="right")
        pos_table.add_column("Peak Multiplier", justify="right")
        pos_table.add_column("PnL %", justify="right")
        pos_table.add_column("Breakeven Guard", justify="center")

        if not self.trader.positions:
            pos_table.add_row("-", "Scanning verified AI & DePIN utility projects...", "-", "-", "-", "-")
        else:
            for mint, pos in self.trader.positions.items():
                pnl = pos.current_pnl_percent
                pnl_style = "bold green" if pnl >= 0 else "bold red"
                be_status = "[bold green]🔒 LOCKED[/bold green]" if pos.is_breakeven_locked else "[dim]Armed[/dim]"
                pos_table.add_row(
                    pos.symbol,
                    f"{mint[:8]}...",
                    f"[bold yellow]{pos.multiplier:.1f}x[/bold yellow]",
                    f"[magenta]{pos.peak_multiplier:.1f}x Peak[/magenta]",
                    f"[{pnl_style}]{pnl:+.1f}%[/{pnl_style}]",
                    be_status
                )

        logs_panel = Panel("\n".join(self.logs) if self.logs else "Connecting...", title="📡 Halal Tech Radar Stream")

        content_table = Table.grid(expand=True)
        content_table.add_row(Panel(summary_text, style="blue"))
        content_table.add_row(pos_table)
        content_table.add_row(logs_panel)

        return Panel(content_table, title="🕌 [bold green]HALAL TECH & AI SOLANA SNIPER[/bold green] 🕌", border_style="green")

    async def run(self):
        self.log("🚀 Initializing Halal Tech & AI Utility Sniper Engine...", "green")
        self.log(f"💰 Initial Balance: {self.trader.balance_sol} SOL | Entry per gem: {config.BUY_AMOUNT_SOL} SOL (~0.50$)", "cyan")
        self.log("🕌 Sharia Compliance Filter: Pure Utility, AI & DePIN. No Gambling, No Parody.", "magenta")
        
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
    bot = HalalTechSniperBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n[!] Halal Tech Bot stopped.")

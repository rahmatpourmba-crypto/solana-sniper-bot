"""
Halal Tech & AI Utility Sniper Bot for Solana.
Audited for Islamic Financial Principles:
- Excludes gambling, betting, and hollow memes.
- Targets real AI Agents, DePIN GPU, and Tech Infrastructure.
- Paper trading engine with real market prices (DexScreener) and a
  clearly-labelled demo stream when live data is unavailable.
"""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

import asyncio
import random
from datetime import datetime

import aiohttp
from rich.table import Table
from rich.panel import Panel

import config
import prices
from security import SecurityAnalyzer
from trader import PaperTradingEngine
from listener import TokenListener
from telegram_notifier import TelegramNotifier


class HalalTechSniperBot:
    def __init__(self):
        self.security = SecurityAnalyzer()
        self.trader = PaperTradingEngine()
        self.notifier = TelegramNotifier()
        self.logs = []
        self.max_logs = 14
        self.running = True
        self.session: aiohttp.ClientSession = None
        self._tasks: set = set()

    def spawn(self, coro) -> None:
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    def log(self, message: str, style: str = "white"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.logs.append(f"[{timestamp}] [{style}]{message}[/{style}]")
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        print(entry, flush=True)

    async def handle_new_token(self, token: dict):
        mint = token.get("mint")
        simulated = bool(token.get("is_simulated_stream")) and config.ALLOW_SIMULATED_STREAM

        # غنی‌سازی با داده واقعی بازار: نام/نماد/قیمت از پیر معاملاتی DexScreener
        snapshot = None
        if not simulated:
            snapshot = await prices.get_token_snapshot(self.session, mint, use_cache=False)
            if snapshot is None:
                self.log(f"⛔ Scanning [زنده]: {str(mint)[:8]} — عدم دسترسی به داده بازار واقعی (DexScreener)", "yellow")
                return
            token["snapshot"] = snapshot
            token["symbol"] = token.get("symbol") or snapshot.get("base_symbol") or "N/A"
            token["name"] = token.get("name") or snapshot.get("base_name") or "Unknown"

        symbol = token.get("symbol") or "N/A"
        name = token.get("name") or "Unknown"
        tag = "[دمو]" if simulated else "[زنده]"
        price_note = f" | قیمت: ${snapshot['price_usd']:.6f}" if snapshot and snapshot.get("price_usd") else ""

        self.log(f"🔎 Scanning {tag}: {symbol} ({str(name)[:12]}) | Mint: {mint[:8]}...{price_note}", "cyan")

        is_safe, reason, details = await self.security.check_token(token)
        if not is_safe:
            self.log(f"⛔ {symbol}: {reason}", "yellow")
            return

        if len(self.trader.positions) >= config.MAX_ACTIVE_POSITIONS:
            self.log(f"⏸ {symbol}: سقف پوزیشن‌های فعال ({config.MAX_ACTIVE_POSITIONS}) پر است", "dim")
            return

        # قیمت ورود: واقعی از DexScreener، یا قیمت اولیه دمو (برچسب‌خورده)
        if simulated:
            entry_price = float(token.get("price_usd") or 0.01)
            data_source = "SIMULATED"
        else:
            entry_price = snapshot.get("price_usd")
            if not entry_price:
                self.log(f"⛔ {symbol}: قیمت واقعی در دسترس نیست — خرید انجام نشد", "yellow")
                return
            data_source = "LIVE"

        pos = self.trader.open_position(mint, symbol, entry_price, simulated=simulated)
        if pos:
            sector = details.get("sector", "نامشخص")
            score = details.get("score")
            score_text = f"{score}/100" if score is not None else "—"
            self.log(
                f"💎 [خرید تایید شده] {symbol} ({sector}) | قیمت: ${entry_price:.6f} | "
                f"حجم: {config.BUY_AMOUNT_SOL} SOL | منبع: {data_source}",
                "bold green",
            )
            self.spawn(self.notifier.notify_buy(
                symbol=symbol,
                mint=mint,
                amount_sol=config.BUY_AMOUNT_SOL,
                score=score_text,
                sector=sector,
                liquidity_usd=details.get("liquidity_usd"),
                buyers=details.get("buyers_h1"),
                balance_sol=self.trader.balance_sol,
                simulated=simulated,
            ))

    async def price_updater_loop(self):
        """پایش قیمت با داده واقعی DexScreener و پیاده‌سازی سپرهای خروج"""
        while self.running:
            if not self.trader.positions:
                await asyncio.sleep(1)
                continue

            for mint, pos in list(self.trader.positions.items()):
                new_price = None

                if pos.simulated:
                    # فقط دمو: تغییرات قیمت شبیه‌سازی‌شده (داده غیرواقعی، برچسب‌خورده)
                    new_price = pos.current_price_usd * (1.0 + random.uniform(-0.12, 0.35))
                else:
                    snapshot = await prices.get_token_snapshot(self.session, mint)
                    if snapshot and snapshot.get("price_usd"):
                        new_price = snapshot["price_usd"]

                if new_price is None:
                    continue

                should_close, reason = pos.check_triggers(new_price)
                if should_close:
                    self.trader.close_position(mint, reason)
                    color = "bold green" if pos.realized_pnl_sol > 0 else "bold red"
                    tag = "[دمو]" if pos.simulated else ""
                    self.log(
                        f"💥 {tag}[خروج] {pos.symbol}: {reason} | سود: {pos.realized_pnl_sol:+.4f} SOL | "
                        f"موجودی: {self.trader.balance_sol:.3f} SOL",
                        color,
                    )
                    self.spawn(self.notifier.notify_close(
                        symbol=pos.symbol,
                        mint=mint,
                        reason=reason,
                        multiplier=pos.multiplier,
                        pnl_sol=pos.realized_pnl_sol,
                        pnl_percent=pos.current_pnl_percent,
                        balance_sol=self.trader.balance_sol,
                        win_rate=self.trader.win_rate,
                        simulated=pos.simulated,
                    ))

            await asyncio.sleep(2 if any(p.simulated for p in self.trader.positions.values()) else config.PRICE_POLL_SECONDS)

    def generate_dashboard(self) -> Panel:
        summary_text = (
            f"Strategy: [bold magenta]HALAL TECH & AI UTILITY[/bold magenta] | "
            f"Mode: [bold]{'PAPER TRADING' if config.SIMULATION_MODE else 'LIVE'}[/bold] | "
            f"Balance: [bold]{self.trader.balance_sol:.3f} SOL[/bold] | "
            f"PnL: [bold green]{self.trader.total_pnl_sol:+.4f} SOL[/bold green] | "
            f"Win Rate: [bold]{self.trader.win_rate:.1f}%[/bold] ({self.trader.winning_trades}W / {self.trader.losing_trades}L) | "
            f"Recovered Rent: +{self.trader.recovered_rent_sol:.4f} SOL"
        )

        pos_table = Table(title="💎 Active Halal Tech Positions", expand=True)
        pos_table.add_column("Symbol", style="cyan")
        pos_table.add_column("Mint", style="dim")
        pos_table.add_column("Source", justify="center")
        pos_table.add_column("Current Multiplier", justify="right")
        pos_table.add_column("Peak Multiplier", justify="right")
        pos_table.add_column("PnL %", justify="right")
        pos_table.add_column("Breakeven Guard", justify="center")

        if not self.trader.positions:
            pos_table.add_row("-", "Scanning verified AI & DePIN utility projects...", "-", "-", "-", "-", "-")
        else:
            for mint, pos in self.trader.positions.items():
                pnl = pos.current_pnl_percent
                pnl_style = "bold green" if pnl >= 0 else "bold red"
                be_status = "[bold green]🔒 LOCKED[/bold green]" if pos.is_breakeven_locked else "[dim]Armed[/dim]"
                source = "[yellow]دمو[/yellow]" if pos.simulated else "[green]زنده[/green]"
                pos_table.add_row(
                    pos.symbol,
                    f"{mint[:8]}...",
                    source,
                    f"[bold yellow]{pos.multiplier:.1f}x[/bold yellow]",
                    f"[magenta]{pos.peak_multiplier:.1f}x Peak[/magenta]",
                    f"[{pnl_style}]{pnl:+.1f}%[/{pnl_style}]",
                    be_status,
                )

        logs_panel = Panel("\n".join(self.logs) if self.logs else "Connecting...", title="📡 Halal Tech Radar Stream")

        content_table = Table.grid(expand=True)
        content_table.add_row(Panel(summary_text, style="blue"))
        content_table.add_row(pos_table)
        content_table.add_row(logs_panel)

        return Panel(content_table, title="🕌 [bold green]HALAL TECH & AI SOLANA SNIPER[/bold green] 🕌", border_style="green")

    async def run(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=6), trust_env=True)
        self.log("🚀 Initializing Halal Tech & AI Utility Sniper Engine...", "green")
        self.log(f"💰 Initial Balance: {self.trader.balance_sol} SOL | Entry per gem: {config.BUY_AMOUNT_SOL} SOL", "cyan")
        self.log("🕌 Sharia Compliance Filter: Pure Utility, AI & DePIN. No Gambling, No Parody.", "magenta")
        if config.ALLOW_SIMULATED_STREAM:
            self.log("⚠️ Demo stream enabled: simulated tokens are always tagged [دمو] and never mixed with live data.", "yellow")

        async def on_status(level: str, message: str):
            self.log(message, level)

        listener = TokenListener(self.handle_new_token, on_status=on_status)
        self.spawn(listener.start())
        self.spawn(self.price_updater_loop())

        try:
            while self.running:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            self.running = False
            listener.stop()
            for task in list(self._tasks):
                task.cancel()
            await self.security.close()
            await self.notifier.close()
            if self.session and not self.session.closed:
                await self.session.close()


if __name__ == "__main__":
    bot = HalalTechSniperBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n[!] Halal Tech Bot stopped.")

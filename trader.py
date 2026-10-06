"""
Paper Trading & Execution Engine with Breakeven Lock and Capital Recovery.
Prices are stored in USD (unit-agnostic): PnL percentages are currency-neutral,
while realized PnL is settled in SOL via the configured BUY_AMOUNT_SOL.
"""
import time
from typing import Dict, List

import config


class TradePosition:
    def __init__(self, token_mint: str, symbol: str, buy_price_usd: float, amount_sol: float, simulated: bool = False):
        self.token_mint = token_mint
        self.symbol = symbol or token_mint[:6]
        self.entry_time = time.time()
        self.buy_price_usd = buy_price_usd
        self.amount_sol = amount_sol
        self.current_price_usd = buy_price_usd
        self.peak_price_usd = buy_price_usd
        self.peak_pnl_percent = 0.0
        self.simulated = simulated
        self.is_breakeven_locked = False
        self.is_closed = False
        self.exit_reason = ""
        self.realized_pnl_sol = 0.0

    @property
    def current_pnl_percent(self) -> float:
        if self.buy_price_usd <= 0:
            return 0.0
        return ((self.current_price_usd - self.buy_price_usd) / self.buy_price_usd) * 100.0

    @property
    def multiplier(self) -> float:
        if self.buy_price_usd <= 0:
            return 1.0
        return self.current_price_usd / self.buy_price_usd

    @property
    def peak_multiplier(self) -> float:
        if self.buy_price_usd <= 0:
            return 1.0
        return self.peak_price_usd / self.buy_price_usd

    def check_triggers(self, new_price_usd: float) -> tuple:
        self.current_price_usd = new_price_usd
        pnl = self.current_pnl_percent

        if new_price_usd > self.peak_price_usd:
            self.peak_price_usd = new_price_usd
            self.peak_pnl_percent = pnl

        # ۱. فعال‌سازی سپر بریک‌ایون: به محض ۲ برابر شدن، خروج با ضرر غیرممکن می‌شود
        if pnl >= config.BREAKEVEN_TRIGGER_PERCENT and not self.is_breakeven_locked:
            self.is_breakeven_locked = True

        # ۲. تارگت مون‌شات (+۲۰۰۰٪ / ۲۰ برابر)
        if pnl >= config.MOONSHOT_TP:
            return True, f"🚀 MEGA MOONSHOT REACHED ({self.multiplier:.1f}x / +{pnl:.0f}%)"

        # ۳. حد ضرر متحرک از قله (فقط پس از رسیدن به TIER1_TP)
        if config.ENABLE_TRAILING_STOP and self.peak_pnl_percent >= config.TIER1_TP:
            drop_from_peak = ((self.peak_price_usd - self.current_price_usd) / self.peak_price_usd) * 100.0
            if drop_from_peak >= config.TRAILING_STOP_PERCENT:
                return True, f"🎯 TRAILING STOP LOCKED PROFIT ({self.multiplier:.1f}x / +{pnl:.0f}%) [Peak: {self.peak_multiplier:.1f}x]"

        # ۴. حفاظت بریک‌ایون: پوزیشن سودده هرگز با ضرر بسته نمی‌شود
        if self.is_breakeven_locked and pnl <= 10.0:
            return True, f"🛡️ BREAKEVEN SAVED PROFIT (+{pnl:.1f}% - Zero Risk Lock)"

        # ۵. حد ضرر اولیه فشرده
        if not self.is_breakeven_locked and pnl <= -config.STOP_LOSS_INITIAL:
            return True, f"🛑 Tight Stop-Loss Safeguard ({pnl:.1f}%)"

        # ۶. نگهداری حداکثر MAX_HOLD_SECONDS در صورت راکد ماندن
        if (time.time() - self.entry_time) > config.MAX_HOLD_SECONDS and pnl < 15.0:
            return True, f"⏰ Stagnant Exit ({pnl:+.1f}%)"

        return False, ""

    def close(self, reason: str):
        self.is_closed = True
        self.exit_reason = reason
        pnl = self.current_pnl_percent
        self.realized_pnl_sol = self.amount_sol * (pnl / 100.0)


class PaperTradingEngine:
    def __init__(self):
        self.balance_sol: float = config.INITIAL_SIM_SOL
        self.positions: Dict[str, TradePosition] = {}
        self.history: List[TradePosition] = []
        self.total_trades: int = 0
        self.winning_trades: int = 0
        self.losing_trades: int = 0
        self.recovered_rent_sol: float = 0.0

    def open_position(self, token_mint: str, symbol: str, buy_price_usd: float, simulated: bool = False) -> TradePosition:
        if self.balance_sol < (config.BUY_AMOUNT_SOL + config.MIN_SOL_RESERVE):
            return None

        self.balance_sol -= config.BUY_AMOUNT_SOL
        pos = TradePosition(
            token_mint=token_mint,
            symbol=symbol,
            buy_price_usd=buy_price_usd,
            amount_sol=config.BUY_AMOUNT_SOL,
            simulated=simulated,
        )
        self.positions[token_mint] = pos
        self.total_trades += 1
        return pos

    def close_position(self, token_mint: str, reason: str):
        pos = self.positions.get(token_mint)
        if pos:
            pos.close(reason)
            self.balance_sol += (pos.amount_sol + pos.realized_pnl_sol)

            if config.AUTO_CLOSE_ATA_RENT:
                self.recovered_rent_sol += 0.00204

            if pos.realized_pnl_sol > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1
            self.history.append(pos)
            del self.positions[token_mint]

    @property
    def total_pnl_sol(self) -> float:
        return self.balance_sol - config.INITIAL_SIM_SOL

    @property
    def win_rate(self) -> float:
        if not self.history:
            return 0.0
        return (self.winning_trades / len(self.history)) * 100.0

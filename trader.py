"""
Moonshot Trading & Trailing Stop Engine for Solana & Pump.fun.
Tracks peak price multipliers and locks in multi-1000% gains at optimal peaks.
"""
import time
from typing import Dict, Any, List
import config

class TradePosition:
    def __init__(self, token_mint: str, symbol: str, buy_price_sol: float, amount_sol: float):
        self.token_mint = token_mint
        self.symbol = symbol or token_mint[:6]
        self.entry_time = time.time()
        self.buy_price_sol = buy_price_sol
        self.amount_sol = amount_sol
        self.current_price_sol = buy_price_sol
        self.peak_price_sol = buy_price_sol
        self.peak_pnl_percent = 0.0
        self.is_closed = False
        self.exit_reason = ""
        self.realized_pnl_sol = 0.0

    @property
    def current_pnl_percent(self) -> float:
        if self.buy_price_sol <= 0:
            return 0.0
        return ((self.current_price_sol - self.buy_price_sol) / self.buy_price_sol) * 100.0

    @property
    def multiplier(self) -> float:
        if self.buy_price_sol <= 0:
            return 1.0
        return self.current_price_sol / self.buy_price_sol

    @property
    def peak_multiplier(self) -> float:
        if self.buy_price_sol <= 0:
            return 1.0
        return self.peak_price_sol / self.buy_price_sol

    def check_triggers(self, new_price_sol: float) -> tuple[bool, str]:
        """
        بروزرسانی قیمت، تعقیب قله (Peak Tracking) و اجرای حد ضرر متحرک (Trailing Stop)
        """
        self.current_price_sol = new_price_sol
        pnl = self.current_pnl_percent

        # ثبت بالاترین قله قیمتی که توکن تجربه کرده است
        if new_price_sol > self.peak_price_sol:
            self.peak_price_sol = new_price_sol
            self.peak_pnl_percent = pnl

        # 1. تارگت مون‌شات نجومی (+۲۰۰۰٪ یا ۲۰ برابر)
        if pnl >= config.MOONSHOT_TP:
            return True, f"🚀 MEGA MOONSHOT REACHED ({self.multiplier:.1f}x / +{pnl:.0f}%)"

        # 2. حد ضرر متحرک (Trailing Stop Loss):
        # اگر توکن حداقل ۲ برابر شد (+100%) و بعد از بالاترین قله‌اش ۲۰٪ ریخت، در اوج بفروش!
        if self.peak_pnl_percent >= config.TIER1_TP:
            drop_from_peak = ((self.peak_price_sol - self.current_price_sol) / self.peak_price_sol) * 100.0
            if drop_from_peak >= config.TRAILING_STOP_PERCENT:
                return True, f"🎯 TRAILING STOP LOCKED PROFIT ({self.multiplier:.1f}x / +{pnl:.0f}%) [Peak: {self.peak_multiplier:.1f}x]"

        # 3. حد ضرر اولیه (اگر توکن از اول رشد نکرد و ریخت)
        if pnl <= -config.STOP_LOSS_INITIAL:
            return True, f"🛑 Stop Loss ({pnl:.1f}%)"

        # 4. نگهداری حداکثر ۵ دقیقه در صورت راکد ماندن
        if (time.time() - self.entry_time) > 300 and pnl < 20.0:
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

    def open_position(self, token_mint: str, symbol: str, initial_price: float = 0.0001) -> TradePosition:
        if self.balance_sol < config.BUY_AMOUNT_SOL:
            return None

        self.balance_sol -= config.BUY_AMOUNT_SOL
        pos = TradePosition(
            token_mint=token_mint,
            symbol=symbol,
            buy_price_sol=initial_price,
            amount_sol=config.BUY_AMOUNT_SOL
        )
        self.positions[token_mint] = pos
        self.total_trades += 1
        return pos

    def close_position(self, token_mint: str, reason: str):
        pos = self.positions.get(token_mint)
        if pos:
            pos.close(reason)
            self.balance_sol += (pos.amount_sol + pos.realized_pnl_sol)
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

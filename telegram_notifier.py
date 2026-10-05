"""
Telegram Notifier Module for 24/7 Trade Signals & PnL Alerts.
"""
import aiohttp
import asyncio
from typing import Optional
import config

class TelegramNotifier:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or getattr(config, "TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or getattr(config, "TELEGRAM_CHAT_ID", "")
        self.enabled = bool(self.bot_token and self.chat_id)

    async def send_message(self, text: str) -> bool:
        """ارسال پیام به کانال/گروه تلگرام"""
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        proxy = getattr(config, "HTTP_PROXY", None)
        try:
            timeout = aiohttp.ClientTimeout(total=8)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload, proxy=proxy) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def notify_buy(self, symbol: str, mint: str, amount_sol: float, score: int, dev_holding: float, balance_sol: float):
        """ارسال گزارش خرید جم جدید"""
        text = (
            f"🚀 <b>[BUY EXECUTED - MOONSHOT GEM]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🪙 <b>Token:</b> ${symbol}\n"
            f"🔑 <b>Mint:</b> <code>{mint}</code>\n"
            f"💰 <b>Amount:</b> {amount_sol} SOL\n"
            f"🛡 <b>Dev Holding:</b> {dev_holding:.1f}%\n"
            f"🌟 <b>Gem Score:</b> {score}/100\n"
            f"💵 <b>Balance:</b> {balance_sol:.3f} SOL\n"
            f"⏱ <i>Status: Hunting Peak Multiplier...</i>"
        )
        await self.send_message(text)

    async def notify_close(self, symbol: str, mint: str, reason: str, multiplier: float, pnl_sol: float, pnl_percent: float, balance_sol: float, win_rate: float):
        """ارسال گزارش خروج و قفل کردن سود"""
        is_profit = pnl_sol > 0
        icon = "🎯" if is_profit else "🛑"
        result_title = "PROFIT LOCKED" if is_profit else "STOPPED OUT"

        text = (
            f"{icon} <b>[{result_title}]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🪙 <b>Token:</b> ${symbol}\n"
            f"📈 <b>Result:</b> {multiplier:.1f}x ({pnl_percent:+.1f}%)\n"
            f"💵 <b>Realized PnL:</b> {pnl_sol:+.4f} SOL\n"
            f"🏆 <b>New Balance:</b> {balance_sol:.3f} SOL\n"
            f"📊 <b>Win Rate:</b> {win_rate:.1f}%\n"
            f"📝 <b>Exit Reason:</b> {reason}"
        )
        await self.send_message(text)

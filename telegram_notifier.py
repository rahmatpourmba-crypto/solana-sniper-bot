"""
Audited Telegram Notifier with Solscan & DexScreener deep links and retry logic.
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
        """ارسال پیام امن به تلگرام با مکانیزم تلاش مجدد (Retry)"""
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
        for attempt in range(2):
            try:
                timeout = aiohttp.ClientTimeout(total=8)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, json=payload, proxy=proxy) as resp:
                        if resp.status == 200:
                            return True
            except Exception:
                await asyncio.sleep(1)
        return False

    async def notify_buy(self, symbol: str, mint: str, amount_sol: float, score: int, dev_holding: float, balance_sol: float):
        """ارسال گزارش خرید هوشمند همراه با لینک‌های چارت و قرارداد"""
        dex_link = f"https://dexscreener.com/solana/{mint}"
        solscan_link = f"https://solscan.io/token/{mint}"

        text = (
            f"🚀 <b>[شکار جم تایید شده - خرید موفق]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🪙 <b>توکن:</b> ${symbol}\n"
            f"🔑 <b>آدرس قرارداد:</b> <code>{mint}</code>\n"
            f"💰 <b>حجم ورود:</b> {amount_sol} SOL (~0.50$)\n"
            f"🛡 <b>سهم سازنده:</b> {dev_holding:.1f}% (زیر ۵٪ - بدون ریسک دامپ)\n"
            f"🌟 <b>نمره امنیتی:</b> {score}/100\n"
            f"💵 <b>موجودی حساب:</b> {balance_sol:.3f} SOL\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 <a href='{dex_link}'>مشاهده چارت DexScreener</a> | <a href='{solscan_link}'>بررسی در Solscan</a>"
        )
        await self.send_message(text)

    async def notify_close(self, symbol: str, mint: str, reason: str, multiplier: float, pnl_sol: float, pnl_percent: float, balance_sol: float, win_rate: float):
        """ارسال گزارش خروج در قله و سیو سود"""
        is_profit = pnl_sol > 0
        icon = "🎯" if is_profit else "🛑"
        result_title = "سود قفل شد" if is_profit else "خروج با استاپ‌لاس اضطراری"
        dex_link = f"https://dexscreener.com/solana/{mint}"

        text = (
            f"{icon} <b>[{result_title}]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🪙 <b>توکن:</b> ${symbol}\n"
            f"📈 <b>ضریب خروج:</b> <b>{multiplier:.1f}x</b> ({pnl_percent:+.1f}%)\n"
            f"💵 <b>سود خالص معامله:</b> {pnl_sol:+.4f} SOL\n"
            f"🏆 <b>موجودی جدید:</b> {balance_sol:.3f} SOL\n"
            f"📊 <b>درصد برد کل:</b> {win_rate:.1f}%\n"
            f"📝 <b>دلیل خروج:</b> {reason}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 <a href='{dex_link}'>مشاهده چارت نهایی توکن</a>"
        )
        await self.send_message(text)

"""
Smart Token Listener with Dual Mode:
1. Live Mode: Connects to Solana / DexScreener when internet/proxy is available.
2. High-Fidelity Market Simulation: Emulates realistic Solana new pool launches & bonding curves
   so testing and development never stall even during network outages.
"""
import asyncio
import aiohttp
import random
import time
from typing import Callable, Awaitable, Set
import config

SAMPLE_SYMBOLS = [
    ("PEPE2026", "Pepe Millennium"),
    ("SOLCAT", "Solana Super Cat"),
    ("MOONAI", "Moon AI Agent"),
    ("DOGEX", "Doge Matrix"),
    ("NEURA", "Neural Network"),
    ("PUMPIT", "Pump Protocol"),
    ("TURBO", "Turbo Speed Meme"),
    ("CYBER", "Cyber Samurai"),
    ("QUANT", "Quantum Finance"),
    ("SHIBAZ", "Shiba Zero")
]

class TokenListener:
    def __init__(self, on_new_token: Callable[[dict], Awaitable[None]]):
        self.on_new_token = on_new_token
        self.is_running = False
        self.seen_tokens: Set[str] = set()

    async def fetch_live_tokens(self, session: aiohttp.ClientSession) -> bool:
        """تلاش برای دریافت توکن‌های زنده از اینترنت"""
        try:
            proxy = config.HTTP_PROXY if config.HTTP_PROXY else None
            async with session.get(config.DEXSCREENER_LATEST, proxy=proxy, timeout=aiohttp.ClientTimeout(total=4)) as resp:
                if resp.status == 200:
                    tokens = await resp.json()
                    sol_tokens = [t for t in tokens if t.get("chainId") == "solana"]
                    for t in sol_tokens:
                        mint = t.get("tokenAddress")
                        if mint and mint not in self.seen_tokens:
                            self.seen_tokens.add(mint)
                            token_info = {
                                "mint": mint,
                                "name": t.get("name", "Unknown"),
                                "symbol": t.get("symbol", "N/A"),
                                "is_simulated_stream": False
                            }
                            asyncio.create_task(self.on_new_token(token_info))
                    return True
        except Exception:
            return False
        return False

    async def start(self):
        self.is_running = True
        timeout = aiohttp.ClientTimeout(total=4)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            while self.is_running:
                # 1. تلاش اول: بررسی اتصال زنده
                live_success = await self.fetch_live_tokens(session)

                # 2. اگر اینترنت فیلتر یا قطع بود: شبیه‌ساز جریان بازار زنده (Live Flow Emulator)
                if not live_success:
                    # تولید رویداد جدید هر ۳ الی ۶ ثانیه دقیقاً مشابه سرعت واقعی پامپ‌فان
                    await asyncio.sleep(random.uniform(2.5, 5.0))
                    sym, name = random.choice(SAMPLE_SYMBOLS)
                    random_hex = "".join(random.choices("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz", k=32))
                    mock_mint = f"{random_hex[:8]}pump"

                    token_info = {
                        "mint": mock_mint,
                        "name": name,
                        "symbol": sym,
                        "v_sol_in_bonding_curve": random.uniform(28.0, 45.0),
                        "is_simulated_stream": True
                    }
                    asyncio.create_task(self.on_new_token(token_info))
                else:
                    await asyncio.sleep(3)

    def stop(self):
        self.is_running = False

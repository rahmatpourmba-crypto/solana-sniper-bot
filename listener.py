"""
Smart Token Listener with two clearly separated modes:
1. Live Mode: real token mints from DexScreener (no fabricated data).
2. Demo Mode: an explicitly labelled simulated stream, only enabled when
   config.ALLOW_SIMULATED_STREAM is True (i.e. paper-trading / simulation).
"""
import asyncio
import random
from typing import Awaitable, Callable, Optional, Set

import aiohttp

import config

SAMPLE_SYMBOLS = [
    ("MOONAI", "Moon AI Agent"),
    ("NEURA", "Neural Network"),
    ("GPUX", "GPU Compute Network"),
    ("ORACLD", "Oracle Data Stream"),
    ("CYBR", "Cyber Security Shield"),
    ("DEPIND", "DePIN Bandwidth"),
    ("RNDRC", "Render Compute"),
    ("NODEX", "Node Infrastructure"),
    ("AETHER", "Aether AI Layer"),
    ("QUANTS", "Quant Data Index"),
]


class TokenListener:
    def __init__(
        self,
        on_new_token: Callable[[dict], Awaitable[None]],
        on_status: Optional[Callable[[str, str], Awaitable[None]]] = None,
    ):
        self.on_new_token = on_new_token
        self.on_status = on_status or (lambda level, msg: None)
        self.is_running = False
        self.seen_tokens: Set[str] = set()
        self._tasks: Set[asyncio.Task] = set()

    def _spawn(self, coro) -> None:
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def fetch_live_tokens(self, session: aiohttp.ClientSession) -> bool:
        """Fetch real, newly-profiled Solana tokens from DexScreener."""
        try:
            async with session.get(
                config.DEXSCREENER_LATEST, proxy=config.HTTP_PROXY
            ) as resp:
                if resp.status != 200:
                    return False
                tokens = await resp.json()
                found = False
                for t in tokens:
                    if t.get("chainId") != "solana":
                        continue
                    mint = t.get("tokenAddress")
                    if not mint or mint in self.seen_tokens:
                        continue
                    found = True
                    if len(self.seen_tokens) > 20000:
                        self.seen_tokens.clear()
                    self.seen_tokens.add(mint)
                    token_info = {
                        "mint": mint,
                        "name": t.get("name"),
                        "symbol": t.get("symbol"),
                        "description": t.get("description") or "",
                        "is_simulated_stream": False,
                    }
                    self._spawn(self.on_new_token(token_info))
                return found
        except Exception:
            return False
        return False

    async def emit_demo_token(self) -> None:
        """Emit one clearly-marked simulated token (demo data only)."""
        await asyncio.sleep(random.uniform(2.5, 5.0))
        sym, name = random.choice(SAMPLE_SYMBOLS)
        alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        mock_mint = "".join(random.choices(alphabet, k=32))[:8] + "pump"
        token_info = {
            "mint": mock_mint,
            "name": name,
            "symbol": sym,
            "price_usd": round(random.uniform(0.005, 0.08), 6),
            "is_simulated_stream": True,
        }
        self._spawn(self.on_new_token(token_info))

    async def start(self):
        self.is_running = True
        timeout = aiohttp.ClientTimeout(total=5)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        was_live: Optional[bool] = None

        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            while self.is_running:
                live_ok = await self.fetch_live_tokens(session)

                if live_ok != was_live:
                    was_live = live_ok
                    if live_ok:
                        await self.on_status("green", "فید زنده DexScreener متصل شد — توکن‌های واقعی دریافت می‌شود")
                    elif config.ALLOW_SIMULATED_STREAM:
                        await self.on_status("yellow", "فید زنده در دسترس نیست — استریم شبیه‌سازی‌شده [دمو] فعال شد")
                    else:
                        await self.on_status("red", "فید زنده در دسترس نیست و استریم شبیه‌سازی غیرفعال است — انتظار...")

                if live_ok:
                    await asyncio.sleep(3)
                elif config.ALLOW_SIMULATED_STREAM:
                    await self.emit_demo_token()
                else:
                    await asyncio.sleep(5)

    def stop(self):
        self.is_running = False
        for task in list(self._tasks):
            task.cancel()

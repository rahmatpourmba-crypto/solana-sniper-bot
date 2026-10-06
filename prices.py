"""
Real market-data helpers backed by the public DexScreener API.
No fabricated prices: every value here comes from an actual on-chain pair.
"""
import time
from typing import Any, Dict, Optional

import aiohttp

import config

WSOL_MINT = "So11111111111111111111111111111111111111112"
_CACHE_TTL = config.PRICE_POLL_SECONDS
_snapshot_cache: Dict[str, tuple] = {}
_sol_price_cache: tuple = (0.0, 0.0)


def _proxy() -> Optional[str]:
    return config.HTTP_PROXY


async def _get_json(session: aiohttp.ClientSession, url: str) -> Optional[Any]:
    try:
        async with session.get(url, proxy=_proxy()) as resp:
            if resp.status == 200:
                return await resp.json()
    except Exception:
        return None
    return None


async def get_sol_price_usd(session: aiohttp.ClientSession) -> Optional[float]:
    """SOL/USD price taken from the WSOL pair (cached for the poll interval)."""
    global _sol_price_cache
    ts, price = _sol_price_cache
    if price and time.time() - ts < 60:
        return price

    data = await _get_json(session, config.DEXSCREENER_PAIR.format(pair=WSOL_MINT))
    pairs = (data or {}).get("pairs") or []
    if not pairs:
        return price or None
    try:
        sol_price = float(pairs[0].get("priceUsd"))
    except (TypeError, ValueError):
        return price or None
    _sol_price_cache = (time.time(), sol_price)
    return sol_price


async def get_token_snapshot(
    session: aiohttp.ClientSession, mint: str, use_cache: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Best available market snapshot for a mint:
    price_usd, price_sol, liquidity_usd, volume_usd_24h, buyers (h1), fdv.
    """
    cached = _snapshot_cache.get(mint)
    if use_cache and cached and time.time() - cached[0] < _CACHE_TTL:
        return cached[1]

    data = await _get_json(session, config.DEXSCREENER_TOKEN.format(mint=mint))
    pairs = (data or {}).get("pairs") or []
    if not pairs:
        return None
    solana_pairs = [p for p in pairs if p.get("chainId") == "solana"]
    candidates = solana_pairs or pairs

    def liquidity_usd(pair: dict) -> float:
        return float(((pair.get("liquidity") or {}).get("usd")) or 0)

    best = max(candidates, key=liquidity_usd)

    try:
        price_usd = float(best.get("priceUsd"))
    except (TypeError, ValueError):
        return None

    sol_price = await get_sol_price_usd(session)
    quote_symbol = str((best.get("quoteToken") or {}).get("symbol", "")).upper()
    price_sol = None
    if quote_symbol in ("SOL", "WSOL"):
        try:
            price_sol = float(best.get("priceNative"))
        except (TypeError, ValueError):
            price_sol = None
    if price_sol is None and sol_price:
        price_sol = price_usd / sol_price

    txns = best.get("txns") or {}
    h1 = txns.get("h1") or {}
    buyers_h1 = int(h1.get("buys") or 0)
    buyers_24h = int((txns.get("h24") or {}).get("buys") or 0)
    volume = float((best.get("volume") or {}).get("h24") or 0)

    base = best.get("baseToken") or {}
    snapshot = {
        "pair_address": best.get("pairAddress"),
        "base_name": base.get("name"),
        "base_symbol": base.get("symbol"),
        "price_usd": price_usd,
        "price_sol": price_sol,
        "liquidity_usd": liquidity_usd(best),
        "volume_usd_24h": volume,
        "buyers_h1": buyers_h1,
        "buyers_24h": buyers_24h,
        "fdv": float(best.get("fdv") or 0),
        "url": best.get("url"),
        "dex": best.get("dexId"),
    }
    _snapshot_cache[mint] = (time.time(), snapshot)
    if len(_snapshot_cache) > 500:
        _snapshot_cache.clear()
    return snapshot


def clear_cache() -> None:
    _snapshot_cache.clear()

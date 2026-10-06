"""
Live swap execution via Jupiter Swap API (v1) with wallet-delta accounting.

Safety:
- LIVE_DRY_RUN=True (default): quotes are fetched and transactions are built,
  but NOTHING is broadcast — fills are simulated from the real quote.
- Real entries are gated by price-impact and wallet-affordability checks.
"""
import base64
from typing import Any, Dict, Optional

import aiohttp
from solders.keypair import Keypair
from solders.pubkey import Pubkey

import config
import wallet
from wallet import LAMPORTS, SolanaRPC, WSOL_MINT


class ExecutionError(Exception):
    pass


class LiveExecutor:
    def __init__(self, session: aiohttp.ClientSession, keypair: Keypair, dry_run: Optional[bool] = None):
        self.session = session
        self.keypair = keypair
        self.dry_run = config.LIVE_DRY_RUN if dry_run is None else dry_run
        self.pubkey = str(keypair.pubkey())
        self.rpc = SolanaRPC(session)

    async def _get_json(self, url: str) -> Dict[str, Any]:
        try:
            async with self.session.get(
                url, proxy=config.HTTP_PROXY, timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise ExecutionError(f"Jupiter HTTP {resp.status}: {body[:200]}")
                return await resp.json()
        except ExecutionError:
            raise
        except Exception as exc:
            raise ExecutionError(f"Jupiter request failed: {exc}")

    async def _post_json(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with self.session.post(
                url, json=payload, proxy=config.HTTP_PROXY, timeout=aiohttp.ClientTimeout(total=20)
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise ExecutionError(f"Jupiter HTTP {resp.status}: {body[:200]}")
                return await resp.json()
        except ExecutionError:
            raise
        except Exception as exc:
            raise ExecutionError(f"Jupiter request failed: {exc}")

    async def quote(self, input_mint: str, output_mint: str, amount_raw: int) -> Dict[str, Any]:
        url = (
            f"{config.JUPITER_BASE}/quote"
            f"?inputMint={input_mint}&outputMint={output_mint}"
            f"&amount={amount_raw}&slippageBps={config.SLIPPAGE_BPS}&swapMode=ExactIn"
        )
        data = await self._get_json(url)
        if not data or "outAmount" not in data:
            raise ExecutionError(f"no route for {input_mint[:6]} -> {output_mint[:6]}")
        return data

    async def _build_and_send(self, quote_response: Dict[str, Any]) -> Dict[str, Any]:
        swap = await self._post_json(
            f"{config.JUPITER_BASE}/swap",
            {
                "quoteResponse": quote_response,
                "userPublicKey": self.pubkey,
                "wrapAndUnwrapSol": True,
                "dynamicComputeUnitLimit": True,
                "prioritizationFeeLamports": "auto",
            },
        )
        if "swapTransaction" not in swap:
            raise ExecutionError(f"swap build failed: {str(swap)[:200]}")

        if self.dry_run:
            # Build & sign to prove the flow works, but never broadcast.
            wallet.sign_base64(swap["swapTransaction"], self.keypair)
            return {"signature": None, "dry_run": True}

        signed_b64 = wallet.sign_base64(swap["swapTransaction"], self.keypair)
        signature = await self.rpc.send_and_confirm(signed_b64)
        return {"signature": signature, "dry_run": False}

    async def can_afford(self, buy_sol: float) -> "tuple[bool, str]":
        """Wallet check: entry + possible ATA rent + fee + reserve."""
        try:
            balance = await self.rpc.get_sol_balance(self.keypair.pubkey())
        except Exception as exc:
            return False, f"خواندن موجودی کیف پول ناموفق بود: {exc}"
        needed = buy_sol + wallet_price_guard() + config.MIN_SOL_RESERVE
        if balance < needed:
            return False, f"موجودی کیف پول {balance:.4f} SOL کمتر از حد نیاز ({needed:.4f} SOL) است"
        return True, f"{balance:.4f} SOL"

    async def buy(self, mint: str, sol_amount: float) -> Dict[str, Any]:
        """Buy `sol_amount` SOL worth of `mint`. Returns wallet-delta accounting."""
        amount_lamports = int(sol_amount * LAMPORTS)
        quote = await self.quote(str(WSOL_MINT), mint, amount_lamports)

        impact = float(quote.get("priceImpactPct") or 0)
        if abs(impact) > config.MAX_PRICE_IMPACT_PCT:
            raise ExecutionError(f"price impact {impact:.2%} above limit {config.MAX_PRICE_IMPACT_PCT:.0%}")

        balance_before = None
        if not self.dry_run:
            balance_before = await self.rpc.get_sol_balance(self.keypair.pubkey())
        result = await self._build_and_send(quote)

        if self.dry_run:
            return {
                "signature": None,
                "dry_run": True,
                "cost_lamports": amount_lamports + int(config.ATA_RENT_SOL * 1e9) + int(config.TX_FEE_SOL * 1e9),
                "out_amount": int(quote["outAmount"]),
                "price_impact": impact,
            }

        balance_after = await self.rpc.get_sol_balance(self.keypair.pubkey())
        spent = balance_before - balance_after
        token_account = await self.rpc.get_token_account(self.keypair.pubkey(), Pubkey.from_string(mint))
        if not token_account or token_account["amount"] <= 0:
            raise ExecutionError("transaction confirmed but no token balance found")

        return {
            "signature": result["signature"],
            "dry_run": False,
            "cost_lamports": int(spent * LAMPORTS),
            "out_amount": token_account["amount"],
            "price_impact": impact,
        }

    async def sell(self, mint: str, token_amount_raw: int) -> Dict[str, Any]:
        """Sell the full token balance back to SOL and reclaim ATA rent."""
        if token_amount_raw <= 0:
            raise ExecutionError("nothing to sell")

        quote = await self.quote(mint, str(WSOL_MINT), token_amount_raw)

        balance_before = None
        if not self.dry_run:
            balance_before = await self.rpc.get_sol_balance(self.keypair.pubkey())
        result = await self._build_and_send(quote)

        if self.dry_run:
            return {
                "signature": None,
                "dry_run": True,
                "proceeds_lamports": int(quote["outAmount"]) + int(config.ATA_RENT_SOL * 1e9) - int(config.TX_FEE_SOL * 1e9),
            }

        # Reclaim rent by closing the (now empty) token account — best effort.
        try:
            token_account = await self.rpc.get_token_account(self.keypair.pubkey(), Pubkey.from_string(mint))
            if token_account and token_account["amount"] == 0:
                close_b64 = await wallet.close_token_account_tx(self.rpc, self.keypair, token_account["pubkey"])
                await self.rpc.send_and_confirm(close_b64)
        except Exception:
            pass  # rent stays locked in the ATA; trade itself succeeded

        balance_after = await self.rpc.get_sol_balance(self.keypair.pubkey())
        proceeds = balance_after - balance_before

        return {
            "signature": result["signature"],
            "dry_run": False,
            "proceeds_lamports": int(proceeds * LAMPORTS),
        }


def wallet_price_guard() -> float:
    """Worst-case extra cost of opening one new position (rent + fee)."""
    return config.ATA_RENT_SOL + config.TX_FEE_SOL

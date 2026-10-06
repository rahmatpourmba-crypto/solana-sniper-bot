"""
Solana wallet & RPC helpers (solders + JSON-RPC).
Loads the key from PHANTOM_PRIVATE_KEY (base58 string or byte-array JSON).
"""
import asyncio
import json
from typing import Any, Dict, List, Optional

import aiohttp
from solders.keypair import Keypair
from solders.instruction import AccountMeta, Instruction
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

import config

LAMPORTS = 1_000_000_000
WSOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
TOKEN_2022_PROGRAM_ID = Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")


def load_keypair() -> Optional[Keypair]:
    raw = (config.PHANTOM_PRIVATE_KEY or "").strip()
    if not raw:
        return None
    try:
        if raw.startswith("["):
            return Keypair.from_bytes(bytes(json.loads(raw)))
        return Keypair.from_base58_string(raw)
    except Exception:
        return None


def load_or_ephemeral() -> "tuple[Keypair, bool]":
    """Real key from env, or an ephemeral throwaway key (dry-run testing only)."""
    kp = load_keypair()
    if kp is not None:
        return kp, False
    return Keypair(), True


class SolanaRPC:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self._url_index = 0

    @property
    def urls(self) -> List[str]:
        return config.RPC_POOL

    async def call(self, method: str, params: list, retries: int = 3) -> Any:
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        last_error: Optional[Exception] = None
        for attempt in range(retries):
            url = self.urls[self._url_index % len(self.urls)]
            try:
                async with self.session.post(
                    url, json=payload, proxy=config.HTTP_PROXY
                ) as resp:
                    data = await resp.json()
                    if "error" in data:
                        raise RuntimeError(f"RPC error: {data['error']}")
                    return data.get("result")
            except Exception as exc:
                last_error = exc
                self._url_index += 1
                await asyncio.sleep(0.3)
        raise RuntimeError(f"RPC call {method} failed: {last_error}")

    async def get_sol_balance(self, pubkey: Pubkey) -> float:
        result = await self.call("getBalance", [str(pubkey), {"commitment": "confirmed"}])
        if isinstance(result, dict):  # JSON-RPC returns {context, value}
            result = result.get("value", 0)
        return (result or 0) / LAMPORTS

    async def get_token_account(self, owner: Pubkey, mint: Pubkey) -> Optional[Dict[str, Any]]:
        """Find the owner's token account for a mint: {pubkey, amount, decimals}."""
        result = await self.call(
            "getTokenAccountsByOwner",
            [str(owner), {"mint": str(mint)}, {"encoding": "jsonParsed", "commitment": "confirmed"}],
        )
        for value in (result or {}).get("value", []):
            info = (value.get("account", {}).get("data", {}) or {}).get("parsed", {}).get("info", {})
            if info.get("tokenOwner") and info.get("mint") == str(mint):
                return {
                    "pubkey": value.get("pubkey"),
                    "amount": int(info.get("tokenAmount", {}).get("amount", 0)),
                    "decimals": int(info.get("tokenAmount", {}).get("decimals", 0)),
                }
        return None

    async def send_and_confirm(self, tx_b64: str, timeout: float = None) -> str:
        timeout = timeout or config.CONFIRM_TIMEOUT_SECONDS
        result = await self.call(
            "sendTransaction",
            [tx_b64, {"encoding": "base64", "preflightCommitment": "confirmed", "skipPreflight": False}],
        )
        signature = result
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            status = await self.call("getSignatureStatuses", [[signature], {"searchTransactionHistory": False}])
            st = (status or {}).get("value", [None])[0]
            if st is not None:
                if st.get("err"):
                    raise RuntimeError(f"Transaction failed: {st['err']} ({signature})")
                if st.get("confirmationStatus") in ("confirmed", "finalized"):
                    return signature
            await asyncio.sleep(1.0)
        raise TimeoutError(f"Confirmation timeout for {signature}")


def sign_base64(tx_b64: str, keypair: Keypair) -> str:
    import base64

    tx = VersionedTransaction.from_bytes(base64.b64decode(tx_b64))
    signed = VersionedTransaction(tx.message, [keypair])
    return base64.b64encode(bytes(signed)).decode()


async def close_token_account_tx(rpc: SolanaRPC, keypair: Keypair, ata_pubkey: str) -> str:
    """Build a signed transaction that closes the ATA and reclaims rent to the wallet."""
    payer = keypair.pubkey()
    blockhash = await rpc.call("getLatestBlockhash", [{"commitment": "confirmed"}])
    recent = blockhash["blockhash"]

    close_ix = Instruction(
        program_id=TOKEN_PROGRAM_ID,
        data=b"",
        accounts=[
            AccountMeta(Pubkey.from_string(ata_pubkey), is_writable=True, is_signer=False),
            AccountMeta(payer, is_writable=True, is_signer=False),
            AccountMeta(payer, is_writable=False, is_signer=True),
        ],
    )
    message = MessageV0.try_compile(payer, [close_ix], [], Pubkey.from_string(recent))
    tx = VersionedTransaction(message, [keypair])
    import base64

    return base64.b64encode(bytes(tx)).decode()

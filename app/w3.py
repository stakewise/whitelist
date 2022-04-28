import logging
import time
from typing import Dict

from eth_typing import BlockNumber
from hexbytes import HexBytes
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware, geth_poa_middleware
from web3.types import TxParams

from app.config import (
    CONFIRMATION_BLOCKS,
    ENABLED_NETWORKS,
    NETWORKS,
    TRANSACTION_TIMEOUT,
)

# WAD base unit
WAD = Web3.toWei(1, "ether")

BLS_WITHDRAWAL_PREFIX: bytes = bytes(1)

YEAR_IN_SECONDS = 31540000
DAY_IN_SECONDS = 86400

WEB3_PROVIDER_TIMEOUT = 60

logger = logging.getLogger(__name__)


def get_web3_client(network: str) -> Web3:
    """Returns instance of the Web3 client."""
    network_config = NETWORKS[network]
    endpoint = network_config["ETH1_ENDPOINT"]

    # Prefer WS over HTTP
    if endpoint.startswith("ws"):
        w3 = Web3(Web3.WebsocketProvider(endpoint, websocket_timeout=60))
        logger.warning(f"[{network}] Web3 websocket endpoint={endpoint}")
    elif endpoint.startswith("http"):
        w3 = Web3(Web3.HTTPProvider(endpoint))
        logger.warning(f"[{network}] Web3 HTTP endpoint={endpoint}")
    else:
        w3 = Web3(Web3.IPCProvider(endpoint))
        logger.warning(f"[{network}] Web3 HTTP endpoint={endpoint}")

    if network_config["IS_POA"]:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        logger.warning(f"[{network}] Injected POA middleware")

    account = w3.eth.account.from_key(NETWORKS[network]["PRIVATE_KEY"])
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
    logger.warning(
        f"[{network}] Injected middleware for capturing transactions and sending as raw"
    )

    w3.eth.default_account = account.address
    logger.info(f"[{network}] Configured default account {w3.eth.default_account}")

    return w3


def get_web3_clients() -> Dict[str, Web3]:
    web3_clients = {}
    for network in ENABLED_NETWORKS:
        web3_clients[network] = get_web3_client(network)
    return web3_clients


def get_transaction_params(network: str, web3_client: Web3) -> TxParams:
    network_config = NETWORKS[network]
    max_fee_per_gas = network_config["MAX_FEE_PER_GAS"]
    account_nonce = web3_client.eth.getTransactionCount(web3_client.eth.default_account)
    latest_block = web3_client.eth.get_block("latest")
    max_priority_fee = min(web3_client.eth.max_priority_fee, max_fee_per_gas)

    base_fee = latest_block["baseFeePerGas"]
    priority_fee = int(str(max_priority_fee), 16)
    max_fee_per_gas = priority_fee + 2 * base_fee

    return TxParams(
        nonce=account_nonce,
        maxPriorityFeePerGas=max_priority_fee,
        maxFeePerGas=hex(min(max_fee_per_gas, max_fee_per_gas)),
    )


def wait_for_transaction(network: str, web3_client: Web3, tx_hash: HexBytes) -> None:
    """Waits for transaction to be confirmed."""
    receipt = web3_client.eth.wait_for_transaction_receipt(
        transaction_hash=tx_hash, timeout=TRANSACTION_TIMEOUT, poll_latency=5
    )
    confirmation_block: BlockNumber = receipt["blockNumber"] + CONFIRMATION_BLOCKS
    current_block: BlockNumber = web3_client.eth.block_number
    while confirmation_block > current_block:
        logger.info(
            f"[{network}] Waiting for {confirmation_block - current_block} confirmation blocks..."
        )
        time.sleep(15)

        receipt = web3_client.eth.get_transaction_receipt(tx_hash)
        confirmation_block = receipt["blockNumber"] + CONFIRMATION_BLOCKS
        current_block = web3_client.eth.block_number

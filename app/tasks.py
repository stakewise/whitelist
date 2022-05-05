import logging
from multiprocessing import Lock

from web3 import Web3

from contract.contract import get_contracts

from .db import delete_record, has_record, insert_record
from .w3 import get_transaction_params, get_web3_clients

logger = logging.getLogger(__name__)


lock = Lock()


def update_whitelist(address: str, status: bool):
    if has_record(address):
        return
    insert_record(address)
    try:
        w3_clients = get_web3_clients()
        whitelist_contracts = get_contracts(w3_clients)
        for network, web3_client in w3_clients.items():
            whitelist_contract = whitelist_contracts[network]
            current_status = whitelist_contract.functions.whitelistedAccounts(
                address
            ).call()
            if current_status != status:
                try:
                    lock.acquire()
                    function_call = whitelist_contract.functions.updateWhiteList(
                        address, status
                    )
                    tx_params = get_transaction_params(network, web3_client)
                    estimated_gas = function_call.estimateGas(tx_params)

                    # add 10% margin to the estimated gas
                    tx_params["gas"] = int(estimated_gas * 0.1) + estimated_gas

                    # execute transaction
                    tx_hash = function_call.transact(tx_params)
                    logger.info(
                        f"[{network}] Submitted transaction: {Web3.toHex(tx_hash)}"
                    )
                finally:
                    lock.release()
    except Exception as e:
        logger.exception(e)
    finally:
        delete_record(address)


def check_whitelist(address: str):
    w3_clients = get_web3_clients()
    whitelist_contracts = get_contracts(w3_clients)
    result = {}
    for network, web3_client in w3_clients.items():
        whitelist_contract = whitelist_contracts[network]
        current_status = whitelist_contract.functions.whitelistedAccounts(
            address
        ).call()
        result[network] = current_status
    return result


def get_status(address):
    return "running" if has_record(address) else "idle"

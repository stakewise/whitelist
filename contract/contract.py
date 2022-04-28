import json
import os
from typing import Dict

from web3 import Web3
from web3.contract import Contract

from app.config import NETWORKS


def get_contracts(w3_clients: Dict[str, Web3]) -> Dict[str, Contract]:
    """:returns instances of `Whitelist` contracts for different networks."""
    current_dir = os.path.dirname(__file__)
    with open(os.path.join(current_dir, "abi/TransparentUpgradeableProxy.json")) as f:
        abi = json.load(f)

    contracts = {}
    for network_name in w3_clients:
        w3 = w3_clients[network_name]
        contracts[network_name] = w3.eth.contract(
            abi=abi, address=NETWORKS[network_name]["CONTRACT_ADDRESS"]
        )

    return contracts

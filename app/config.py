from decouple import Csv, config
from web3 import Web3

HARBOR_MAINNET = "harbor_mainnet"
HARBOR_GOERLI = "harbor_goerli"

HARBOR_GOERLI_UPPER = HARBOR_GOERLI.upper()
HARBOR_MAINNET_UPPER = HARBOR_MAINNET.upper()

# auth key for server-server auth
API_KEY = config("API_KEY", default=None)
ENABLED_NETWORKS = config(
    "ENABLED_NETWORKS",
    default=HARBOR_GOERLI,
    cast=Csv(),
)
CONFIRMATION_BLOCKS: int = config("CONFIRMATION_BLOCKS", default=15, cast=int)
TRANSACTION_TIMEOUT = config("TRANSACTION_TIMEOUT", default=900, cast=int)

NETWORKS = {
    HARBOR_GOERLI: dict(
        ETH1_ENDPOINT=config(f"{HARBOR_GOERLI_UPPER}_ETH1_ENDPOINT", default=""),
        IS_POA=True,
        MAX_FEE_PER_GAS=config(
            f"{HARBOR_GOERLI_UPPER}_MAX_FEE_PER_GAS_GWEI",
            default=150,
            cast=lambda x: Web3.toWei(x, "gwei"),
        ),
        CONTRACT_ADDRESS="0x176Bf5626C6e9Cd82a13CD69997fA58c633fcF7B",
        PRIVATE_KEY=config(
            f"{HARBOR_GOERLI_UPPER}_PRIVATE_KEY",
            default=None,
        ),
    ),
    HARBOR_MAINNET: dict(
        ETH1_ENDPOINT=config(f"{HARBOR_MAINNET_UPPER}_ETH1_ENDPOINT", default=""),
        IS_POA=False,
        MAX_FEE_PER_GAS=config(
            f"{HARBOR_MAINNET_UPPER}_MAX_FEE_PER_GAS_GWEI",
            default=150,
            cast=lambda x: Web3.toWei(x, "gwei"),
        ),
        CONTRACT_ADDRESS="0x57a9cbED053f37EB67d6f5932b1F2f9Afbe347F3",
        PRIVATE_KEY=config(
            f"{HARBOR_MAINNET_UPPER}_PRIVATE_KEY",
            default=None,
        ),
    ),
}

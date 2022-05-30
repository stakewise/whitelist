from decouple import Csv, config
from web3 import Web3

HARBOUR_MAINNET = "harbour_mainnet"
HARBOUR_GOERLI = "harbour_goerli"

HARBOUR_GOERLI_UPPER = HARBOUR_GOERLI.upper()
HARBOUR_MAINNET_UPPER = HARBOUR_MAINNET.upper()

# auth key for server-server auth
API_KEY = config("API_KEY", default=None)
DATABASE_PATH = config("DATABASE_PATH", default="whitelist.db")
ENABLED_NETWORKS = config(
    "ENABLED_NETWORKS",
    default=HARBOUR_GOERLI,
    cast=Csv(),
)
CONFIRMATION_BLOCKS: int = config("CONFIRMATION_BLOCKS", default=15, cast=int)
TRANSACTION_TIMEOUT = config("TRANSACTION_TIMEOUT", default=900, cast=int)

NETWORKS = {
    HARBOUR_GOERLI: dict(
        ETH1_ENDPOINT=config(f"{HARBOUR_GOERLI_UPPER}_ETH1_ENDPOINT", default=""),
        IS_POA=True,
        MAX_FEE_PER_GAS=config(
            f"{HARBOUR_GOERLI_UPPER}_MAX_FEE_PER_GAS_GWEI",
            default=150,
            cast=lambda x: Web3.toWei(x, "gwei"),
        ),
        CONTRACT_ADDRESS="0x176Bf5626C6e9Cd82a13CD69997fA58c633fcF7B",
        PRIVATE_KEY=config(
            f"{HARBOUR_GOERLI_UPPER}_PRIVATE_KEY",
            default=None,
        ),
    ),
    HARBOUR_MAINNET: dict(
        ETH1_ENDPOINT=config(f"{HARBOUR_MAINNET_UPPER}_ETH1_ENDPOINT", default=""),
        IS_POA=False,
        MAX_FEE_PER_GAS=config(
            f"{HARBOUR_MAINNET_UPPER}_MAX_FEE_PER_GAS_GWEI",
            default=150,
            cast=lambda x: Web3.toWei(x, "gwei"),
        ),
        CONTRACT_ADDRESS="0x57a9cbED053f37EB67d6f5932b1F2f9Afbe347F3",
        PRIVATE_KEY=config(
            f"{HARBOUR_MAINNET_UPPER}_PRIVATE_KEY",
            default=None,
        ),
    ),
}

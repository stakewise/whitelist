import binascii
import typing

from eth_utils import decode_hex
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, validator
from web3 import Web3

from app import config

from .tasks import check_whitelist, update_whitelist

w3 = Web3()
app = FastAPI()


class AddressRequest(BaseModel):
    address: str

    @validator("address")
    def address_validation(cls, value):
        if len(value) != 42 or not value.startswith("0x"):
            raise ValueError("Invalid ETH Address")
        if not Web3.isChecksumAddress(value):
            raise ValueError("Invalid ETH Address")
        try:
            decode_hex(value)
        except (binascii.Error, TypeError):
            raise ValueError("Invalid ETH Address")


class AuthorizerDependency:
    def __call__(self, api_key: typing.Optional[str] = Header(...)):
        if api_key and api_key != config.API_KEY:
            raise HTTPException(status_code=401, detail="unauthorized")
        return api_key


@app.get("/heathz")
async def heathz():
    return {}


@app.post("/service/whitelist", dependencies=[Depends(AuthorizerDependency())])
async def whitelist_add(
    address_request: AddressRequest, background_tasks: BackgroundTasks
):
    address = address_request.address
    background_tasks.add_task(update_whitelist, address, True)
    return {"status": "success"}


@app.delete("/service/whitelist", dependencies=[Depends(AuthorizerDependency())])
async def whitelist_delete(
    address_request: AddressRequest, background_tasks: BackgroundTasks
):
    address = address_request.address
    background_tasks.add_task(update_whitelist, address, False)
    return {"status": "success"}


@app.get("/service/whitelist", dependencies=[Depends(AuthorizerDependency())])
async def whitelist_get(address: str):
    try:
        AddressRequest.address_validation(address)
    except ValueError as e:
        return {"error": str(e)}
    return {"result": check_whitelist(address)}

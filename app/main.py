import binascii
import typing

from eth_utils import decode_hex
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, validator
from web3 import Web3

from app import config

from .db import setup_db
from .tasks import check_whitelist, get_status, update_whitelist

w3 = Web3()
app = FastAPI()
setup_db()


class AddressRequest(BaseModel):
    address: str

    @validator("address")
    def address_validation(cls, value):
        invalid_address = "Invalid ETH Address"
        if len(value) != 42 or not value.startswith("0x"):
            raise HTTPException(status_code=400, detail=invalid_address)
        if not Web3.isChecksumAddress(value):
            raise HTTPException(status_code=400, detail=invalid_address)
        try:
            decode_hex(value)
        except (binascii.Error, TypeError):
            raise HTTPException(status_code=400, detail=invalid_address)
        return value


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
    AddressRequest.address_validation(address)
    return {"result": check_whitelist(address)}


@app.get("/service/status", dependencies=[Depends(AuthorizerDependency())])
async def status(address: str):
    AddressRequest.address_validation(address)
    return {"status": get_status(address)}

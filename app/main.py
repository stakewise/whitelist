import typing

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from app import config

from .tasks import update_whitelist

app = FastAPI()


class AddressRequest(BaseModel):
    address: str


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

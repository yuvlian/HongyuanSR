from common import (
    SDKSERVER_ADDR,
    GAMESERVER_ADDR,
    ASSET_BUNDLE_URL,
    EX_RESOURCE_URL,
    LUA_URL,
)
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, JSONResponse
from proto import GateServer, Dispatch, RegionInfo
import base64
import uvicorn

app = FastAPI()


@app.get("/query_dispatch")
async def query_dispatch() -> PlainTextResponse:
    rsp = Dispatch(
        region_list=[
            RegionInfo(
                name="House of Spiders",
                title="H.O.S",
                env_type="9",
                dispatch_url=f"http://{SDKSERVER_ADDR[0]}:{SDKSERVER_ADDR[1]}/query_gateway",
            )
        ]
    )
    rsp = bytes(rsp)
    rsp = base64.b64encode(rsp)

    return PlainTextResponse(rsp)


@app.get("/query_gateway")
async def query_gateway() -> PlainTextResponse:
    rsp = GateServer(
        ip=GAMESERVER_ADDR[0],
        port=GAMESERVER_ADDR[1],
        asset_bundle_url=ASSET_BUNDLE_URL,
        ex_resource_url=EX_RESOURCE_URL,
        lua_url=LUA_URL,
        ifix_version="0",
        # starting from 4.2 prod, hsr forces KCP.
        # use_tcp=True,
        unk1=True,
        unk2=True,
        unk3=True,
        unk4=True,
        unk5=True,
        unk6=True,
        unk7=True,
    )
    rsp = bytes(rsp)
    rsp = base64.b64encode(rsp)

    return PlainTextResponse(rsp)


@app.post("/hkrpg_cn/mdk/shield/api/login")
async def login_with_password() -> JSONResponse:
    rsp = {
        "data": {
            "account": {
                "area_code": "**",
                "email": "go.play@limbus.company",
                "country": "ID",
                "is_email_verify": "1",
                "token": "arayashiki",
                "uid": "1",
            },
            "device_grant_required": False,
            "reactivate_required": False,
            "realperson_required": False,
            "safe_mobile_required": False,
        },
        "message": "OK",
        "retcode": 0,
    }

    return JSONResponse(rsp)


@app.post("/hkrpg_cn/mdk/shield/api/verify")
async def login_with_session_token() -> JSONResponse:
    rsp = {
        "data": {
            "account": {
                "area_code": "**",
                "email": "go.play@limbus.company",
                "country": "ID",
                "is_email_verify": "1",
                "token": "arayashiki",
                "uid": "1",
            },
            "device_grant_required": False,
            "reactivate_required": False,
            "realperson_required": False,
            "safe_mobile_required": False,
        },
        "message": "OK",
        "retcode": 0,
    }

    return JSONResponse(rsp)


@app.post("/hkrpg_cn/combo/granter/login/v2/login")
async def granter_login_verification() -> JSONResponse:
    rsp = {
        "data": {
            "account_type": 1,
            "combo_id": "1",
            "combo_token": "arayashiki",
            "data": '{"guest":false}',
            "heartbeat": False,
            "open_id": "1",
        },
        "message": "OK",
        "retcode": 0,
    }

    return JSONResponse(rsp)


@app.post("/account/risky/api/check")
async def risky_api_check() -> JSONResponse:
    rsp = {
        "data": {"id": "arayashiki", "action": "ACTION_NONE", "geetest": None},
        "message": "OK",
        "retcode": 0,
    }

    return JSONResponse(rsp)


@app.post("/account/ma-cn-passport/app/loginByPassword")
async def apn_login_with_password() -> JSONResponse:
    rsp = {
        "data": {
            "token": {"token": "arayashiki", "token_type": 1},
            "user_info": {
                "aid": "1",
                "mid": "1",
                "is_email_verify": 1,
                "area_code": "**",
                "country": "ID",
                "is_adult": 1,
                "email": "go.play@limbus.company",
            },
        },
        "message": "OK",
        "retcode": 0,
    }

    return JSONResponse(rsp)


@app.post("/account/ma-cn-session/app/verify")
async def apn_verify_token() -> JSONResponse:
    rsp = {
        "data": {
            "tokens": [{"token": "arayashiki", "token_type": 1}],
            "user_info": {
                "aid": "1",
                "mid": "1",
                "is_email_verify": 1,
                "area_code": "**",
                "country": "ID",
                "is_adult": 1,
                "email": "go.play@limbus.company",
            },
        },
        "message": "OK",
        "retcode": 0,
    }

    return JSONResponse(rsp)


if __name__ == "__main__":
    uvicorn.run(app, host=SDKSERVER_ADDR[0], port=SDKSERVER_ADDR[1])

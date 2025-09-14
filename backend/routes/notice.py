from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
import json

router = APIRouter()

@router.post("/topview")
async def topview_notice(request: Request):
    try:
        raw = await request.body()
        body_text = raw.decode("utf-8", errors="replace")
        body_json = json.loads(body_text)
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": "Invalid JSON", "result": None}
        )

    notice_uuid = body_json.get("uuid")
    topview_uid = os.getenv("TOPVIEW_UID")

    return JSONResponse(
        status_code=200,
        content={
            "code": 200,
            "message": "Success",
            "result": {
                "uuid": notice_uuid,
                "topviewUid": topview_uid,
                "result": "success"
            }
        }
    )

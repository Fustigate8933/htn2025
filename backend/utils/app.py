# app.py
import os, json, datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import requests

load_dotenv()
app = FastAPI()

@app.post("/notice/topview")
async def topview_notice(request: Request):
    headers = dict(request.headers)
    query = dict(request.query_params)
    raw = await request.body()
    body_text = raw.decode("utf-8", errors="replace")

    result_status = "fail"
    notice_uuid = None
    topview_uid = None

    if body_json:
        notice_uuid = body_json.get("uuid")
        topview_uid = os.getenv("TOPVIEW_UID")

    return JSONResponse({
        "code": "200",
        "message": "Success",
        "result": {
            "uuid": notice_uuid,
            "topviewUid": topview_uid,
            "result": "success"
        }
    })


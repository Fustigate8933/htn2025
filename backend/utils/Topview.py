import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
AUTH = os.getenv("TOPVIEW_AUTH")
UID  = os.getenv("TOPVIEW_UID")
BASE = "https://api.topview.ai/v1"

MIME_TYPES = {
    "mp4": "video/mp4",
    "mov": "video/quicktime",
}

def headers(json=True):
    h = {"Authorization": f"Bearer {AUTH}", "Topview-Uid": UID}
    if json:
        h["Content-Type"] = "application/json"
    return h

# ---------- 上传部分 ----------
def get_upload_credential(file_format: str):
    url = f"{BASE}/upload/credential?format={file_format}"
    r = requests.get(url, headers=headers(json=False))
    r.raise_for_status()
    data = r.json()
    if data.get("code") != "200":
        raise RuntimeError(f"credential error: {data}")
    return data["result"]

def put_file(upload_url: str, file_path: str, content_type: str):
    with open(file_path, "rb") as f:
        r = requests.put(upload_url, headers={"Content-Type": content_type}, data=f)
    r.raise_for_status()
    if r.status_code not in (200, 204):
        raise RuntimeError(f"put failed {r.status_code}")

def check_upload(file_id: str, interval=1, max_retries=30) -> bool:
    url = f"{BASE}/upload/check?fileId={file_id}"
    for i in range(max_retries):
        r = requests.get(url, headers=headers(json=False))
        r.raise_for_status()
        data = r.json()
        print(f"[Check {i+1}] {data}")
        if data.get("result") is True:
            return True
        time.sleep(interval)
    return False

def upload_video(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lstrip(".").lower()
    if ext not in MIME_TYPES:
        raise ValueError(f"Unsupported format: {ext}, only {list(MIME_TYPES)}")
    cred = get_upload_credential(ext)
    file_id = cred["fileId"]
    upload_url = cred["uploadUrl"]
    put_file(upload_url, file_path, MIME_TYPES[ext])
    ok = check_upload(file_id)
    if not ok:
        raise TimeoutError("Upload not confirmed")
    print("Upload success, fileId =", file_id)
    return file_id

# ---------- avatar 部分 ----------
def submit_video2avatar(video_file_id: str) -> str:
    url = f"{BASE}/common_task/video2aiAvatar/submit"
    payload = {"videoFileId": video_file_id}
    r = requests.post(url, headers=headers(), json=payload)
    r.raise_for_status()
    data = r.json()
    return data["result"]["taskId"]

def query_video2avatar(task_id: str, interval=2, max_tries=6000) -> str:
    url = f"{BASE}/common_task/video2aiAvatar/query"
    for i in range(max_tries):
        r = requests.get(url, headers=headers(json=False), params={"taskId": task_id})
        r.raise_for_status()
        data = r.json()
        print(f"[Query Avatar {i+1}] {data}")
        if data.get("result", {}).get("status") == "success":
            return data["result"]["aiAvatarId"]
        if data.get("result", {}).get("status") == "failed":
            raise RuntimeError(f"video2aiAvatar failed: {data}")
        time.sleep(interval)
    raise TimeoutError("video2aiAvatar not finished")

# ---------- video task 部分 ----------
def submit_video_task(ai_avatar_id: str, tts_text: str, notice_url=None) -> str:
    url = f"{BASE}/video_avatar/task/submit"
    payload = {
        "avatarSourceFrom": "2",  # 自定义 aiAvatar
        "aiAvatarId": ai_avatar_id,
        "audioSourceFrom": "1",   # TTS
        "ttsText": tts_text,
        "modeType": "0"
    }
    if notice_url:
        payload["noticeUrl"] = notice_url
    r = requests.post(url, headers=headers(), json=payload)
    r.raise_for_status()
    data = r.json()
    return data["result"]["taskId"]

def query_video_task(task_id: str, interval=5, max_tries=12000) -> str:
    url = f"{BASE}/video_avatar/task/query"
    for i in range(max_tries):
        r = requests.get(url, headers=headers(json=False),
                         params={"taskId": task_id, "needCloudFrontUrl": "true"})
        r.raise_for_status()
        data = r.json()
        print(f"[Query Video {i+1}] {data}")
        if data.get("result", {}).get("status") == "success":
            return data["result"]["outputVideoUrl"]
        if data.get("result", {}).get("status") == "failed":
            raise RuntimeError(f"video task failed: {data}")
        time.sleep(interval)
    raise TimeoutError("video task not finished")


def gen_video(video_path: str, tts_text: str)
    video_file_id = upload_video(video_path)

    avatar_task_id = submit_video2avatar(video_file_id)
    print("Submitted video2aiAvatar, taskId =", avatar_task_id)
    ai_avatar_id = query_video2avatar(avatar_task_id)
    print("Got aiAvatarId =", ai_avatar_id)

    video_task_id = submit_video_task(ai_avatar_id, tts_text,
                                      notice_url="https://410534426f02.ngrok-free.app/notice/topview")
    print("Submitted video task, taskId =", video_task_id)
    output_url = query_video_task(video_task_id)
    print("Final video URL:", output_url)

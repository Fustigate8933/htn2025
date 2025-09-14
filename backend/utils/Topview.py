import os
import time
import requests
import datetime
from typing import List
from dotenv import load_dotenv

load_dotenv()
AUTH = os.getenv("TOPVIEW_AUTH")
VIDEO_DIR = os.getenv("VIDEO_DIR", "./videos")
UID  = os.getenv("TOPVIEW_UID")
BASE = "https://api.topview.ai/v1"

def headers(json=True):
    h = {"Authorization": f"Bearer {AUTH}", "Topview-Uid": UID}
    if json:
        h["Content-Type"] = "application/json"
    return h

MIME_TYPES = {
    "mp4": "video/mp4",
    "mov": "video/quicktime",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "m4a": "audio/mp4"
}

def get_upload_credential(file_format: str):
    url = f"{BASE}/upload/credential?format={file_format}"
    r = requests.get(url, headers=headers(json=False))
    r.raise_for_status()
    return r.json()["result"]

def put_file(upload_url: str, file_path: str, content_type: str):
    with open(file_path, "rb") as f:
        r = requests.put(upload_url, headers={"Content-Type": content_type}, data=f)
    r.raise_for_status()

def check_upload(file_id: str, interval=1, max_retries=30) -> bool:
    url = f"{BASE}/upload/check?fileId={file_id}"
    for i in range(max_retries):
        r = requests.get(url, headers=headers(json=False))
        r.raise_for_status()
        data = r.json()
        if data.get("result") is True:
            return True
        time.sleep(interval)
    return False

def upload_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lstrip(".").lower()
    if ext not in MIME_TYPES:
        raise ValueError(f"Unsupported format: {ext}, allowed={list(MIME_TYPES)}")
    cred = get_upload_credential(ext)
    file_id = cred["fileId"]
    put_file(cred["uploadUrl"], file_path, MIME_TYPES[ext])
    if not check_upload(file_id):
        raise TimeoutError("Upload not confirmed")
    return file_id

def submit_voice_clone(origin_voice_file_id: str) -> str:
    url = f"{BASE}/voice/clone/task/submit"
    payload = {"originVoiceFileId": origin_voice_file_id, "voiceSpeed": "0.8"}
    r = requests.post(url, headers=headers(), json=payload)
    r.raise_for_status()
    return r.json()["result"]["taskId"]

def query_voice_clone(task_id: str, interval=3, max_tries=60) -> str:
    url = f"{BASE}/voice/clone/task/query"
    for i in range(max_tries):
        r = requests.get(url, headers=headers(json=False), params={"taskId": task_id})
        r.raise_for_status()
        data = r.json()
        result = data.get("result", {})
        if result.get("status") == "success":
            voice = result.get("voice") or {}
            voice_id = voice.get("voiceId") or result.get("voiceId")
            if voice_id:
                return voice_id
            else:
                raise RuntimeError(f"Success but no voiceId: {result}")
        if result.get("status") == "failed":
            raise RuntimeError(f"Voice clone failed: {result}")
        time.sleep(interval)
    raise TimeoutError("Voice clone not finished")

def _download_video(url: str, task_id: str | None = None) -> str:
    name = f"result_{task_id}.mp4" if task_id else f"result_{int(datetime.datetime.utcnow().timestamp())}.mp4"
    local_path = os.path.join(VIDEO_DIR, name)

    with requests.get(url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return local_path


def submit_video_task(video_file_id: str, voice_id: str, tts_text: str, notice_url=None) -> str:
    url = f"{BASE}/video_avatar/task/submit"
    payload = {
        "avatarSourceFrom": "0",
        "videoFileId": video_file_id,
        "audioSourceFrom": "1",
        "ttsText": tts_text,
        "voiceoverId": voice_id,
        "modeType": "0"
    }
    if notice_url:
        payload["noticeUrl"] = notice_url
    r = requests.post(url, headers=headers(), json=payload)
    r.raise_for_status()
    return r.json()["result"]["taskId"]

def query_video_task(task_id: str, interval=5, max_tries=120) -> str:
    url = f"{BASE}/video_avatar/task/query"
    for i in range(max_tries):
        r = requests.get(url, headers=headers(json=False),
                         params={"taskId": task_id, "needCloudFrontUrl": "true"})
        r.raise_for_status()
        data = r.json()
        result = data.get("result", {})
        if result.get("status") == "success":
            video_url = result.get("outputVideoUrl")
            return _download_video(video_url, task_id)
        if result.get("status") == "failed":
            raise RuntimeError(f"Video task failed: {result}")
        time.sleep(interval)
    raise TimeoutError("Video task not finished")

def gen_video(audio_path: str, video_path: str, tts_text: str):
    origin_file_id = upload_file(audio_path)

    task_id = submit_voice_clone(origin_file_id)
    voice_id = query_voice_clone(task_id)

    video_file_id = upload_file(video_path)
    
    video_task_id = submit_video_task(video_file_id, voice_id, tts_text,
                                      notice_url="https://410534426f02.ngrok-free.app/notice/topview")
    output_url = query_video_task(video_task_id)


def gen_video_batch(audio_path: str, video_path: str, tts_text: List[str]):
    """
    Generate videos and return IDs - supports both demo and production modes
    """
    import os
    DEMO_MODE = os.getenv('DEMO_MODE', 'false').lower() == 'true'
    
    if DEMO_MODE:
        print(f"DEMO MODE: gen_video_batch called with {len(tts_text)} scripts")
        print(f"DEMO MODE: Would normally process audio_path={audio_path}, video_path={video_path}")
        
        # DEMO MODE: Return hardcoded video paths for each script
        hardcoded_videos = ["/1.mp4", "/2.mp4", "/3.mp4", "/4.mp4"]
        
        # DEMO MODE: Generate dummy IDs for testing
        import uuid
        dummy_voice_id = f"demo_voice_{uuid.uuid4().hex[:8]}"
        dummy_video_file_id = f"demo_video_{uuid.uuid4().hex[:8]}"
        
        print(f"DEMO MODE: Generated dummy voice_id: {dummy_voice_id}")
        print(f"DEMO MODE: Generated dummy video_file_id: {dummy_video_file_id}")
        
        # Return the appropriate number of videos based on the number of scripts
        out = []
        for i, text in enumerate(tts_text):
            if i < len(hardcoded_videos):
                video_path = hardcoded_videos[i]
                print(f"DEMO MODE: Returning hardcoded video {i+1}: {video_path} for script: {text[:50]}...")
                out.append(video_path)
            else:
                # If there are more scripts than videos, cycle through the available videos
                video_path = hardcoded_videos[i % len(hardcoded_videos)]
                print(f"DEMO MODE: Cycling video for script {i+1}: {video_path} for script: {text[:50]}...")
                out.append(video_path)
        
        print(f"DEMO MODE: Returning {len(out)} hardcoded video paths")
        return {
            "video_urls": out,
            "voice_id": dummy_voice_id,
            "video_file_id": dummy_video_file_id
        }
    else:
        print(f"PRODUCTION MODE: gen_video_batch called with {len(tts_text)} scripts")
        print(f"PRODUCTION MODE: Processing audio_path={audio_path}, video_path={video_path}")
        
        # Step 1: Upload voice file and get voice_id
        print("PRODUCTION MODE: Uploading voice file and cloning voice...")
        origin_file_id = upload_file(audio_path)
        task_id = submit_voice_clone(origin_file_id)
        voice_id = query_voice_clone(task_id)
        print(f"PRODUCTION MODE: Generated voice_id: {voice_id}")
        
        # Step 2: Upload video file and get video_file_id
        print("PRODUCTION MODE: Uploading video file...")
        video_file_id = upload_file(video_path)
        print(f"PRODUCTION MODE: Generated video_file_id: {video_file_id}")
        
        # Step 3: Generate videos for each script
        print("PRODUCTION MODE: Generating videos for each script...")
        video_urls = []
        for i, text in enumerate(tts_text):
            print(f"PRODUCTION MODE: Generating video {i+1}/{len(tts_text)} for script: {text[:50]}...")
            
            # Submit video task
            video_task_id = submit_video_task(video_file_id, voice_id, text)
            
            # Query video task and get result
            output_path = query_video_task(video_task_id)
            video_urls.append(output_path)
            
            print(f"PRODUCTION MODE: Generated video {i+1}: {output_path}")
        
        print(f"PRODUCTION MODE: Generated {len(video_urls)} real videos")
        return {
            "video_urls": video_urls,
            "voice_id": voice_id,
            "video_file_id": video_file_id
        }

if __name__ == "__main__":
    gen_video('/mnt/ianch-Secondary/Programming/htn2025/public/University of Waterloo.mp3', '/mnt/ianch-Secondary/Programming/htn2025/public/4cfc3a660bc9c4ebf4ed073025dd0252.mp4', "Hello world")


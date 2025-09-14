from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from services.asr import ASRService
from utils.gcp import GCSClient
from utils.audio_preprocess import to_linear16_wav_file
import uuid, os, tempfile
import soundfile as sf
from pydub import AudioSegment
from services.answer_question import generate_answer
from Topview import gen_video_answer

router = APIRouter()
asr = ASRService()
gcs = GCSClient()

@router.post("/audio-to-text")
async def process_question_audio(
    audio: UploadFile = File(...),
    language: str = Form(default="en-US"),
    ppt_url: str = Form(default=None),
    voice_id: str = Form(default=None),
    video_file_id: str = Form(default=None),
    slide_number: int = Form(default=0)
):
    """
    Process uploaded audio file and convert to text using ASR
    """
    try:
        # 先把上传的文件保存到临时目录
        suffix = os.path.splitext(audio.filename)[-1]
        temp_in = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{suffix}")
        with open(temp_in, "wb") as f:
            f.write(await audio.read())

        # 用 pydub 打开
        audio_seg = AudioSegment.from_file(temp_in)

        local_mp3_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.mp3")
        audio_seg.export(local_mp3_path, format="mp3")

        local_ppt_path = None
        if ppt_url:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as ppt_temp:
                gcs.download_file(ppt_url, ppt_temp.name)
                local_ppt_path = ppt_temp.name

        # 调用 generate_answer
        speech = generate_answer(
            page_num=slide_number,
            audio_path=local_mp3_path,
            ppt_path=local_ppt_path,
            style="humorous",
            max_tokens=50
        )

        path = gen_video_answer(video_file_id, voice_id, speech)

        return JSONResponse({
            "code": 200,
            "message": "Success",
            "result_video_path": gen_video_answer
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio conversion failed: {e}")

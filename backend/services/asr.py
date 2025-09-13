from typing import List
from google.cloud import speech
from utils.audio_preprocess import to_linear16_wav_file  # 如果你的工具在 utils/audio_io.py

class ASRService:
    def __init__(self):
        self.client = speech.SpeechClient()

    def transcribe_local(self, path: str, language_code: str = "en-US", sample_rate: int = 16000) -> str:
        wav_path = to_linear16_wav_file(path, target_sr=sample_rate)
        with open(wav_path, "rb") as f:
            data = f.read()

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        audio = speech.RecognitionAudio(content=data)
        resp = self.client.recognize(config=config, audio=audio)
        texts: List[str] = [r.alternatives[0].transcript for r in resp.results]
        return "\n".join(texts).strip()

    def transcribe_gcs(self, gcs_uri: str, language_code: str = "en-US", sample_rate: int = 16000) -> str:
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        audio = speech.RecognitionAudio(uri=gcs_uri)
        op = self.client.long_running_recognize(config=config, audio=audio)
        resp = op.result(timeout=3600)
        texts = [r.alternatives[0].transcript for r in resp.results]
        return "\n".join(texts).strip()

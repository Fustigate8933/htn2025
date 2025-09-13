import os
import io
import uuid
import numpy as np
import soundfile as sf
import librosa
import tempfile

def to_linear16_wav_file(src_path: str, target_sr: int = 16000) -> str:
    """
    把任意常见音频转成16k PCM16 WAV，返回临时文件路径。
    """
    y, sr = librosa.load(src_path, sr=None, mono=False)

    # 转单声道
    if y.ndim > 1:
        if y.shape[0] < y.shape[1]:
            y = np.mean(y, axis=0)
        else:
            y = np.mean(y, axis=1)

    if sr != target_sr:
        y = librosa.resample(y.astype(np.float32), orig_sr=sr, target_sr=target_sr)
        sr = target_sr

    peak = float(np.max(np.abs(y)) + 1e-9)
    y = (y / peak) * 0.99
    y_i16 = (y * 32767.0).astype(np.int16)

    tmp_path = os.path.join(tempfile.gettempdir(), f"lin16_{uuid.uuid4().hex}.wav")
    sf.write(tmp_path, y_i16, sr, subtype="PCM_16")

    with sf.SoundFile(tmp_path) as f:
        ch, rate = f.channels, f.samplerate
    if ch != 1 or rate != target_sr:
        raise RuntimeError(f"Conversion failed: channels={ch}, sample_rate={rate}, expect mono/{target_sr}")

    return tmp_path

from gtts import gTTS
import base64
from io import BytesIO

def text_to_voice(text: str, lang="en"):
    """
    Convert text to speech using gTTS
    Returns base64 encoded mp3 string
    """
    tts = gTTS(text=text, lang=lang)
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    audio_bytes = buf.read()
    return base64.b64encode(audio_bytes).decode("utf-8")

# services/text_to_voice.py
import base64
from google.cloud import texttospeech

def text_to_voice(text: str, lang: str = "en") -> str:
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=lang,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Convert audio content to base64 string
    audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")
    return audio_base64

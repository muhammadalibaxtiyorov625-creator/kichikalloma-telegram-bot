import os
import re
import logging
from elevenlabs.client import ElevenLabs
from elevenlabs import save, VoiceSettings

logger = logging.getLogger(__name__)

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', 'sk_730428986b5e2df84bb1601f8031b460b3e147879b38be3c')

def sanitize_text_for_speech(text: str) -> str:
    """HTML teglar va ortiqcha belgilarni tozalash"""
    clean = re.sub(r'<[^>]+>', '', text)
    # Ba'zi emojilarni olib tashlash yoki soddalashtirish
    clean = re.sub(r'[🔢🎉✨💡🚀👏🗣️🇬🇧💖⭐🎯🆘ℹ️🔄🤖]', '', clean)
    clean = clean.replace('\n', ' ').strip()
    return clean[:400]

def generate_voice(text: str, output_path: str = 'javob.mp3', voice_id: str = 'JBFqnCBsd6RMkjVDRZzb') -> str:
    """Matnni ElevenLabs orqali insondek jonli va tiniq ovozga aylantirish"""
    try:
        clean_text = sanitize_text_for_speech(text)
        if not clean_text:
            clean_text = "Salom, do'stim! Sizga yordam berishdan xursandman."

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.text_to_speech.convert(
            text=clean_text,
            voice_id=voice_id,
            model_id='eleven_multilingual_v2',
            voice_settings=VoiceSettings(
                stability=0.45,
                similarity_boost=0.85,
                style=0.5,
                use_speaker_boost=True
            )
        )
        save(audio, output_path)
        return output_path
    except Exception as e:
        logger.error(f'ElevenLabs TTS xatosi: {e}')
        return None


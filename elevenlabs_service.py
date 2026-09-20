import os
import re
import hashlib
import logging
import asyncio
import tempfile
import subprocess

logger = logging.getLogger(__name__)

# Edge-TTS import
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# ImageIO-FFmpeg va SpeechRecognition import (Aniq STT uchun)
try:
    import imageio_ffmpeg
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    imageio_ffmpeg = None
    sr = None
    STT_AVAILABLE = False

# ElevenLabs import (zaxira uchun)
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', 'sk_730428986b5e2df84bb1601f8031b460b3e147879b38be3c')
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def sanitize_text_for_speech(text: str, lang: str = "uz") -> str:
    """
    Ovoz uchun matnni tozalash:
    - Barcha HTML teglar olib tashlanadi
    - Barcha emoji va maxsus belgilar olib tashlanadi
    - Qavs ichidagi talaffuz yo'riqnomalari olib tashlanadi: [heloʻu], [epl]
    - Asterisk, o'q, iqtibos belgilari olib tashlanadi
    - Faqat O'zbek ovozi bilan o'qiladigan matni qoldiradi
    """
    # 1. HTML teglarni olib tashlash
    clean = re.sub(r'<[^>]+>', '', text)
    # 2. Barcha emoji va unicode maxsus belgilarni olib tashlash
    clean = re.sub(
        r'[\U0001F000-\U0001FFFF'
        r'\U00002702-\U000027B0'
        r'\U000024C2-\U0001F251'
        r'\U0001f926-\U0001f937'
        r'\u200d\u2640-\u2642'
        r'\u2600-\u2B55'
        r'\u23cf\u23e9\u231a\ufe0f\u3030]+',
        '', clean, flags=re.UNICODE
    )
    # 3. Qavs ichidagi talaffuz yo'riqnomalarini olib tashlash: [heloʻu] [epl] [frend]
    clean = re.sub(r'\[.*?\]', '', clean)
    # 4. Raqamli ro'yxat belgisi (1. 2. 3.) ni tozalash
    clean = re.sub(r'^\s*\d+\.\s*', '', clean, flags=re.MULTILINE)
    # 5. Maxsus belgilarni tozalash
    clean = re.sub(r'[•\*\-–—►▶→↓↑]', ' ', clean)
    # 6. Ko'p bo'sh joy va yangi satrlarni birlashtirish
    clean = re.sub(r'\s+', ' ', clean).strip()
    # 7. Maksimal uzunlik: 380 belgi
    if len(clean) > 380:
        clean = clean[:380].rsplit(' ', 1)[0] + '.'
    return clean

def transcribe_voice(audio_file_path: str, lang: str = "uz") -> str:
    """Ovozli xabarni (STT) tinglab, tanlangan tilga mos matnga aylantirish"""
    if not os.path.exists(audio_file_path):
        return None

    # Tilga mos Google STT kodi
    stt_lang = "uz-UZ"
    if lang == "ru":
        stt_lang = "ru-RU"
    elif lang == "en":
        stt_lang = "en-US"

    # 1-USUL: Google Speech Recognition + FFmpeg (O'ta aniq va bepul!)
    if STT_AVAILABLE and imageio_ffmpeg and sr:
        try:
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            temp_wav = audio_file_path + ".temp.wav"
            cmd = [
                ffmpeg_exe, "-y", "-i", audio_file_path,
                "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
                temp_wav
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=12)
            if res.returncode == 0 and os.path.exists(temp_wav):
                r = sr.Recognizer()
                with sr.AudioFile(temp_wav) as source:
                    audio = r.record(source)
                try:
                    text = r.recognize_google(audio, language=stt_lang)
                    if text and len(text.strip()) > 0:
                        logger.info(f"SpeechRecognition muvaffaqiyatli eshitdi ({stt_lang}): {text}")
                        return text.strip()
                except Exception:
                    pass
                finally:
                    if os.path.exists(temp_wav):
                        try: os.remove(temp_wav)
                        except Exception: pass
        except Exception as e:
            logger.warning(f"Google STT xatosi: {e}")

    # 2-USUL: ElevenLabs Scribe zaxirasi
    if ELEVENLABS_AVAILABLE and ELEVENLABS_API_KEY:
        try:
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            with open(audio_file_path, "rb") as f:
                res = client.speech_to_text.convert(
                    file=f,
                    model_id="scribe_v1",
                    language_code=lang if lang in ["uz", "ru", "en"] else "uz"
                )
                text = res.text.strip() if res and hasattr(res, "text") else ""
                if text:
                    logger.info(f"ElevenLabs STT muvaffaqiyatli eshitdi: {text}")
                    return text
        except Exception as e:
            logger.error(f"ElevenLabs STT xatolik: {e}")

    return None

def generate_voice(text: str, output_path: str = 'javob.mp3', lang: str = 'uz') -> str:
    """Matnni Microsoft Neural Edge-TTS orqali FAQAT O'zbek SardorNeural ovoziga aylantirish"""
    try:
        clean_text = sanitize_text_for_speech(text, lang)
        if not clean_text or len(clean_text.strip()) < 2:
            clean_text = "Salom, do'stim! Sizga yordam berishdan xursandman."

        # FAQAT O'zbek Sardor ovozi — bitta, izchil, boy ovozi
        voice_name = "uz-UZ-SardorNeural"
        pitch = "+12Hz"
        rate = "+2%"

        # 1. Tezkor kesh tekshiruvi
        text_hash = hashlib.md5(f"{lang}:{voice_name}:{clean_text}".encode('utf-8')).hexdigest()
        cached_file = os.path.join(CACHE_DIR, f"{text_hash}.mp3")
        if os.path.exists(cached_file) and os.path.getsize(cached_file) > 1000:
            import shutil
            shutil.copy2(cached_file, output_path)
            return output_path

        # 2. Microsoft Edge-TTS orqali jonli, tabiiy ovoz
        if EDGE_TTS_AVAILABLE:
            try:
                async def _gen():
                    comm = edge_tts.Communicate(clean_text, voice=voice_name, rate=rate, pitch=pitch)
                    await comm.save(cached_file)

                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as pool:
                            pool.submit(lambda: asyncio.run(_gen())).result(timeout=10)
                    else:
                        asyncio.run(_gen())
                except Exception:
                    asyncio.run(_gen())

                if os.path.exists(cached_file) and os.path.getsize(cached_file) > 1000:
                    import shutil
                    shutil.copy2(cached_file, output_path)
                    logger.info(f"Edge-TTS ({voice_name}) ovoz muvaffaqiyatli yaratildi.")
                    return output_path
            except Exception as edge_err:
                logger.warning(f"Edge-TTS xatosi: {edge_err}")

        # 3. Zaxira: ElevenLabs
        if ELEVENLABS_AVAILABLE and ELEVENLABS_API_KEY:
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            audio = client.text_to_speech.convert(
                text=clean_text,
                voice_id='JBFqnCBsd6RMkjVDRZzb',
                model_id='eleven_multilingual_v2',
                voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
            )
            save(audio, cached_file)
            import shutil
            shutil.copy2(cached_file, output_path)
            return output_path

    except Exception as e:
        logger.error(f"Ovoz yaratishda umumiy xatolik: {e}")

    return None

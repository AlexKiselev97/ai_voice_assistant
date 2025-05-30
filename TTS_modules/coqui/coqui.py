from TTS.api import TTS
from playsound import playsound
import torch

def text_to_speech(engine: TTS, text, lang, stop_event):
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    for s in sentences:
        if stop_event():
            return
        #print('converting text to wav...')
        engine.tts_to_file(s,
                        speaker=engine.speakers[36],
                        language=lang,
                        file_path="coqui_output.wav")
        playsound("coqui_output.wav")

def get_voice_engine(lang_):
    print('Loading voice engine...')
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(TTS().list_models())
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)
    print(tts.speakers)
    print('Done!')
    return tts

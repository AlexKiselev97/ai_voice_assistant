import time
import pyttsx3
import os

def text_to_speech(engine, text, lang, is_running):
    engine.say(text)
    engine.runAndWait()

def get_voice_engine(lang):
    print('Loading voice engine...')
    engine = pyttsx3.init(driverName='sapi5' if os.name == "win" else "espeak")
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[102].id if lang == 'ru' else voices[23].id) 
    #if os.name == "win":
    #    engine.setProperty('voice', voices[0 if lang == 'ru' else 1].id)
    time.sleep(5)
    print('Done!')
    return engine

if __name__ == "__main__":
    eng = get_voice_engine('ru')
    text_to_speech(eng, 'Привет, как дела?', 'ru', lambda: False)
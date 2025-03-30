import time
import pyttsx3
import os

def text_to_speech(engine, text, lang, is_running):
    engine.say(text)
    engine.runAndWait()

def get_voice_engine(lang):
    print('Loading voice engine...')
    engine = pyttsx3.init(driverName='sapi5' if os.name == "win" else "espeak")
    #voices = engine.getProperty('voices')
    #if os.name == "win":
    #    engine.setProperty('voice', voices[0 if lang == 'ru-RU' else 1].id)
    #else:
        #engine.setProperty('voice', voices[62].id if lang == 'ru-RU' else voices[11].id) 
    time.sleep(5)
    print('Done!')
    return engine
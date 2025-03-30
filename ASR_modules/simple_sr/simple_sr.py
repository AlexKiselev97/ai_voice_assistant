import speech_recognition as sr
from playsound import playsound

lang_ = None

def convert_lang(lang):
    return lang
    #return 'en-EN' if lang == 'en' else 'ru-RU'

def get_asr_engine(lang):
    global lang_
    lang_ = lang
    return sr.Recognizer()

def detect_keyword(keyword, model : sr.Recognizer, stop_event):
    try:
        with sr.Microphone() as source:
            print("Listening for keyword...")
            audio = model.listen(source, timeout=3)
    except:
        return False
    
    try:
        detected_text = model.recognize_google(audio, language=convert_lang(lang_))
        return keyword.lower() in detected_text.lower()
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return False
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return False
    except:
        return False
    
    
def capture_command(asr_engine, stop_event):
    with sr.Microphone() as source:
        print("Please say your command...")
        audio = asr_engine.listen(source)
    
    try:
        command = asr_engine.recognize_google(audio, language=convert_lang(lang_))
        print(f"Command recognized: {command}")
        return command
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

if __name__ == "__main__":
    eng = get_asr_engine('en')
    capture_command(eng)
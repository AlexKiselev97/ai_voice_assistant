import speech_recognition as sr
from playsound import playsound

lang_ = None

def get_asr_engine(lang):
    global lang_
    lang_ = lang
    return sr.Recognizer()

def detect_keyword(keyword, model : sr.Recognizer, stop_event):
    while not stop_event():
        print(f"Listening for keyword: '{keyword}'...")
        try:
            with sr.Microphone() as source:
                audio = model.listen(source)
            detected_text = model.recognize_google(audio, language=lang_)
            if keyword.lower() in detected_text.lower():
                return True
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except:
            pass
    
def capture_command(asr_engine, stop_event):
    print('Listening for command...')
    with sr.Microphone() as source:
        audio = asr_engine.listen(source)
    
    try:
        command = asr_engine.recognize_google(audio, language=lang_)
        print(f"Command recognized: {command}")
        return command
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

if __name__ == "__main__":
    eng = get_asr_engine('ru')
    capture_command(eng, lambda: False)
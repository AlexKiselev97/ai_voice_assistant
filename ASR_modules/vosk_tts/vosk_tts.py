import pyaudio
from vosk import Model, KaldiRecognizer, SetLogLevel
import json
import os

def get_model_name(lang):
    return "vosk-model-ru-0.42" if lang == 'ru' \
        else "vosk-model-en-us-0.22"

def get_asr_engine(lang):
    model_name = get_model_name(lang)
    SetLogLevel(-1)
    try:
        print(f'Loading {model_name}...')
        return Model(model_name)
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def detect_keyword(keyword, model, stop_event):
    if model is None:
        return False
    
    recognizer = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                   channels=1,
                   rate=16000,
                   input=True,
                   frames_per_buffer=1024)
    
    print(f"Listening for keyword: '{keyword}'...")
    try:
        while not stop_event():
            data = stream.read(1024)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                if result:  # Check if we got actual text
                    text = result['text'] if type(result) != type("") else result
                    if text:
                        print('Recognized: ' + text)
                    # Check if keyword is present (case-insensitive)
                    if keyword.lower() in text.lower():
                        print(f"Keyword '{keyword}' detected!")
                        return True
                    
            # Check partial results
            elif recognizer.PartialResult():
                partial = recognizer.PartialResult()
                # Get text from partial result
                if len(partial.split()) > 1:
                    text = json.loads(partial)["partial"]
                    if text:
                        print('Recognized: ' + text)
                    # Check if keyword is present in partial result
                    if keyword.lower() in text.lower():
                        print(f"Keyword '{keyword}' detected!")
                        return True
                    
    except KeyboardInterrupt:
        print("\nDetection stopped by user")
    finally:
        # Cleanup resources
        stream.stop_stream()
        stream.close()
        p.terminate()

def capture_command(model, stop_event):
    recognizer = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                   channels=1,
                   rate=16000,
                   input=True,
                   frames_per_buffer=1024)
    
    print("Listening for command...")
    try:
        while not stop_event():
            data = stream.read(1024)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = result['text'] if type(result) != type("") else json.loads(result)["text"]
                if text.strip():
                    print(f"\nCommand captured: '{text}'")
                    return text
    finally:
        # Cleanup resources
        stream.stop_stream()
        stream.close()
        p.terminate()
    return ""

if __name__ == "__main__":
    eng = get_asr_engine('ru')
    while True:
        capture_command(eng, lambda: False)
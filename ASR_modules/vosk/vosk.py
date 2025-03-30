import pyaudio
from vosk import Model, KaldiRecognizer, SetLogLevel
import json
import os

def get_model_name(lang):
    return "vosk-model-ru-0.42" if lang == 'ru' \
        else "vosk-model-en-us-0.22"

def get_asr_engine(lang):
    model_name = get_model_name(lang)
    # Initialize Vosk model
    SetLogLevel(-1)
    try:
        return Model(model_name)
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

def detect_keyword(keyword, model, stop_event):
    """
    Detects a specific keyword from microphone input using Vosk speech recognition.
        
    Returns:
        bool: True if keyword is detected, False otherwise
    """
    
    # Create recognizer with sample rate 16000
    recognizer = KaldiRecognizer(model, 16000)
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # Open microphone stream
    stream = p.open(format=pyaudio.paInt16,
                   channels=1,
                   rate=16000,
                   input=True,
                   frames_per_buffer=1024)
    
    print(f"Listening for keyword: '{keyword}'...")
    
    try:
        while not stop_event():
            # Read audio data
            data = stream.read(1024)
            
            # Check if we got a final result
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                print(result)
                
                # Get the text from the result
                if result:  # Check if we got actual text
                    print(type(result))
                    text = result['text'] if type(result) != type("") else result
                    
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
    """
    Captures a voice command from microphone input using Vosk speech recognition.
        
    Returns:
        str: Transcribed text from voice input
    """
    SetLogLevel(-1)
    
    # Create recognizer with sample rate 16000
    recognizer = KaldiRecognizer(model, 16000)
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # Open microphone stream
    stream = p.open(format=pyaudio.paInt16,
                   channels=1,
                   rate=16000,
                   input=True,
                   frames_per_buffer=1024)
    
    print("Listening for command...")
    
    try:
        while not stop_event():
            # Read audio data
            data = stream.read(1024)
            
            # Check if we got a final result
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                
                # Get the text from the result
                text = json.loads(result)['text']
                
                # Only return if we actually got some text
                if text.strip():
                    print(f"\nCommand captured: '{text}'")
                    return text
                    
            # Check partial results
            elif recognizer.PartialResult():
                partial = recognizer.PartialResult()
                # Don't process partial results here - wait for complete phrase
                
    except KeyboardInterrupt:
        print("\nCapture stopped by user")
    finally:
        # Cleanup resources
        stream.stop_stream()
        stream.close()
        p.terminate()
    return ""

import os
import torch
import sounddevice as sd
import string

def load_silero_model(model_path):
    print(f'Loading {model_path}...')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found. Please download it manually.")
    device = torch.device('cpu')
    torch.set_num_threads(4)
    # Load the model directly without downloading
    model = torch.package.PackageImporter(model_path).load_pickle("tts_models", "model")
    model.to(device)
    print('Silero model is loaded!')
    return model, device

def text_to_speech(engine, text, lang, stop_event):
    speaker = 'en_0' if lang == 'en' else 'xenia'

    russian_alphabet_lowercase = ""
    for c in range(ord('а'), ord('я')+1):
        russian_alphabet_lowercase += chr(c)
    russian_alphabet_uppercase = ""
    for c in range(ord('А'), ord('Я')+1):
        russian_alphabet_uppercase += chr(c)
    alphabet = string.ascii_lowercase + string.ascii_uppercase + russian_alphabet_lowercase + russian_alphabet_uppercase

    sentences = [s.strip() for s in text.split('.') if s.strip()]
    for s in sentences:
        if stop_event():
            return
        if all(c not in s for c in alphabet):
            continue
        print(f'saying: {s}')
        audio = engine.apply_tts(
            text=s,
            speaker=speaker,
            sample_rate=48000
        )
        sd.play(audio, 48000)
        status = sd.wait()

def get_voice_engine(lang):
    model, device = load_silero_model('v3_en.pt' if lang == 'en' else 'v4_ru.pt')
    return model

if __name__ == "__main__":
    eng = get_voice_engine('en')
    text_to_speech(eng, 'hello, my name is Bill', 'en', lambda: False)
    eng = get_voice_engine('ru')
    text_to_speech(eng, 'привет, меня зовут Антоша', 'ru', lambda: False)
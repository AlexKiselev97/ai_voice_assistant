from os import walk
import importlib

def get_available_tts():
    for (dirpath, dirnames, filenames) in walk("./TTS_modules"):
        return [d for d in dirnames if "__" not in d]
    
def get_func(module_name, func_name):
    module = importlib.import_module(f"TTS_modules.{module_name}.{module_name}")
    return getattr(module, func_name)

def text_to_speech(module_name, engine, text, lang, stop_event):
    return get_func(module_name, 'text_to_speech')(engine, text, lang, stop_event)

def get_voice_engine(module_name, lang):
    return get_func(module_name, 'get_voice_engine')(lang)
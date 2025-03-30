from os import walk
import importlib

def get_available_asr():
    for (dirpath, dirnames, filenames) in walk("./ASR_modules"):
        return [d for d in dirnames if "__" not in d]

def get_func(module_name, func_name):
    module = importlib.import_module(f"ASR_modules.{module_name}.{module_name}")
    return getattr(module, func_name)

def get_asr_engine(module_name, lang):
    return get_func(module_name, 'get_asr_engine')(lang)

def detect_keyword(module_name, keyword, model, stop_event):
    return get_func(module_name, 'detect_keyword')(keyword, model, stop_event)

def capture_command(module_name, asr_engine, stop_event):
    return get_func(module_name, 'capture_command')(asr_engine, stop_event)

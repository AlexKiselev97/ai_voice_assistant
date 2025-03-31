from os import walk
import importlib

def get_available_llm():
    for (dirpath, dirnames, filenames) in walk("./LLM_modules"):
        return [d for d in dirnames if "__" not in d]

def get_func(module_name, func_name):
    module = importlib.import_module(f"LLM_modules.{module_name}.{module_name}")
    return getattr(module, func_name)

def get_model_list(module_name):
    return get_func(module_name, 'get_model_list')()

def get_response(module_name, command, model, lang):
    return get_func(module_name, 'get_response')(command, model, lang)

def parse_response(module_name, content):
    return get_func(module_name, 'parse_response')(content)

def print_model_response(module_name, thoughts, response):
    return get_func(module_name, 'print_model_response')(thoughts, response)

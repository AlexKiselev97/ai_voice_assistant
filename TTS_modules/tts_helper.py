from os import walk

def get_available_asr():
    for (dirpath, dirnames, filenames) in walk("./TTS_modules"):
        return [d for d in dirnames if "__" not in d]
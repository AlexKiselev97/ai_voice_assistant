import subprocess
import ollama

def get_model_list():
    result = subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        text=True,
        check=True
    )
    models = []
    for line in result.stdout.splitlines():
        name = line.split(' ')[0]
        if (name == "NAME"):
            continue
        models.append(name)
    return models

def get_response(command, model, lang):
    print(f'Getting response from {model}...')
    core_prompt = {
        "en" : "You are a helpful assistant. You will be asked a question. Answer the question as short as you can.",
        "ru" : "Ты голосовой ассистент. Тебе будет задан вопрос от пользователя и тебе нужно ответить коротко и ясно.",
    }
    messages = [
        {
            'role': 'system',
            'content': core_prompt[lang]
        },
        {
            'role': 'user',
            'content': command
        }
    ]
    response = ollama.chat(model=model, messages=messages)
    return response

def parse_response(content):
    thoughts = []
    response = []
    is_thinking = False
    for line in content.splitlines():
        if line == '':
            continue
        if line.startswith('<think>'):
            is_thinking = True
            continue
        if line.startswith('</think>'):
            is_thinking = False
            continue
        line = line.replace('**', '')
        if is_thinking:
            thoughts.append(line)
        else:
            response.append(line)
    return thoughts, response

def print_model_response(thoughts, response):
    #print('Model thoughts:')
    #for line in thoughts:
    #    print(line)
    #print('---------------------')
    print('Model response:')
    for line in response:
        print(line)
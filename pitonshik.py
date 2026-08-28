import os
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, MessagesRole ,Function, FunctionParameters, FunctionCall
import webbrowser
import subprocess

load_dotenv()

def verify_with_model(chad, user_request, code_output):
    """Использует модель для проверки соответствия кода запросу"""
    verification_messages = [
        {"role": "system", "content": "Ты проверяешь, соответствует ли вывод программы запросу пользователя. Отвечай только 'True' - если да или 'Fasle' - если нет."},
        {"role": "user", "content": f"Запрос: {user_request}\nВывод программы: {code_output}\nСоответствует?"}
    ]
    
    verification_response = chad.get_response(verification_messages)

    return verification_response

def check(code):
    """Проверяет код и возвращает результат"""
    with open("project_info.py", 'w', encoding='utf-8') as f:
        f.write(code)
    
    result = subprocess.run(
        ['python', 'project_info.py'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() or None
    }

    
few_shot_examples = [
    {
        'role': 'user',
        'content': 'Напиши мне код который выводит hello world',
    },
    {
        'role': 'assistant',
        'content': "hello_world!('print')"
    },
]

class gigachat:
    def __init__(self, api_key: str = os.getenv("API_KEY"), model: str = "GigaChat-2-Max"):
        self.api_key = api_key

        self.model = model
        self.client = self.get_client()

        self.dialog_history = []
        self.promt = ''
        
    def get_client(self):
        return GigaChat(
            base_url="https://api.giga.chat/v1",
            credentials=self.api_key,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False,
        )
    
    def get_response(self, MESSAGE):
        chat = Chat(
        model=self.model,
        messages=MESSAGE,
        functions=[
            Function(
                name='vibe_code',
                description='Вызывай когда нужно написать код. Передавай код в параметре code',
                parameters=FunctionParameters(
                    type='object',
                    properties={
                        'code': {
                            'type': 'string',
                            'description': 'Python код для выполнения'
                        }
                    },
                    required=['code']
                )
            ),
        ],
        function_call="auto"
    )
        return self.client.chat(chat)
    
    def create_system_prompt(self) -> str:
        prompt = f"""Ты - интеллектуальный автоответчик для проекта '{self.promt}'

Правила работы:
1. Когда пользователь просит написать код, ВЫЗЫВАЙ функцию vibe_code
2. Передавай код в параметре 'code' функции vibe_code
3. Код должен быть чистым Python кодом без пояснений
4. Если результат не тот который ожидался, переписываешь код"""
        return prompt

    
    
    def hand_func(self, response):
        if hasattr(response.choices[0].message, 'function_call') and response.choices[0].message.function_call:
            func_name = response.choices[0].message.function_call.name
            if func_name == 'vibe_code':
                return ['vibe_code', check(response)]
        else:
            return None

def main():
    name_file = "project_info.py"
    chad = gigachat()


    MESSAGES = [
        {"role": "system", "content": chad.create_system_prompt()}
    ]
    for i in few_shot_examples:
        MESSAGES.append(i)

    while True:
        promt = input("\nВведи запрос: ")

        if promt == "exit":
            break
        
        USER_PROMPT = {"role": "user", "content": promt}
        MESSAGES.append(USER_PROMPT)
        
        final_response = None
        code_success = False
        

        resp = chad.get_response(MESSAGES)
        
        f_recp = chad.hand_func(resp)
        if f_recp:
            
            print('Произошел вызов функции!')
            for i in range(3):
                args_str = resp.choices[0].message.function_call.arguments or "{}"
                try:
                    args_dict = json.loads(args_str)
                    code = args_dict.get('code') or resp.choices[0].message.content or ''
                except:
                    code = resp.choices[0].message.content or ''
            
            # Проверяем код на синтаксис
                check_result = check(code)
            
                if check_result["success"] and verify_with_model():
                    # Код выполнился без ошибок
                    print(f'✅ Код выполнен без ошибок')
                    print(f'📋 Вывод: {check_result["output"]}')
                    code_success = True
                    break
            args_str = resp.choices[0].message.function_call.arguments or "{}"
            try:
                args_dict = json.loads(args_str) if args_str else {}
            except (json.JSONDecodeError, TypeError):
                args_dict = {}
            assistant_message = {
            "role": "assistant",
            "content": resp.choices[0].message.content or "",
            "function_call": {
                "name": resp.choices[0].message.function_call.name,
                "arguments": args_dict
            }
            }
            MESSAGES.append(assistant_message)
            MESSAGES.append({"role": "function", "name": f_recp[0], "content": f_recp[1]})
            response = chad.get_response(MESSAGES)
        else:
            response = resp
        
        ANSWER = {"role": response.choices[0].message.role, "content": response.choices[0].message.content}
    
        MESSAGES.append(ANSWER)
    
    
    
        print(f"\n\nВам ответил {response.choices[0].message.content}")
        print(f"\nПотрачено: {response.usage.total_tokens}")
        
if __name__ == '__main__':
    main()
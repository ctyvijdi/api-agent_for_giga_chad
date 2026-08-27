import os
import json
import subprocess
import random
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Function, FunctionParameters
from datetime import datetime

load_dotenv()

def create_file(name_file): # Плохо прописано, не прверяет наличие дириктории. Создает файл если путь корректный. Нужно дописать обработку на существование папки и корректность пути
    open(name_file, "w", encoding="utf-8").close()
    
def write_file(name_file, content): # Теже недочеты что и с create_file
    file = open(name_file, "a", encoding="utf-8")
    file.write(content)
    file.close    

def adding_numbers(a, b):
    try:
        return json.dumps({"result": float(a) + float(b)})
    except:
        return json.dumps({"error": "Неверные аргументы"})
    
    
    
def handle_commands(prompt, MESSAGES):
    if prompt == "\\history":
        print_MESSAGES(MESSAGES)
        return True
    if prompt == "\\help":
        print("Команды:\nhistory – история\nhelp – справка\nexit – выход")
        return True
    if prompt == "\\exit":
        print("\nДо свидания!\n")
        exit(0)
    return False
    
def print_MESSAGES(MESSAGES):
    print("-" * 60)
    for msg in MESSAGES:
        print(msg)
    print("-" * 60)
    
def print_hello(V):
    print("Helper for изучения русского языка")
    print(f"VERSIONE: {V}")
    print("Выберите режим работы:\n1) Выдать текст из папки 'exp_text'\n2) Вытащить текст из вашего файла")
    while True:
        answer = input("Выбор: ")
        if answer == '1':
            return 1
        if answer == '2':
            file_PATH = input("Путь до файла и название файла в виде '\папка1\папка\название_файла': ")
            return file_PATH
        else:
            print('поробуйте еще раз:')
            
            
# ---------- РАБОТА С МОДЕЛЬЮ ----------
def get_response(client, MESSAGES):
    """Отправляет запрос к GigaChat."""
    
    # Иначе передаём все функции
    functions = [
        Function(
            name="adding_numbers",
            description="Складывает два числа и возвращает результат. Работает только с числами (целыми или дробными). Не выполняет другие математические операции.",
            parameters=FunctionParameters(
                type="object",
                properties={
                    "a": {"type": "number", "description": "Первое слагаемое (число)"},
                    "b": {"type": "number", "description": "Второе слагаемое (число)"}
                },
                required=["a", "b"]
            )
        )
    ]
    
    chat = Chat(
        model="GigaChat-2",
        messages=MESSAGES,
        functions=functions,
        function_call="auto"
    )
    return client.chat(chat)





def handle_function_call(response):
    """Обрабатывает вызов функции из ответа модели."""
    msg = response.choices[0].message
    if hasattr(msg, 'function_call') and msg.function_call:
        func_name = msg.function_call.name
        args = msg.function_call.arguments
        
        if func_name == "get_current_time":
            return ("get_current_time", get_current_time())
        elif func_name == "adding_numbers":
            return ("adding_numbers", adding_numbers(args['a'], args['b']))
        
    return None

def get_client():
    return GigaChat(
        base_url="https://api.giga.chat/v1",
        credentials=os.getenv("API_KEY"),
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )
    
# ---------- НАСТРОЙКА МОДЕЛИ ----------
model = "GigaChat-2"

SYSTEM_PROMPT_MD = "Полученный текст переведи в .md верству и выдай ответ обратно, чтобы его было удобно вставить в файл. Не пиши ничего лишнего. Работай только с текстом который тебе отправлен и ничего не меняй в нем"
SYSTEM_PROMPT = ""

MESSAGES_MD = [{"role": "system", "content": SYSTEM_PROMPT_MD}]
MESSAGES = [{"role": "system", "content": SYSTEM_PROMPT}]

# ---------- ОСНОВНОЙ ЦИКЛ ----------
def main():
    TOKEN_USE = 0
    client = get_client()
    
    ###ПОЛУЧЕНИЕ ТЕКСТА, ВЫБОР РЕЖИМА РАБОТЫ. СОЗДАНИЕ text.md
    Working_hours = print_hello("1.0") # Выбор режима работы и приветствие
    text = ''
    
    if Working_hours == 1:
        text_files_name = os.listdir('exp_text/') # Файлы с текстами
        name_file = "exp_text\\" + random.choice(text_files_name)
        file = open(name_file, 'r', encoding="utf-8")
        text = file.read()
        file.close()
    else:
        file = open(Working_hours, 'r', encoding="utf-8")
        text = file.read()
        file.close()
        
    print("-=" * 40)
    print(text)
    print("-=" * 40)    
    
    MESSAGES_MD.append({"role": "user", "content": text})
    
    response_md = get_response(client, MESSAGES_MD)
    
    create_file("text.md")
    write_file("text.md", response_md.choices[0].message.content)
    print("\n--------Копия текста из терминала сохранена в text.md--------\n")
    ###ПОЛУЧЕНИЕ ТЕКСТА, ВЫБОР РЕЖИМА РАБОТЫ. СОЗДАНИЕ text.md
    
    
    
        
    
    
    
    

    

    # Первый запрос пользователя
    while True:
        prompt = input("\nВведи запрос: ")
        if handle_commands(prompt, MESSAGES):
            continue
        break
    
    MESSAGES.append({"role": "user", "content": prompt})

    while True:
        # 1. Отправляем запрос к модели
        response = get_response(client, MESSAGES)
        
        # 2. Проверяем, не вызвала ли модель функцию
        func_result = handle_function_call(response)
        
        if func_result:
            func_name, func_content = func_result
            
            # Добавляем сообщение о вызове функции
            func_call_msg = {
                "role": response.choices[0].message.role,
                "content": response.choices[0].message.content or "",
                "function_call": {
                    "name": func_name,
                    "arguments": response.choices[0].message.function_call.arguments
                }
            }
            MESSAGES.append(func_call_msg)
            
            # Добавляем результат функции
            func_result_msg = {
                "role": "function",
                "name": func_name,
                "content": func_content
            }
            MESSAGES.append(func_result_msg)
            
            # Если это был запрос пользователя, то мы уже внутри user_answer получили ввод,
            # и он вернул JSON с полем "answer". Добавим это сообщение пользователя в историю.
            if func_name == "user_answer":
                user_data = json.loads(func_content)
                user_prompt = user_data["answer"]
                MESSAGES.append({"role": "user", "content": user_prompt})
            
            # Продолжаем цикл – отправляем новый запрос с обновлённой историей
            continue
        
        # 3. Если вызова функции не было – это обычный текстовый ответ
        print(f"\n\nВам ответил {model}: {response.choices[0].message.content}")
        assistant_msg = {"role": "assistant", "content": response.choices[0].message.content}
        MESSAGES.append(assistant_msg)
        print(f"\nПротрачено за запрос (токенов): {response.usage.total_tokens}")
        TOKEN_USE += response.usage.total_tokens
        print(f"Протрачено всего (токенов): {TOKEN_USE}")

        
        # 4. Запрашиваем новый ввод пользователя
        while True:
            prompt = input("\nВведи запрос: ")
            if handle_commands(prompt, MESSAGES):
                continue
            break
        MESSAGES.append({"role": "user", "content": prompt})
        # Цикл повторяется – отправим запрос с функциями, т.к. последнее сообщение – user

if __name__ == "__main__":
    main()

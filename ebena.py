import os
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, MessagesRole

load_dotenv()

class gigachat:
    def __init__(self, api_key: str = os.getenv("API_KEY"), model: str = "GigaChat-2-Max"):
        self.api_key = api_key or os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API ключ не найден. Укажите его в .env файле")
        
        self.model = model
        self.client = self.get_client()
        self.project_info = ""
        self.project_name = "Проект"
        self.info_loaded = False
        self.dialog_history = []
        
    def get_client(self) -> GigaChat:
        return GigaChat(
            base_url="https://api.giga.chat/v1",
            credentials=self.api_key,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False,
            model=self.model
        )
    
    def load_project_info(self, filepath: str = "project_info.txt") -> bool:
        try:
            path = Path(filepath)
            if not path.exists():
                print(f"❌ Ошибка: Файл {filepath} не найден")
                return False
            
            if path.suffix.lower() != '.txt':
                print(f"❌ Ошибка: Файл {filepath} не является текстовым файлом")
                return False
            
            # Читаем файл
            with open(path, 'r', encoding='utf-8') as file:
                self.project_info = file.read()
            
            if not self.project_info.strip():
                print("❌ Ошибка: Файл пустой")
                return False
            
            # Пытаемся найти название проекта (первая строка)
            lines = self.project_info.strip().split('\n')
            if lines:
                first_line = lines[0].strip()
                if first_line.startswith('#') or first_line.startswith('Название'):
                    self.project_name = first_line.lstrip('#').strip()
                    if ':' in self.project_name:
                        self.project_name = self.project_name.split(':', 1)[1].strip()
            
            self.info_loaded = True
            print(f"✅ Описание проекта загружено: {self.project_name}")

            self.dialog_history = []
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при чтении файла: {e}")
            return False
    
    def create_system_prompt(self) -> str:
        if not self.info_loaded:
            return "Ты - интеллектуальный помощник."
        
        return f"""Ты - интеллектуальный автоответчик для проекта '{self.project_name}'.

Вот информация о проекте:
{self.project_info}

Отвечай на вопросы пользователей, используя информацию о проекте. Если ответа нет в информации - скажи об этом."""

    def get_response(self, messages: List[Dict]) -> Optional[Chat]:
        try:
            if not self.client:
                self.client = self.get_client()

            # Проверяем, есть ли системный промпт
            has_system = any(msg.get("role") == "system" for msg in messages)
            
            # Если нет системного промпта и есть информация о проекте - добавляем
            if not has_system and self.info_loaded:
                system_prompt = self.create_system_prompt()
                # ВСТАВЛЯЕМ системный промпт в НАЧАЛО списка
                messages.insert(0, {"role": "system", "content": system_prompt})
            elif not has_system:
                # Если нет системного промпта и нет информации о проекте
                messages.insert(0, {"role": "system", "content": "Ты - интеллектуальный помощник."})

            chat = Chat(
                model=self.model,
                messages=messages
            )
            response = self.client.chat(chat)
            return response
        except Exception as e:
            print(f'Ошибка: {e}')
            return None

def save_response(response, model):
    with open("answer.md", "a", encoding="utf-8") as file:
        file.write(f"\n\nВам ответил {model}:")
        file.write(response.choices[0].message.content)
        file.write(f"\nПотрачено: {response.usage.total_tokens}")

API_KEY = os.getenv("API_KEY")
MODEL = "GigaChat-2"

name_file = "answer.md"
chad = gigachat()
chad.load_project_info()

# Инициализация истории сообщений - УБИРАЕМ системное сообщение отсюда
MESSAGES = []  # Пустой список

while True:
    promt = input("\nВведи запрос: ")
    
    if promt == "exit":
        break
    
    USER_PROMPT = {"role": "user", "content": promt}
    MESSAGES.append(USER_PROMPT)
    
    # Получаем ответ от модели
    resp = chad.get_response(MESSAGES)
    
    if resp is None:
        print("❌ Не удалось получить ответ")
        MESSAGES.pop()  # Удаляем последнее сообщение пользователя
        continue
    
    ANSWER = {"role": resp.choices[0].message.role, "content": resp.choices[0].message.content}
    MESSAGES.append(ANSWER)
    
    print(f"\n\nВам ответил {MODEL}: {resp.choices[0].message.content}")
    print(f"\nПотрачено: {resp.usage.total_tokens}")
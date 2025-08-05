import json
import os
import weaviate
from weaviate.classes.config import Property, DataType
from typing import List, Dict, Any


def populate_weaviate_collection(client: weaviate.Client, json_file_path: str):
    """Заполняет коллекцию Weaviate данными из JSON-файла"""

    # 1. Проверка существования файла
    if not os.path.exists(json_file_path):
        print(f"Ошибка: Файл {json_file_path} не существует")
        return

    # 2. Получаем коллекцию
    try:
        chunks_collection = client.collections.get("Knowledge_graph1")
    except Exception as e:
        print(f"Ошибка при получении коллекции: {str(e)}")
        return

    # 3. Чтение и обработка JSON файла
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Если данные не являются списком, преобразуем в список
            if not isinstance(data, list):
                data = [data]

            # 4. Вставка данных в коллекцию
            for item in data:
                try:
                    # Подготовка свойств с проверкой наличия ключей
                    properties = {
                        "chunk_id": item.get("chunk_id", ""),
                        "label": item.get("label", ""),
                        "definition": item.get("definition", ""),
                        "abbreviation": item.get("abbreviation", ""),  # Исправлено опечатку "abbrevation"
                        "hasStatement": item.get("hasStatement", []),
                        "type": item.get("type", "")
                    }

                    # Вставка объекта
                    chunks_collection.data.insert(properties=properties)
                    print(f"Добавлена сущность: {properties['label']} (ID: {properties['chunk_id']})")

                except Exception as e:
                    print(f"Ошибка при обработке элемента: {str(e)}")
                    continue

    except json.JSONDecodeError:
        print("Ошибка: Неверный формат JSON файла")
    except Exception as e:
        print(f"Ошибка при чтении файла: {str(e)}")


if __name__ == "__main__":
    # Конфигурация
    JSON_FILE_PATH = "C:/Users/MSI/PycharmProjects/PythonProject/utilities/merge_json.json"

    try:
        # Подключение к Weaviate
        client = weaviate.connect_to_local(
            host="localhost",
            port=8081,
            grpc_port=50051,
        )
        # Заполнение коллекции
        populate_weaviate_collection(client, JSON_FILE_PATH)

        print("Загрузка данных завершена успешно")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    finally:
        # Закрытие соединения
        if 'client' in locals():
            client.close()
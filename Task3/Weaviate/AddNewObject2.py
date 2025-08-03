import json
import os

import weaviate
from weaviate import Client
from weaviate.classes.config import Property, DataType

def populate_weaviate_collection(client: Client, chunks_dir: str):
    """Заполняет коллекцию Weaviate чанками из JSON-файлов"""

    # 1. Получаем коллекцию
    chunks_collection = client.collections.get("ClientProcessChunks")

    # 2. Читаем все JSON-файлы в указанной директории
    for filename in os.listdir(chunks_dir):
        if not filename.endswith('.json'):
            continue

        with open(os.path.join(chunks_dir, filename), 'r', encoding='utf-8') as f:
            try:
                chunk_data = json.load(f)

                # 3. Подготавливаем данные для вставки
                properties = {
                    "content": chunk_data["content"],
                    "chunk_id": chunk_data["id"],
                    "type": chunk_data.get("type", ""),
                    "source": chunk_data.get("source", ""),
                    "keywords": chunk_data.get("keywords", [])
                }

                # 4. Добавляем объект в коллекцию
                chunks_collection.data.insert(
                    properties=properties,
                    # vector=vector  # Можно предварительно рассчитать векторы
                )

                print(f"Добавлен чанк: {chunk_data['id']}")

            except Exception as e:
                print(f"Ошибка при обработке {filename}: {str(e)}")


# Использование
if __name__ == "__main__":
    # Путь к папке с чанками
    CHUNKS_DIR = "C:/Users/MSI/PycharmProjects/PythonProject/2text_chunks/chunks2"

    client = weaviate.connect_to_local(
        host="localhost",
        port=8081,
        grpc_port=50051,
    )
    # Заполнение коллекции
    populate_weaviate_collection(client, CHUNKS_DIR)

    print("Загрузка чанков завершена")
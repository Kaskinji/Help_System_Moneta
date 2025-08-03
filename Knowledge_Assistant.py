import weaviate
from weaviate.classes.query import Filter, MetadataQuery
import re
from typing import List, Dict, Optional
import string
from pymorphy2 import MorphAnalyzer  # Для русского языка
import nltk
from nltk.corpus import stopwords

# Инициализация инструментов для русского языка
nltk.download('stopwords')
morph = MorphAnalyzer()
russian_stopwords = stopwords.words('russian')


class QueryProcessor:
    def __init__(self):
        # Подключение к Weaviate
        self.client = weaviate.connect_to_local(
            host="localhost",
            port=8081,
            grpc_port=50051
        )
        self.collection = self.client.collections.get("Knowledge_graph")

    def preprocess_query(self, query: str) -> str:
        """
        Препроцессинг пользовательского запроса:
        1. Удаление пунктуации
        2. Приведение к нижнему регистру
        3. Удаление стоп-слов
        4. Лемматизация
        """
        # Удаление пунктуации
        query = query.translate(str.maketrans('', '', string.punctuation))

        # Приведение к нижнему регистру и разбиение на слова
        words = query.lower().split()

        # Удаление стоп-слов и лемматизация
        processed_words = []
        for word in words:
            if word not in russian_stopwords and len(word) > 2:
                lemma = morph.parse(word)[0].normal_form
                processed_words.append(lemma)

        return ' '.join(processed_words)

    def semantic_search(self, processed_query: str, entity_type: Optional[str] = None) -> List[Dict]:
        """
        Семантический поиск в Weaviate с возможностью фильтрации по типу сущности
        """
        # Подготовка фильтра
        filters = Filter.by_property("type").equal(entity_type) if entity_type else None

        # Выполнение гибридного запроса
        response = self.collection.query.hybrid(
            query=processed_query,
            alpha=0.5,  # Баланс между семантикой и ключевыми словами
            query_properties=["label^2", "hasStatement"],  # Удвоенный вес для label
            filters=filters,
            return_metadata=MetadataQuery(score=True),
            limit=5
        )

        # Форматирование результатов
        results = []
        for obj in response.objects:
            result = {
                "label": obj.properties["label"],
                "type": obj.properties["type"],
                "score": round(obj.metadata.score, 3),
                "relations": obj.properties.get("hasStatement", []),
                "chunk_id": obj.properties.get("chunk_id", "")
            }
            results.append(result)

        return results

    def close(self):
        self.client.close()

if __name__ == "__main__":
    processor = QueryProcessor()

    try:
        # Пример запроса пользователя
        user_query = "Клиенту отказано в регистрации заявки из-за того, что Клиент с такой эл. почтой уже зарегистрирован в Системе. Что делать?"

        # Препроцессинг запроса
        processed_query = processor.preprocess_query(user_query)
        print(f"Обработанный запрос: {processed_query}")

        # Семантический поиск (с фильтрацией по типу Process)
        search_results = processor.semantic_search(processed_query, entity_type="Process")

        # Вывод результатов
        print("\nРезультаты поиска:")
        for idx, result in enumerate(search_results, 1):
            print(f"\n{idx}. {result['label']} (тип: {result['type']}, score: {result['score']})")
            print(f"   Отношения: {result['relations']}")
            print(f"   Источник: chunk_id={result['chunk_id']}")

    finally:
        processor.close()
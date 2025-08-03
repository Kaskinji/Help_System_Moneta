import weaviate
from weaviate import Config
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import List, Dict


class DocumentSearcher:
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        self.client = weaviate.connect_to_local(
            host="localhost",
            port=8081,
            grpc_port=50051,
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """Извлекает ключевые слова из запроса"""
        # Удаляем стоп-слова и выделяем существительные/глаголы
        keywords = re.findall(r'\b[А-Яа-яЁёA-Za-z]{4,}\b', text.lower())
        return list(set(keywords))  # Удаляем дубли

    def _enforce_keywords(self, text: str, keywords: List[str], threshold: int = 1) -> bool:
        """Проверяет, содержит ли текст достаточно ключевых слов"""
        count = sum(1 for kw in keywords if kw in text.lower())
        return count >= threshold

    def search(self, user_query: str) -> Dict:
        """Основная функция поиска"""
        keywords = self._extract_keywords(user_query)
        print(f"Ключевые слова запроса: {keywords}")

        # 1. Поиск в Weaviate с учетом ключевых слов
        response = (
            self.client.collections.get("Vectorise_chunks2")
            .query.hybrid(
                query=user_query,
                alpha=0.5,  # Баланс между семантикой и ключевыми словами
                limit=5,
                return_properties=["content", "chunk_id"],
                return_metadata=weaviate.classes.query.MetadataQuery(score=True)
            )
        )

        if not response.objects:
            return {"error": "Релевантных чанков не найдено"}

        # 2. Поиск наиболее релевантного фрагмента
        query_embedding = self.model.encode(user_query)
        best_match = None
        best_score = -1

        for chunk in response.objects:
            content = chunk.properties["content"]

            # Разбиваем на предложения
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', content) if s.strip()]

            # Векторизуем все предложения
            sentence_embeddings = self.model.encode(sentences)

            # Сравниваем с запросом
            similarities = cosine_similarity([query_embedding], sentence_embeddings)[0]

            for i, score in enumerate(similarities):
                sentence = sentences[i]

                # Учитываем только фрагменты, содержащие ключевые слова
                if self._enforce_keywords(sentence, keywords) and score > best_score:
                    best_score = score
                    best_match = {
                        "text": sentence,
                        "chunk_id": chunk.properties["chunk_id"],
                        "score": float(score),
                        "keywords_found": [kw for kw in keywords if kw in sentence.lower()]
                    }

        if not best_match:
            return {"error": "Точного ответа не найдено"}

        return best_match


# Пример использования
if __name__ == "__main__":
    searcher = DocumentSearcher()
    user_query = "Что делать, если Клиент получил отказ в регистрации по причине «Не зарегистрирован в ЕГРЮЛ»"

    result = searcher.search(user_query)

    if "error" in result:
        print(result["error"])
    else:
        print("Найденный ответ:")
        print(result["text"])
        print(f"\nКлючевые слова в ответе: {result['keywords_found']}")
        print(f"ID чанка: {result['chunk_id']}")
        print(f"Score: {result['score']:.4f}")

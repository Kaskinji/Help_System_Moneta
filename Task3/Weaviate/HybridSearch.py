from Entities_extraction import Extract_Entities_Querry
import weaviate
from weaviate.classes.query import HybridFusion
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import parsing_ttl2
from typing import List, Dict
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    Doc
)

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

client = weaviate.connect_to_local(
    host="localhost",
    port=8081,
    grpc_port=50051,
)

def extract_relevant_part(text: str, query: str, min_similarity: float = 0.7) -> str:
    sentences = re.split(r'([.!?]\s+)', text)
    sentences = [sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else '')
                 for i in range(0, len(sentences), 2) if sentences[i].strip()]

    if not sentences:
        return ""

    query_embedding = model.encode(query)
    sentence_embeddings = model.encode([re.sub(r'[.!?]\s*$', '', s) for s in sentences])

    similarities = cosine_similarity([query_embedding], sentence_embeddings)[0]

    first_relevant_idx = next(
        (i for i, score in enumerate(similarities) if score >= min_similarity),
        -1
    )

    if first_relevant_idx == -1:
        return sentences[np.argmax(similarities)].strip()

    relevant_part = ''.join(sentences[first_relevant_idx:]).strip()
    relevant_part = re.sub(r'(?<!\w)\.(?!\s|$)', '', relevant_part)

    return relevant_part

def search_precise_answer(user_query: str, limit: int = 1):
    try:
        chunks_collection = client.collections.get("ClientProcessChunks")
        response = chunks_collection.query.hybrid(
            query=user_query,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            limit=limit,
            alpha=0.7,
            return_metadata=["score"],
            return_properties=["content", "chunk_id"]
        )

        if not response.objects:
            return {"status": "not_found", "message": "Ответ не найден"}

        best_chunk = response.objects[0]
        relevant_part = extract_relevant_part(
            best_chunk.properties["content"],
            user_query,
            min_similarity=0.6
        )

        if not relevant_part:
            relevant_part = "Точный ответ не найден в документе. Обратитесь к эксперту."

        return {
            "status": "success",
            "answer": relevant_part,
            "source": best_chunk.properties["chunk_id"],
            "score": best_chunk.metadata.score
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

def extract_and_enrich_terms(answer_text: str, weaviate_client) -> Dict[str, List[Dict]]:
    def extract_terms_with_nlp(text: str) -> List[str]:
        """Интеллектуальное извлечение терминов с помощью NLP"""
        segmenter = Segmenter()
        morph_vocab = MorphVocab()
        emb = NewsEmbedding()
        morph_tagger = NewsMorphTagger(emb)

        doc = Doc(text)
        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)

        terms = set()
        current_term = []

        for token in doc.tokens:
            if len(token.text) < 3 and not token.text.isupper():
                continue

            if token.text.istitle() or token.text.isupper():
                current_term.append(token.text)
            else:
                if current_term:
                    terms.add(' '.join(current_term))
                    current_term = []

        if current_term:
            terms.add(' '.join(current_term))

        patterns = [
            r'\b[А-ЯЁA-Z][а-яёa-z-]+\s[А-ЯЁA-Z][а-яёa-z-]+\b',
            r'\b[А-ЯЁA-Z]{2,}\b',
            r'\b[а-яёa-z-]+\.[а-яёa-z-]+\b'
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text):
                terms.add(match.group())

        return sorted(terms, key=len, reverse=True)

    def find_term_definitions(terms: List[str], client) -> List[Dict]:
        glossary = client.collections.get("Knowledge_graph1")
        found_terms = []

        for term in terms:
            response = glossary.query.hybrid(
                query=term,
                query_properties=["label", "hasStatement"],
                limit=1,
                alpha=0.5
            )

            if response.objects:
                term_data = response.objects[0]
                found_terms.append({
                    "term": term_data.properties["label"],
                    "definition": term_data.properties["definition"]
                })

        return found_terms

    potential_terms = extract_terms_with_nlp(answer_text)
    enriched_terms = find_term_definitions(potential_terms, weaviate_client)

    return {
        "original_text": answer_text,
        "terms": enriched_terms
    }


def format_terms_for_display(terms: List[Dict]) -> str:
    """Форматирует список терминов для вывода в требуемом формате"""
    if not terms:
        return "Нет определений терминов"

    formatted = []
    for term in terms:
        formatted.append(f"{term['term']} - {term['definition']}")

    return "\n".join(formatted)


if __name__ == "__main__":
    queries = [
        "Клиенту отказано в регистрации заявки из-за того, что Клиент с такой эл. почтой уже зарегистрирован в Системе. Что делать?",
        "Как узнать результат проверки заявки отделом ОБР?",
        "Что делать, если Клиент получил отказ в регистрации по причине «Не зарегистрирован в ЕГРЮЛ»."
    ]

    for query in queries:
        print(f"\nЗапрос: '{query}'")
        result = search_precise_answer(query)

        if result["status"] == "success":
            querry_entities = Extract_Entities_Querry(result['answer'])
            querry_json = parsing_ttl2(querry_entities, "0")
            print(querry_json)
            print("\nТочный ответ:")
            print(result["answer"])
            print(f"\nID чанка: {result['source']}")

            print(f"\nScore: {result['score']:.3f}")
        else:
            print("Ошибка:", result["message"])

    client.close()
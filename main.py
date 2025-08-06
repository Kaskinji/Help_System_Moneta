from Weaviate.HybridSearch import search_precise_answer
from Weaviate.parsing_ttl2 import parse_ttl_to_json, create_ttl_file
from Weaviate.SearchHybridUp import search_hybrid_up
from Entities_extraction.Extract_Entities_Querry import extract_entities_from_chunk2

ENTITIES_IN = 'C:/Users/MSI/PycharmProjects/PythonProject/utilities/entities.ttl'
ENTITIES_OUT = 'C:/Users/MSI/PycharmProjects/PythonProject/utilities/entities.json'
REQUEST = 'Как происходит подключение к системе монета.ру?'

requests = [
        "Как узнать, что ригистрация заявки на подключение прошла успешно?"
    ]
for request in requests:
    result = search_precise_answer(request)
    triplets = extract_entities_from_chunk2(result['answer'])
    create_ttl_file(ENTITIES_IN, triplets)
    parse_ttl_to_json(triplets, ENTITIES_IN, ENTITIES_OUT)
    result2 = search_hybrid_up(ENTITIES_OUT)
    print(f'ЗАПРОС:\n {request}\nОТВЕТ:\n {result['answer']}\nТРИПЛЕТЫ:\n {triplets}\nОТВЕТ2:\n {result2}')


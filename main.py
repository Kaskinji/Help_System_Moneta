from Task3.Weaviate.HybridSearch import search_precise_answer
from Task3.Weaviate.parsing_ttl2 import parse_ttl_to_json, create_ttl_file
from Task3.Weaviate.SearchHybridUp import search_hybrid_up
from Entities_extraction.Extract_Entities_Querry import extract_entities_from_chunk2


REQUEST = 'Как происходит подключение к системе монета.ру?'
ENTITIES_IN = 'C:/Users/MSI/PycharmProjects/PythonProject/utilities/entities.ttl'
ENTITIES_OUT = 'C:/Users/MSI/PycharmProjects/PythonProject/utilities/entities.json'


result = search_precise_answer(REQUEST)
triplets = extract_entities_from_chunk2(result['answer'])
create_ttl_file(ENTITIES_IN, triplets)
parse_ttl_to_json(triplets, ENTITIES_IN, ENTITIES_OUT)
hz_kak_nazvat = search_hybrid_up(ENTITIES_OUT)
#l

print(f'ЗАПРОС:\n {REQUEST}\nОТВЕТ:\n {result['answer']}\nТРИПЛЕТЫ:\n {triplets}\nОТВЕТ2:\n {hz_kak_nazvat}')
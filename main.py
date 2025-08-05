from Task3.Weaviate.HybridSearch import search_precise_answer
from Task3.Weaviate.parsing_ttl2 import parse_ttl_to_json
from Task3.Weaviate.SearchHybridUp import search_hybrid_up
from Entities_extraction.Extract_Entities_Querry import extract_entities_from_chunk2


REQUEST = 'Клиенту отказано в регистрации заявки из-за того, что Клиент с такой эл. почтой уже зарегистрирован в Системе. Что делать?'
ENTITIES_IN = '/Users/ilya/Documents/GitHub/Help_System_Moneta/utilities/entities.ttl'
ENTITIES_OUT = '/Users/ilya/Documents/GitHub/Help_System_Moneta/utilities/entities.json'


result = search_precise_answer(REQUEST)
triplets = extract_entities_from_chunk2(result['answer']), ENTITIES_IN, ENTITIES_OUT
parse_ttl_to_json(triplets, ENTITIES_IN, ENTITIES_OUT)
hz_kak_nazvat = search_hybrid_up(ENTITIES_OUT)

print(f'ЗАПРОС:\n {REQUEST}\nОТВЕТ:\n {result['answer']}\nТРИПЛЕТЫ:\n {triplets}\nОТВЕТ2:\n {hz_kak_nazvat}')
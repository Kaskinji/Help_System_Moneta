import os
import json
from openai import OpenAI
from Comcore_E_Ontology import comcore_E_ontology
from Comcore_R_Ontology import comcore_R_ontology
import time
import re

or_api_key = "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"
os.environ["OR_TOKEN"] = or_api_key
# Настройки
model = "deepseek/deepseek-r1-0528:free"  # Или другая модель
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OR_TOKEN"],
)
output_dir = "C:/Users/MSI/PycharmProjects/PythonProject/triplets/triplets2"


def read_json_files(directory):
    """Чтение всех JSON файлов из указанной директории с сортировкой по числовому ID"""
    json_contents = []

    # Получаем все JSON-файлы и сортируем их по числовому ID
    n = 1 # Начальный
    m = 39 # Конечный
    files = list(filter(lambda x: x.endswith('.json') and int(re.search(r'\d+', x).group()) in range(n, m+1), os.listdir(directory)))

    # Новая функция для извлечения числового ID из имени файла
    def extract_id(filename):
        # Удаляем 'chunk' и '.json', затем берем только числовую часть перед любыми суффиксами
        base = filename.replace('chunk', '').replace('.json', '')
        # Извлекаем только цифры из начала строки
        num_part = ''
        for char in base:
            if char.isdigit():
                num_part += char
            else:
                break
        return int(num_part) if num_part else 0

    files.sort(key=extract_id)  # Сортировка по ID

    for filename in files:
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if 'content' in data:
                    json_contents.append({
                        'id': extract_id(filename),
                        'content': data['content']
                    })
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Ошибка при чтении файла {filename}: {str(e)}")

    return json_contents


def extract_entities_from_chunk(chunk_content, chunk_id):
    prompt = f'''
    ТЕХНИЧЕСКОЕ ЗАДАНИЕ:
    Извлеки из предоставленного текста ВСЕ сущности и отношения, СТРОГО СООТВЕТСТВУЮЩИЕ ОНТОЛОГИИ СУЩНОСТЕЙ И ОТНОШЕНИЙ.
    Формат вывода ТОЛЬКО Turtle (ttl) без каких-либо пояснений или комментариев.

    ЖЕСТКИЕ ТРЕБОВАНИЯ:
    1. Извлечение:
    - ТОЛЬКО сущности и отношения, СТРОГО соответствующие классам и свойствам онтологии
    - НИКАКИХ посторонних элементов или интерпретаций
    - Если сущность не соответствует онтологии - НЕ включать её
    - идентификаторы извлеченных сущностей формируются по правилу ":label", где label - это словоформа, описывающая сущность (метка или имя сущности); при этом, если словоформа длиннее, чем 40 символов, то она обрезается на 40-м символе; если словоформа состоит из нескольких слов, то она формируется как одно слово, в котором вместо пробела подставляется нижнее подчеркивание (например ":оператор_отдела"); если такой идентификатор уже существует, то либо это та же сущность и надо только добавить новые ее атрибуты или связи или, если это другая похожая по начальному имени сущность, то сформировать идентификатор с добавлением в конце инкрементируемого номера (":оператор_отдела_02")
    - идентификатор_предиката берется из файла описывающего онтологию в соответствии с форматом ont_name:predicate_name;
    - 1. Извлечение:
    - ТОЛЬКО сущности и отношения, явно соответствующие классам и свойствам онтологии
    - НИКАКИХ посторонних элементов или интерпретаций
    - Если сущность не соответствует онтологии - НЕ включать её
    - идентификаторы извлеченных сущностей формируются по правилу ":label", где label - это словоформа, описывающая сущность (метка или имя сущности); при этом, если словоформа длиннее, чем 40 символов, то она обрезается на 40-м символе; если словоформа состоит из нескольких слов, то она формируется как одно слово, в котором вместо пробела подставляется нижнее подчеркивание (например ":оператор_отдела"); если такой идентификатор уже существует, то либо это та же сущность и надо только добавить новые ее атрибуты или связи или, если это другая похожая по начальному имени сущность, то сформировать идентификатор с добавлением в конце инкрементируемого номера (":оператор_отдела_02")
    - идентификатор_предиката берется из файла описывающего онтологию в соответствии с форматом ont_name:predicate_name;
    - должна быть гарантия, что каждая сущность 
    - Для КАЖДОЙ сущности добавьте связь с чанком через предикат comcore:mentionedIn
    Пример:
     :регистрация comcore:mentionedIn : 42 .
     id текущего чанка: {chunk_id}
     
    2. Формат идентификаторов:
    - :lowercase_with_underscores
    - Максимум 40 символов
    
    3. (ОБЯЗАТЕЛЬНО) Для каждой сущности минимум три триплета: тип, метка и связь:
    (идентификатор_сущности, rdf:type, ont_name:class_name);
    (идентификатор_сущности, rdfs:label, "имя сущности");
    (идентификатор_сущности, идентификатор_предиката, идентификатор_сущности_2);
    
    4. ЗАПРЕЩЕНО:
    - в ответе выдавать блок <think>
    - Добавлять комментарии
    - Изменять формат вывода
    - Изобретать несуществующие в онтологии свойства
    
    5. Для каждой сущности формата "Термин - определение" к триплету добавить свойство dc:definition. Предыдущие поля с отношениями должны быть указаны обязательно независимо от того фигурируют они или нет в definition.
    Пример:
    :авторизационные_данные rdf:type comcore:Resource ;
    rdfs:label "Авторизационные данные"@ru ;
    comcore:isResourceOf :вход_в_личный_кабинет ;
    dc:definition "Авторизационные данные - адрес электронной почты, представляемый НКО Получателем при регистрации в Системе МОНЕТА.РУ для входа в Личный кабинет в Системе МОНЕТА.РУ." .

                 
    ТЕКСТ: 
{chunk_content}
    ОНТОЛОГИЯ: 
{comcore_E_ontology}
    ОТНОШЕНИЯ: 
{comcore_R_ontology}

    Пример КОРРЕКТНОГО вывода:
    ```
    :тариф rdf:type comcore:Resource ;
    rdfs:label "Тариф"@ru ;
    comcore:isResourceOf :упрощенная_идентификация ;
    comcore:canBeResourceFor :начисление_вознаграждения ;
    dc:description """
    Тариф - определение...""".
    :торговая_площадка rdf:type comcore:Agent ;
    rdfs:label "Торговая площадка"@ru ;
    comcore:isActorOf :обеспечение_взаимодействия ;
    comcore:isResponsibleFor :программно-аппаратный_комплекс ;
    dc:description """
    Торговая площадка - определение...""".

    :упрощенная_идентификация rdf:type comcore:Process ;
    rdfs:label "Упрощенная идентификация"@ru ;
    comcore:hasResult :статус_неидентифицированного_клиента ;
    comcore:isPartOf :процедура_проверки_клиента ;
    dc:description """
    Упрощенная идентификация - определение...""".
    '''

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3  # Для более детерминированных результатов
    )

    return response.choices[0].message.content


def process_json_files(json_contents):
    """Обработка всех JSON файлов и сохранение результатов в отдельные TTL файлы"""
    for item in json_contents:
        chunk_id = item['id']
        chunk_content = item['content']
        output_file = os.path.join(output_dir, f"rdf_triplets_{chunk_id}.ttl")

        try:
            # Извлекаем сущности и отношения
            entities_ttl = extract_entities_from_chunk(chunk_content, chunk_id)

            # Записываем в файл
            with open(output_file, 'w', encoding='utf-8') as ttl_file:
                # Записываем префиксы в начало файла
                ttl_file.write("@prefix : <#> .\n")
                ttl_file.write("@prefix comcore: <https://kb.moneta.ru/terms/common/coreontology#> .\n")
                ttl_file.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
                ttl_file.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n")

                # Записываем заголовок с ID чанка
                ttl_file.write(f"\n{entities_ttl}\n")

            print(f"Обработан чанк {chunk_id}, результат сохранен в {output_file}")
            time.sleep(10)
        except Exception as e:
            print(f"Ошибка при обработке чанка {chunk_id}: {str(e)}")
            continue


# Укажите директорию с JSON файлами
json_directory = "C:/Users/MSI/PycharmProjects/PythonProject/chunks/chunks_111"
json_contents = read_json_files(json_directory)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

process_json_files(json_contents)
print("Обработка всех файлов завершена")
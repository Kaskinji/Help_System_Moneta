import weaviate
from weaviate.classes.query import MetadataQuery
import json
import re

# Загрузка данных из NeedEntity.json
with open("/Users/ilya/Documents/GitHub/Help_System_Moneta/utilities/entities.json", "r", encoding="utf-8") as f:
    need_entities = json.load(f)
    print(f"Загружено {len(need_entities)} сущностей")

# Подключение к Weaviate
client = weaviate.connect_to_local(
    host="localhost",
    port=8081,
    grpc_port=50051,
)

collection = client.collections.get("Knowledge_graph1")

# Список для хранения всех результатов
all_results = []

for entity in need_entities:
    # Формируем запрос из доступных полей
    query_parts = [
        entity.get("label", ""),
        entity.get("abbreviation", ""),
    ]
    query_text = " ".join(filter(None, query_parts))
    
    # Получаем тип, если есть
    entity_type = entity.get("type")
    

    # Создаем фильтр по типу, если он указан
    class_filter = weaviate.classes.query.Filter.by_property("type").equal(entity_type) if entity_type else None

    try:
        response = collection.query.hybrid(
            query=query_text,
            alpha=0.4,
            query_properties=["label^2", "definition"],  # Увеличиваем вес label
            filters=class_filter,
            return_metadata=MetadataQuery(score=True),
            limit=5
        )

        # Обрабатываем результаты
        for obj in response.objects:
            if obj.metadata.score > 0.5:  # Понижаем порог score для большего охвата
                label = obj.properties.get("label", obj.properties.get("name", "N/A"))
                definition = obj.properties.get("definition", "No definition available")
                score = obj.metadata.score
                
                if definition != '': 
                    result_str = f"{entity.get('label', '')}({label}) - {definition} (score: {score:.2f})\n"
                    print(result_str)

    except Exception as e:
        print(f"Ошибка при поиске для {entity.get('label', 'N/A')}: {str(e)}")

# Закрытие соединения
client.close()

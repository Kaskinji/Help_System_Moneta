import weaviate
from weaviate.classes.config import Configure, Tokenization
import weaviate.classes as wvc

# Стандартный порт для подключения к БД, это 8080. Но так как в docker-compose мы указали свободные порт 8081, то необходимо принудительно передать аргумент
client = weaviate.connect_to_local(
    host="localhost",
    port=8081,
    grpc_port=50051,
)
try:
    client.collections.delete("Knowledge_graph1")
    # Здесь создаём БД (коллекцию), перечисляем необходимые нам атрибуты у сущности
    collection = client.collections.create(
        name="Knowledge_graph1", # название коллекции
        properties=[
            wvc.config.Property(
                name="chunk_id",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
                index_filterable=True,
            ),
            wvc.config.Property(
                name="label",  # имя свойства
                data_type=wvc.config.DataType.TEXT,  # тип данных
                vectorize_property_name=True,  # векторизируем это свойство
                tokenization=Tokenization.LOWERCASE,  # токенизация по нижнему регистру
                index_filterable=True,  # индексация для фильтрации
                index_searchable=True,  # индексация для поиска
            ),
            wvc.config.Property(
                name="definition",
                data_type=wvc.config.DataType.TEXT,
                vectorize_property_name=True,
                tokenization=Tokenization.LOWERCASE,
                index_filterable=True,
                index_searchable=True,
            ),
            wvc.config.Property(
                name="abbreviation",
                data_type=wvc.config.DataType.TEXT,
                vectorize_property_name=True,
                tokenization=Tokenization.LOWERCASE,
                index_filterable=True,
                index_searchable=True,
            ),
            wvc.config.Property(
                name="hasStatement",
                data_type=wvc.config.DataType.TEXT_ARRAY,
                vectorize_property_name=True,
                tokenization=Tokenization.LOWERCASE,
                index_filterable=True,
                index_searchable=True,
            ),
            wvc.config.Property(
                name="type",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,  # не векторизируем
            ),
        ],
        vectorizer_config=Configure.Vectorizer.text2vec_transformers()
    )
finally:
    print('Collection created')
    client.close()

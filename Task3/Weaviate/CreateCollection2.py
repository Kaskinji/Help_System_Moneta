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
    client.collections.delete("ClientProcessChunksFinal")
    # Здесь создаём БД (коллекцию), перечисляем необходимые нам атрибуты у сущности
    collection = client.collections.create(
        name="ClientProcessChunksFinal", # название коллекции
        properties=[
            wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT, description="Текст чанка"
            ),
            wvc.config.Property(
                name="chunk_id", data_type=wvc.config.DataType.NUMBER, skip_vectorization=True
            ),
            wvc.config.Property(
                name="type", data_type=wvc.config.DataType.TEXT, index_filterable=True
            )
        ],
        vectorizer_config=Configure.Vectorizer.text2vec_transformers(

            pooling_strategy="masked_mean"  # Лучше для коротких текстов
        )
    )
finally:
    print('Collection created')
    client.close()

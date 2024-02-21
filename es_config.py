from elasticsearch import AsyncElasticsearch

client = AsyncElasticsearch(
    [
        {
            "scheme": "http",
            "host": "es",
            "port": 9200
        }
    ]
)

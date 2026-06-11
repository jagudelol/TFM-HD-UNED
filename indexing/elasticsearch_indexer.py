from elasticsearch import Elasticsearch
import os
import json

ELASTIC_PASSWORD = "PASSWORD"
CERT_FINGERPRINT = "FINGERPRINT"
# Create the client instance
es = Elasticsearch(
    "https://localhost:9200",
    ssl_assert_fingerprint=CERT_FINGERPRINT,
    basic_auth=("elastic", ELASTIC_PASSWORD),
)

indexes = ["aphorisms_basic", "aphorisms_stemmed", "aphorisms_bigram"]

for index in indexes:
    if not es.indices.exists(index=index):
        body1 = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {"analyzer": {"standard_analyzer": {"type": "standard"}}},
            },
            "mappings": {
                "properties": {
                    "author": {"type": "keyword"},
                    "book": {"type": "text", "analyzer": "standard_analyzer"},
                    "aphorism_number": {"type": "integer"},
                    "aphorism_content": {
                        "type": "text",
                        "analyzer": "standard_analyzer",
                    },
                }
            },
        }

        body2 = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "filter": {
                        "english_stemmer": {"type": "stemmer", "language": "english"},
                        "english_stopwords": {"type": "stop", "stopwords": "_english_"},
                    },
                    "analyzer": {
                        "stemmed_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "asciifolding",
                                "english_stopwords",
                                "english_stemmer",
                            ],
                        }
                    },
                },
            },
            "mappings": {
                "properties": {
                    "author": {"type": "keyword"},
                    "book": {"type": "text", "analyzer": "stemmed_analyzer"},
                    "aphorism_number": {"type": "integer"},
                    "aphorism_content": {
                        "type": "text",
                        "analyzer": "stemmed_analyzer",
                    },
                }
            },
        }

        body3 = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "filter": {
                        "ngram_filter": {
                            "type": "shingle",
                            "min_shingle_size": 2,
                            "max_shingle_size": 3,
                        },
                    },
                    "analyzer": {
                        "ngram_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "ngram_filter"],
                        },
                    },
                },
            },
            "mappings": {
                "properties": {
                    "author": {"type": "keyword"},
                    "book": {"type": "text", "analyzer": "ngram_analyzer"},
                    "aphorism_number": {"type": "integer"},
                    "aphorism_content": {"type": "text", "analyzer": "ngram_analyzer"},
                }
            },
        }

        es.indices.create(index=indexes[0], body=body1)
        print(f"Index '{indexes[0]}' created.")
        es.indices.create(index=indexes[1], body=body2)
        print(f"Index '{indexes[1]}' created.")
        es.indices.create(index=indexes[2], body=body3)
        print(f"Index '{indexes[2]}' created.")
    else:
        print(f"Index '{index}' already exists.")

folder_path = "folder/path"

for filename in os.listdir(folder_path):
    if filename.endswith(".es.json"):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r") as file:
            document = json.load(file)
        for index in indexes:
            es.index(index=index, body=document)
            print(f"Document from '{filename}' indexed in index {index}.")

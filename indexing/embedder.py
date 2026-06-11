import os
import json
import numpy as np
from elasticsearch import Elasticsearch
import gensim.downloader as api
from gensim.models import KeyedVectors


# 1) Parámetros
DATA_DIR = "data/directory"
INDEX_NAME = "INDEX NAME"
ELASTIC_URL = "https://localhost:9200"
ELASTIC_USER = "elastic user"
ELASTIC_PASS = "password"
CERT_FINGERPRINT = "Fingerprint"

# 2) Carga del modelo de embeddings

model = api.load("glove-wiki-gigaword-300")
model2 = KeyedVectors.load_word2vec_format("numberbatch-en-17.06.txt.gz", binary=False)
# 3) Conexión a Elasticsearch
es = Elasticsearch(
    ELASTIC_URL,
    ssl_assert_fingerprint=CERT_FINGERPRINT,
    basic_auth=(ELASTIC_USER, ELASTIC_PASS),
)

# 4) Crear índice si no existe
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(
        index=INDEX_NAME,
        body={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "filter": {
                        "english_stemmer": {"type": "stemmer", "language": "english"}
                    },
                    "analyzer": {
                        "stemmed_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "asciifolding",
                                "english_stemmer",
                            ],
                        }
                    },
                },
            },
            "mappings": {
                "properties": {
                    "author": {"type": "keyword"},
                    "book": {"type": "keyword"},
                    "aphorism_number": {"type": "integer"},
                    "aphorism_content": {
                        "type": "text",
                        "analyzer": "stemmed_analyzer",
                    },
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 300,
                        "index": True,
                        "similarity": "cosine",
                    },
                }
            },
        },
    )

# 5) Funciones de tokenización y embedding


def embed(text, mdl):
    tokens = [t for t in text.lower().split() if t in mdl]
    if not tokens:
        return np.zeros(mdl.vector_size, dtype=float)
    return np.mean([mdl[t] for t in tokens], axis=0)


# 6) Recorre JSON y indexa uno a uno
for fname in os.listdir(DATA_DIR):
    if not fname.endswith(".json"):
        continue

    path = os.path.join(DATA_DIR, fname)
    with open(path, encoding="utf8") as f:
        doc = json.load(f)

    author = doc.get("author", "")
    book = doc.get("book", "")
    num = doc.get("aphorism_number", "")
    content = doc.get("aphorism_content", "")

    vec = embed(content, model2)

    try:
        es.index(
            index=INDEX_NAME,
            document={
                "author": author,
                "book": book,
                "aphorism_number": num,
                "aphorism_content": content,
                "embedding": vec,
            },
        )
        print(f"Indexado: {author, book, num}")
    except Exception as e:
        print(f"ERROR al indexar {author, book, num}: {e}")

print("Proceso completado.")

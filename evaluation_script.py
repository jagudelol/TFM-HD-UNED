import csv
from datetime import datetime
import gensim.downloader as api
import numpy as np
import pandas as pd
from elasticsearch import Elasticsearch
from gensim.models import KeyedVectors


# Configuración del cliente Elasticsearch
ELASTIC_PASSWORD = "PASSWORD"
CERT_FINGERPRINT = "FINGERPRINT"
es = Elasticsearch(
    "https://localhost:9200",
    ssl_assert_fingerprint=CERT_FINGERPRINT,
    basic_auth=("elastic", ELASTIC_PASSWORD),
)


class AphorismEvaluator:
    def __init__(self, k):
        self.indices = [
            "aphorisms_basic",
            "aphorisms_stemmed",
            "aphorisms_bigram",
            "aphorisms_embeddings_1",
            "aphorisms_embeddings_2",
            "aphorisms_hybrid",
        ]
        self.k_value = k  # Top-K valores para evaluar

    def execute_search_across_indices(self, query):
        """Ejecuta una consulta en todos los índices y retorna resultados"""
        k = self.k_value
        results = {}

        def embed(text, mdl):
            tokens = [t for t in text.lower().split() if t in mdl]
            if not tokens:
                return np.zeros(mdl.vector_size, dtype=float)
            return np.mean([mdl[t] for t in tokens], axis=0)

        for index_name in self.indices:
            try:
                if index_name == "aphorisms_embeddings_1":
                    model1 = api.load("glove-wiki-gigaword-300")
                    query_vec1 = embed(query, model1)

                    search_body = {
                        "query": {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.qvec, 'embedding') + 1.0",
                                    "params": {"qvec": query_vec1},
                                },
                            }
                        },
                        "size": k,
                    }
                elif index_name == "aphorisms_embeddings_2":
                    model2 = KeyedVectors.load_word2vec_format(
                        "numberbatch-en-17.06.txt.gz", binary=False
                    )
                    query_vec2 = embed(query, model2)

                    search_body = {
                        "query": {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.qvec, 'embedding') + 1.0",
                                    "params": {"qvec": query_vec2},
                                },
                            }
                        },
                        "size": k,
                    }
                elif index_name == "aphorisms_hybrid":
                    model3 = KeyedVectors.load_word2vec_format(
                        "numberbatch-en-17.06.txt.gz", binary=False
                    )
                    query_vec3 = embed(query, model3)
                    search_body = {
                        "query": {
                            "bool": {
                                "should": [
                                    {
                                        "multi_match": {
                                            "query": query,
                                            "fields": [
                                                "book",
                                                "aphorism_content",
                                                "author",
                                            ],
                                            "type": "best_fields",
                                            "boost": 0.5,
                                        }
                                    },
                                    {
                                        "knn": {
                                            "field": "embedding",
                                            "query_vector": query_vec3,
                                            "k": k,
                                            "num_candidates": 100,
                                            "boost": 0.5,
                                        }
                                    },
                                ]
                            }
                        },
                        "size": k,
                    }
                else:
                    search_body = {
                        "query": {
                            "multi_match": {
                                "query": query,
                                "fields": "aphorism_content",
                                "type": "best_fields",
                                "fuzziness": "AUTO",
                            }
                        },
                        "size": k,
                    }

                result = es.search(index=index_name, body=search_body)
                results[index_name] = result["hits"]["hits"]

            except Exception as e:
                print(f"Error en búsqueda {index_name}: {e}")
                results[index_name] = []

        return results

    def create_evaluation_pool(self, queries):
        """Crea un pool de documentos únicos para evaluación"""
        all_docs = set()
        query_results = {}

        for i, query in enumerate(queries, 1):
            print(f"Procesando consulta {i}: {query}")
            results = self.execute_search_across_indices(query)
            query_results[f"Q{i}"] = {"query": query, "results": results}

            # Recopilar todos los documentos únicos
            for index_name, hits in results.items():
                for hit in hits:
                    all_docs.add(hit["_id"])

        return query_results, list(all_docs)

    def export_for_evaluation(self, queries, output_file="evaluation_pool.csv"):
        """Exporta resultados para evaluación manual"""
        query_results, unique_docs = self.create_evaluation_pool(queries)

        # Crear CSV para evaluadores
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Query_ID",
                "Query_Text",
                "Index_Name",
                "Document_ID",
                "Author",
                "Book",
                "Aphorism_Number",
                "Aphorism_Content",
                "Search_Score",
                "Relevance_Score",
                "Evaluator_Comments",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for query_id, query_data in query_results.items():
                query_text = query_data["query"]

                for index_name, hits in query_data["results"].items():
                    for hit in hits:
                        source = hit["_source"]
                        writer.writerow(
                            {
                                "Query_ID": query_id,
                                "Query_Text": query_text,
                                "Index_Name": index_name,
                                "Document_ID": hit["_id"],
                                "Author": source.get("author", ""),
                                "Book": source.get("book", ""),
                                "Aphorism_Number": source.get("aphorism_number", ""),
                                "Aphorism_Content": source.get("aphorism_content", ""),
                                "Search_Score": hit["_score"],
                                "Relevance_Score": "",  # Para completar por evaluadores
                                "Evaluator_Comments": "",  # Para completar por evaluadores
                            }
                        )

        print(f"Archivo de evaluación creado: {output_file}")
        print(f"Total consultas: {len(queries)}")
        print(f"Total documentos únicos en pool: {len(set(unique_docs))}")

        return query_results

    def calculate_metrics(self, evaluations_file):
        """Calcula métricas de precisión y recall desde evaluaciones completadas"""
        df = pd.read_csv(evaluations_file)

        # Filtrar solo documentos relevantes (asumiendo escala 0-2, relevante >= 1)
        relevant_threshold = 1

        metrics_results = {}

        for query_id in df["Query_ID"].unique():
            query_data = df[df["Query_ID"] == query_id]
            metrics_results[query_id] = {}
            # REVISAR BIEN ESTE FUNCIONAMIENTO
            val_pool = query_data[query_data["Relevance_Score"] == 1][
                "Aphorism_Number"
            ].nunique()
            for index_name in self.indices:
                index_data = query_data[
                    query_data["Index_Name"] == index_name
                ].sort_values("Search_Score", ascending=False)

                if len(index_data) == 0:
                    continue

                relevant_docs = index_data[
                    index_data["Relevance_Score"] >= relevant_threshold
                ]
                total_relevant = len(relevant_docs)

                print(f"Query ID: {query_id}")
                print(f"Index Name: {index_name}")
                print(f"Total documents: {len(index_data)}")
                print(f"Total relevant documents: {total_relevant}")

                precision_at_k_list = []
                index_metrics = {}

                for k in range(1, self.k_value + 1):
                    top_k = index_data.head(k)
                    relevant_in_k = len(
                        top_k[top_k["Relevance_Score"] >= relevant_threshold]
                    )

                    precision_k = relevant_in_k / k if k > 0 else 0
                    recall_k = relevant_in_k / val_pool if val_pool > 0 else 0
                    f1_k = (
                        2 * ((precision_k * recall_k) / (precision_k + recall_k))
                        if (precision_k + recall_k) > 0
                        else 0
                    )
                    index_metrics[f"Precision@{k}"] = precision_k
                    index_metrics[f"Recall@{k}"] = recall_k
                    index_metrics[f"F1-Score@{k}"] = f1_k
                    if index_data.iloc[k - 1]["Relevance_Score"] >= relevant_threshold:
                        precision_at_k_list.append(precision_k)
                print("Precision at k list:", precision_at_k_list)

                index_metrics["Average_Precision"] = (
                    sum(precision_at_k_list) / total_relevant
                    if total_relevant > 0
                    else 0
                )
                metrics_results[query_id][index_name] = index_metrics

        return metrics_results

    def generate_evaluation_report(
        self, metrics_results, output_file="evaluation_report.csv"
    ):
        """Genera reporte de evaluación en formato CSV"""
        # Preparar listas para crear el DataFrame
        rows = []

        # Iterar sobre cada query
        for query_id, query_metrics in metrics_results.items():
            # Iterar sobre cada índice
            for index_name, index_metrics in query_metrics.items():
                # Crear un diccionario para esta fila
                row = {
                    "Query_ID": query_id,
                    "Index_Name": index_name,
                    "Evaluation_Date": datetime.now().isoformat(),
                }
                # Agregar todas las métricas
                row.update(index_metrics)
                rows.append(row)

        # Crear DataFrame
        df = pd.DataFrame(rows)
        df = df.drop_duplicates()
        # Guardar como CSV
        df.to_csv(output_file, index=False, encoding="utf-8")

        print(f"Reporte generado: {output_file}")
        return df


# Función principal de uso
def run_evaluation(queries_list, k):
    """Función principal para ejecutar evaluación completa"""
    evaluator = AphorismEvaluator(k)

    print("=== INICIANDO EVALUACIÓN K-POOL ===")
    print(f"Consultas a evaluar: {len(queries_list)}")

    # Paso 1: Crear pool de evaluación
    query_pool = evaluator.export_for_evaluation(queries_list)

    print("\n=== SIGUIENTE PASO ===")
    print(
        "1. Completa el archivo 'evaluation_pool.csv' con las puntuaciones de relevancia"
    )
    print(
        "2. Ejecuta calculate_final_metrics('evaluation_pool_completed.csv') para obtener métricas"
    )

    return query_pool


def calculate_final_metrics(completed_evaluations_file, k):
    """Calcula métricas finales desde evaluaciones completadas"""
    evaluator = AphorismEvaluator(k)
    metrics = evaluator.calculate_metrics(completed_evaluations_file)
    report = evaluator.generate_evaluation_report(metrics)
    print("\n=== MÉTRICAS CALCULADAS ===")
    for index, row in report.iterrows():
        print(
            f"\n{row['Index_Name'].upper()}: \nAverage Precision: {row['Average_Precision']:.4f}"
        )

    return report


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo con consultas de prueba
    welcome = int(
        input(
            "Bienvenidx. \nIngresa 1 para ingresar consultas.\nIngrese 2 para el siguiente paso.\n"
        )
    )

    if welcome == 1:
        limite = int(input("Ingrese el número de consultas a realizar: "))
        if limite > 0:
            queries = [input(f"Ingrese la consulta {i + 1}: ") for i in range(limite)]
        else:
            None
    else:
        None

    option = int(
        input(
            "Selecciona 1 para generar documento de evaluación y 2 para calcular métricas: "
        )
    )

    if option == 1:
        k = int(input("Ingrese el número de resultados por consulta: "))
        run_evaluation(queries, k)
        print("Evaluación generada.")
    else:
        report = str(input("Ingrese nombre y formato del reporte: "))
        k = int(input("Ingrese el número de resultados por modelo: "))
        calculate_final_metrics(report, k)
        print("Reporte con métricas generado.")

    print("Hasta pronto")

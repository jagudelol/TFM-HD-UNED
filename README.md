# Sistemas de Recuperación de Información en Aforismos Filosóficos
# Information Retrieval Systems for Philosophical Aphorisms

**Trabajo Fin de Máster — Máster Universitario en Humanidades Digitales: Métodos y Buenas Prácticas**  
**Master's Thesis — Master's Degree in Digital Humanities: Methods and Best Practices**  
Universidad Nacional de Educación a Distancia (UNED) · 2025–2026

Autor / Author: Jose Agudelo Londoño  
Directora / Supervisor: Alba García Seco de Herrera

---

## Descripción / Description

**ES** — Este repositorio contiene los scripts desarrollados para el TFM *Desarrollo y Uso de Sistemas de Recuperación de Información Aplicados a Aforismos Filosóficos*. El proyecto implementa y evalúa seis índices de búsqueda en Elasticsearch sobre un corpus de 1254 aforismos filosóficos alemanes del siglo XIX, comparando estrategias léxicas, semánticas e híbridas mediante métricas de Precision@K, Recall@K, F1-Score y MAP.

**EN** — This repository contains the scripts developed for the Master's thesis *Development and Use of Information Retrieval Systems Applied to Philosophical Aphorisms*. The project implements and evaluates six Elasticsearch search indices over a corpus of 1,254 19th-century German philosophical aphorisms, comparing lexical, semantic, and hybrid strategies using Precision@K, Recall@K, F1-Score, and MAP metrics.

---

## Corpus

**ES** — Los aforismos provienen de las siguientes obras, disponibles en acceso abierto o dominio público:

**EN** — The aphorisms come from the following works, available in open access or public domain:

| Autor / Author | Obra / Work | Fuente / Source |
|---|---|---|
| Johann Wolfgang von Goethe | *Maxims and Reflections* | [Project Gutenberg](www.gutenberg.org/ebooks/33670) |
| Johann Wolfgang von Goethe | *On Nature* | [Project Gutenberg](www.gutenberg.org/ebooks/33670) |
| Friedrich Nietzsche | *The Joyful Wisdom* | [Project Gutenberg](https://www.gutenberg.org/ebooks/52881) |
| Friedrich Nietzsche | *The Antichrist* | [Project Gutenberg](https://www.gutenberg.org/ebooks/19322) |
| Ludwig Feuerbach | *The Essence of Religion* | [Internet Archive](https://archive.org/details/essenceofreligio00feue/page/n5/mode/2up) |
| Ludwig Feuerbach | *The Philosophy of the Future* | [Marxists Internet Archive](https://www.marxists.org/reference/archive/feuerbach/works/future/index.htm) |
| Ludwig Feuerbach | *Provisional Theses for the Reformation of Philosophy* | [University of Sussex](https://users.sussex.ac.uk/~sefd0/tx/pt.htm) |

---

## Estructura del repositorio / Repository Structure

```
📁 scrapers/          Scripts de extracción de aforismos por sitio web
                      Aphorism extraction scripts by website

📁 processing/        Scripts de procesamiento y formateo JSON
                      JSON formatting and processing scripts

📁 indexing/          Scripts de creación de índices en Elasticsearch
                      Elasticsearch index creation scripts

📁 evaluation/        Script de evaluación y cálculo de métricas
                      Evaluation and metrics calculation script

```

---

## Scripts

### Extracción / Extraction (`scrapers/`)

**ES** — Cada script está diseñado para el formato específico del sitio web del que se extrajeron los aforismos. El nombre del script indica para qué fuente fue desarrollado.

**EN** — Each script is designed for the specific format of the website from which the aphorisms were extracted. The script name indicates which source it was developed for.

| Script | Fuente / Source | Obras / Works |
|---|---|---|
| `scrapper_gutenberg_n.py` | Project Gutenberg | *Maxims and Reflections*, *The Joyful Wisdom*, *The Antichrist* |
| `scrapper_marxists.py` | marxists.org | *The Philosophy of the Future* |
| `scrapper_sussex.py` | University of Sussex | *Provisional Theses for the Reformation of Philosophy* |
| `manual.py` | Local / Manual input | *The Essence of Religion*, *On Nature* |

**ES** — El script `manual.py` se usó para los textos que requirieron corrección manual previa con expresiones regulares (caracteres extraños, saltos de página) antes de ser formateados como JSON.

**EN** — The `manual.py` script was used for texts that required prior manual correction with regular expressions (odd characters, page breaks) before being formatted as JSON.

### Procesamiento / Processing (`processing/`)

| Script | Función / Function |
|---|---|
| `jsonsplit.py` | Divide el fichero JSON único en documentos JSON individuales por aforismo / Splits the single JSON file into individual JSON documents per aphorism |

**ES** — Cada aforismo queda almacenado como un JSON con los atributos: `author`, `book`, `aphorism_number`, `aphorism_content`.

**EN** — Each aphorism is stored as a JSON with the attributes: `author`, `book`, `aphorism_number`, `aphorism_content`.

### Indexación / Indexing (`indexing/`)

| Script | Índices que crea / Indices it creates |
|---|---|
| `elasticsearch_indexer.py` | `aphorisms_basic`, `aphorisms_stemmed`, `aphorisms_bigram` |
| `embedder.py` | `aphorisms_embeddings_1` (GloVe), `aphorisms_embeddings_2` (ConceptNet), `aphorisms_hybrid` |

**ES** — Los scripts no solo crean los índices sino que también cargan los documentos JSON. El script `embedder.py` calcula la media de los vectores de cada palabra en el documento para generar el vector del aforismo completo.

**EN** — The scripts not only create the indices but also load the JSON documents. The `embedder.py` script computes the mean of the word vectors in each document to generate the full aphorism vector.

### Evaluación / Evaluation (`evaluation/`)

| Script | Función / Function |
|---|---|
| `evaluation_script.py` | Lanza consultas en todos los índices, genera el pool de evaluación CSV y calcula métricas / Runs queries across all indices, generates the CSV evaluation pool, and calculates metrics |

**ES** — El script genera dos ficheros CSV:
- `evaluation_pool.csv`: resultados de las consultas con campo `Relevation_Score` para calificación binaria manual (1 = relevante, 0 = no relevante).
- `evaluation_report.csv`: métricas calculadas (Precision@K, Recall@K, F1-Score@K, Average Precision) tras ingresar el fichero calificado.

**EN** — The script generates two CSV files:
- `evaluation_pool.csv`: query results with a `Relevation_Score` field for manual binary scoring (1 = relevant, 0 = not relevant).
- `evaluation_report.csv`: calculated metrics (Precision@K, Recall@K, F1-Score@K, Average Precision) after uploading the scored file.

> **ES** — La versión inicial de este script fue generada con asistencia de Claude Sonnet 4 y modificada para los propósitos del proyecto. La versión original puede consultarse en: https://claude.ai/public/artifacts/bf255204-5032-47c8-8768-d836ae9b2aa0
>
> **EN** — The initial version of this script was generated with assistance from Claude Sonnet 4 and modified for the project's purposes. The original version can be consulted at: https://claude.ai/public/artifacts/bf255204-5032-47c8-8768-d836ae9b2aa0

---

## Requisitos / Requirements

```
Python 3.x
Elasticsearch 8.x (local, single node)
gensim
```

**ES** — Los modelos de embeddings deben descargarse por separado:
- **GloVe** (`glove-wiki-gigaword-300`): disponible a través de la librería Gensim.
- **ConceptNet Numberbatch** (`numberbatch-17-06-300`): descargable desde [conceptnet.io](https://conceptnet.io/).

**EN** — The embedding models must be downloaded separately:
- **GloVe** (`glove-wiki-gigaword-300`): available through the Gensim library.
- **ConceptNet Numberbatch** (`numberbatch-17-06-300`): downloadable from [conceptnet.io](https://conceptnet.io/).

---

## Referencia / Reference

**ES** — Si usas este repositorio en tu investigación, por favor cita el TFM asociado:

**EN** — If you use this repository in your research, please cite the associated thesis:

```
Agudelo Londoño, J. (2026). Desarrollo y Uso de Sistemas de Recuperación de 
Información Aplicados a Aforismos Filosóficos [Trabajo Fin de Máster]. 
Universidad Nacional de Educación a Distancia (UNED).
https://github.com/jagudelol/TFM-HD-UNED
```

---

## Licencia / License

**ES** — El código de este repositorio se distribuye bajo licencia MIT. Los textos del corpus son de dominio público o acceso abierto según las fuentes indicadas.

**EN** — The code in this repository is distributed under the MIT license. The corpus texts are in the public domain or open access as indicated by their respective sources.

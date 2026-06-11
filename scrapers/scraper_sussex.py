import requests
from bs4 import BeautifulSoup
import json
import re

url = "https://users.sussex.ac.uk/~sefd0/tx/pt.htm"

try:
    response = requests.get(url)
    response.raise_for_status()  # Lanza un error si la solicitud falla
except requests.RequestException as e:
    print(f"Error al realizar la solicitud: {e}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")
text = soup.get_text()

# Usar regex para dividir el texto en párrafos
paragraphs = re.split(r"\n\s*\n+", text)

data = []
counter = -1  # Contador para los números de los aforismos

for paragraph in paragraphs:
    paragraph = paragraph.strip()
    paragraph = re.sub(r"\r\n|\r|\n", " ", paragraph)

    # Ignorar párrafos que comienzan con un número
    if paragraph and not paragraph[0].isdigit():
        section_data = {
            "author": "Ludwig Feuerbach",
            "book": "Philosophy of Future",
            "aphorism_number": str(counter),
            "aphorism_content": paragraph,
        }
        data.append(section_data)
        counter += 1  # Incrementar el contador solo si se agrega un párrafo

# Guardar los datos en un archivo JSON
try:
    with open("Feuerbach4.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print("Datos extraidos y guardados en Feuerbach4.json")
except IOError as e:
    print(f"Error al guardar el archivo: {e}")

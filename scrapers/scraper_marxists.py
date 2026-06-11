import requests
from bs4 import BeautifulSoup
import re
import json

url = "https://www.marxists.org/reference/archive/feuerbach/works/future/future2.htm"

try:
    response = requests.get(url)
    response.raise_for_status()  # Lanza un error si la solicitud falla
except requests.RequestException as e:
    print(f"Error al realizar la solicitud: {e}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")
text = soup.get_text()

# Usar una expresión regular para encontrar secciones que comienzan con "§" seguido de un número
pattern = r"§\s*(\d+)\s*(.*?)(?=§\s*\d+|$)"
matches = re.findall(pattern, text, re.DOTALL)

data = []

for number, section_text in matches:
    section_text = section_text.strip()

    section_data = {
        "author": "Ludwig Feuerbach",
        "book": "Philosophy of Future",
        "aphorism_number": number,
        "aphorism_content": section_text,
    }

    data.append(section_data)

# Guardar los datos en un archivo JSON
try:
    with open(
        "Feuerbach3.json", "w", encoding="utf-8"
    ) as json_file:  # Asegurarse de usar la codificación UTF-8
        json.dump(
            data, json_file, ensure_ascii=False, indent=4
        )  # Evitar la codificación ASCII
    print("Datos extraidos y guardados en Feuerbach3.json")
except IOError as e:
    print(f"Error al guardar el archivo: {e}")

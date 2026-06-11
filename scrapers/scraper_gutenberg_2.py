import requests
import re
import json
from tqdm import tqdm

Author = "Friedrich Wilhelm Nietzsche"
Book = "Beyond Good and Evil"

# URL del sitio web
url = "https://gutenberg.org/cache/epub/4363/pg4363.txt"

# Delimitadores personalizables
start_delimiter = r"CHAPTER I. PREJUDICES OF PHILOSOPHERS"
end_delimiter = r"FROM THE HEIGHTS"

# Obtener el contenido de la página
response = requests.get(url)
text = response.text

# Ignorar contenido antes y después de los delimitadores
text = re.sub(rf".*?{start_delimiter}", "", text, flags=re.S)
text = re.sub(rf"{end_delimiter}.*", "", text, flags=re.S)

# Separar el texto en líneas
lines = text.splitlines()

data = []
aphorism_number = None  # Inicializar el número del aforismo
section_text = ""  # Inicializar el texto del aforismo

# Usar tqdm para mostrar una barra de carga mientras se procesan los fragmentos
for i in tqdm(range(len(lines)), desc="Procesando fragmentos"):
    current_line = lines[i].strip()

    # Verificar si la línea contiene un número seguido de un punto
    match = re.match(r"^(\d+)\s*(.*)", current_line)
    if match:
        # Si hay un número, guardar el número del aforismo
        if aphorism_number is not None:
            # Si ya teníamos un aforismo anterior, guardar su contenido
            section_data = {
                "author": Author,
                "book": Book,
                "aphorism_number": aphorism_number,
                "aphorism_content": section_text.strip(),
            }
            data.append(section_data)

        aphorism_number = match.group(1)  # Captura el número del aforismo
        section_text = match.group(2)  # Captura el contenido de la línea

    elif (
        aphorism_number is not None and current_line
    ):  # Si hay un aforismo en curso y la línea no está vacía
        section_text += " " + current_line  # Agregar la línea al texto del aforismo

# Guardar el último aforismo si existe
if aphorism_number is not None:
    section_data = {
        "author": Author,
        "book": Book,
        "aphorism_number": aphorism_number,
        "aphorism_content": section_text.strip(),
    }
    data.append(section_data)

# Guardar los datos en un archivo JSON
with open("Nietzsche2.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

print("Datos extraidos y guardados en Nietzsche2.json")

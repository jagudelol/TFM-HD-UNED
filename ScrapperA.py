import requests
import re
import json

Author = "Friedrich Wilhelm Nietzsche"
Book = "The Joyful Wisdom"

# URL del libro en texto plano
url = "https://gutenberg.org/cache/epub/52124/pg52124.txt"

# Obtener el contenido de la página
response = requests.get(url)
text = response.text

# Delimitadores para ignorar contenido no deseado
start_delimiter = r"To thee one law--be pure and bright!"
end_delimiter = r"APPENDIX"
text = re.search(rf"{start_delimiter}(.*?){end_delimiter}", text, re.DOTALL)

if text:
    text = text.group(1)
else:
    print("No se encontraron los delimitadores.")
    exit()

# Separar el texto en líneas
lines = text.splitlines()

data = []
aphorism_number = None  # Inicializar el número del aforismo
section_text = ""  # Inicializar el texto del aforismo

# Procesar los fragmentos
for current_line in lines:
    current_line = current_line.strip()

    # Verificar si la línea contiene un número seguido de un punto
    if re.match(r"^\d+\.$", current_line):
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

        aphorism_number = current_line[
            :-1
        ]  # Captura el número del aforismo (sin el punto)
        section_text = ""  # Reiniciar el texto del aforismo

    elif aphorism_number is not None and current_line:
        # Si hay un aforismo en curso y la línea no está vacía
        section_text += current_line + " "  # Agregar la línea al texto del aforismo

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
with open("Nietzsche_1.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

print("Datos extraidos y exportados a Nietzsche_Aphorisms.json")

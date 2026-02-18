import json
import os

# Definir el autor y el libro
Author = "Johann Wolfgang von Goethe"
Book = "Nature"

# Nombre del archivo JSON
filename = "Goethe2.json"

# Cargar datos existentes si el archivo ya existe
data = []
if os.path.exists(filename):
    with open(filename, "r") as json_file:
        data = json.load(json_file)

# Obtener el número del próximo aforismo
aphorism_number = len(data) + 1

while True:
    # Ingresar el contenido del aforismo
    aphorism_content = input(
        "Ingrese el contenido del aforismo (o 'salir' para terminar): "
    )

    if aphorism_content.lower() == "salir":
        break

    # Crear un diccionario para el aforismo
    section_data = {
        "author": Author,
        "book": Book,
        "aphorism_number": aphorism_number,
        "aphorism_content": aphorism_content.strip(),
    }

    # Agregar el aforismo a la lista
    data.append(section_data)

    # Incrementar el número del aforismo
    aphorism_number += 1

# Guardar los datos en el archivo JSON
with open(filename, "w") as json_file:
    json.dump(data, json_file, indent=4)

print(f"Datos guardados en {filename}.")

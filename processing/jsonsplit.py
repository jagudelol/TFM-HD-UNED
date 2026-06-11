import json
import os

input_file = "archivo.json"
output_dir = "output/directory"

os.makedirs(output_dir, exist_ok=True)

with open(input_file, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

if isinstance(data, list):
    for index, item in enumerate(data):
        output_file = os.path.join(output_dir, f"nombre_archivo_{index + 1}.json")
        with open(output_file, "w") as out_f:
            json.dump(item, out_f, indent=4)
else:
    print("El archivo JSON no está en el directorio.")

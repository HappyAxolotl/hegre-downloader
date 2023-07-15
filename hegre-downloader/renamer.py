import os
import json
from datetime import datetime

downloads_folder = os.path.abspath("./downloads")

for filename in os.listdir(downloads_folder):
    name, ext = os.path.splitext(filename)
    if ext == ".json":
        continue

    metadata_file = os.path.join(downloads_folder, name + ".json")

    if not os.path.exists(metadata_file):
        print(f"Error: could not find metadata file for {filename}!")
        continue

    metadata = json.load(open(metadata_file))

    movie_date = datetime.fromisoformat(metadata["date"])
    date_str = movie_date.strftime("%Y.%m.%d")

    print(metadata["title"])

    # new_name = f"{date_str}-{metadata['code']}-{name}{ext}"
    # new_file = os.path.join(downloads_folder, new_name)

    # new_meta_name = f"{date_str}-{metadata['code']}-{name}.json"
    # new_meta_file = os.path.join(downloads_folder, new_meta_name)

    # print(f"rename '{os.path.join(downloads_folder, filename)}' -> '{new_file}'")
    # os.rename(os.path.join(downloads_folder, filename), new_file)

    # print(f"rename '{metadata_file}' -> '{new_meta_file}'")
    # os.rename(metadata_file, new_meta_file)

from __future__ import annotations

import json
import os

from DOM.hashing import get_hash


def generate_media_hash() -> tuple[dict, str]:
    target_file_path = "resources/files.json"
    data = {}
    for root, dirs, files in os.walk("resources"):
        for file_name in files:
            file_path = os.path.join(root, file_name).replace("\\", "/")
            if file_path != "resources/files.json":
                data[file_path.removeprefix("resources/")] = get_hash(file_path)

    with open(target_file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    return data, get_hash(target_file_path)


if __name__ == "__main__":
    data_hash = generate_media_hash()[1]
    os.system(f"heroku config:set DATA_HASH={data_hash} -a dungeon-of-masters")

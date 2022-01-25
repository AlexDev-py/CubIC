from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass
class Character:
    name: str
    icon: str


with open(
    os.path.join(os.environ["CHARACTERS_PATH"], "characters.json"), encoding="utf-8"
) as file:
    characters: list[Character] = [
        Character(**character) for character in json.load(file)["characters"]
    ]

__all__ = ["Character", "characters"]

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from .item import Item


@dataclass
class Character:
    name: str
    icon: str

    coins: int = 0
    damage: int = 0
    attack_range: int = 0
    max_hp: int = 0
    hp: int = 0
    armor: int = 0
    move_speed: int = 0
    life_abduction: int = 0
    items: list[Item | None] = field(default_factory=list)

    def __post_init__(self):
        self.items = [
            Item(**item) if isinstance(item, dict) else None for item in self.items
        ]


with open(
    os.path.join(os.environ["CHARACTERS_PATH"], "characters.json"), encoding="utf-8"
) as file:
    characters: list[Character] = [
        Character(**character) for character in json.load(file)["characters"]
    ]

__all__ = ["Character", "characters"]

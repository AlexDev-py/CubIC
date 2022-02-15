from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from .item import Item

characters: list[Character] = []


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
    pos: tuple[int, int] = (0, 0)

    def update(self, data: dict) -> None:
        items = data.pop("items")
        self.__dict__.update(data)
        self.items = [
            Item(**item) if isinstance(item, dict) else None for item in items
        ]

    def __post_init__(self):
        self.items = [
            Item(**item) if isinstance(item, dict) else None for item in self.items
        ]


def init() -> None:
    if not len(characters):
        if os.path.isfile(
            file_path := os.path.join(os.environ["CHARACTERS_PATH"], "characters.json")
        ):
            with open(file_path, encoding="utf-8") as file:
                for character in json.load(file)["characters"]:
                    characters.append(Character(**character))


__all__ = ["Character", "characters"]

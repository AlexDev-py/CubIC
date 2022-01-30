from __future__ import annotations

import json
import os
import typing as ty
from dataclasses import dataclass, field

if ty.TYPE_CHECKING:
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
    items: list[Item] = field(default_factory=list)


with open(
    os.path.join(os.environ["CHARACTERS_PATH"], "characters.json"), encoding="utf-8"
) as file:
    characters: list[Character] = [
        Character(**character) for character in json.load(file)["characters"]
    ]

__all__ = ["Character", "characters"]

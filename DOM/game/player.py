from __future__ import annotations

import typing as ty
from dataclasses import dataclass, field

from .character import characters

if ty.TYPE_CHECKING:
    from ..network import User
    from .character import Character


@dataclass
class Player:
    uid: int
    username: str
    icon: int
    coins: int = 0
    character_id: int = ...
    is_owner: True | False = False
    character: Character = ...
    ready: True | False = False
    items: list = field(default_factory=list)

    def __post_init__(self):
        if self.character_id is None:
            self.character_id: int = ...
        elif isinstance(self.character_id, int):
            self.select_character(self.character_id)

    def select_character(self, character_id: int) -> None:
        self.character_id = character_id
        self.character = characters[character_id]

    @classmethod
    def from_user(cls, user: User, is_owner: True | False = False) -> Player:
        return cls(user.uid, user.username, user.icon, is_owner=is_owner)

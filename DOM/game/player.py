from __future__ import annotations

import typing as ty
from dataclasses import dataclass

from .character import Character
from .character import characters

if ty.TYPE_CHECKING:
    from ..network import User


@dataclass
class Player:
    uid: int
    username: str
    icon: int
    character: Character = ...
    character_id: int = ...

    is_owner: True | False = False
    ready: True | False = False

    def __post_init__(self):
        if self.character is None:
            self.character: Character = ...
        elif isinstance(self.character, dict):
            self.character = Character(
                icon=characters[self.character_id].icon, **self.character
            )

        if self.character_id is None:
            self.character_id: int = ...
        elif isinstance(self.character_id, int) and self.character is ...:
            self.select_character(self.character_id)

    def select_character(self, character_id: int) -> None:
        self.character_id = character_id
        self.character = characters[character_id]

    @classmethod
    def from_user(cls, user: User, is_owner: True | False = False) -> Player:
        return cls(user.uid, user.username, user.icon, is_owner=is_owner)

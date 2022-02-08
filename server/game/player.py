from __future__ import annotations

import typing as ty

from .characters import characters

if ty.TYPE_CHECKING:
    from database import Users
    from .characters.base import BaseCharacter


class Player:
    def __init__(self, user: Users):
        self.uid = user.id
        self.username = user.username
        self.icon = user.icon
        self.character: BaseCharacter = ...
        self.character_id: int = ...

    def select_character(self, character_id: int) -> None:
        self.character_id = character_id
        self.character = characters[character_id]()

    def to_dict(self) -> dict:
        return dict(
            uid=self.uid,
            username=self.username,
            icon=self.icon,
            character=(
                self.character.to_dict() if self.character_id is not ... else None
            ),
            character_id=self.character_id if self.character_id is not ... else None,
        )

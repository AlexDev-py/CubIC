from __future__ import annotations

import typing as ty

from .player import Player

if ty.TYPE_CHECKING:
    from ..network import User


class Room:
    def __init__(self, room_id: int):
        self.room_id = room_id
        self.game = False

        self.players: list[Player] = []
        self.field: list[list[True | False]] = ...
        self.shop: list = ...

    def join(self, user: User, is_owner: True | False = False) -> None:
        self.players.append(Player(user, is_owner))

    def leave(self, uid: int) -> None:
        if player := self.get_by_uid(uid):
            self.players.remove(player)
        if len(self.players):
            self.players[0].is_owner = True

    def get_by_uid(self, uid: int) -> Player | None:
        if players := [player for player in self.players if player.uid == uid]:
            return players[0]

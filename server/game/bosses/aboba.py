from __future__ import annotations

import typing as ty
import random

from .base import BaseBoss
from ..tools import get_closest_player, get_farthest_player

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class Aboba(BaseBoss):
    @property
    def name(self) -> str:
        return "Абоба"

    @property
    def base_hp(self) -> int:
        return 100

    def first_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        self.hit(closest_player.character.pos, players, 10)

    def second_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        random_player = random.choice(players)
        self.hit(random_player.character.pos, players, 8)

    def third_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        farthest_player = get_farthest_player(self.pos, players)
        self.hit(farthest_player.character.pos, players, 6)

    def fourth_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        self.hit([player.character.pos for player in players], players, 2)
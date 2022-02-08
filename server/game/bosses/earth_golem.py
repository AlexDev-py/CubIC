from __future__ import annotations

import typing as ty

from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, get_delta_cord

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class EarthGolem(BaseBoss):
    @property
    def name(self) -> str:
        return "Земляной голем"

    @property
    def base_hp(self) -> int:
        return 40

    def first_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord = get_delta_cord(self.pos, closest_player.character.pos, delta=1)
        cord = (self.pos[0] + delta_cord[0], self.pos[1] + delta_cord[1])
        self.hit([cord], players, 4)

    def second_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        cords = get_all_neighboring_cords(*self.pos)
        self.hit(cords, players, 1)

    def third_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord = get_delta_cord(self.pos, closest_player.character.pos, delta=2)
        cord = (self.pos[0] + delta_cord[0], self.pos[1] + delta_cord[1])
        cords = get_all_neighboring_cords(*cord)
        self.hit(cords, players, 2)

    def fourth_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        cords = [player.character.pos for player in players]
        self.hit(list(set(cords)), players, 2)

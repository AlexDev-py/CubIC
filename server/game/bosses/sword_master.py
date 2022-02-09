from __future__ import annotations

import typing as ty
import random

from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, get_delta_cord, get_ray

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class SwordMaster(BaseBoss):
    @property
    def name(self) -> str:
        return "Мастер меча"

    @property
    def base_hp(self) -> int:
        return 80

    def first_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord = get_delta_cord(self.pos, closest_player.character.pos, delta=1)
        ray = get_ray(self.pos, delta=delta_cord, field_size=len(room.field), length=4)
        self.hit([ray[0]], players, 10)
        self.hit([ray[1], ray[2], ray[3]], players, 8)

    def second_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        pass
    # TODO: cделать атаку радиус 2, вокруг, я сделаю (Саша)


    def third_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord = get_delta_cord(self.pos, closest_player.character.pos, delta=2)
        cord = (self.pos[0] + delta_cord[0], self.pos[1] + delta_cord[1])
        cords = get_all_neighboring_cords(*cord)
        self.hit(cords, players, 6)


    def fourth_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        self.hit(closest_player.character.pos, players, 6)
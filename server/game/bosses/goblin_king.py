from __future__ import annotations

import random
import typing as ty

from .base import BaseBoss
from ..tools import (
    get_closest_player,
    get_all_neighboring_cords,
    get_delta_cord,
    get_ray,
)

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class GoblinKing(BaseBoss):
    @property
    def name(self) -> str:
        return "Король гоблинов"

    @property
    def base_hp(self) -> int:
        return 40

    def first_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        rays = [
            get_ray(
                self.pos,
                delta=get_delta_cord(self.pos, cord, 1),
                field_size=len(room.field),
            )
            for cord in get_all_neighboring_cords(*self.pos)
        ]
        for ray in rays:
            if any(player.character.pos in ray for player in players):
                self.hit(ray, players, 1)
                return
        self.hit(random.choice(rays), players, 1)

    def second_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        pass

    def third_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        cords = get_all_neighboring_cords(*self.pos)
        self.hit(cords, players, 1)

    def fourth_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord = get_delta_cord(self.pos, closest_player.character.pos, delta=1)
        ray = get_ray(self.pos, delta=delta_cord, field_size=len(room.field), length=3)
        self.hit([ray[0], ray[2]], players, 2)
        self.hit([ray[1]], players, 3)

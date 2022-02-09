from __future__ import annotations

import typing as ty
import random

from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, get_delta_cord, get_ray

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class SoulStealer(BaseBoss):
    @property
    def name(self) -> str:
        return "Похититель душ"

    @property
    def base_hp(self) -> int:
        return 20

    def first_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        rays = []
        for cord in get_all_neighboring_cords(*self.pos):
            rays.extend(get_ray(
                self.pos,
                delta=get_delta_cord(self.pos, cord, 1),
                field_size=len(room.field),
                length=2
            ))
        self.hit(rays, players, 3)

    def second_skill(
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
                self.hit(ray, players, 4)
                return
        self.hit(random.choice(rays), players, 4)

    def third_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        cords = get_all_neighboring_cords(*self.pos)
        self.hit(cords, players, 4)

    def fourth_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        self.hit(closest_player.character.pos, players, 7)

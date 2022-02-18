from __future__ import annotations

import typing as ty

from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, get_delta_cord, get_ray

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class Half_Wolf(BaseBoss):
    @property
    def name(self) -> str:
        return "Графиня Дракула"

    @property
    def base_hp(self) -> int:
        return 30

    def first_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        coord_all = get_all_neighboring_cords(*self.pos)
        rays = [
            get_ray(
                self.pos,
                delta=get_delta_cord(self.pos, cord, 1),
                field_size=len(room.field),
            )
            for cord in [coord_all[3], coord_all[0], coord_all[1], coord_all[2], coord_all[4]]
        ]
        for ray in rays:
            if any(player.character.pos in ray for player in players):
                self.hit(ray, players, 4)

    def second_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        players_cosets = get_closest_player(self.pos, players)
        self.hit(players_cosets.character.pos, players, 3)

    def third_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        pass

    def fourth_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        pass

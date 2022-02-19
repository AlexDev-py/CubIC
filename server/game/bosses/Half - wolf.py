from __future__ import annotations
import random
import typing as ty

from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, get_delta_cord, get_ray

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class Half_Wolf(BaseBoss):
    @property
    def name(self) -> str:
        return "Полуволк"

    @property
    def base_hp(self) -> int:
        return 35

    def first_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        player_coord = random.choice(players)
        self.hit(player_coord.character.pos, players, 4)

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
                self.hit(ray, players, 3)

    def third_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        coords_kvadrat = [(self.pos[0] - 1, self.pos[1] - 1),
                          (self.pos[0] - 1, self.pos[1]),
                          (self.pos[0] - 1, self.pos[1] + 1),
                          (self.pos[0] - 2, self.pos[1] - 1),
                          (self.pos[0] - 2, self.pos[1]),
                          (self.pos[0] - 2, self.pos[1] + 1)]
        self.hit(coords_kvadrat, players, 2)

    def fourth_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        pass



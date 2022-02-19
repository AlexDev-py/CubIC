from __future__ import annotations

import typing as ty
import random
from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, get_delta_cord, get_ray, get_rect

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class Half_Wolf(BaseBoss):
    @property
    def name(self) -> str:
        return "Диабло"

    @property
    def base_hp(self) -> int:
        return 50

    def first_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        player_coord = random.choice(players)
        self.hit(player_coord.character.pos, players, 4)

    def second_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord = get_delta_cord(self.pos, closest_player.character.pos, delta=2)
        cord = (self.pos[0] + delta_cord[0], self.pos[1] + delta_cord[1])
        cords = get_all_neighboring_cords(*cord)
        self.hit(cords, players, 5)

    def third_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        for player in players:
            self.hit(player.character.pos, players, 2)

    def fourth_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        coord_all = [
            (self.pos[0] - 2, self.pos[1] - 2),
            (self.pos[0] - 2, self.pos[1] - 1),
            (self.pos[0] - 2, self.pos[1]),
            (self.pos[0] - 2, self.pos[1] + 1),
            (self.pos[0] - 2, self.pos[1] + 2),
            (self.pos[0], self.pos[1] - 2),
            (self.pos[0], self.pos[1] - 1),
            (self.pos[0], self.pos[1] + 2),
            (self.pos[0], self.pos[1] + 1),
            (self.pos[0] + 2, self.pos[1] - 2),
            (self.pos[0] + 2, self.pos[1] - 1),
            (self.pos[0] + 2, self.pos[1]),
            (self.pos[0] + 2, self.pos[1] + 1),
            (self.pos[0] + 2, self.pos[1] + 2)
        ]
        for ray in coord_all:
            if any(player.character.pos in ray for player in players):
                self.hit([ray], players, 5)

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

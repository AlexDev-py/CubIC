from __future__ import annotations

import typing as ty

from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, get_delta_cord, get_ray, get_rect

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class Half_Wolf(BaseBoss):
    @property
    def name(self) -> str:
        return "Падший ангел"

    @property
    def base_hp(self) -> int:
        return 45

    def first_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        rays = [
            get_ray(
                self.pos,
                delta=get_delta_cord(self.pos, cord, 1),
                field_size=len(room.field),
                length=3
            )
            for cord in [(self.pos[0], self.pos[1] - 1), (self.pos[0], self.pos[1] + 1)]
        ]
        for ray in rays:
            if any(player.character.pos in ray for player in players):
                self.hit(ray, players, 4)

    def second_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        coord_2_3 = [
                get_rect(
                    center=self.pos,
                    radius=2,
                    field_size=len(room.field),

                )
        ]
        for i in coord_2_3:
            if any(player.character.pos for player in players):
                self.hit(i, players, 3)

    def third_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        coord_left = [
            get_ray(
                (self.pos[0] - 1, self.pos[1] - 1),
                delta=get_delta_cord(self.pos, cord, 1),
                field_size=len(room.field),
                length=3
            )
            for cord in [(self.pos[0] - 1, self.pos[1])]
        ]
        for cord_l in coord_left:
            if any(player.character.pos in cord_l for player in players):
                self.hit(cord_l, players, 5)

        coord_right = [
            get_ray(
                (self.pos[0] - 1, self.pos[1] + 1),
                delta=get_delta_cord(self.pos, corf, 1),
                field_size=len(room.field),
                length=3
            )
            for corf in [(self.pos[0] - 1, self.pos[1])]
        ]
        for coord_r in coord_right:
            if any(player.character.pos in coord_r for player in players):
                self.hit(coord_r, players, 5)

        coord_meduim = [
            get_ray(
                (self.pos[0] - 1, self.pos[1]),
                delta=get_delta_cord(self.pos, cord, 1),
                field_size=len(room.field),
                length=3
            )
            for cord in [(self.pos[0] - 1, self.pos[1])]
        ]
        for cord_m in coord_meduim:
            if any(player.character.pos in cord_m for player in players):
                self.hit(cord_m, players, 4)

    def fourth_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        player_close = get_closest_player(self.pos, players)
        self.hit(player_close.character.pos, players, 4)

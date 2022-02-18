from __future__ import annotations

import typing as ty

from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, get_delta_cord

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class Guardian_of_the_Ruins(BaseBoss):
    @property
    def name(self) -> str:
        return "Страж руин"

    @property
    def base_hp(self) -> int:
        return 40

    def first_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        coords_hit = [(self.pos[0] - 1, self.pos[1] - 2),
                      (self.pos[0] - 1, self.pos[1] - 1),
                      (self.pos[0], self.pos[1] - 2),
                      (self.pos[0], self.pos[1] - 1),
                      (self.pos[0] + 1, self.pos[1] - 2),
                      (self.pos[0] + 1, self.pos[1] - 1),

                      (self.pos[0], self.pos[1] + 1),
                      (self.pos[0] - 1, self.pos[1] + 1),
                      (self.pos[0] - 1, self.pos[1] + 2),
                      (self.pos[0], self.pos[1] + 2),
                      (self.pos[0] + 1, self.pos[1] + 1),
                      (self.pos[0] + 1, self.pos[1] + 1)]
        self.hit(coords_hit, players, 3)

    def second_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        cords = get_all_neighboring_cords(*self.pos)
        self.hit(cords, players, 4)
        coord_hit_2 = [
                        (self.pos[0] - 2, self.pos[1] - 2),
                        (self.pos[0] - 2, self.pos[1]),
                        (self.pos[0] - 2, self.pos[1] + 2),

                        (self.pos[0], self.pos[1] - 2),
                        (self.pos[0], self.pos[1] + 2),

                        (self.pos[0] + 2, self.pos[1] - 2),
                        (self.pos[0] + 2, self.pos[1]),
                        (self.pos[0] + 2, self.pos[1] + 2),
                    ]
        cords_2 = get_all_neighboring_cords(*coord_hit_2)
        self.hit(cords_2, players, 2)

    def third_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord = get_delta_cord(self.pos, closest_player.character.pos, delta=1)
        cord = (self.pos[0] + delta_cord[0], self.pos[1] + delta_cord[1])
        self.hit([cord], players, 8)

    def fourth_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        self.hit(closest_player.character.pos, players, 2)



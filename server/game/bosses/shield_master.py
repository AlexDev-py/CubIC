from __future__ import annotations

import typing as ty
import random

from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, get_delta_cord, get_ray, get_rect

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class ShieldMaster(BaseBoss):
    @property
    def name(self) -> str:
        return "Мастер щита"

    @property
    def base_hp(self) -> int:
        return 125

    def first_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord_2 = get_delta_cord(self.pos, closest_player.character.pos, delta=2)
        cords = []
        cords_2 = get_all_neighboring_cords(*self.pos)

        cord_2 = (self.pos[0] + delta_cord_2[0], self.pos[1] + delta_cord_2[1])
        cords.append(cord_2)
        if cord_2[0] == self.pos[0] and cord_2[1] != self.pos[1]:
            cord_top_2 = (cord_2[0] - 1, cord_2[1])
            cord_bottom_2 = (cord_2[0] + 1, cord_2[1])
            cords.extend([cord_top_2, cord_bottom_2])
        elif cord_2[0] != self.pos[0] and cord_2[1] == self.pos[1]:
            cord_left_2 = (cord_2[0], cord_2[1] - 1)
            cord_right_2 = (cord_2[0], cord_2[1] + 1)
            cords.extend([cord_left_2, cord_right_2])
        else:
            cord_first_2 = (cord_2[0], cord_2[1] + delta_cord_2[1])
            cord_second_2 = (cord_2[0] + delta_cord_2[0], cord_2[1])
            cords.extend([cord_first_2, cord_second_2])
        self.hit(cords, players, 4)
        self.hit(cords_2, players, 3)

    def second_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord = get_delta_cord(self.pos, closest_player.character.pos, delta=2)
        cord = (self.pos[0] + delta_cord[0], self.pos[1] + delta_cord[1])
        cords = get_all_neighboring_cords(*cord)
        self.hit(cords, players, 3)

    def third_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        self.hit(closest_player.character.pos, players, 5)

    def fourth_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        pass
from __future__ import annotations

import typing as ty
import random

from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, get_delta_cord, get_ray, get_rect

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
        cords = get_rect(self.pos, radius=2, field_size=len(room.field))
        self.hit(cords, players, 4)

    def third_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord_2 = get_delta_cord(self.pos, closest_player.character.pos, delta=2)
        delta_cord_1 = get_delta_cord(self.pos, closest_player.character.pos, delta=1)
        cords = []

        cord_1 = (self.pos[0] + delta_cord_1[0], self.pos[1] + delta_cord_1[1])
        cords.append(cord_1)
        if cord_1[0] == self.pos[0] and cord_1[1] != self.pos[1]:
            cord_top = (cord_1[0] - 1, cord_1[1])
            cord_bottom = (cord_1[0] + 1, cord_1[1])
            cords.extend([cord_top, cord_bottom])
        elif cord_1[0] != self.pos[0] and cord_1[1] == self.pos[1]:
            cord_left = (cord_1[0], cord_1[1] - 1)
            cord_right = (cord_1[0], cord_1[1] + 1)
            cords.extend([cord_left, cord_right])
        else:
            cord_first = (cord_1[0], cord_1[1] + delta_cord_1[1])
            cord_second = (cord_1[0] + delta_cord_1[0], cord_1[1])
            cords.extend([cord_first, cord_second])

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
        self.hit(cords, players, 6)

    def fourth_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        self.hit(closest_player.character.pos, players, 6)
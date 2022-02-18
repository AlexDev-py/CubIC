from __future__ import annotations

import typing as ty
import random

from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, \
    get_delta_cord, get_ray, get_rect, get_farthest_player

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class BowMaster(BaseBoss):
    @property
    def name(self) -> str:
        return "Мастер лука"

    @property
    def base_hp(self) -> int:
        return 75

    def first_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord = get_delta_cord(self.pos, closest_player.character.pos, delta=1)
        ray = get_ray(self.pos, delta=delta_cord, field_size=len(room.field), length=2)
        self.hit(ray, players, 3)

    def second_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        rays = []
        for cord in get_all_neighboring_cords(*self.pos):
            rays.extend(get_ray(
                self.pos,
                delta=get_delta_cord(self.pos, cord, 1),
                field_size=len(room.field)
            ))
        self.hit(rays, players, 5)

    def third_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        closest_player = get_closest_player(self.pos, players)
        delta_cord_1 = get_delta_cord(self.pos, closest_player.character.pos, delta=1)
        delta_cord_2 = get_delta_cord(self.pos, closest_player.character.pos, delta=2)
        delta_cord_3 = get_delta_cord(self.pos, closest_player.character.pos, delta=3)
        delta_cord_4 = get_delta_cord(self.pos, closest_player.character.pos, delta=4)
        delta_cord_5 = get_delta_cord(self.pos, closest_player.character.pos, delta=5)

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
            cord_top = (cord_2[0] - 1, cord_2[1])
            cord_bottom = (cord_2[0] + 1, cord_2[1])
            cords.extend([cord_top, cord_bottom])
        elif cord_2[0] != self.pos[0] and cord_2[1] == self.pos[1]:
            cord_left = (cord_2[0], cord_2[1] - 1)
            cord_right = (cord_2[0], cord_2[1] + 1)
            cords.extend([cord_left, cord_right])
        else:
            cord_first = (cord_2[0], cord_2[1] + delta_cord_2[1])
            cord_second = (cord_2[0] + delta_cord_2[0], cord_2[1])
            cords.extend([cord_first, cord_second])

        cord_3 = (self.pos[0] + delta_cord_3[0], self.pos[1] + delta_cord_3[1])
        cords.append(cord_3)
        if cord_3[0] == self.pos[0] and cord_3[1] != self.pos[1]:
            cord_top = (cord_3[0] - 1, cord_3[1])
            cord_bottom = (cord_3[0] + 1, cord_3[1])
            cords.extend([cord_top, cord_bottom])
        elif cord_3[0] != self.pos[0] and cord_3[1] == self.pos[1]:
            cord_left = (cord_3[0], cord_3[1] - 1)
            cord_right = (cord_3[0], cord_3[1] + 1)
            cords.extend([cord_left, cord_right])
        else:
            cord_first = (cord_3[0], cord_3[1] + delta_cord_2[1])
            cord_second = (cord_3[0] + delta_cord_2[0], cord_3[1])
            cords.extend([cord_first, cord_second])

        cord_4 = (self.pos[0] + delta_cord_4[0], self.pos[1] + delta_cord_4[1])
        cords.append(cord_4)
        if cord_4[0] == self.pos[0] and cord_4[1] != self.pos[1]:
            cord_top = (cord_4[0] - 1, cord_4[1])
            cord_bottom = (cord_4[0] + 1, cord_4[1])
            cords.extend([cord_top, cord_bottom])
        elif cord_4[0] != self.pos[0] and cord_4[1] == self.pos[1]:
            cord_left = (cord_4[0], cord_4[1] - 1)
            cord_right = (cord_4[0], cord_4[1] + 1)
            cords.extend([cord_left, cord_right])
        else:
            cord_first = (cord_4[0], cord_4[1] + delta_cord_2[1])
            cord_second = (cord_4[0] + delta_cord_2[0], cord_4[1])
            cords.extend([cord_first, cord_second])

        cord_5 = (self.pos[0] + delta_cord_5[0], self.pos[1] + delta_cord_5[1])
        cords.append(cord_5)
        if cord_5[0] == self.pos[0] and cord_5[1] != self.pos[1]:
            cord_top = (cord_5[0] - 1, cord_5[1])
            cord_bottom = (cord_5[0] + 1, cord_5[1])
            cords.extend([cord_top, cord_bottom])
        elif cord_5[0] != self.pos[0] and cord_5[1] == self.pos[1]:
            cord_left = (cord_5[0], cord_5[1] - 1)
            cord_right = (cord_5[0], cord_5[1] + 1)
            cords.extend([cord_left, cord_right])
        else:
            cord_first = (cord_5[0], cord_5[1] + delta_cord_2[1])
            cord_second = (cord_5[0] + delta_cord_2[0], cord_5[1])
            cords.extend([cord_first, cord_second])

        self.hit(cords, players, 6)

    def fourth_skill(
            self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        farthest_player = get_farthest_player(self.pos, players)
        self.hit(farthest_player.character.pos, players, 4)
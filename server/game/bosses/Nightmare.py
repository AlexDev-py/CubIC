from __future__ import annotations

import typing as ty

from .base import BaseBoss
from ..tools import get_closest_player, get_all_neighboring_cords, get_delta_cord, get_ray, get_farset_playters, \
    get_farthest_player

if ty.TYPE_CHECKING:
    from ..player import Player
    from ..room import Room


class Nightmare(BaseBoss):
    @property
    def name(self) -> str:
        return "Кошмар"

    @property
    def base_hp(self) -> int:
        return 35

    def first_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        all_nb_cords = get_all_neighboring_cords(self.pos[0], self.pos[1])
        rays_left_right = [
            get_ray(
                self.pos,
                delta=get_delta_cord(self.pos, cord, 1),
                field_size=len(room.field),
                length=3
            )
            for cord in [all_nb_cords[3], all_nb_cords[4]]
        ]
        for hits in rays_left_right:
            if any(player.character.pos in hits for player in players):
                self.hit(hits, players, 3)

        rays_up_down = [
            get_ray(
                self.pos,
                delta=get_delta_cord(self.pos, cord, 1),
                field_size=len(room.field),
                length=5
            )
            for cord in [all_nb_cords[1], all_nb_cords[6]]
        ]
        for hits_up_down in rays_up_down:
            if any(player.character.pos in hits_up_down for player in players):
                self.hit(hits_up_down, players, 4)


    def second_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        all_nb_cords = get_all_neighboring_cords(self.pos[0], self.pos[1])
        get_five_coord = [
            get_ray(
                self.pos,
                delta=get_delta_cord(self.pos, cord, 1),
                field_size=len(room.field),
                length=3
            )
            for cord in [all_nb_cords[1], all_nb_cords[0], all_nb_cords[3],
                         all_nb_cords[4], all_nb_cords[2]]
        ]
        for five in get_five_coord:
            if any(player.character.pos in five for player in players):
                self.hit(five, players, 5)

    def third_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        farset_players = get_farthest_player(self.pos, players)
        self.hit(farset_players.character.pos, players, 3)

    def fourth_skill(
        self, field: list[list[True | False]], players: list[Player], room: Room
    ) -> None:
        pass



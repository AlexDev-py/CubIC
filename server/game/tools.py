from __future__ import annotations

import typing as ty

if ty.TYPE_CHECKING:
    from .player import Player

    Cord = tuple[int, int]  # y, x
    Cords = list[Cord, ...]


def get_all_neighboring_cords(y: int, x: int) -> Cords:
    """
    :param y: y координата клетки.
    :param x: x координата клетки.
    :return: Список координат соседних клеток.
    """
    return [
        # top
        (y - 1, x - 1),  # Сверху слева
        (y - 1, x),  # Сверху
        (y - 1, x + 1),  # Сверху справа
        # center
        (y, x - 1),  # Слева
        (y, x + 1),  # Справа
        # bottom
        (y + 1, x - 1),  # Снизу слева
        (y + 1, x),  # Снизу
        (y + 1, x + 1),  # Снизу справа
    ]


def get_neighboring_cords(y: int, x: int) -> Cords:
    """
    :param y: y координата клетки.
    :param x: x координата клетки.
    :return: Список координат соседних клеток, исключая диагонали.
    """
    all_nb_cords = get_all_neighboring_cords(y, x)
    return [all_nb_cords[1], all_nb_cords[3], all_nb_cords[4], all_nb_cords[6]]


def get_closest_player(pos: Cord, players: list[Player]) -> Player:
    """
    :param pos: Позиция отсчета.
    :param players: Список игроков.
    :return: Ближайший к позиции отсчета игрок.
    """
    closest_player_distance = (float("inf"), float("inf"))
    closest_player: Player = ...

    for player in players:
        distance = (
            abs(pos[0] - player.character.pos[0]),
            abs(pos[1] - player.character.pos[1]),
        )
        if sum(distance) < sum(closest_player_distance):
            closest_player_distance = distance
            closest_player = player

    return closest_player


def get_ray(
    cord: Cord, delta: tuple[int, int], field_size: int, length: int | None = None
) -> list[Cord]:
    """
    :param cord: Начальная точка.
    :param delta: Направление.
    :param field_size: Размер поля.
    :param length: Длина луча.
    :return: Точки луча.
    """
    cords = []

    while True:
        cord = (cord[0] + delta[0], cord[1] + delta[1])
        if not (0 <= cord[0] < field_size) or not (0 <= cord[1] < field_size):
            break
        cords.append(tuple(cord))
        if length and len(cords) >= length:
            break

    return cords


def get_delta_cord(
    first: Cord, second: Cord, delta: int | None = None
) -> tuple[int, int]:
    """
    :param first: Первая точка.
    :param second: Вторая точка.
    :param delta: нужное расстояние.
    :return: Коэффициенты смещения от первой точки до второй.
    """
    d_y = first[0] - second[0]
    if delta:
        d_y = delta * d_y // (abs(d_y) or 1)
    d_x = first[1] - second[1]
    if delta:
        d_x = delta * d_x // (abs(d_x) or 1)
    return -d_y, -d_x

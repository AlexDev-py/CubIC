from __future__ import annotations

import typing as ty

if ty.TYPE_CHECKING:
    Cord = tuple[int, int]  # y, x
    Cords = list[Cord, ...]
    Line = list[True | False]
    Field = list[Line]


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


def get_neighboring(
    field_: Field,
    cords: Cords,
) -> Line:
    """
    :param field_: Поле, с которым нужно работать.
    :param cords: Список координат клеток.
    :return: Возвращает список со значениями клеток.
    """
    w, h = len(field_[0]), len(field_) - 1
    neighboring = []
    for c in cords:
        if 0 <= c[0] <= h and 0 <= c[1] < w:
            neighboring.append(field_[c[0]][c[1]])
        else:
            neighboring.append(False)
    return neighboring


def get_ways(
    branch: Cord, length: int, field: Field, way: set[Cord] = ()
) -> list[Cords]:
    ways: list[Cords] = []
    way = [] if isinstance(way, tuple) else way
    way.append(branch)

    neighboring_cords = get_neighboring_cords(*branch)
    for cord in way:
        if cord in neighboring_cords:
            neighboring_cords.remove(cord)
    neighboring = get_neighboring(field, neighboring_cords)

    while len(way) < length + 1:
        if neighboring.count(True) == 0:
            break
        elif neighboring.count(True) == 1:
            cord = neighboring_cords[neighboring.index(True)]
            way.append(cord)
            neighboring_cords = get_neighboring_cords(*cord)
            for cord in way:
                if cord in neighboring_cords:
                    neighboring_cords.remove(cord)
            neighboring = get_neighboring(field, neighboring_cords)
        else:
            for neighboring_cord, cell in zip(neighboring_cords, neighboring):
                if cell:
                    ways.extend(get_ways(neighboring_cord, length, field, way.copy()))
            break

    ways.append(way)

    return ways

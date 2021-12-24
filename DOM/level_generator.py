"""

Алгоритм случайной генерации игрового поля.

Создание основы, с двумя свободными клетками: начало и конец.
 Остальные клетки заняты стенами.
Пока существуют клетки с одним вариантом пути:
    Создание случайной фигуры: вертикальной или горизонтальной прямой.
    Освободить клетки, на которых лежит прямая.
    Если появились проходы шириной в 2 клетки
     или осталась стена в одну клетку
     или прямая пересекает другие свободные клетки больше чем 2 раза:
        Удалить созданную прямую

"""

from __future__ import annotations

import copy
import random
import typing as ty

if ty.TYPE_CHECKING:

    Line = list[ty.Optional[bool]]
    Field = list[Line]
    Cord = tuple[int, int]
    Cords = list[Cord, ...]


def pp(field: Field):
    """
    Красивый вывод поля в консоль.
    """
    for i, line in enumerate(field):
        t = "".join(map(str, line))
        t = t.replace("None", " # ").replace("True", "   ")
        print(t)
    print("\n\n")


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
            neighboring.append(None)
    return neighboring


def _generate(w: int, h: int) -> list:
    def get_lonely() -> ty.Optional[Cord]:
        """
        :return: Координаты первой попавшейся клетки, у которой только 1 сосед.
        """
        for y, line in enumerate(field):
            for x, cell in enumerate(line):
                if cell is True:
                    neighboring = get_neighboring(field, get_neighboring_cords(y, x))
                    if neighboring.count(True) < 2:
                        return y, x
        return None

    def get_vertical(y: int, x: int) -> Cords:
        """
        Создает вертикальный проход случайной высоты.
        :param y: y координата начальной точки.
        :param x: x координата начальной точки.
        :return: Список с координатами клеток.
        """
        max_h = h // 2  # Максимальная высота прохода
        way_cords = []

        top = random.randint(2, max_h // 2)  # Кол-во клеток наверх
        top = top + 1 if top % 2 != 0 else top  # Делаем число кратным двум
        for i in range(top):  # Добавляем координаты в список
            way_cords.append((y - i - 1, x))

        bottom = random.randint(2 if top == 0 else 0, max_h // 2)  # Кол-во клеток вниз
        bottom = bottom + 1 if bottom % 2 != 0 else bottom
        for i in range(bottom):  # Добавляем координаты в список
            way_cords.append((y + i + 1, x))

        return way_cords

    def get_horizontal(y: int, x: int) -> Cords:
        """
        Создает горизонтальный проход случайной ширины.
        :param y: y координата начальной точки.
        :param x: x координата начальной точки.
        :return: Список с координатами клеток.
        """
        max_w = w // 2  # Максимальная ширина прохода
        way_cords = []

        left = random.randint(0, max_w // 2)  # Кол-во клеток влево
        left = left + 1 if left % 2 != 0 else left
        for i in range(left):
            way_cords.append((y, x - i - 1))

        right = random.randint(
            2 if left == 0 else 0, max_w // 2
        )  # Кол-во клеток вправо
        right = right + 1 if right % 2 != 0 else right
        for i in range(right):
            way_cords.append((y, x + i + 1))

        return way_cords

    def validate_field() -> True | False:
        """
        Проверка правильности генерации поля.
        :return: True или False
        """
        for y, line in enumerate(_field):
            for x, cell in enumerate(line):
                all_neighboring = get_neighboring(
                    _field, get_all_neighboring_cords(y, x)
                )
                neighboring = get_neighboring(_field, get_neighboring_cords(y, x))
                if cell is True:  # Клетка, на которой можно ходить
                    # У клетки, которая соприкасается с 4-мя другими,
                    # может быть максимум 4 соседа.
                    if neighboring.count(True) == 4:
                        if all_neighboring.count(True) > 4:
                            return False
                    # У клетки, соприкасающейся с 3-мя другими,
                    # может быть максимум 5 соседей
                    elif neighboring.count(True) == 3:
                        if all_neighboring.count(True) > 4:
                            return False
                    # У клетки, соприкасающейся с 2-мя другими,
                    # может быть максимум 6 соседей
                    elif neighboring.count(True) == 2:
                        if all_neighboring.count(True) > 6:
                            return False
                else:  # Стена
                    # у стены должен быть хотя-бы 1 сосед-стена
                    if all_neighboring.count(True) == 8:
                        return False
        return True

    # Изначальное поле
    field: Field = [[None] * w for _ in range(h - 1)]
    field.append([*[None] * (w // 2), True, *[None] * (w // 2)])
    field.insert(0, [*[None] * (w // 2), True, *[None] * (w // 2)])

    ways = [get_vertical, get_horizontal]  # Возможные генерации путей
    errors: dict[Cord, int] = {}  # Ошибки

    while cords := get_lonely():  # Пока есть клетки с одним проходом
        errors[cords] = errors.get(cords) or 0
        way = random.choice(ways)(*cords)  # Случайно выбираем путь
        collide_count = 0  # Кол-во столкновений выбранного пути с существующими
        _field = copy.deepcopy(field)  # Копия поля
        for cord in way:
            if 0 <= cord[0] <= h and 0 <= cord[1] < w:  # Входит ли координата в поле
                if _field[cord[0]][cord[1]] is True:  # Если уже занята
                    collide_count += 1
                if collide_count > 2:  # Если больше двух столкновений
                    errors[cords] += 1
                    break

                _field[cord[0]][cord[1]] = True

        if validate_field():  # Если поле прошло проверку
            field = copy.deepcopy(_field)  # Заменяем поле на копию
        else:
            errors[cords] += 1

        # Если произошло больше 3-х ошибок с генерацией на одном и том же месте
        if errors[cords] > 3:
            # Откатываем клетку и ее соседей
            for cord in get_neighboring_cords(*cords):
                if 0 <= cord[0] <= h and 0 <= cord[1] < w:
                    field[cord[0]][cord[1]] = None
            field[cords[0]][cords[1]] = None
            del errors[cords]

    return field


def generate(w: int, h: int) -> Field:
    """
    Создает случайное игровое поле с определенным размером.
    :param w:
    :param h:
    :return:
    """
    w = w + 1 if w % 2 == 0 else w
    h = h - 1 if h % 2 != 0 else h

    field: Field = ...
    _field = [False] * w * h

    # Пока кол-во свободных клеток меньше 35% от всей площади.
    # Что-бы поле не было слишком маленьким.
    while _field.count(True) < len(_field) / 100 * 35:
        field = _generate(w, h)
        _field = []
        for line in field:
            _field += line

    # Добавляем рамки, вход и выход.
    w += 4
    h += 4
    board = [
        [*[None] * (w // 2 - 2), True, True, True, True, *[None] * (w // 2 - 1)],
        [*[None] * (w // 2), True, *[None] * (w // 2)],
    ]
    for line in field:
        board.append([None, None, *line, None, None])
    board.append([*[None] * (w // 2), True, *[None] * (w // 2)])
    board.append([None] * w)

    return board


if __name__ == "__main__":
    size = (25, 25)
    pp(generate(*size))

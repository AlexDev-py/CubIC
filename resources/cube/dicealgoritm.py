from __future__ import annotations

import random

TOP = "top"
LEFT = "left"
FRONT = "front"
BACK = "back"
RIGHT = "right"
BOTTOM = "bottom"


class DiceAlgoritm:
    """
    Симулирует бросок кости.
    """

    def __init__(self):
        """
        _________¶¶¶¶¶¶¶¶¶¶¶
        ______¶¶¶¶¶_______¶¶¶¶¶
        ___¶¶¶¶¶_____________¶¶¶¶
        _¶¶¶¶________§§§§________¶¶¶
        ¶¶¶___________§§§§________¶¶¶
        ¶_¶¶¶¶¶________________¶¶¶¶_¶
        ¶_____¶¶¶¶__________¶¶¶¶¶___¶
        ¶_§§§§_¶¶¶¶¶____¶¶¶¶___§§§§_¶
        ¶__§§§§____¶¶¶¶¶¶¶____§§§§__¶
        ¶_____________¶¶____________¶
        ¶_____________¶_____§§§§____¶
        ¶_____________¶____§§§§_____¶
        ¶_______§§§§__¶_____________¶
        ¶¶¶______§ü§§_¶_§§§§______¶¶¶
        __¶¶¶¶________¶§§§§____¶¶¶¶¶
        ____¶¶¶¶¶_____¶_____¶¶¶¶¶
        _______¶¶¶¶¶¶_¶_¶¶¶¶¶¶
        __________¶¶¶¶¶¶¶¶¶
        Изначальное положение кости:
        Мы смотрим на единицу.
        2 - на левой грани от единицы
        3 - на нижней грани от единицы
        4 - на верхней грани от единицы
        5 - на правой грани от единицы
        6 - на противоположной единице стороне
        """
        self.data = {1: TOP, 2: LEFT, 3: FRONT, 4: BACK, 5: RIGHT, 6: BOTTOM}

    def move_top(self) -> None:
        """
        Поворот вверх от наблюдаемой стороны.
        """
        movement = [TOP, BACK, BOTTOM, FRONT]
        rev = self.rev
        new_data = {rev[movement[i]]: movement[(i + 1) % 4] for i in range(4)}
        self.data.update(new_data)

    def move_bottom(self) -> None:
        """
        Поворот вниз от наблюдаемой стороны.
        """
        movement = [TOP, FRONT, BOTTOM, BACK]
        rev = self.rev
        new_data = {rev[movement[i]]: movement[(i + 1) % 4] for i in range(4)}
        self.data.update(new_data)

    def move_left(self) -> None:
        """
        Поворот влево от наблюдаемой стороны.
        """
        movement = [TOP, LEFT, BOTTOM, RIGHT]
        rev = self.rev
        new_data = {rev[movement[i]]: movement[(i + 1) % 4] for i in range(4)}
        self.data.update(new_data)

    def move_right(self) -> None:
        """
        Поворот вправо от наблюдаемой стороны.
        """
        movement = [TOP, RIGHT, BOTTOM, LEFT]
        rev = self.rev
        new_data = {rev[movement[i]]: movement[(i + 1) % 4] for i in range(4)}
        self.data.update(new_data)

    @property
    def rev(self) -> dict[str, int]:
        return {v: k for k, v in self.data.items()}

    def roll(self, k: int | None = None) -> tuple[list[int], int]:
        """
        Случайный бросок.
        """
        _movement = [self.move_right, self.move_left, self.move_bottom, self.move_top]
        movement = []
        last = -1
        for _ in range(k or random.randint(10, 25)):
            move = [0, 1, 2, 3]
            if last == 0:
                move.remove(1)
            elif last == 1:
                move.remove(0)
            elif last == 2:
                move.remove(3)
            elif last == 3:
                move.remove(2)

            last = random.choice(move)
            _movement[last]()
            movement.append([last, self.rev[TOP]])

        return movement


if __name__ == "__main__":
    dice = DiceAlgoritm()
    print(*dice.roll(), sep="\n")
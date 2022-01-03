"""

Функции и классы, которые используются в приложении.

"""

import os

import pygame as pg
from loguru import logger

from base import Alert, Text, Button
from base.text_filters import LengthTextFilter, AlphabetTextFilter

NickTextFilter = LengthTextFilter(35) & AlphabetTextFilter(
    ["-", "_"], nums=True, eng=True, rus=True, ignore_case=True
)


class FinishStatus:
    """
    Статус с которым функция завершила работу.
    """

    close: str = "close"  # Закрытие клиента
    auth_failed: str = "auth_failed"  # Ошибка авторизации
    ok: str = "ok"  # Успешная загрузка

    fail_msg: str = ""  # Текст ошибки

    @classmethod
    def set_msg(cls, msg: str) -> None:
        cls.fail_msg = msg


def check_password(password: str) -> True | False:
    """
    TODO
    Проверка сложности пароля.
    :param password:
    :return: True - пароль подходит
    """
    return True


def load_image(
    name: str, size: tuple[int, int] = None, color_key: int = None
) -> pg.Surface:
    path = os.path.join("data", name)
    if not os.path.isfile(path):
        logger.opt(colors=True).error(f"Файл <y>{path}</y> не найден")
        return pg.Surface((1, 1), pg.SRCALPHA).convert_alpha()

    image = pg.image.load(path)
    if size is not None:
        image = pg.transform.scale(image, size)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()

    return image


class InfoAlert(Alert):
    """
    Виджет, для отображения ошибки авторизации.
    """

    def __init__(self, parent, parent_size: tuple[int, int], width: int):
        super(InfoAlert, self).__init__(
            parent,
            parent_size=parent_size,
            width=width,
            padding=20,
            background=pg.Color("black"),
            fogging=100,
        )

        self._text = Text(
            self,
            x=0,
            y=0,
            width=self.rect.width - self.padding * 2,
            text="",
            color=pg.Color("red"),
            font=pg.font.Font(None, 30),
            soft_split=True,
        )

        self.continue_button = Button(
            self,
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2),
            y=lambda obj: self._text.rect.bottom + 20,
            text="ок",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(None, 25),
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: self.hide(),
        )

    def show_message(self, text: str) -> None:
        self._text.text = text
        self.show()

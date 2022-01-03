"""

Функции и классы, которые используются в приложении.

"""

import os

import pygame as pg
from loguru import logger

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

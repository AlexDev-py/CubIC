"""

Функции и классы, которые используются в приложении.

"""

from __future__ import annotations

import os
import typing as ty

import pygame as pg
from loguru import logger

from base import Alert, Text, Button, WidgetsGroup
from base.text_filters import LengthTextFilter, AlphabetTextFilter
from database.field_types import Resolution

if ty.TYPE_CHECKING:
    from base.types import CordFunction
    from base.group import Group

NickTextFilter = LengthTextFilter(15) & AlphabetTextFilter(
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
        """
        Изменяет сообщение.
        :param msg: Новое сообщение.
        """
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
    file_name: str,
    namespace: str = None,
    size: tuple[int, int] = None,
    color_key: int = None,
) -> pg.Surface:
    path = os.path.join(namespace or os.environ["APP_DIR"], file_name)
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
    Информационный виджет.
    Текст и кнопка "ок", закрывающая сообщение.
    """

    def __init__(self, parent: Group, parent_size: tuple[int, int], width: int):
        """
        Виджет, отображающий информационное сообщение.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
        :param parent_size: Размеры родительского виджета.
        :param width: Ширина информационного виджета.
        """
        super(InfoAlert, self).__init__(
            parent,
            parent_size=parent_size,
            width=width,
            padding=20,
            background=pg.Color("black"),
            border_color=pg.Color("red"),
            border_width=3,
            fogging=100,
        )

        self._text = Text(
            self,
            x=0,
            y=0,
            width=self.rect.width - self.padding * 2,
            text="...",
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
        """
        Изменяет текст и показывает виджет.
        :param text: Текст сообщения.
        """
        self._text.text = text
        self.show()


class DropMenu(WidgetsGroup):
    def __init__(
        self,
        parent: WidgetsGroup,
        *,
        width: int | CordFunction | None = None,
        height: int | CordFunction | None = None,
        padding: int = 0,
        background: pg.Color | None = None,
        border_color: pg.Color = pg.Color(255, 255, 255),
        border_width: int = 0,
    ):
        """
        Выпадающий виджет.
        Активируется по нажатию правой кнопкой мыши по определенному виджету.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является WidgetsGroup.
        :param width: Ширина виджета.
        :type width: Число или функция вычисляющая ширину.
        :param height: Высота виджета.
        :type height: Число или функция вычисляющая высоту.
        :param padding: Отступы от границ виджета.
        :param background: Цвет фона.
        :param border_color: Цвет обводки виджета.
        :param border_width: Ширина обводки.
        """

        # Получаем исходного родителя
        _parent = parent.parent
        while _parent.parent is not None:
            _parent = _parent.parent

        self._widget = parent

        super(DropMenu, self).__init__(
            _parent,
            x=0,
            y=0,
            width=width,
            height=height,
            padding=padding,
            background=background,
            border_color=border_color,
            border_width=border_width,
            hidden=True,
        )

        self.hide()

    def handle_event(self, event: pg.event.Event) -> None:
        super(DropMenu, self).handle_event(event)
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_RIGHT:
                # Открываем виджет
                if self._widget.get_global_rect().collidepoint(event.pos):
                    self.open(event.pos)
                    return
            # Скрываем виджет
            if hasattr(event, "pos"):
                if self.enabled:
                    if not self.rect.collidepoint(event.pos):
                        self.hide()

    def open(self, pos: tuple[int, int]) -> None:
        """
        Открывает меню в определенной позиции.
        :param pos: Координаты меню.
        """
        resolution = Resolution.converter(os.environ["resolution"])  # Разрешение окна

        # Смещаем меню, если оно не вмещается
        x, y = pos
        if x + self.rect.width > resolution.width:
            x -= self.rect.width
        if y + self.rect.height > resolution.height:
            y -= self.rect.height

        self.x = x
        self.y = y

        self.show()  # Показываем
        self.enable()  # Активируем

    def hide(self) -> None:
        """
        Скрывает и деактивирует меню.
        """
        super(DropMenu, self).hide()
        self.disable()

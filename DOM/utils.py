"""

Функции и классы, которые используются в приложении.

"""

from __future__ import annotations

import os
import re
import typing as ty

import pygame as pg
from loguru import logger

from base import Alert, Text, Button, WidgetsGroup, Anchor
from base.text_filters import LengthTextFilter, AlphabetTextFilter
from database.field_types import Resolution

if ty.TYPE_CHECKING:
    from base.types import CordFunction
    from base.group import Group

# Фильтр содержания ника
# Максимальная длинна: 15
# Возможные символы: -; _; <цифры>; <английский алфавит>; <русский алфавит>
NickTextFilter = LengthTextFilter(15) & AlphabetTextFilter(
    ["-", "_"], nums=True, eng=True, rus=True, ignore_case=True
)

PasswordTextFilter = LengthTextFilter(40) & AlphabetTextFilter(
    list("-_@$!%*#?&"), nums=True, eng=True, rus=False, ignore_case=True
)

_images_cash = {}


class FinishStatus:
    """
    Статус с которым функция завершила работу.
    """

    close: str = "close"  # Закрытие клиента
    auth_failed: str = "auth_failed"  # Ошибка авторизации
    ok: str = "ok"  # Успешная загрузка

    enter_game: str = "enter_game"  # Запуск игрового клиента
    exit_game: str = "exit_game"  # Выход в меню

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
    Проверка сложности пароля.
    :param password:
    :return: True - пароль подходит
    """

    # Проверяет что длина пароля больше 12 и содержатся ли заглавные,
    # строчные буквы и есть ли символы
    if re.search(
        re.compile(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&\-_])"
            r"[A-Za-z\d@$!#%*?&\-_]{12,40}$"
        ),
        password,
    ):
        return True

    # Если пароль длинный с символами, строчными буквами, но без заглавных.
    elif re.search(
        re.compile(
            r"^(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&\-_])[a-z\d@$!%*#?&\-_]{12,40}$"
        ),
        password,
    ):
        return True

    # Дополнительное условие, что пароль по длине больше 9 и в нём есть символы,
    # заглавные буквы, но без строчных.
    elif re.search(
        re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&\-_])[A-Z\d@$!%*#?&\-_]{9,40}$"),
        password,
    ):
        return True

    # Пароль сложный так или иначе должен содержать символы
    # так что проверку без символов не делаем.
    return False


def load_image(
    file_name: str,
    namespace: str = None,
    size: tuple[int | None, int | None] = None,
    save_ratio: True | False = False,
) -> pg.Surface:
    """
    Загрузка изображения.
    :param file_name: Название файла.
    :param namespace: Окружение(директория с файлом).
    :param size: Размер изображения.
        size - Кортеж из двух элементов типа int | None.
        None значение поддерживается только при save_ratio=True
        None значением может быть только один из элементов кортежа.
    :param save_ratio: True - Сохраняет пропорции при масштабировании.
    :return: Готовое изображение.
    """
    # Путь к файлу(если namespace не указан, файл ищется в директории приложения)
    path = os.path.join(namespace or os.environ["APP_DIR"], file_name)
    if not os.path.isfile(path):
        if path not in _images_cash:
            _images_cash[path] = None
            logger.opt(colors=True).error(f"Файл <y>{path}</y> не найден")
        # Возвращаем пустое изображение
        return pg.Surface((1, 1), pg.SRCALPHA).convert_alpha()

    if not (image := _images_cash.get(path)):
        image = pg.image.load(path).convert_alpha()
        _images_cash[path] = image
    if size is not None:
        if not save_ratio:
            image = pg.transform.scale(image, size)
        else:
            # Масштабирование с сохранением пропорций
            base_size = image.get_size()  # Изначальный размер изображения
            # Изменение ширины
            delta_w = abs(size[0] - base_size[0]) if size[0] is not None else 0
            # Изменение высоты
            delta_h = abs(size[1] - base_size[1]) if size[1] is not None else 0
            if delta_w > delta_h:
                # Высчитываем подходящее значение высоты
                size = (size[0], (size[0] * base_size[1]) / base_size[0])
            else:
                # Высчитываем подходящее значение ширины
                size = ((size[1] * base_size[0]) / base_size[1], size[1])
            image = pg.transform.scale(image, size)

    return image


class LoadingAlert(Alert):
    def __init__(
        self,
        parent: Group,
        name: str = None,
        *,
        parent_size: tuple[int, int],
        width: int,
    ):
        """
        Виджет загрузки.
        Не имеет кнопки закрытия. Закрывается только программно.
        :param parent: Объект к которому принадлежит виджет.
        :param name: Название объекта.
        :param parent_size: Размер родительского виджета.
        :param width: Ширина виджета.
        """
        font_size = int(os.environ.get("font_size", 20))
        font = os.environ.get("font")

        super(LoadingAlert, self).__init__(
            parent,
            name,
            parent_size=parent_size,
            width=width,
            padding=20,
            background=pg.Color("#122321"),
            border_color=pg.Color("#b9a66d"),
            border_width=3,
            fogging=100,
        )

        self.text = Text(
            self,
            x=0,
            y=0,
            width=self.rect.width - self.padding * 2 - self.border_width * 2,
            text="...",
            font=pg.font.Font(font, font_size),
            anchor=Anchor.center,
            soft_split=True,
        )

    def show_message(self, text: str) -> None:
        """
        Изменяет текст и показывает виджет.
        :param text: Текст сообщения.
        """
        self.text.text = text
        self.show()


class InfoAlert(LoadingAlert):
    """
    Информационный виджет.
    Текст и кнопка "ок", закрывающая сообщение.
    """

    def __init__(
        self,
        parent: Group,
        name: str = None,
        *,
        parent_size: tuple[int, int],
        width: int,
    ):
        """
        Виджет, отображающий информационное сообщение.
        :param parent: Объект к которому принадлежит виджет.
        :param name: Название объекта.
        :param parent_size: Размеры родительского виджета.
        :param width: Ширина информационного виджета.
        """
        font_size = int(os.environ.get("font_size", 17))
        font = os.environ.get("font")

        super(InfoAlert, self).__init__(
            parent, name, parent_size=parent_size, width=width
        )

        self.continue_button = Button(
            self,
            x=lambda obj: round(
                (self.rect.width - self.padding * 2 - self.border_width * 2) / 2
                - obj.rect.width / 2
            ),
            y=lambda obj: self.text.rect.bottom + 20,
            text="ок",
            padding=5,
            active_background=pg.Color(222, 222, 222, 100),
            font=pg.font.Font(font, font_size),
            border_width=2,
            callback=lambda event: self.hide(),
        )


class DropMenu(WidgetsGroup):
    def __init__(
        self,
        parent: WidgetsGroup,
        name: str = None,
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
        Закрывается при нажатии в другое место экрана.
        :param parent: Объект к которому принадлежит виджет.
        :param name: Название объекта.
        :param width: Ширина виджета.
        :param height: Высота виджета.
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
            name,
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
        if self.enabled:
            if not self.hidden:
                super(DropMenu, self).handle_event(event)
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_RIGHT:
                    # Открываем виджет
                    if self._widget.get_global_rect().collidepoint(event.pos):
                        self.open(event.pos)
                        return
                # Скрываем виджет
                if hasattr(event, "pos"):
                    if not self.hidden:
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

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)


class LoadingScreen(Alert):
    def __init__(
        self, parent: Group, name: str = None, *, parent_size: tuple[int, int]
    ):
        """
        Экран загрузки.
        Не имеет кнопки закрытия. Закрывается только программно.
        :param parent: Объект к которому принадлежит виджет.
        :param name: Название объекта.
        :param parent_size: Размер родительского виджета.
        """
        font_size = int(os.environ.get("font_size", 20))
        font = os.environ.get("font")

        super(LoadingScreen, self).__init__(
            parent,
            name,
            parent_size=parent_size,
            width=round(parent_size[0] * 0.8),
            background=pg.Color("black"),
            fogging=255,
        )

        self.text = Text(
            self,
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2),
            y=0,
            width=self.rect.width - self.padding * 2,
            text="...",
            font=pg.font.Font(font, font_size),
            anchor=Anchor.center,
            soft_split=True,
        )

    def show_message(self, text: str) -> None:
        """
        Изменяет текст и показывает виджет.
        :param text: Текст сообщения.
        """
        self.text.text = text
        self.show()

    def update(self) -> None:
        super(LoadingScreen, self).update()
        if self.parent.parent.objects and self.parent in self.parent.parent.objects:
            if self.parent.parent.objects[-1] is not self.parent:
                self.parent.parent._objects.remove(self.parent)
                self.parent.parent.objects.append(self.parent)

    def show(self) -> None:
        super(LoadingScreen, self).show()
        self.parent.parent.disable()

    def hide(self) -> None:
        super(LoadingScreen, self).hide()
        self.parent.parent.enable()

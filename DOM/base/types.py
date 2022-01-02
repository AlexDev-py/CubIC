"""

Аннотации типов данных.

"""

from __future__ import annotations

import typing as ty

if ty.TYPE_CHECKING:
    from .widget import BaseWidget
    from .events import ButtonClickEvent

    # Тип данных, обозначающий результат выполнения функции в отдельном потоке
    Response = ty.TypeVar("Response")

    # Описание функции вычисления координаты виджета
    CordFunction = ty.Callable[[BaseWidget], int]

    # Описание функции - обработчика нажатия на кнопку
    ButtonCallback = ty.Callable[[ButtonClickEvent], ...]

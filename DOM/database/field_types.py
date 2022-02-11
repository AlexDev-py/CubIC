from __future__ import annotations

import os
import sqlite3 as sql
from typing import NamedTuple


class Resolution(NamedTuple):
    """
    Тип данных для хранения разрешения в базе данных.
    """

    width: int
    height: int

    def __repr__(self):
        return f"{self.width};{self.height}"

    @classmethod
    def adapter(cls, obj: Resolution) -> bytes:
        return str(obj).encode()

    @classmethod
    def converter(cls, obj: bytes | str) -> Resolution:
        return Resolution(*map(int, obj.split(b";" if isinstance(obj, bytes) else ";")))


sql.register_adapter(Resolution, Resolution.adapter)
sql.register_converter(
    Resolution.__name__.lower(), lambda obj: Resolution.converter(obj)
)

# TODO: Протестировать на разных разрешениях монитора
# Возможные разрешения экрана
ALLOWED_RESOLUTION = [
    Resolution(1024, 576),
    Resolution(1280, 720),
    Resolution(1600, 900),
    Resolution(1920, 1080),
    Resolution(2560, 1440),
    Resolution(3840, 2160),
    Resolution(5112, 2880),
]  # Базовые разрешения 16:9

# Разрешение монитора
max_resolution = Resolution.converter(os.environ["MAX_RESOLUTION"])

# Если разрешение монитора меньше 1024x576
if max_resolution < ALLOWED_RESOLUTION[0]:
    ALLOWED_RESOLUTION = [
        Resolution(max_resolution.width // 2, int(max_resolution.width // 2 / 16 * 9)),
        Resolution(max_resolution.width, int(max_resolution.width / 16 * 9)),
    ]

for i, resolution in enumerate(ALLOWED_RESOLUTION):
    if (
        resolution.width > max_resolution.width
        or resolution.height > max_resolution.height
    ):  # Если разрешение больше возможного
        # Отсеиваем это разрешение и далее идущие
        ALLOWED_RESOLUTION = ALLOWED_RESOLUTION[:i]
        break


__all__ = ["Resolution", "ALLOWED_RESOLUTION"]

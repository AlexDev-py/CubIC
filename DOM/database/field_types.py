from __future__ import annotations

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

# Возможные разрешения экрана
ALLOWED_RESOLUTION = [
    Resolution(1024, 576),
    Resolution(1280, 720),
    Resolution(1600, 900),
    Resolution(1920, 1080),
    Resolution(2560, 1440),
]


__all__ = ["Resolution", "ALLOWED_RESOLUTION"]

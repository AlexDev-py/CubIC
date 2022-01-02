"""

Фильтры для текста, который пользователь вводит в InputLine.

"""

from __future__ import annotations

import typing as ty
from abc import ABC, abstractmethod
from dataclasses import dataclass

if ty.TYPE_CHECKING:
    import pygame as pg


class BaseTextFilter(ABC):
    """
    Описание фильтра.
    """

    @abstractmethod
    def validate(self, text: str) -> True | False:
        ...

    def __or__(self, other: BaseTextFilter) -> OrTextFilter:
        return OrTextFilter(self, other)

    def __and__(self, other: BaseTextFilter) -> AndTextFilter:
        return AndTextFilter(self, other)


@dataclass
class OrTextFilter(BaseTextFilter):
    """
    Объединение двух фильтров оператором | (or).
    """

    filter1: BaseTextFilter
    filter2: BaseTextFilter

    def validate(self, text: str) -> bool:
        if self.filter1.validate(text):
            return True
        return self.filter2.validate(text)


@dataclass
class AndTextFilter(BaseTextFilter):
    """
    Объединение двух фильтров оператором & (and).
    """

    filter1: BaseTextFilter
    filter2: BaseTextFilter

    def validate(self, text: str) -> bool:
        if not self.filter1.validate(text):
            return False
        return self.filter2.validate(text)


class LengthTextFilter(BaseTextFilter):
    def __init__(self, max_length: int):
        """
        Фильтр длинны текста.
        :param max_length: Максимальная длинна текста.
        """
        self.max_length = max_length

    def validate(self, text: str) -> bool:
        return len(text) <= self.max_length


class WidthTextFilter(BaseTextFilter):
    def __init__(self, max_width: int, font: pg.font.SysFont):
        """
        Фильтр ширины текста.
        :param max_width: Максимальная ширина текста.
        :param font: Шрифт.
        """
        self.max_width = max_width
        self.font = font

    def validate(self, text: str) -> bool:
        return self.font.size(text)[0] <= self.max_width


class AlphabetTextFilter(BaseTextFilter):
    rus = [*[chr(n) for n in range(ord("а"), ord("а") + 32)], "ё"]
    eng = [chr(n) for n in range(ord("a"), ord("a") + 26)]
    nums = [chr(n) for n in range(ord("0"), ord("0") + 10)]

    def __init__(
        self,
        allow_symbols: list[str] = (),
        *,
        nums: bool,
        eng: bool,
        rus: bool,
        ignore_case: bool = False
    ):
        """
        Фильтр алфавита текста.
        :param allow_symbols: Список разрешенных символов.
        :param nums: True - Разрешает цифры.
        :param eng: True - Разрешает английские буквы.
        :param rus: True - Разрешает русские буквы.
        :param ignore_case: True - Игнорирует регистр.
        """
        self.alphabet = list(allow_symbols)
        self.ignore_case = ignore_case
        if nums:
            self.alphabet.extend(self.nums)
        if eng:
            self.alphabet.extend(self.eng)
        if rus:
            self.alphabet.extend(self.rus)

    def validate(self, text: str) -> True | False:
        for char in text:
            if (char.lower() if self.ignore_case else char) not in self.alphabet:
                return False
        return True

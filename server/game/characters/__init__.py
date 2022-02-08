from __future__ import annotations

import typing as ty

from .archer import Archer
from .base import BaseCharacter
from .magician import Magician
from .tank import Tank
from .warrior import Warrior

characters: list[ty.Type[BaseCharacter]] = [Warrior, Tank, Archer, Magician]

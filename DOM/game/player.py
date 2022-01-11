from __future__ import annotations

import typing as ty

if ty.TYPE_CHECKING:
    from ..network import User


class Player:
    def __init__(self, user: User, is_owner: True | False = False):
        self.uid = user.uid
        self.username = user.username
        self.icon = user.icon

        self.is_owner = is_owner
        self.ready = False
        self.items = []

from __future__ import annotations

import os
import typing as ty

import pygame as pg
from loguru import logger

from base import (
    Button,
    WidgetsGroup,
    Label,
    Anchor,
    Line,
    Thread,
    Alert,
    InputBox,
)
from base.events import ButtonClickEvent
from database.field_types import Resolution
from utils import load_image, NickTextFilter, InfoAlert, DropMenu

if ty.TYPE_CHECKING:
    from network import User, NetworkClient
    from base.group import Group


class FriendDropMenu(DropMenu):
    def __init__(self, parent: UserWidget):
        font_size = int(os.environ["font_size"])

        super(FriendDropMenu, self).__init__(
            parent,
            background=pg.Color("gray"),
            border_color=pg.Color("red"),
            border_width=2,
        )

        self.delete_friend = Button(
            self,
            x=0,
            y=0,
            text="Удалить друга",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("black"),
            font=pg.font.Font(None, int(font_size * 0.6)),
        )


class UserWidget(WidgetsGroup):
    def __init__(
        self,
        parent: Group,
        x: int,
        y: int,
        user: User,
        icon_size: int = None,
        font_size: int = None,
        width: int = None,
    ):
        font_size = font_size or int(os.environ["font_size"])
        icon_size = icon_size or int(os.environ["icon_size"])

        super(UserWidget, self).__init__(
            parent,
            x=x,
            y=y,
            width=width,
            padding=20,
        )

        self.user = user
        self.icon = Label(
            self,
            x=0,
            y=0,
            width=icon_size,
            height=icon_size,
            anchor=Anchor.center,
            sprite=load_image(
                rf"icons\icon_{user.icon}.png",
                (icon_size - 2, icon_size - 2),
            ),
        )

        # TODO: Ник может быть слишком длинным
        self.username = Label(
            self,
            x=self.icon.rect.right + 30,
            y=0,
            text=user.username,
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
        )

        self.status = Label(
            self,
            x=self.icon.rect.right + 30,
            y=self.username.rect.bottom + 5,
            text=user.status.text,
            color=pg.Color(user.status.color),
            font=pg.font.Font(None, int(font_size * 0.8)),
        )


class FriendWidget(UserWidget):
    def __init__(
        self,
        parent: Social,
        x: int,
        y: int,
        user: User,
        font_size: int,
        delete_friend: ty.Callable[[FriendWidget], ...],
    ):
        font_size = font_size or int(os.environ["font_size"])
        icon_size = int(os.environ["icon_size"])

        super(FriendWidget, self).__init__(parent, x, y, user, icon_size, font_size)

        self.delete_friend = delete_friend
        self.drop_menu = FriendDropMenu(self)

    def delete(self):
        self.parent.remove(self)
        self.drop_menu.parent.remove(self.drop_menu)

    def handle_event(self, event: pg.event.Event) -> None:
        super(FriendWidget, self).handle_event(event)
        if event.type == ButtonClickEvent.type:
            if event.obj == self.drop_menu.delete_friend:
                self.delete_friend(self)


class FriendRequestWidget(UserWidget):
    def __init__(
        self,
        parent: FriendRequests,
        x: int,
        y: int,
        user: User,
        icon_size: int,
        font_size: int,
        callback: ty.Callable[[ty.Literal["ok", "cancel"], FriendRequestWidget], ...],
    ):

        super(FriendRequestWidget, self).__init__(
            parent,
            x,
            y,
            user,
            icon_size,
            font_size,
            width=(parent.rect.width - parent.padding * 2) // 3,
        )

        self.ok_button = Button(
            self,
            x=0,
            y=self.icon.rect.bottom + 5,
            text=" + ",
            padding=1,
            color=pg.Color("red"),
            active_background=pg.Color("gray"),
            font=pg.font.Font(None, int(font_size * 0.8)),
            callback=lambda event: callback("ok", self),
        )

        self.cancel_button = Button(
            self,
            x=self.ok_button.rect.right + 5,
            y=self.icon.rect.bottom + 5,
            text=" - ",
            padding=1,
            color=pg.Color("red"),
            active_background=pg.Color("gray"),
            font=pg.font.Font(None, int(font_size * 0.8)),
            callback=lambda event: callback("cancel", self),
        )


class FriendRequests(Alert):
    def __init__(self, parent: Group, network_client: NetworkClient):
        resolution = Resolution.converter(os.environ["resolution"])
        font_size = int(os.environ["font_size"])

        self.network_client = network_client

        super(FriendRequests, self).__init__(
            parent,
            parent_size=resolution,
            width=int(resolution.width * 0.5),
            height=int(resolution.height * 0.8),
            padding=20,
            background=pg.Color("black"),
            fogging=50,
        )

        self.info_alert = InfoAlert(
            parent, parent_size=resolution, width=int(resolution.width * 0.5)
        )

        self.exit_btn = Button(
            self,
            x=0,
            y=0,
            text=" X ",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(None, int(font_size * 0.7)),
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: self.hide(),
        )

        self.title = Label(
            self,
            x=lambda obj: round(
                self.rect.width / 2 - obj.rect.width / 2 - self.padding * 2
            ),
            y=0,
            text="Добавить друзей",
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
        )

        self.username_input = InputBox(
            self,
            x=0,
            y=self.title.rect.bottom + 30,
            description="Имя пользователя",
            width=int(self.rect.width * 0.8) - self.padding * 2,
            padding=5,
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
            inactive_border_color=pg.Color("red"),
            active_border_color=pg.Color("white"),
            border_width=5,
            text_filter=NickTextFilter,
        )

        self.find_friend_button = Button(
            self,
            x=self.username_input.rect.right + 10,
            y=self.username_input.rect.top + self.username_input.input_line.rect.top,
            width=int(self.rect.width * 0.2) - self.padding,
            height=self.username_input.input_line.rect.height,
            text="Найти",
            padding=5,
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
            active_background=pg.Color("gray"),
            border_color=pg.Color("red"),
            border_width=5,
            callback=lambda event: self.send_request(),
        )

        self.friend_requests_label = Label(
            self,
            x=lambda obj: round(
                self.rect.width / 2 - obj.rect.width / 2 - self.padding * 2
            ),
            y=self.find_friend_button.rect.bottom + 10,
            text="Запросы в друзья",
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
        )

        self.friend_requests = []

    def send_request(self) -> None:
        if not (username := self.username_input.input_line.text.strip()):
            self.username_input.input_line.active = True
            return

        self.disable()
        self.network_client.send_friend_request(
            username,
            success_callback=lambda: (
                self.info_alert.show_message("Запрос отправлен"),
                self.enable(),
            ),
            fail_callback=lambda msg: (
                self.info_alert.show_message(msg),
                self.enable(),
            ),
        )

    def manage_friend_request(
        self, status: ty.Literal["ok", "cancel"], widget: FriendRequestWidget
    ) -> None:
        self.disable()
        if status == "ok":
            self.add_friend(widget)
        elif status == "cancel":
            self.delete_friend_request(widget)

    def add_friend(self, widget: FriendRequestWidget) -> None:
        self.network_client.add_friend(
            widget.user,
            callback=lambda: (
                self.remove(widget),
                self.friend_requests.remove(widget),
                self.parent.update(),
                self.enable(),
                Social.thread.__setattr__("_last_start", 0),
            ),
        )

    def delete_friend_request(self, widget: FriendRequestWidget) -> None:
        self.network_client.delete_friend_request(
            widget.user,
            callback=lambda: (
                self.remove(widget),
                self.friend_requests.remove(widget),
                self.parent.update(),
                self.enable(),
                Social.thread.__setattr__("_last_start", 0),
            ),
        )


class Social(WidgetsGroup):
    thread: Thread = ...

    def __init__(self, parent: Group, network_client: NetworkClient):
        resolution = Resolution.converter(os.environ["resolution"])
        font_size = int(os.environ["font_size"])
        icon_size = int(os.environ["icon_size"])

        super(Social, self).__init__(
            parent,
            x=lambda obj: resolution.width - obj.rect.width,
            y=0,
            width=int(resolution.width * 0.2),
            height=resolution.height,
            border_color=pg.Color("red"),
            border_width=5,
        )

        self.network_client = network_client
        self.friend_requests = FriendRequests(parent, network_client)

        self.user = UserWidget(
            self, x=0, y=0, user=network_client.user, icon_size=int(icon_size * 1.2)
        )
        self.line = Line(
            self,
            x=0,
            y=self.user.rect.bottom,
            width=self.rect.width,
            height=5,
            color=pg.Color("red"),
        )

        self.social_label = Label(
            self,
            x=5,
            y=self.line.rect.bottom + 5,
            text="Сообщество",
            color=pg.Color("red"),
            font=pg.font.Font(None, int(font_size * 0.8)),
        )
        self.add_friend_button = Button(
            self,
            x=self.social_label.rect.right + 10,
            y=self.social_label.rect.top,
            text=" + ",
            color=pg.Color("red"),
            font=pg.font.Font(None, int(font_size * 0.8)),
            padding=1,
            active_background=pg.Color("gray"),
            callback=lambda event: self.friend_requests.show(),
        )

        self.friends: list[FriendWidget] = []

        if self.thread is ...:
            self.__class__.thread = Thread(
                worker=self.load_friends,
                repetitive=True,
                timeout=10,
            )
            self.__class__.thread.run()

    def delete_friend(self, widget: FriendWidget) -> None:
        self.network_client.delete_friend(
            widget.user,
            callback=lambda: (
                widget.delete(),
                self.friend_requests.remove(widget),
                self.parent.update(),
                Social.thread.__setattr__("_last_start", 0),
            ),
        )

    def load_friends(self) -> None:
        font_size = int(os.environ["font_size"])
        icon_size = int(os.environ["icon_size"])

        self.network_client.update_user()

        logger.opt(colors=True).trace(
            f"Обновление списка друзей: <y>{self.network_client.user.friends}</y>"
        )
        friends = [
            self.network_client.get_user(uid)
            for uid in self.network_client.user.friends
        ]

        for friend in self.friends:
            friend.delete()
        self.friends.clear()

        y = self.social_label.rect.bottom + 10
        for user in friends:
            self.friends.append(
                FriendWidget(
                    self,
                    x=0,
                    y=y,
                    user=user,
                    font_size=int(font_size * 0.7),
                    delete_friend=self.delete_friend,
                )
            )
            y += self.friends[-1].rect.height

        self.parent.update()

        if self.network_client.user.friend_requests:
            logger.opt(colors=True).trace(
                "Обновление списка запросов в друзья: "
                f"<y>{self.network_client.user.friend_requests}</y>"
            )
            users = [
                self.network_client.get_user(uid)
                for uid in self.network_client.user.friend_requests
            ]

            for user in self.friend_requests.friend_requests:
                self.friend_requests.remove(user)
            self.friend_requests.friend_requests.clear()

            y = self.friend_requests.friend_requests_label.rect.bottom + 20
            x = 0
            for i, user in enumerate(users):
                self.friend_requests.friend_requests.append(
                    FriendRequestWidget(
                        self.friend_requests,
                        x=x,
                        y=y,
                        user=user,
                        icon_size=int(icon_size),
                        font_size=int(font_size),
                        callback=self.friend_requests.manage_friend_request,
                    ),
                )
                x += self.friend_requests.friend_requests[-1].rect.width
                if (i + 1) % 3 == 0:
                    x = 0
                    y += self.friend_requests.friend_requests[-1].rect.height

            self.add_friend_button.color = pg.Color("green")
            self.parent.update()
        else:
            self.add_friend_button.color = pg.Color("red")

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
    from network import User, NetworkClient, UserStatus
    from base.group import Group
    from base.types import CordFunction


class FriendDropMenu(DropMenu):
    def __init__(self, parent: UserWidget, can_invite: ty.Callable[[], True | False]):
        font_size = int(os.environ["font_size"])

        self.can_invite = can_invite

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

        self.send_invite_button = Button(
            self,
            x=0,
            y=self.delete_friend.rect.bottom,
            text="Пригласить в группу",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("black"),
            font=pg.font.Font(None, int(font_size * 0.6)),
        )

    def show(self) -> None:
        self.remove(self.send_invite_button)
        if self.can_invite():
            self.add(self.send_invite_button)
        self.parent.update()
        super(FriendDropMenu, self).show()


class UserWidget(WidgetsGroup):
    def __init__(
        self,
        parent: Group,
        x: int | CordFunction,
        y: int | CordFunction,
        user: User,
        icon_size: int | None = None,
        font_size: int | None = None,
        width: int | None = None,
    ):
        font_size = font_size or int(os.environ["font_size"])
        icon_size = icon_size or int(os.environ["icon_size"])

        self.user = user

        super(UserWidget, self).__init__(
            parent,
            x=x,
            y=y,
            width=width,
            padding=20,
        )

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

    def set_status(self, status: UserStatus) -> None:
        self.status.text = status.text
        self.status.color = status.color


class FriendWidget(UserWidget):
    def __init__(
        self,
        parent: Social,
        y: int | CordFunction,
        user: User,
    ):
        font_size = int(int(os.environ["font_size"]) * 0.7)

        self.social = parent

        super(FriendWidget, self).__init__(
            parent, x=0, y=y, user=user, font_size=font_size
        )

        self.drop_menu = FriendDropMenu(
            self, can_invite=lambda: parent.network_client.room is not ...
        )

    def delete(self):
        self.parent.remove(self)
        self.drop_menu.parent.remove(self.drop_menu)

    def handle_event(self, event: pg.event.Event) -> None:
        super(FriendWidget, self).handle_event(event)
        if event.type == ButtonClickEvent.type:
            if event.obj == self.drop_menu.delete_friend:
                self.social.network_client.delete_friend(uid=self.user.uid)
                self.drop_menu.hide()
            elif event.obj == self.drop_menu.send_invite_button:
                self.social.network_client.send_invite(
                    self.user,
                    fail_callback=lambda msg: self.social.info_alert.show_message(msg),
                )
                self.drop_menu.hide()


class FriendRequestWidget(UserWidget):
    def __init__(
        self,
        parent: FriendRequests,
        x: int | CordFunction,
        y: int | CordFunction,
        user: User,
        callback: ty.Callable[[ty.Literal["ok", "cancel"], FriendRequestWidget], ...],
    ):
        font_size = int(os.environ["font_size"])

        super(FriendRequestWidget, self).__init__(
            parent,
            x,
            y,
            user,
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
        self.username_input.input_line.text = ""
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
        if status == "ok":
            self.add_friend(widget)
        elif status == "cancel":
            self.delete_friend_request(widget)

    def add_friend(self, widget: FriendRequestWidget) -> None:
        self.remove(widget)
        self.friend_requests.remove(widget)
        self.parent.update()
        self.network_client.add_friend(uid=widget.user.uid)

    def delete_friend_request(self, widget: FriendRequestWidget) -> None:
        self.remove(widget),
        self.friend_requests.remove(widget)
        self.parent.update()
        self.network_client.delete_friend_request(user=widget.user)


class Social(WidgetsGroup):
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

        self.info_alert = InfoAlert(
            parent, parent_size=resolution, width=int(resolution.width * 0.5)
        )

        self.friends: list[FriendWidget] = []

        network_client.on_delete_friend(callback=self.on_delete_friend)
        network_client.on_add_friend(callback=self.on_add_friend)
        network_client.on_change_user_status(callback=self.on_change_user_status)
        network_client.on_friend_request(callback=self.on_friend_request)

        Thread(worker=self.load_friends).run()
        Thread(worker=self.load_friend_requests).run()

    def on_delete_friend(self, user: User) -> None:
        widget = [friend for friend in self.friends if friend.user.uid == user.uid][0]
        widget.delete()
        self.friends.remove(widget)
        self.remove(widget)
        self.parent.update()

    def on_add_friend(self, user: User) -> None:
        y = (
            self.social_label.rect.bottom
            if not len(self.friends)
            else self.friends[-1].rect.bottom
        ) + 10
        self.friends.append(FriendWidget(self, y=y, user=user))

    def on_change_user_status(self, user: User) -> None:
        if user.uid == self.network_client.user.uid:
            widget = self.user
        else:
            widget = [friend for friend in self.friends if friend.user.uid == user.uid]
            if not len(widget):
                return
            widget = widget[0]
        widget.set_status(user.status)

    def on_friend_request(self) -> None:
        self.load_friend_requests()

    def load_friends(self) -> None:
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

        for user in friends:
            self.friends.append(
                FriendWidget(
                    self,
                    y=lambda obj: (
                        self.social_label.get_global_rect().bottom
                        + 10
                        + (
                            sum(
                                widget.rect.height
                                for widget in self.friends[: self.friends.index(obj)]
                            )
                            if obj in self.friends
                            else 0
                        )
                    ),
                    user=user,
                )
            )

        self.parent.update()

    def load_friend_requests(self):
        self.network_client.update_user()

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
                    callback=self.friend_requests.manage_friend_request,
                ),
            )
            x += self.friend_requests.friend_requests[-1].rect.width
            if (i + 1) % 3 == 0:
                x = 0
                y += self.friend_requests.friend_requests[-1].rect.height

        self.parent.update()

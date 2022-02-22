"""

Интерфейсы взаимодействия с игровым сообществом.
Интерфейс списка друзей.
Интерфейс меню запросов в друзья.

Реализует функциональность системы друзей.

"""

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
    def __init__(
        self,
        parent: UserWidget,
        name: str = None,
        *,
        can_invite: ty.Callable[[], True | False] = False,
    ):
        """
        Выпадающее меню для виджета друга.
        :param parent: ...
        :param name: Название объекта.
        :param can_invite: Может ли пользователь пригласить этого друга в группу.
        """
        font_size = int(os.environ["font_size"])  # Размер текста
        font = os.environ.get("font")

        self.can_invite = can_invite

        super(FriendDropMenu, self).__init__(
            parent,
            name,
            background=pg.Color("gray"),
            border_color=pg.Color("red"),
            border_width=2,
        )

        self.delete_friend_button = Button(
            self,
            f"{name}-DeleteFriendButton",
            x=0,
            y=0,
            text="Удалить друга",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("black"),
            font=pg.font.Font(font, int(font_size * 0.6)),
        )

        self.send_invite_button = Button(
            self,
            f"{name}-SendInviteButton",
            x=0,
            y=self.delete_friend_button.rect.bottom,
            text="Пригласить в группу",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("black"),
            font=pg.font.Font(font, int(font_size * 0.6)),
        )

    def show(self) -> None:
        """
        Модифицирует базовый метод show.
        Отображает или скрывает кнопку "Пригласить в группу" если нужно.
        """
        self.remove(self.send_invite_button)
        if self.can_invite():
            self.add(self.send_invite_button)
        self.parent.update()

        super(FriendDropMenu, self).show()


class UserWidget(WidgetsGroup):
    def __init__(
        self,
        parent: Group | None,
        x: int | CordFunction,
        y: int | CordFunction,
        user: User,
        icon_size: int | None = None,
        font_size: int | None = None,
        width: int | None = None,
    ):
        """
        Виджет пользователя.
        :param parent: Объект к которому принадлежит виджет.
        :param x: Координата x.
        :param y: Координата y.
        :param user: Объект пользователя.
        :param icon_size: Размер иконки пользователя.
        :param font_size: Размер текста.
        :param width: Ширина виджета.
        """
        font_size = font_size or int(os.environ["font_size"])
        icon_size = icon_size or int(os.environ["icon_size"])
        font = os.environ.get("font")

        self.user = user

        super(UserWidget, self).__init__(
            parent,
            f"{user.username}-UserWidget",
            x=x,
            y=y,
            width=width,
            padding=20,
        )

        self.icon = Label(
            self,
            f"{user.username}-IconLabel",
            x=0,
            y=0,
            width=icon_size,
            height=icon_size,
            anchor=Anchor.center,
            sprite=load_image(
                f"icon_{user.icon}.png",
                namespace=os.environ["USER_ICONS_PATH"],
                size=(icon_size - 2, icon_size - 2),
            ),
        )

        # TODO: Ник может быть слишком длинным
        self.username = Label(
            self,
            f"{user.username}-UsernameLabel",
            x=self.icon.rect.right + 30,
            y=0,
            text=user.username,
            color=pg.Color("red"),
            font=pg.font.Font(font, font_size),
        )

        self.status = Label(
            self,
            f"{user.username}-StatusLabel",
            x=self.icon.rect.right + 30,
            y=self.username.rect.bottom + 5,
            text=user.status.text,
            color=pg.Color(user.status.color),
            font=pg.font.Font(font, int(font_size * 0.8)),
        )

    def set_status(self, status: UserStatus) -> None:
        """
        Изменяет статус пользователя.
        :param status: Новый статус.
        """
        logger.opt(colors=True).info(
            f"{self.user.username} <le>status</le>=<y>{status.text}</y>"
        )
        self.status.text = status.text
        self.status.color = status.color


class FriendWidget(UserWidget):
    def __init__(
        self,
        parent: Social,
        y: int | CordFunction,
        user: User,
    ):
        """
        Виджет друга.
        :param parent: Объект к которому принадлежит виджет.
        :param y: Координата y.
        :param user: Объект пользователя.
        """
        font_size = int(int(os.environ["font_size"]) * 0.7)

        self.social = parent

        super(FriendWidget, self).__init__(
            None, x=0, y=y, user=user, font_size=font_size
        )

        self.drop_menu: FriendDropMenu = ...

    def delete(self) -> None:
        """
        Удаляет виджет.
        """
        self.parent.remove(self)
        self.drop_menu.parent.remove(self.drop_menu)

    def handle_event(self, event: pg.event.Event) -> None:
        super(FriendWidget, self).handle_event(event)
        if event.type == ButtonClickEvent.type and self.drop_menu is not ...:
            # Обработка нажатий на кнопки в выпадающем меню
            if event.obj == self.drop_menu.delete_friend_button:
                self.social.network_client.delete_friend(uid=self.user.uid)
                self.drop_menu.hide()  # Скрываем меню
            elif event.obj == self.drop_menu.send_invite_button:
                self.social.network_client.send_invite(
                    self.user,
                    fail_callback=lambda msg: self.social.info_alert.show_message(msg),
                )
                self.drop_menu.hide()  # Скрываем меню


class FriendRequestWidget(UserWidget):
    def __init__(
        self,
        parent: FriendRequests,
        x: int | CordFunction,
        y: int | CordFunction,
        user: User,
        callback: ty.Callable[[ty.Literal["ok", "cancel"], FriendRequestWidget], ...],
    ):
        """
        Виджет запроса в друзья.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
        :param y: Координата y.
        :type y: Число или функция вычисляющая координату.
        :param user: Объект пользователя.
        :param callback: Обработчик нажатия на кнопки.
        :type callback: Функция, принимающая действие: "ok" или "cancel"
            и объект этого виджета.
        """
        font_size = int(os.environ["font_size"])
        font = os.environ.get("font")

        super(FriendRequestWidget, self).__init__(
            parent,
            x,
            y,
            user,
            width=(parent.rect.width - parent.padding * 2) // 3,
        )

        self.ok_button = Button(
            self,
            f"{user.username}-OkButton",
            x=0,
            y=self.icon.rect.bottom + 5,
            text=" + ",
            padding=1,
            color=pg.Color("red"),
            active_background=pg.Color("gray"),
            font=pg.font.Font(font, int(font_size * 0.8)),
            callback=lambda event: callback("ok", self),
        )

        self.cancel_button = Button(
            self,
            f"{user.username}-CancelButton",
            x=self.ok_button.rect.right + 5,
            y=self.icon.rect.bottom + 5,
            text=" - ",
            padding=1,
            color=pg.Color("red"),
            active_background=pg.Color("gray"),
            font=pg.font.Font(font, int(font_size * 0.8)),
            callback=lambda event: callback("cancel", self),
        )


class FriendRequests(Alert):
    def __init__(self, parent: Group, network_client: NetworkClient):
        """
        Меню запросов в друзья.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
        :param network_client: ...
        """
        resolution = Resolution.converter(os.environ["resolution"])
        font_size = int(os.environ["font_size"])
        font = os.environ.get("font")

        self.network_client = network_client

        super(FriendRequests, self).__init__(
            parent,
            "FriendRequestsAlert",
            parent_size=resolution,
            width=int(resolution.width * 0.5),
            height=int(resolution.height * 0.8),
            padding=20,
            background=pg.Color("black"),
            fogging=50,
        )

        self.info_alert = InfoAlert(
            parent,
            f"{self.name}-InfoAlert",
            parent_size=resolution,
            width=int(resolution.width * 0.5),
        )

        self.exit_button = Button(
            self,
            f"{self.name}-ExitButton",
            x=0,
            y=0,
            text=" X ",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(font, int(font_size * 0.7)),
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: self.hide(),
        )

        self.title = Label(
            self,
            f"{self.name}-TitleLabel",
            x=lambda obj: round(
                self.rect.width / 2 - obj.rect.width / 2 - self.padding * 2
            ),
            y=0,
            text="Добавить друзей",
            color=pg.Color("red"),
            font=pg.font.Font(font, font_size),
        )

        self.username_input = InputBox(
            self,
            f"{self.name}-InputBox",
            x=0,
            y=self.title.rect.bottom + 30,
            description="Имя пользователя",
            width=int(self.rect.width * 0.8) - self.padding * 2,
            padding=5,
            color=pg.Color("red"),
            font=pg.font.Font(font, font_size),
            inactive_border_color=pg.Color("red"),
            active_border_color=pg.Color("white"),
            border_width=5,
            text_filter=NickTextFilter,
        )

        self.find_friend_button = Button(
            self,
            f"{self.name}-FIndFriendButton",
            x=self.username_input.rect.right + 10,
            y=self.username_input.rect.top + self.username_input.input_line.rect.top,
            width=int(self.rect.width * 0.2) - self.padding,
            height=self.username_input.input_line.rect.height,
            text="Найти",
            padding=5,
            color=pg.Color("red"),
            font=pg.font.Font(font, font_size),
            active_background=pg.Color("gray"),
            border_color=pg.Color("red"),
            border_width=5,
            callback=lambda event: self.send_request(),
        )

        self.title = Label(
            self,
            f"{self.name}-TitleLabel",
            x=lambda obj: round(
                self.rect.width / 2 - obj.rect.width / 2 - self.padding * 2
            ),
            y=self.find_friend_button.rect.bottom + 10,
            text="Запросы в друзья",
            color=pg.Color("red"),
            font=pg.font.Font(font, font_size),
        )

        self.friend_requests = []

    def send_request(self) -> None:
        """
        Отправка запроса в друзья.
        """
        # Проверка наличия текста в поле ввода
        if not (username := self.username_input.input_line.text.strip()):
            self.username_input.input_line.active = True
            return

        self.disable()  # Временно отключаем работоспособность виджета
        self.username_input.input_line.text = ""  # Очищаем поле ввода
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
        )  # Отправляем запрос

    def manage_friend_request(
        self, status: ty.Literal["ok", "cancel"], widget: FriendRequestWidget
    ) -> None:
        """
        Принимает или отклоняет запрос дружбы.
        :param status: Вердикт пользователя.
        :param widget: Виджет запроса.
        """
        if status == "ok":
            self.add_friend(widget)
        elif status == "cancel":
            self.delete_friend_request(widget)

    def add_friend(self, widget: FriendRequestWidget) -> None:
        """
        Добавляет пользователя в друзья.
        :param widget: Виджет запроса.
        """
        # Удаляем виджет запроса в друзья
        self.remove(widget)
        self.friend_requests.remove(widget)
        self.parent.update()

        self.network_client.add_friend(uid=widget.user.uid)

    def delete_friend_request(self, widget: FriendRequestWidget) -> None:
        """
        Отклоняет запрос.
        :param widget: Виджет запроса.
        """
        # Удаляем виджет запроса в друзья
        self.remove(widget),
        self.friend_requests.remove(widget)
        self.parent.update()

        self.network_client.delete_friend_request(user=widget.user)


class Social(WidgetsGroup):
    def __init__(self, parent: Group, network_client: NetworkClient):
        """
        Виджет игрового сообщества.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
        :param network_client: ...
        """
        resolution = Resolution.converter(os.environ["resolution"])
        font_size = int(os.environ["font_size"])
        icon_size = int(os.environ["icon_size"])
        font = os.environ.get("FONT")

        super(Social, self).__init__(
            parent,
            "Social",
            x=lambda obj: resolution.width - obj.rect.width,
            y=0,
            width=int(resolution.width * 0.2),
            height=resolution.height,
            border_color=pg.Color("red"),
            border_width=5,
        )

        self.network_client = network_client
        self.friend_requests = FriendRequests(parent, network_client)

        self.user_widget = UserWidget(
            self, x=0, y=0, user=network_client.user, icon_size=int(icon_size * 1.2)
        )

        self.line = Line(
            self,
            x=0,
            y=self.user_widget.rect.bottom,
            width=self.rect.width,
            height=5,
            color=pg.Color("red"),
        )

        self.title = Label(
            self,
            f"{self.name}-TitleLabel",
            x=5,
            y=self.line.rect.bottom + 5,
            text="Сообщество",
            color=pg.Color("red"),
            font=pg.font.Font(font, int(font_size * 0.8)),
        )
        self.add_friend_button = Button(
            self,
            f"{self.name}-AddFriendButton",
            x=self.title.rect.right + 10,
            y=self.title.rect.top,
            text=" + ",
            color=pg.Color("red"),
            font=pg.font.Font(font, int(font_size * 0.8)),
            padding=1,
            active_background=pg.Color("gray"),
            callback=lambda event: self.friend_requests.show(),
        )

        self.info_alert = InfoAlert(
            parent,
            f"{self.name}-InfoAlert",
            parent_size=resolution,
            width=int(resolution.width * 0.5),
        )

        self.friends: list[FriendWidget] = []

        # Подключаем обработчики событий сообщества
        network_client.on_delete_friend(callback=self.on_delete_friend)
        network_client.on_add_friend(callback=self.on_add_friend)
        network_client.on_change_user_status(callback=self.on_change_user_status)
        network_client.on_friend_request(callback=self.on_friend_request)

        # Обновляем список друзей и запросов в отдельном потоке
        Thread(worker=self.load_friends).run()
        Thread(worker=self.load_friend_requests).run()

    def on_delete_friend(self, user: User) -> None:
        """
        Удаление друга.
        :param user: Пользователь.
        """
        # Получаем виджет друга
        widget = [friend for friend in self.friends if friend.user.uid == user.uid][0]
        # Удаляем виджет друга
        widget.delete()
        self.friends.remove(widget)

    def on_add_friend(self, user: User) -> None:
        """
        Добавление друга.
        :param user: Пользователь.
        """
        widget = FriendWidget(
            self,
            y=lambda obj: (
                self.title.get_global_rect().bottom
                + 10
                + (
                    sum(w.rect.height for w in self.friends[: self.friends.index(obj)])
                    if obj in self.friends
                    else 0
                )
            ),  # Динамическая координата Y
            user=user,
        )
        self.friends.append(widget)  # Добавляем виджет друга
        self.add(widget)
        widget.drop_menu = FriendDropMenu(
            widget,
            f"{widget.user.username}-DropMenu",
            can_invite=lambda: self.network_client.room is not ...,
        )

    def on_change_user_status(self, user: User) -> None:
        """
        Изменение статуса активности пользователя.
        :param user: Пользователь.
        """
        if user.uid == self.network_client.user.uid:  # Если это текущий пользователь
            widget = self.user_widget
        else:
            # Получаем виджеты пользователь по uid
            widget = [friend for friend in self.friends if friend.user.uid == user.uid]
            if not len(widget):
                return
            widget = widget[0]
        try:
            widget.set_status(user.status)
        except pg.error:
            pass

    def on_friend_request(self) -> None:
        """
        Запрос в друзья.
        """
        self.load_friend_requests()

    def load_friends(self) -> None:
        """
        Обновляет список друзей.
        """
        self.network_client.update_user()  # Обновляем данные о текущем пользователе
        self.user_widget.status.text = self.network_client.user.status.text
        self.user_widget.status.color = self.network_client.user.status.color

        logger.opt(colors=True).trace(
            f"Обновление списка друзей: <y>{self.network_client.user.friends}</y>"
        )
        friends = [
            self.network_client.get_user(uid)
            for uid in self.network_client.user.friends
        ]  # Получаем информацию о друзьях

        # Удаляем старые виджеты
        for friend in self.friends:
            friend.delete()
        self.friends.clear()

        # Добавляем новые виджеты

        self.friends = [
            FriendWidget(
                self,
                y=lambda obj: (
                    self.title.get_global_rect().bottom
                    + 10
                    + (
                        sum(
                            w.rect.height
                            for w in self.friends[: self.friends.index(obj)]
                        )
                        if obj in self.friends
                        else 0
                    )
                ),  # Динамическая координата Y
                user=user,
            )
            for user in friends
        ]
        self.add(*self.friends)

        for widget in self.friends:
            widget.drop_menu = FriendDropMenu(
                widget,
                f"{widget.user.username}-DropMenu",
                can_invite=lambda: self.network_client.room is not ...,
            )

    def load_friend_requests(self) -> None:
        """
        Обновляет список запросов в друзья.
        """
        self.network_client.update_user()  # Обновляем данные о текущем пользователе

        logger.opt(colors=True).trace(
            "Обновление списка запросов в друзья: "
            f"<y>{self.network_client.user.friend_requests}</y>"
        )
        users = [
            self.network_client.get_user(uid)
            for uid in self.network_client.user.friend_requests
        ]  # Получаем информацию о пользователях, отправивших запрос дружбы

        # Удаляем старые виджеты
        for user in self.friend_requests.friend_requests:
            self.friend_requests.remove(user)
        self.friend_requests.friend_requests.clear()

        # Добавляем новые виджеты
        y = self.friend_requests.title.rect.bottom + 20
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

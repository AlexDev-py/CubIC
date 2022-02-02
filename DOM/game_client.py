"""

Игровой клиента.

"""

from __future__ import annotations

import os
import typing as ty

import pygame as pg

from base import WidgetsGroup, Group, Label, Alert, Button, Anchor, Line
from database.field_types import Resolution
from settings_alert import Settings
from utils import load_image, FinishStatus, InfoAlert

if ty.TYPE_CHECKING:
    from network import NetworkClient
    from game.player import Player
    from game.item import Item


class EscMenu(Alert):
    def __init__(self, parent: GameClientScreen):
        resolution = Resolution.converter(os.environ["resolution"])
        font_size = int(os.environ["font_size"])
        font = os.environ.get("font")

        super(EscMenu, self).__init__(
            parent,
            "Menu",
            parent_size=resolution,
            width=int(resolution.width * 0.5),
            padding=20,
            background=pg.Color("black"),
            border_color=pg.Color("red"),
            border_width=3,
            fogging=100,
        )

        self.title = Label(
            self,
            f"{self.name}-TitleLabel",
            x=0,
            y=0,
            width=self.rect.width,
            text="Меню",
            color=pg.Color("red"),
            font=pg.font.Font(font, font_size),
            anchor=Anchor.center,
        )

        self.continue_button = Button(
            self,
            f"{self.name}-ContinueButton",
            x=lambda obj: self.rect.width / 2 - obj.rect.width / 2,
            y=self.title.rect.bottom + 10,
            width=int(self.rect.width * 0.8),
            text="Продолжить",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("gray"),
            font=pg.font.Font(font, font_size),
            anchor=Anchor.center,
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: self.hide(),
        )

        self.settings_button = Button(
            self,
            f"{self.name}-SettingsButton",
            x=lambda obj: self.rect.width / 2 - obj.rect.width / 2,
            y=self.continue_button.rect.bottom + 10,
            width=int(self.rect.width * 0.8),
            text="Настройки",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("gray"),
            font=pg.font.Font(font, font_size),
            anchor=Anchor.center,
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: self.settings.show(),
        )

        self.exit_button = Button(
            self,
            f"{self.name}-ExitButton",
            x=lambda obj: self.rect.width / 2 - obj.rect.width / 2,
            y=self.settings_button.rect.bottom + 10,
            width=int(self.rect.width * 0.8),
            text="Выйти",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("gray"),
            font=pg.font.Font(font, font_size),
            anchor=Anchor.center,
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: (
                parent.network_client.leave_lobby(),
                parent.__setattr__("finish_status", FinishStatus.exit_game),
                parent.terminate(),
            ),
        )

        self.settings = Settings(parent)


class Field(WidgetsGroup):
    def __init__(self, parent: GameClientScreen):
        resolution = Resolution.converter(os.environ["resolution"])

        height = width = min(resolution)
        self.network_client = parent.network_client

        self._field_image = pg.Surface((width, height))

        super(Field, self).__init__(
            parent,
            f"Field",
            x=lambda obj: resolution.width / 2 - obj.rect.width / 2,
            y=lambda obj: resolution.height / 2 - obj.rect.height / 2,
            width=width,
            height=height,
        )

        self._generate_location_map()

        self._label = Label(
            self,
            f"{self.name}-Label",
            x=0,
            y=0,
            width=width,
            height=height,
            sprite=self._field_image,
        )

        self.update_field()

    def _generate_location_map(self) -> None:
        self.floors: list[tuple[pg.Surface, pg.Rect]] = []
        self.walls: list[tuple[pg.Surface, pg.Rect]] = []

        block_width, block_height = (
            self.width / len(self.network_client.room.field[0]),
            self.height / len(self.network_client.room.field),
        )

        for i, (board_line, location_line) in enumerate(
            zip(self.network_client.room.field, self.network_client.room.location)
        ):
            y = block_height * i
            for j, (board_block, location_block) in enumerate(
                zip(board_line, location_line)
            ):
                x = block_width * j
                rect = pg.Rect(x, y, block_width, block_height * 1.3)
                if board_block is True:
                    self.floors.append(
                        (
                            load_image(
                                f"floor{location_block}.png",
                                namespace=os.path.join(
                                    os.environ["LOCATIONS_PATH"],
                                    self.network_client.room.location_name,
                                    "floors",
                                ),
                                size=(
                                    round(block_width) + 1,
                                    round(block_height * 1.3),
                                ),
                            ),
                            rect,
                        )
                    )
                else:
                    self.walls.append(
                        (
                            load_image(
                                f"wall{location_block}.png",
                                namespace=os.path.join(
                                    os.environ["LOCATIONS_PATH"],
                                    self.network_client.room.location_name,
                                    "walls",
                                ),
                                size=(
                                    round(block_width) + 1,
                                    round(block_height * 1.3),
                                ),
                            ),
                            rect,
                        )
                    )

    def update_field(self) -> None:
        image = pg.Surface(self._field_image.get_size())
        for floor_image, floor_rect in self.floors:
            image.blit(floor_image, floor_rect)
        for wall_image, wall_rect in self.walls:
            image.blit(wall_image, wall_rect)

        self.field_image = image

    @property
    def field_image(self) -> pg.Surface:
        return self._field_image

    @field_image.setter
    def field_image(self, value: pg.Surface):
        self._field_image = value
        if hasattr(self, "_label"):
            self._label.sprite = self._field_image


class StatWidget(WidgetsGroup):
    def __init__(self, name: str, x: int, y: int, icon: str, value: int):
        icon_size = int(int(os.environ["icon_size"]) * 0.5)
        font = os.environ.get("font")

        super(StatWidget, self).__init__(None, name, x=x, y=y, padding=5)

        self.icon = Label(
            self,
            f"{self.name}-IconLabel",
            x=0,
            y=0,
            width=icon_size,
            height=icon_size,
            sprite=load_image(
                icon,
                namespace=os.environ["UI_ICONS_PATH"],
                size=(icon_size, icon_size),
            ),
        )

        self.value = Label(
            self,
            f"{self.name}-ValueLabel",
            x=self.icon.rect.right + 5,
            y=lambda obj: self.icon.height / 2 - obj.rect.height / 2,
            text=str(value),
            color=pg.Color("red"),
            font=pg.font.Font(font, icon_size),
        )


class StatsWidget(WidgetsGroup):
    def __init__(self, parent: PlayerWidget):
        super(StatsWidget, self).__init__(
            parent,
            f"{parent.name}-StatsWidget",
            x=int(parent.width / 2),
            y=parent.line.rect.bottom + 5,
            width=int(parent.width / 2),
        )

        self.stats: list[StatWidget] = []

        self.hp = self.add_stat("hp.png", parent.player.character.hp)
        self.damage = self.add_stat("damage.png", parent.player.character.damage)
        self.attack_range = self.add_stat(
            "attack_range.png", parent.player.character.attack_range
        )
        self.armor = self.add_stat("armor.png", parent.player.character.armor)
        self.move_speed = self.add_stat(
            "move_speed.png", parent.player.character.move_speed
        )
        self.life_abduction = self.add_stat(
            "life_abduction.png", parent.player.character.life_abduction
        )

        self.add(*self.stats)

    def add_stat(self, icon: str, value: int) -> StatWidget:
        if not len(self.stats):
            x = y = 0
        else:
            y = self.stats[-1].rect.y
            x = self.stats[-1].rect.right
            if x + self.stats[-1].rect.width > self.rect.width:
                x = 0
                y += self.stats[-1].rect.height

        widget = StatWidget(f"{self.name}-{icon}-StatWidget", x, y, icon, value)
        self.stats.append(widget)
        return widget


class ItemWidget(WidgetsGroup):
    def __init__(self, name: str, x: int, y: int, item: Item | None):
        icon_size = int(int(os.environ["icon_size"]) * 0.9)

        self.item: Item | None = ...

        super(ItemWidget, self).__init__(None, name, x=x, y=y)

        self.item_icon = Label(
            self,
            f"{name}-ItemIconLabel",
            x=0,
            y=0,
            width=icon_size,
            height=icon_size,
            padding=2,
            text="",
        )

        self.border_icon = Label(
            self,
            f"{name}-ItemIconLabel",
            x=0,
            y=0,
            width=icon_size,
            height=icon_size,
            text="",
        )

        self.init(item)

    def init(self, item: Item | None):
        icon_size = int(int(os.environ["icon_size"]) * 0.9)

        self.item = item

        if item:
            self.item_icon.sprite = load_image(
                item.icon,
                namespace=os.environ["ITEMS_PATH"],
                size=(icon_size - self.item_icon.padding, None),
                save_ratio=True,
            )
            self.border_icon.sprite = load_image(
                f"lvl{item.lvl}.png",
                namespace=os.environ["ITEM_BORDERS_PATH"],
                size=(icon_size, None),
                save_ratio=True,
            )
        else:
            self.item_icon.sprite = load_image(
                "damage.png",
                namespace=os.environ["UI_ICONS_PATH"],
                size=(round(icon_size * 0.7 - self.item_icon.padding), None),
                save_ratio=True,
            )
            self.border_icon.sprite = load_image(
                f"lvl1.png",
                namespace=os.environ["ITEM_BORDERS_PATH"],
                size=(icon_size, None),
                save_ratio=True,
            )


class ItemsWidget(WidgetsGroup):
    def __init__(self, parent: PlayerWidget):
        super(ItemsWidget, self).__init__(
            parent,
            "ItemsWidget",
            x=0,
            y=parent.line.rect.bottom + 5,
            width=int(parent.width / 2),
        )

        self.items = []
        for item in parent.player.character.items:
            self.add_item(item)

        self.add(*self.items)

    def add_item(self, item: Item | None) -> ItemWidget:
        if not len(self.items):
            x = y = 0
        else:
            y = self.items[-1].rect.y
            x = self.items[-1].rect.right + 2
            if x + self.items[-1].rect.width > self.rect.width:
                x = 0
                y += self.items[-1].rect.height + 2

        widget = ItemWidget(f"{self.name}-{len(self.items) + 1}-ItemWidget", x, y, item)
        self.items.append(widget)
        return widget


class PlayerWidget(WidgetsGroup):
    def __init__(self, parent: PlayersMenu, player: Player, index: int = 0):
        font_size = int(os.environ["font_size"])
        icon_size = int(os.environ["icon_size"])
        font = os.environ.get("font")

        self.player = player

        y = 0 if index == 0 else parent.players[index - 1].get_global_rect().bottom + 10
        super(PlayerWidget, self).__init__(
            None,
            f"{player.username}-Widget",
            x=0,
            y=y,
            width=parent.rect.width - parent.padding * 2,
        )

        self.icon = Label(
            self,
            f"{self.name}-IconLabel",
            x=0,
            y=0,
            width=icon_size,
            height=icon_size,
            sprite=load_image(
                player.character.icon,
                namespace=os.environ["CHARACTERS_PATH"],
                size=(icon_size, icon_size),
            ),
        )

        self.username = Label(
            self,
            f"{self.name}-UsernameLabel",
            x=self.icon.rect.right + 5,
            y=lambda obj: self.icon.rect.height / 2 - obj.rect.height / 2,
            text=player.username,
            color=pg.Color("red"),
            font=pg.font.Font(font, font_size),
        )

        self.line = Line(
            self,
            x=0,
            y=self.icon.rect.bottom + 5,
            width=self.rect.width,
            height=2,
            color=pg.Color("red"),
        )

        self.items = ItemsWidget(self)
        self.stats = StatsWidget(self)

    def delete(self) -> None:
        self.parent.remove(self)


class PlayersMenu(WidgetsGroup):
    def __init__(self, parent: GameClientScreen):
        resolution = Resolution.converter(os.environ["resolution"])

        self.network_client = parent.network_client

        super(PlayersMenu, self).__init__(
            parent,
            "PlayersMenu",
            x=0,
            y=0,
            width=parent.field.rect.left,
            height=resolution.height,
            padding=5,
        )

        self.players: list[PlayerWidget] = []

        self.update_players()

    def update_players(self) -> None:
        for player in self.players:
            player.delete()

        self.players.clear()

        for i, player in enumerate(self.network_client.room.players):
            self.players.append(PlayerWidget(self, player, index=i))
        self.add(*self.players)


class ItemStand(WidgetsGroup):
    def __init__(self, name: str, x: int, y: int, width: int, item: Item):
        icon_size = int(int(os.environ["icon_size"]))
        self.item = item

        super(ItemStand, self).__init__(None, "name", x=x, y=y, width=width)

        self.stand = Label(
            self,
            f"{name}-StandLabel",
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2),
            y=round(icon_size / 2),
            width=lambda obj: obj.sprite.get_width(),
            height=lambda obj: obj.sprite.get_height(),
            sprite=load_image(
                "item_stand.png",
                namespace=os.environ["UI_ICONS_PATH"],
                size=(icon_size * 2, None),
                save_ratio=True,
            ),
        )

        self.item = Label(
            self,
            f"{name}-ItemLabel",
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2),
            y=0,
            width=icon_size,
            height=icon_size,
            sprite=load_image(
                item.icon,
                namespace=os.environ["ITEMS_PATH"],
                size=(icon_size, icon_size),
            ),
        )


class ShopMenu(WidgetsGroup):
    def __init__(self, parent: GameClientScreen):
        resolution = Resolution.converter(os.environ["resolution"])

        self.network_client = parent.network_client

        super(ShopMenu, self).__init__(
            parent,
            "ShopMenu",
            x=parent.field.rect.right,
            y=0,
            width=resolution.width - parent.field.rect.right,
            height=resolution.height,
            padding=5,
        )

        self.items = []
        for item in self.network_client.room.shop:
            self.add_item(item)

        self.add(*self.items)

    def add_item(self, item: Item | None) -> ItemStand:
        icon_size = int(int(os.environ["icon_size"]))

        in_line_count = len(self.network_client.room.players)
        if len(self.network_client.room.players) == 4:
            in_line_count = 3
        width = int((self.rect.width - self.padding * 2) / in_line_count)
        while width < icon_size * 2:
            in_line_count -= 1
            width = int((self.rect.width - self.padding * 2) / in_line_count)

        if not len(self.items):
            x = y = 0
        else:
            y = self.items[-1].rect.y
            x = self.items[-1].rect.right
            if x + self.items[-1].rect.width > self.rect.width:
                x = 0
                y += self.items[-1].rect.height + icon_size / 3

        widget = ItemStand(
            f"{self.name}-{len(self.items) + 1}-ItemWidget", x, y, width, item
        )
        self.items.append(widget)
        return widget


class GameClientScreen(Group):
    def __init__(self, network_client: NetworkClient = None):
        resolution = Resolution.converter(os.environ["resolution"])

        self.running = True
        self.finish_status = FinishStatus.close

        super(GameClientScreen, self).__init__(name="GameClientScreen")
        self.network_client = (
            self.network_client if hasattr(self, "network_client") else network_client
        )

        # Если выставлено максимально возможное разрешение, открываем окно в полный экран
        if resolution >= Resolution.converter(os.environ["MAX_RESOLUTION"]):
            self.screen = pg.display.set_mode(resolution, pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode(resolution)

        self.field = Field(self)
        self.players_menu = PlayersMenu(self)
        self.shop = ShopMenu(self)

        self.esc_menu = EscMenu(self)
        self.info_alert = InfoAlert(
            self,
            f"{self.name}-InfoAlert",
            parent_size=resolution,
            width=int(resolution.width * 0.7),
        )

        self.network_client.on_leaving_the_lobby(
            callback=lambda msg: (
                self.players_menu.update_players(),
                self.info_alert.show_message(msg),
            )
        )

    def exec(self) -> str:
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.terminate()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if self.esc_menu.parent.hidden:
                            self.esc_menu.show()
                        else:
                            self.esc_menu.settings.hide()
                            self.esc_menu.hide()
                self.handle_event(event)
            self.render()
        return self.finish_status

    def render(self) -> None:
        self.screen.fill("white")
        self.draw(self.screen)

        pg.display.flip()

    def terminate(self) -> None:
        self.running = False

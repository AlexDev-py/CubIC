"""

Игровой клиента.

"""

from __future__ import annotations

import os
import typing as ty

import pygame as pg

from base import WidgetsGroup, Group, Label, Alert, Button, Anchor, Line, Text
from base.events import ButtonClickEvent
from database.field_types import Resolution
from settings_alert import Settings
from utils import load_image, FinishStatus, InfoAlert, DropMenu

if ty.TYPE_CHECKING:
    from network import NetworkClient
    from game.player import Player
    from game.item import Item
    from base.types import CordFunction


class EscMenu(Alert):
    def __init__(self, parent: GameClientScreen):
        """
        Меню игрового клиента.
        Открывается по нажатию клавиши Escape.
        :param parent: ...
        """
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

        self.settings = Settings(parent)  # Подключаем виджет настроек


class ItemDropMenu(DropMenu):
    def __init__(self, parent: PlayerWidget, can_remove: True | False):
        """
        Выпадающее меню для предметов.
        :param parent: ...
        :param can_remove: Может ли пользователь продать предметы.
        """
        font_size = int(os.environ["font_size"])
        font = os.environ.get("font")

        super(ItemDropMenu, self).__init__(
            parent,
            f"{parent.name}-DropMenu",
            padding=10,
            background=pg.Color("gray"),
            border_color=pg.Color("red"),
            border_width=2,
        )

        self.item: Item = ...
        self.item_index: int = ...

        self.item_desc: ItemDescription = ...
        if can_remove:
            self.remove_button = Button(
                self,
                name=f"{self.name}-RemoveButton",
                x=0,
                y=lambda obj: (self.item_desc.rect.bottom + 10)
                if self.item_desc is not ...
                else 0,
                width=lambda obj: self.rect.width
                - self.padding * 2
                - self.border_width * 2,
                text="Продать",
                padding=5,
                color=pg.Color("red"),
                active_background=pg.Color("gray"),
                font=pg.font.Font(font, font_size),
                anchor=Anchor.center,
                border_color=pg.Color("red"),
                border_width=2,
                callback=lambda event: (
                    self.hide(),
                    parent.network_client.remove_item(self.item_index),
                ),
            )

    def init(self, item: Item, item_index: int) -> None:
        """
        Инициализация предмета.
        :param item: Предмет.
        :param item_index: Индекс предмета в инвентаре.
        """
        self.item = item
        self.item_index = item_index
        if self.item_desc is not ...:  # Удаляем старое описание
            self.remove(self.item_desc)
        self.item_desc = ItemDescription(
            self, f"{self.name}-ItemDesc", x=0, y=0, item=item, item_index=item_index
        )

    def handle_event(self, event: pg.event.Event) -> None:
        """
        Модифицируем базовый метод.
        Отключаем открытие меню по нажатию на виджет.
        :param event: ...
        """
        if not self.hidden:
            WidgetsGroup.handle_event(self, event)
        if event.type == pg.MOUSEBUTTONDOWN:
            # Скрываем виджет
            if event.button == pg.BUTTON_RIGHT:
                if self._widget.get_global_rect().collidepoint(event.pos):
                    return
            if hasattr(event, "pos"):
                if not self.hidden:
                    if not self.rect.collidepoint(event.pos):
                        self.hide()


class Field(WidgetsGroup):
    def __init__(self, parent: GameClientScreen):
        """
        Виджет поля.
        :param parent: ...
        """
        resolution = Resolution.converter(os.environ["resolution"])

        height = width = min(resolution)  # Размеры поля

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

        self._boss_image = load_image(
            "diablo.png",
            namespace=os.environ["BOSSES_PATH"],
            size=(None, round(self.block_height * 2)),
            save_ratio=True,
        )

        self._enemy_image = load_image(
            "mogus.png",
            namespace=os.environ["ENEMIES_PATH"],
            size=(None, round(self.block_height * 1.25)),
            save_ratio=True,
        )

        self.update_field()

    def _generate_location_map(self) -> None:
        """
        Создает картинку поля.
        """
        self.floors: list[tuple[pg.Surface, pg.Rect]] = []  # Элементы пола
        self.walls: list[list[tuple[pg.Surface, pg.Rect] | None]] = []  # Элементы стен

        self.block_width, self.block_height = (
            self.width / len(self.network_client.room.field[0]),
            self.height / len(self.network_client.room.field),
        )  # Размеры одного блока

        for i, (board_line, location_line) in enumerate(
            zip(self.network_client.room.field, self.network_client.room.location)
        ):
            walls_line: list[tuple[pg.Surface, pg.Rect] | None] = []
            y = self.block_height * i
            for j, (board_block, location_block) in enumerate(
                zip(board_line, location_line)
            ):
                x = self.block_width * j
                if board_block is True:  # Если блок - элемента пола
                    rect = pg.Rect(x, y, self.block_width, self.block_height)
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
                                    round(self.block_width) + 1,
                                    round(self.block_height * 1.3),
                                ),
                            ),
                            rect,
                        )
                    )
                    walls_line.append(None)
                else:  # Если блок - элемент стены
                    rect = pg.Rect(
                        x,
                        y - self.block_height * 0.3,
                        self.block_width,
                        self.block_height * 1.3,
                    )
                    walls_line.append(
                        (
                            load_image(
                                f"wall{location_block}.png",
                                namespace=os.path.join(
                                    os.environ["LOCATIONS_PATH"],
                                    self.network_client.room.location_name,
                                    "walls",
                                ),
                                size=(
                                    round(self.block_width) + 1,
                                    round(self.block_height * 1.3),
                                ),
                            ),
                            rect,
                        )
                    )
            self.walls.append(walls_line)

    def update_field(self) -> None:
        """
        Отображение игры.
        """
        image = pg.Surface(self._field_image.get_size())
        for floor_image, floor_rect in self.floors:
            image.blit(floor_image, floor_rect)

        boss_rect = pg.Rect(
            self.block_width * self.network_client.room.boss.pos[1]
            - self.block_width * 0.5,
            self.block_height * self.network_client.room.boss.pos[0] - self.block_width,
            self.block_width,
            self.block_height,
        )

        enemies: dict[tuple[int, int], tuple[pg.Surface, pg.Rect]] = {}
        for enemy in self.network_client.room.enemies:
            enemy_rect = pg.Rect(
                self.block_width * enemy.pos[1]
                - ((self._enemy_image.get_width() - self.block_width) / 2),
                self.block_height * enemy.pos[0] - self.block_width * 0.25,
                self.block_width,
                self.block_height,
            )
            enemies[tuple(enemy.pos)] = (self._enemy_image, enemy_rect)

        players: dict[tuple[int, int], tuple[pg.Surface, pg.Rect]] = {}
        for player in self.network_client.room.players:
            player_image = load_image(
                player.character.icon,
                namespace=os.environ["CHARACTERS_PATH"],
                size=(None, round(self.block_height * 1.5)),
                save_ratio=True,
            )
            player_rect = pg.Rect(
                self.block_width * player.character.pos[1]
                - ((player_image.get_width() - self.block_width) / 2),
                self.block_height * player.character.pos[0] - self.block_width * 0.5,
                self.block_width,
                self.block_height,
            )
            players[tuple(player.character.pos)] = (player_image, player_rect)

        for i, walls_line in enumerate(self.walls):
            for j, wall in enumerate(walls_line):
                if wall:
                    image.blit(*wall)
                j -= 1
                if enemy := enemies.get((i, j)):
                    image.blit(*enemy)
                if player := players.get((i, j)):
                    image.blit(*player)
                if tuple(self.network_client.room.boss.pos) == (i, j):
                    image.blit(self._boss_image, boss_rect)

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
    def __init__(self, name: str, x: int, y: int, icon: str, value: str):
        """
        Виджет характеристики.
        Иконка + значение.
        :param name: Название элемента.
        :param x: Координата x.
        :param y: Координата y.
        :param icon: Название файла с иконкой.
        :param value: Значение характеристики.
        """
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
            text=value,
            color=pg.Color("red"),
            font=pg.font.Font(font, icon_size),
        )


class StatsWidget(WidgetsGroup):
    def __init__(self, parent: PlayerWidget):
        """
        Виджет характеристик персонажа.
        :param parent: ...
        """
        super(StatsWidget, self).__init__(
            parent,
            f"{parent.name}-StatsWidget",
            x=int(parent.width / 2),
            y=parent.line.rect.bottom + 5,
            width=int(parent.width / 2),
        )

        self.stats: list[StatWidget] = []  # Характеристики персонажа

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
        self.coins = self.add_stat("coins.png", parent.player.character.coins)

        self.add(*self.stats)

    def add_stat(self, icon: str, value: int) -> StatWidget:
        """
        Добавление характеристики.
        Автоматически смещает характеристику на новую линию,
        если нехватает места для ее отображения.
        :param icon: Название файла с иконкой.
        :param value: Значение характеристики.
        :return: Виджет характеристики.
        """
        if not len(self.stats):  # Если это первая характеристика
            x = y = 0
        else:
            y = self.stats[-1].rect.y
            x = self.stats[-1].rect.right
            # Если не хватает места
            if x + self.stats[-1].rect.width > self.rect.width:
                x = 0
                y += self.stats[-1].rect.height

        widget = StatWidget(f"{self.name}-{icon}-StatWidget", x, y, icon, str(value))
        self.stats.append(widget)  # Добавляем в список
        return widget

    def update_stats(self, player: Player) -> None:
        """
        Обновляет характеристики.
        :param player: Экземпляр игрока.
        """
        # Перебор всех характеристик
        for stat in {
            "hp",
            "damage",
            "attack_range",
            "armor",
            "move_speed",
            "life_abduction",
            "coins",
        }:
            widget: StatWidget = self.__getattribute__(stat)
            # Если значение изменилось
            if widget.value.text != (
                value := str(player.character.__getattribute__(stat))
            ):
                widget.value.text = value


class ItemWidget(WidgetsGroup):
    def __init__(self, name: str, x: int, y: int, item: Item | None):
        """
        Виджет предмета в инвентаре.
        :param name: Название виджета.
        :param x: Координата x.
        :param y: Координата y.
        :param item: Предмет.
        """
        icon_size = int(int(os.environ["icon_size"]) * 0.9)

        self.item: Item | None = ...

        super(ItemWidget, self).__init__(None, name, x=x, y=y)

        self.item_icon = Label(
            self,
            f"{name}-ItemIconLabel",
            x=2,
            y=2,
            width=icon_size - 4,
            height=icon_size - 4,
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

    def init(self, item: Item | None) -> None:
        """
        Инициализирует предмет.
        :param item: Предмет.
        """
        icon_size = int(int(os.environ["icon_size"]) * 0.9)

        self.item = item

        self.item_icon.sprite = load_image(
            # Если слот пустой, ставим соответствующую иконку
            item.icon if item else "default.png",
            namespace=os.environ["ITEMS_PATH"],
            size=(icon_size - 4, None),
            save_ratio=True,
        )
        self.border_icon.sprite = load_image(
            # Если слот пустой, ставим рамку первого уровня
            f"lvl{item.lvl if item else 1}.png",
            namespace=os.environ["ITEM_BORDERS_PATH"],
            size=(icon_size, None),
            save_ratio=True,
        )


class ItemsWidget(WidgetsGroup):
    def __init__(self, parent: PlayerWidget):
        """
        Виджет инвентаря персонажа.
        :param parent: ...
        """
        super(ItemsWidget, self).__init__(
            parent,
            "ItemsWidget",
            x=0,
            y=parent.line.rect.bottom + 5,
            width=int(parent.width / 2),
        )

        self.items: list[ItemWidget] = []  # Слоты
        for item in parent.player.character.items:
            self.add_item(item)

        self.add(*self.items)

    def add_item(self, item: Item | None) -> ItemWidget:
        """
        Добавляет предмет в инвентарь.
        Автоматически смещает слот на новую линию,
        если нехватает места для его отображения.
        :param item: Предмет.
        :return: Виджет предмета.
        """
        if not len(self.items):  # Если это первый слот
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

    def update_items(self, player: Player) -> None:
        """
        Обновляет предметы.
        :param player: Экземпляр игрока.
        """
        for item_index, (item, item_widget) in enumerate(
            zip(player.character.items, self.items)
        ):
            # Если предмет изменился
            if (item.name if item else None) != (
                item_widget.item.name if item_widget.item else None
            ):
                item_widget.init(item)


class PlayerWidget(WidgetsGroup):
    def __init__(self, parent: PlayersMenu, player: Player, index: int = 0):
        """
        Виджет игрока.
        Объединяет информацию об игроке, его предметы и характеристики.
        :param parent: ...
        :param player: Экземпляр игрока.
        :param index: Индекс(для определения координаты Y).
        """
        font_size = int(os.environ["font_size"])
        icon_size = int(os.environ["icon_size"])
        font = os.environ.get("font")

        self.player = player
        self.network_client = parent.network_client

        # Определяем положение виджета
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
                size=(None, icon_size),
                save_ratio=True,
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
        )  # Линия - разделитель

        self.items = ItemsWidget(self)
        self.stats = StatsWidget(self)
        self.drop_menu: ItemDropMenu = ...

    def update_data(self, player: Player) -> None:
        """
        Обновляет данные об игроке.
        :param player: Новый экземпляр игрока.
        """
        self.player = player
        self.items.update_items(self.player)
        self.stats.update_stats(self.player)

    def handle_event(self, event: pg.event.Event) -> None:
        super(PlayerWidget, self).handle_event(event)
        if self.enabled:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_RIGHT:
                    # Открытие выпадающего меню предмета
                    if (
                        self.items.get_global_rect().collidepoint(event.pos)
                        and self.drop_menu is not ...
                    ):
                        for i, item_widget in enumerate(self.items.items):
                            if item_widget.item:
                                # Открытие при нажатии на предмет
                                if item_widget.get_global_rect().collidepoint(
                                    event.pos
                                ):
                                    self.drop_menu.init(item_widget.item, i)
                                    self.drop_menu.open(event.pos)
                                    self.drop_menu.update()
                                    break


class PlayersMenu(WidgetsGroup):
    def __init__(self, parent: GameClientScreen):
        """
        Виджет игроков.
        :param parent: ...
        """
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

        self.players: list[PlayerWidget] = []  # Список игроков

        self.update_players()

    def update_players(self) -> None:
        """
        Обновляет список игроков.
        """
        # Удаление старых виджетов
        self.parent.remove(*(widget.drop_menu for widget in self.players))
        self.remove(*self.players)

        self.players.clear()

        # Создание новых виджетов
        for i, player in enumerate(self.network_client.room.players):
            self.players.append(PlayerWidget(self, player, index=i))
        self.add(*self.players)

        # Создание выпадающих меню
        for widget in self.players:
            widget.drop_menu = ItemDropMenu(
                widget, can_remove=widget.player.uid == self.network_client.user.uid
            )

    def update_player(self, player: Player) -> None:
        """
        Обновление одного из игроков.
        :param player: Экземпляр игрока.
        """
        # Поиск по uid
        players = [p for p in self.players if p.player.uid == player.uid]
        players[0].update_data(player)


class ItemStand(WidgetsGroup):
    def __init__(self, name: str, x: int, y: int, width: int, item: Item):
        """
        Стэнд с предметом.
        :param name: Название виджета.
        :param x: Координата x.
        :param y: Координата y.
        :param width: Ширина виджета.
        :param item: Предмет.
        """
        icon_size = int(os.environ["icon_size"])

        self.item = item

        super(ItemStand, self).__init__(None, "name", x=x, y=y, width=width)

        self.stand = Label(
            self,
            f"{name}-StandLabel",
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2),
            y=round(icon_size / 3),
            width=lambda obj: obj.sprite.get_width(),
            height=lambda obj: obj.sprite.get_height(),
            sprite=load_image(
                f"stand{item.lvl if item else 1}.png",
                namespace=os.environ["ITEM_STANDS_PATH"],
                size=(icon_size * 2, None),
                save_ratio=True,
            ),
        )

        self.item_icon = Label(
            self,
            f"{name}-ItemIconLabel",
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2),
            y=0,
            width=icon_size,
            height=icon_size,
            sprite=(
                load_image(
                    item.icon,
                    namespace=os.environ["ITEMS_PATH"],
                    size=(icon_size, icon_size),
                )
                if item
                else None
            ),
            text="",
        )

    def sales(self) -> None:
        """
        Помечает предмет как проданный.
        """
        self.item_icon.sprite = None
        self.item = None


class ItemDescription(WidgetsGroup):
    def __init__(
        self,
        parent: WidgetsGroup,
        name: str,
        x: int | CordFunction,
        y: int | CordFunction,
        item: Item,
        item_index: int,
    ):
        """
        Описание предмета.
        Иконка, название, цена, характеристики.
        :param parent: ...
        :param name: Название виджета.
        :param x: Координата x.
        :param y: Координата y.
        :param item: Предмет.
        :param item_index: Индекс предмета в инвентаре или магазине.
        """
        font_size = int(os.environ["font_size"])
        icon_size = int(os.environ["icon_size"])
        font = os.environ.get("font")

        self.item = item
        self.item_index = item_index

        super(ItemDescription, self).__init__(parent, name, x=x, y=y)

        self.icon = Label(
            self,
            f"{self.name}-IconLabel",
            x=0,
            y=0,
            width=icon_size,
            height=icon_size,
            sprite=load_image(
                item.icon,
                namespace=os.environ["ITEMS_PATH"],
                size=(icon_size, icon_size),
            ),
        )

        # Если parent имеет ограниченную ширину, то используем Text
        self.name = (Text if parent.width else Label)(
            self,
            f"{self.name}-NameLabel",
            x=self.icon.rect.right + 5,
            y=lambda obj: self.icon.rect.height / 2 - obj.rect.height / 2,
            width=(
                (parent.rect.width - parent.padding * 2 - icon_size - 5)
                if parent.width
                else None
            ),
            text=item.name,
            color=pg.Color("red"),
            font=pg.font.Font(font, font_size),
            **dict(soft_split=True) if parent.width else {},
        )

        self.price_label = Label(
            self,
            f"{self.name}-PriceLabel",
            x=0,
            y=self.icon.rect.bottom + 5,
            text=f"Цена: {item.price}",
            color=pg.Color("red"),
            font=pg.font.Font(font, font_size),
        )
        self.price_icon_label = Label(
            self,
            f"{self.name}-CoinsIconLabel",
            x=self.price_label.rect.right,
            y=self.price_label.rect.top,
            width=lambda obj: obj.sprite.get_width(),
            height=lambda obj: obj.sprite.get_height(),
            sprite=load_image(
                "coins.png",
                namespace=os.environ["UI_ICONS_PATH"],
                size=(None, self.price_label.rect.height),
                save_ratio=True,
            ),
        )

        self.stats: list[StatWidget] = []  # Характеристики предмета

        for stat_name, stat_value in self.item.desc.items():
            if stat_name == "max_hp":
                stat_name = "hp"
            self.add_stat(f"{stat_name}.png", stat_value)

        self.add(*self.stats)

    def add_stat(self, icon: str, value: str) -> StatWidget:
        """
        Добавляет характеристику к предмету.
        Автоматически смещает характеристику на новую линию,
        если нехватает места для ее отображения.
        :param icon: Название файла с иконкой характеристики.
        :param value: Значение характеристики.
        :return: Виджет характеристики.
        """
        if not len(self.stats):  # Если это первая характеристика
            x = 0
            y = self.price_label.rect.bottom + 5
        else:
            y = self.stats[-1].rect.y
            x = self.stats[-1].rect.right
            if x + self.stats[-1].rect.width > self.rect.width:
                x = 0
                y += self.stats[-1].rect.height

        widget = StatWidget(f"{self.name}-{icon}-StatWidget", x, y, icon, value)
        self.stats.append(widget)
        return widget


class ShopMenu(WidgetsGroup):
    def __init__(self, parent: GameClientScreen):
        """
        Магазин.
        :param parent: ...
        """
        font_size = int(os.environ["font_size"])
        font = os.environ.get("font")
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

        self.items: list[ItemStand] = []  # Предметы
        for item in self.network_client.room.shop:
            self.add_item(item)

        self.add(*self.items)

        # Меню покупки предмета
        self.item_preview = WidgetsGroup(
            self,
            f"{self.name}-ItemPreview",
            x=0,
            y=lambda obj: round(self.rect.bottom - obj.rect.height),
            width=self.width - self.padding * 2,
            padding=10,
            hidden=True,
        )
        self.item_preview.disable()

        self.item_desc: ItemDescription = ...  # Описание выбранного предмета

        self.buy_button = Button(
            self.item_preview,
            name=f"{self.item_preview.name}-BuyButton",
            x=0,
            y=lambda obj: (self.item_desc.rect.bottom + 10)
            if self.item_desc is not ...
            else 0,
            width=self.item_preview.rect.width - self.item_preview.padding * 2,
            text="Купить",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("gray"),
            font=pg.font.Font(font, font_size),
            anchor=Anchor.center,
            border_color=pg.Color("red"),
            border_width=2,
        )

    def add_item(self, item: Item | None) -> ItemStand:
        """
        Добавляет предмет в магазин.
        Автоматически смещает предмет на новую линию,
        если нехватает места для его отображения.
        :param item:
        :return:
        """
        icon_size = int(int(os.environ["icon_size"]))

        # Кол-во предметов в строке
        in_line_count = len(self.network_client.room.players)
        if len(self.network_client.room.players) == 4:
            in_line_count = 3
        width = int((self.rect.width - self.padding * 2) / in_line_count)
        while width < icon_size * 2:
            in_line_count -= 1
            width = int((self.rect.width - self.padding * 2) / in_line_count)

        if not len(self.items):  # Если это первый предмет
            x = 0
            y = 20
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

    def handle_event(self, event: pg.event.Event) -> None:
        super(ShopMenu, self).handle_event(event)
        if self.enabled:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_LEFT:
                    if self.get_global_rect().collidepoint(event.pos):
                        for i, item in enumerate(self.items):
                            # Выбор предмета
                            if item.get_global_rect().collidepoint(event.pos):
                                if item.item:  # Если предмет еще не продан
                                    # Удаляем старое описание предмета
                                    if self.item_desc is not ...:
                                        self.item_preview.remove(self.item_desc)
                                    # Создаем новое описание предмета
                                    self.item_desc = ItemDescription(
                                        self.item_preview,
                                        f"{self.item_preview.name}-{i}-ItemDescription",
                                        x=0,
                                        y=0,
                                        item=item.item,
                                        item_index=i,
                                    )
                                    self.item_preview.enable()
                                    self.item_preview.show()
                                else:
                                    self.item_preview.disable()
                                    self.item_preview.hide()
                                self.item_preview.update()
                                break


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
        self.network_client.on_buying_an_item(
            callback=lambda item_index, player: (
                self.shop.items[item_index].sales(),
                self.players_menu.update_player(player),
                (
                    (self.shop.item_preview.hide(), self.shop.item_preview.disable())
                    if self.shop.item_desc is not ...
                    and self.shop.item_desc.item_index == item_index
                    else ...
                ),
            )
        )
        self.network_client.on_removing_an_item(
            callback=lambda player: self.players_menu.update_player(player)
        )

    def exec(self) -> str:
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.terminate()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        # Обработка открытия / закрытия меню
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

    def handle_event(self, event: pg.event.Event) -> None:
        super(GameClientScreen, self).handle_event(event)
        if self.enabled:
            if event.type == ButtonClickEvent.type:
                # Кнопка покупки предмета
                if event.obj == self.shop.buy_button:
                    if self.shop.item_desc is not ...:
                        self.network_client.buy_item(
                            self.shop.item_desc.item_index,
                            fail_callback=lambda msg: self.info_alert.show_message(msg),
                        )

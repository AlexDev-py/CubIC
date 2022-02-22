from __future__ import annotations

import os
import typing as ty
import webbrowser

import pygame as pg

from base import Button, Alert, Label, Anchor, WidgetsGroup
from database.field_types import Resolution
from utils import load_image

if ty.TYPE_CHECKING:
    from base import Group


class MemberWidget(WidgetsGroup):
    def __init__(
        self,
        parent: AppInfoAlert,
        y: int,
        role: str,
        name: str,
        site: str | None = None,
    ):
        font_size = int(os.environ.get("font_size"))
        font = os.environ.get("font")

        super(MemberWidget, self).__init__(
            parent,
            f"{parent.name}-{name}-MemberWidget",
            x=0,
            y=y,
        )

        self.name_button = Button(
            self,
            f"{self.name}-NameButton",
            x=0,
            y=0,
            text=name,
            color=(pg.Color("#f0ce69") if site else pg.Color("white")),
            font=pg.font.Font(font, font_size),
            callback=lambda event: (webbrowser.open_new_tab(site) if site else ...),
        )

        self.role_label = Label(
            self,
            f"{self.name}-RoleLabel",
            x=self.name_button.rect.right,
            y=0,
            text=f" - {role}",
            font=pg.font.Font(font, font_size),
        )


class AppInfoAlert(Alert):
    def __init__(self, parent: Group):
        resolution = Resolution.converter(os.environ["resolution"])
        font_size = int(os.environ.get("font_size"))
        font = os.environ.get("font")
        icon_size = int(os.environ["icon_size"])

        super(AppInfoAlert, self).__init__(
            parent,
            name="AppInfoAlert",
            parent_size=resolution,
            width=round(resolution.width * 0.7),
            height=round(resolution.height * 0.7),
            padding=20,
            background=pg.Color("#122321"),
            border_color=pg.Color("#b9a66d"),
            border_width=3,
        )

        self.title = Label(
            self,
            f"{self.name}-TitleLabel",
            x=lambda obj: round(
                (self.rect.width - self.padding * 2) / 2 - obj.rect.width / 2
            ),
            y=0,
            width=self.rect.width,
            text="Об игре",
            font=pg.font.Font(font, font_size),
            anchor=Anchor.center,
        )

        self.icon_label = Label(
            self,
            name=f"{self.name}-IconLabel",
            x=0,
            y=self.title.rect.bottom + 10,
            width=icon_size * 2,
            height=icon_size * 2,
            sprite=load_image("icon.png", size=(icon_size * 2, None), save_ratio=True),
        )

        self.name_label = Label(
            self,
            f"{self.name}-NameLabel",
            x=self.icon_label.rect.right + 20,
            y=lambda obj: 0,
            text="Dungeon of Masters",
            color=pg.Color("#b9a66d"),
            font=pg.font.Font(font, font_size),
        )
        self.version_label = Label(
            self,
            f"{self.name}-VersionLabel",
            x=self.icon_label.rect.right + 20,
            y=lambda obj: 0,
            text=f"Версия: {os.environ['VERSION']}",
            font=pg.font.Font(font, font_size),
        )
        block_height = self.name_label.rect.h + self.version_label.rect.h + 5
        self.name_label.y = lambda obj: self.icon_label.rect.y + round(
            self.icon_label.rect.h / 2 - block_height / 2
        )
        self.version_label.y = lambda obj: self.name_label.rect.bottom + 5

        self.alex_dev = MemberWidget(
            self,
            self.icon_label.rect.bottom + 30,
            "Программист",
            'Алексей "AlexDev"',
            "https://github.com/AlexDev-py",
        )
        self.victory05 = MemberWidget(
            self,
            self.alex_dev.rect.bottom + 10,
            "Программист",
            'Александр "VIctory05"',
            "https://github.com/VIctory05",
        )
        self.qvert = MemberWidget(
            self,
            self.victory05.rect.bottom + 10,
            "Программист",
            'Глеб "Qvert"',
            "https://github.com/Qvert",
        )
        self.konan = MemberWidget(
            self,
            self.qvert.rect.bottom + 10,
            "Дизайнер",
            'Артур "konan"',
            "https://discord.com/users/384262096839376898",
        )
        self.wyvverna = MemberWidget(
            self,
            self.konan.rect.bottom + 10,
            "Гейм дизайнер",
            'Илья "Wyvverna"',
            "https://discord.com/users/800106614383575050",
        )

        self.project_link_button = Button(
            self,
            f"{self.name}-ProjectLinkButton",
            x=0,
            y=self.wyvverna.rect.bottom + 30,
            text="Страница проекта",
            color=pg.Color("#f0ce69"),
            font=pg.font.Font(font, font_size),
            callback=lambda event: webbrowser.open_new_tab(
                "https://github.com/AlexDev-py/DOM"
            ),
        )

        self.continue_button = Button(
            self,
            x=lambda obj: round(
                (self.rect.width - self.padding * 2) / 2 - obj.rect.width / 2
            ),
            y=lambda obj: (self.rect.height - self.padding * 2 - self.border_width * 2)
            - obj.rect.height,
            text="Закрыть",
            padding=5,
            active_background=pg.Color(222, 222, 222, 100),
            font=pg.font.Font(font, font_size),
            border_width=2,
            callback=lambda event: self.hide(),
        )

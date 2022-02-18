from __future__ import annotations

import os
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass

items: dict[int, list[Item]] = {}


@dataclass
class Item(object):
    name: str
    lvl: int
    count: str
    price: int
    group: str | None
    icon: str
    description: dict[str, str]

    @classmethod
    def load(cls, file_path: str) -> Item | None:
        try:
            tree = ElementTree.parse(file_path)
            data = tree.getroot()

            name = data.attrib["name"]
            lvl = int(data.attrib["lvl"])
            count = data.attrib["count"]
            price = int(data.attrib["price"] or 0)
            group = data.attrib.get("group") or None
            icon = data.attrib["icon"]

            description = {}
            for attrib in data.find("desc"):
                description[attrib.tag] = attrib.text

            return Item(name, lvl, count, price, group, icon, description)

        except Exception:
            print(f"error on loading {file_path}")

    def to_dict(self) -> dict:
        return dict(
            name=self.name,
            lvl=self.lvl,
            price=self.price,
            icon=self.icon,
            desc=self.description,
        )


if len(items) == 0:
    for root, _, files in os.walk(r"game/items"):
        for file_name in files:
            if file_name.endswith(".item"):
                if item := Item.load(os.path.join(root, file_name)):
                    if item.lvl not in items:
                        items[item.lvl] = []
                    if item.name not in items[item.lvl]:
                        items[item.lvl].append(item)

from dataclasses import dataclass


@dataclass
class Item:
    name: str
    lvl: int
    price: int
    icon: str
    desc: dict[str, str]

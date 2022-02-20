from dataclasses import dataclass


@dataclass
class Boss:
    name: str
    hp: int
    pos: list[int, int]
    desc: list[dict]
    icon: str

from dataclasses import dataclass


@dataclass
class Boss:
    name: str
    hp: int
    pos: tuple[int, int]
    desc: list[dict]

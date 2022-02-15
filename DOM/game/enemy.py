from dataclasses import dataclass


@dataclass
class Enemy:
    eid: int
    name: str
    hp: int
    damage: int
    attack_range: int
    reward: int
    pos: tuple[int, int]

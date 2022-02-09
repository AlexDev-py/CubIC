from dataclasses import dataclass


@dataclass
class Enemy:
    name: str
    hp: int
    damage: int
    attack_range: int
    reward: int
    pos: tuple[int, int]

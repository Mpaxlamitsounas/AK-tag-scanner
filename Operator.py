from dataclasses import dataclass


@dataclass(frozen=True)
class Operator:
    name: str
    tags: frozenset[str]
    rarity: int
    code_name: str

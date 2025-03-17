from dataclasses import dataclass


@dataclass(frozen=True)
class Operator:
    code_name: str
    name: str
    tags: frozenset[str]
    rarity: int


@dataclass(frozen=True)
class RecruitResult:
    tags: frozenset[str]
    operators: frozenset[Operator]
    rarity: int
    operator_rarities: dict[int, int]

    def get_sorted_operators(self) -> list[Operator]:
        return sorted(self.operators, key=lambda x: (-x.rarity, x.name))


@dataclass
class Config:  # filled with default values
    data_dir_path: str = "data/"
    allow_robots: bool = True
    automatically_select_4stars: bool = True

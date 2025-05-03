from dataclasses import dataclass, field

import orjson


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

    def read_config(self):
        try:
            with open("./config.json", "rb") as file:
                config = Config(**orjson.loads(file.read()))
                self.data_dir_path = config.data_dir_path
                self.allow_robots = config.allow_robots
                self.automatically_select_4stars = config.automatically_select_4stars

        except FileNotFoundError:
            self.write_default_config()

    def write_default_config(self):
        with open("./config.json", "wb") as file:
            file.write(orjson.dumps(vars(self), option=orjson.OPT_INDENT_2))


@dataclass
class Data:
    cached_ETag: str = ""
    recruitable_operators: frozenset[Operator] = frozenset()
    recruitment_tags: frozenset[str] = frozenset()
    cased_recruitment_tag_lookup: dict[str, str] = field(default_factory=dict)
    tag_results: dict[str, frozenset[Operator]] = field(default_factory=dict)

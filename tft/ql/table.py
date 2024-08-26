from abc import abstractmethod
from typing import Iterable, override
import attrs
import tft.ql.expr as ql
from tft.ql.util import avg_place
from tft.queries.champs import get_champ_name_map
from tft.queries.items import get_item_name_map

@attrs.define
class Field:
    name: str = attrs.field()
    query: ql.BaseQuery = attrs.field()
    length: int = attrs.field()

    def __attrs_post_init__(self):
        # Self length based on field name.
        self.length = max(len(self.name), self.length)

    @abstractmethod
    def get(self, source: dict) -> str:
        raise NotImplementedError("render() must be implemented!")

@attrs.define
class ItemNameField(Field):
    """Used to print the name of an item. Will auto convert to the
    readable item name."""
    length: int = attrs.field(default=20)

    def coerce_item_name(self, name_or_uid: str) -> str:
        item_name_map = get_item_name_map()
        if name_or_uid not in item_name_map:
            return name_or_uid
        return item_name_map[name_or_uid]

    @override
    def get(self, source: dict) -> str:
        return f"{self.query.unary(self.coerce_item_name).eval(source):{self.length}}"
    

@attrs.define
class ChampionNameField(Field):
    """Used to print a champion name. Will auto convert to the
    readable champion name."""
    length: int = attrs.field(default=20)

    def coerce_champ_name(self, name_or_uid: str) -> str:
        champ_name_map = get_champ_name_map()
        if name_or_uid not in champ_name_map:
            return name_or_uid
        return champ_name_map[name_or_uid]

    @override
    def get(self, source: dict) -> str:
        return f"{self.query.unary(self.coerce_champ_name).eval(source):{self.length}}"

@attrs.define
class GamesPlayedField(Field):
    """Used to print games played from a placement count."""
    length: int = attrs.field(default=8)

    @override
    def get(self, source: dict) -> str:
        return f"{self.query.unary(sum).eval(source):{self.length}}"

@attrs.define
class AvgPlaceField(Field):
    """Used to print the average placement from a placement count."""
    length: int = attrs.field(default=5)
    decimals: int = attrs.field(default=2)

    @override
    def get(self, source: dict) -> str:
        return f"{self.query.unary(avg_place).eval(source):{self.length}.{self.decimals}f}"

@attrs.define
class Table:
    fields: list[Field] = attrs.field()
    delim: str = attrs.field(default=' | ')

    def print(self, rows: Iterable) -> None:
        header = self.delim.join([f"{field.name:{field.length}}" for field in self.fields])
        print("-" * len(header))
        print(header)
        print("-" * len(header))
        for row in rows:
            print(self.delim.join([field.get(row) for field in self.fields]))
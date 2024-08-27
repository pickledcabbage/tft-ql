from abc import abstractmethod
from typing import Iterable, override
import attrs
import tft.ql.expr as ql
from tft.ql.util import avg_place
from tft.queries.champs import get_champ_name_map
from tft.queries.items import get_item_name_map
from tft.queries.traits import get_trait_name_map

@attrs.define
class Field:
    name: str = attrs.field()
    query: ql.BaseQuery = attrs.field()
    length: int = attrs.field()

    def __attrs_post_init__(self):
        # Set length based on field name.
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
    length: int = attrs.field(default=15)

    def coerce_champ_name(self, name_or_uid: str) -> str:
        champ_name_map = get_champ_name_map()
        if name_or_uid not in champ_name_map:
            return name_or_uid
        return champ_name_map[name_or_uid]

    @override
    def get(self, source: dict) -> str:
        return f"{self.query.unary(self.coerce_champ_name).eval(source):{self.length}}"

@attrs.define
class ChampionListField(Field):
    """Used to print a list of champions. Will auto convert to 
    readable champion names."""
    length: int = attrs.field(default=90)
    delim: str = attrs.field(default=', ')

    @override
    def get(self, source: dict) -> str:
        # Just to use coerce. We should move this out.
        field = ChampionNameField('test', ql.query())
        names = [field.coerce_champ_name(name) for name in self.query.eval(source)]
        names_string = ', '.join(names)
        if len(names_string) > self.length:
            names_string = names_string[:self.length-3] + '...'
        return f"{names_string:{self.length}}"

@attrs.define
class GamesPlayedField(Field):
    """Used to print games played. Can take a placement count or a number."""
    length: int = attrs.field(default=8)

    def coerce_games_played(self, places) -> int:
        if isinstance(places, list):
            return sum(places)
        return places

    @override
    def get(self, source: dict) -> str:
        return f"{self.query.unary(self.coerce_games_played).eval(source):{self.length}}"

@attrs.define
class AvgPlaceField(Field):
    """Used to print the average placement. Can take a placement count or a number."""
    length: int = attrs.field(default=5)
    decimals: int = attrs.field(default=2)

    def coerce_avg_place(self, places) -> float:
        if isinstance(places, list):
            return avg_place(places)
        return places

    @override
    def get(self, source: dict) -> str:
        return f"{self.query.unary(self.coerce_avg_place).eval(source):{self.length}.{self.decimals}f}"

@attrs.define
class TraitField(Field):
    """Used to print out a trait name."""
    length: int = attrs.field(default=15)

    def coerce_trait_name(self, name_or_uid: str) -> str:
        trait_name_map = get_trait_name_map()
        if name_or_uid in trait_name_map:
            return trait_name_map[name_or_uid]
        return name_or_uid

    @override
    def get(self, source: dict) -> str:
        # Trait names are already readable.
        return f"{self.query.eval(source):{self.length}}"

@attrs.define
class CostField(Field):
    length: int = attrs.field(default=3)
    
    @override
    def get(self, source: dict) -> str:
        # Trait names are already readable.
        return f"{self.query.eval(source):{self.length}}"

@attrs.define
class CompClusterField(Field):
    length: int = attrs.field(default=3)

    @override
    def get(self, source: dict) -> str:
        return f"{self.query.eval(source):{self.length}}"

@attrs.define
class StaticField(Field):
    value: str = attrs.field()

    @override
    def get(self, source: dict) -> str:
        return f"{self.value:{self.length}}"

@attrs.define
class Table:
    fields: list[Field] = attrs.field()
    delim: str = attrs.field(default=' | ')
    header: bool = attrs.field(default=True)

    def print(self, rows: Iterable) -> None:
        header = self.delim.join([f"{field.name:{field.length}}" for field in self.fields])
        if self.header:
            print("-" * len(header))
            print(header)
            print("-" * len(header))
        for row in rows:
            print(self.delim.join([field.get(row) for field in self.fields]))
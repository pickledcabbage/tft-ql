# Contains a set of classes to easily create tables to render in a text format.

from abc import abstractmethod
from typing import Iterable, override
import attrs
import tft.ql.expr as ql
from tft.ql.util import avg_place
from tft.queries.augs import get_aug_name_map
from tft.queries.champs import get_champ_name_map
from tft.queries.items import get_item_name_map
from tft.queries.traits import get_trait_name_map
from tft.ql.coerce import *

def adjust_field_to_size(s, length):
    """
    If a field is longer than its length, perform shortening.
    """
    if len(s) > length:
        return s[:length-3] + "..."
    return s

@attrs.define
class Field:
    """
    A base field class which has its own associated query and field length.
    """
    name: str = attrs.field()
    query: ql.BaseQuery = attrs.field()
    length: int = attrs.field()

    def __attrs_post_init__(self):
        # Set length based on field name.
        self.length = max(len(self.name), self.length)

    def _get(self, source: dict) -> str:
        val = self.query.eval(source)
        return f"{val:{self.length}}"
    
    def get(self, source: dict) -> str:
        return adjust_field_to_size(self._get(source), self.length)

@attrs.define
class ItemNameField(Field):
    """Used to print the name of an item. Will auto convert to the
    readable item name."""
    length: int = attrs.field(default=20)

    @override
    def _get(self, source: dict) -> str:
        return f"{self.query.unary(coerce_item_name).eval(source):{self.length}}"

@attrs.define
class ItemListField(Field):
    """
    Used to print a list of items.
    """
    length: int = attrs.field(default=80)
    delim: str = attrs.field(default=', ')
    same_length: int | None = attrs.field(default=None)

    @override
    def _get(self, source: dict) -> str:
        names = [coerce_item_name(name) if self.same_length is None else f"{coerce_item_name(name):{self.same_length}}" for name in self.query.eval(source)]
        names_string = self.delim.join(names)
        return f"{names_string:{self.length}}"
    

@attrs.define
class ChampionNameField(Field):
    """Used to print a champion name. Will auto convert to the
    readable champion name."""
    length: int = attrs.field(default=15)

    @override
    def _get(self, source: dict) -> str:
        return f"{self.query.unary(coerce_champ_name).eval(source):{self.length}}"

@attrs.define
class ChampionListField(Field):
    """Used to print a list of champions. Will auto convert to 
    readable champion names."""
    length: int = attrs.field(default=90)
    delim: str = attrs.field(default=', ')
    stars: ql.BaseQuery | None = attrs.field(default=None)

    def champ_name_with_stars(self, champ_id, stars) -> str:
        
        name = coerce_champ_name(champ_id)
        if champ_id in stars:
            return name + "***"
        return name

    @override
    def _get(self, source: dict) -> str:
        stars = self.stars.unary(set).eval(source) if self.stars is not None else set()
        # Just to use coerce. We should move this out.
        names = [self.champ_name_with_stars(name, stars) for name in self.query.eval(source)]
        names_string = self.delim.join(names)
        return f"{names_string:{self.length}}"

@attrs.define
class GamesPlayedField(Field):
    """Used to print games played. Can take a placement count or a number."""
    length: int = attrs.field(default=8)

    @override
    def _get(self, source: dict) -> str:
        return f"{self.query.unary(coerce_games_played).eval(source):{self.length}}"

@attrs.define
class AvgPlaceField(Field):
    """Used to print the average placement. Can take a placement count or a number."""
    length: int = attrs.field(default=5)
    decimals: int = attrs.field(default=2)

    @override
    def _get(self, source: dict) -> str:
        return f"{self.query.unary(coerce_avg_place).eval(source):{self.length}.{self.decimals}f}"

@attrs.define
class TraitField(Field):
    """Used to print out a trait name."""
    length: int = attrs.field(default=15)

    @override
    def _get(self, source: dict) -> str:
        return f"{self.query.unary(coerce_trait_name).eval(source):{self.length}}"

@attrs.define
class AugmentField(Field):
    """Used to print out an augment name."""
    length: int = attrs.field(default=20)
    
    @override
    def _get(self, source: dict) -> str:
        return f"{self.query.unary(coerce_augment_name).eval(source):{self.length}}"


@attrs.define
class CostField(Field):
    length: int = attrs.field(default=3)
    
    @override
    def _get(self, source: dict) -> str:
        # Trait names are already readable.
        return f"{self.query.eval(source):{self.length}}"

@attrs.define
class CompClusterField(Field):
    length: int = attrs.field(default=6)

    @override
    def _get(self, source: dict) -> str:
        return f"{self.query.eval(source):{self.length}}"

@attrs.define
class CompNameField(Field):
    length: int = attrs.field(default=20)

    @override
    def _get(self, source: dict) -> str:
        output = []
        mapping_order = [get_aug_name_map(), get_trait_name_map(), get_champ_name_map()]
        name_list = self.query.eval(source)
        for mapping in mapping_order:
            for item in name_list:
                if item['name'] in mapping:
                    output.append(mapping[item['name']])
        return f"{' '.join(output):{self.length}}"

@attrs.define
class StaticField(Field):
    value: str = attrs.field()

    @override
    def _get(self, source: dict) -> str:
        return f"{self.value:{self.length}}"

@attrs.define
class PercentField(Field):
    length: int = attrs.field(default=5)

    @override
    def _get(self, source: dict) -> str:
        return f"{self.query.eval(source) * 100:5.2f}"

@attrs.define
class Table:
    fields: list[Field] = attrs.field()
    delim: str = attrs.field(default=' | ')
    header: bool = attrs.field(default=True)

    def render(self, rows: Iterable) -> str:
        output = ''
        header = self.delim.join([f"{field.name:{field.length}}" for field in self.fields])
        if self.header:
            output += "-" * len(header) + "\n"
            output += header + "\n"
            output += "-" * len(header) + "\n"
        for row in rows:
            output += self.delim.join([field.get(row) for field in self.fields]) + "\n"
        return output

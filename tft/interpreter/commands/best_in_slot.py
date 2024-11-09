import tft.ql.expr as ql
import tft.client.meta as meta

from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.ql.table import AvgPlaceField, GamesPlayedField, ItemNameField, Table
from tft.ql.util import avg_place, count_match_score
from tft.queries.aliases import get_champ_aliases
from tft.queries.items import ItemType, get_item_name_map, get_recipes
import tft.interpreter.validation as valid

@register(name='bis')
class BestInSlotCommand(Command):
    @override
    def validate(self, inputs: list | None = None) -> Any:
        valid_output = valid.evaluate_validation(valid.Sequence([
            valid.IsChampion(),
            valid.Many(valid.IsItem(ItemType.COMPONENT))
        ]), inputs)
        champ = valid_output[0]
        components = valid_output[1:]
        return champ, components
    
    @override
    def execute(self, inputs: Any = None) -> Any:
        champ, components = inputs
        q = ql.query(meta.get_champ_item_data(champ)).idx(f"{champ}.builds").map(ql.sub({
            'items': ql.idx('buildNames').split('|'),
            'places': ql.idx('places')
        }))
        # Items are in the item name map and builds have 3 items.
        q = q.filter(ql.all([
            ql.idx('items').map(ql.in_set(get_item_name_map())).unary(all),
            ql.idx('items').len().eq(3)
        ]))
        # Converts item to components if it has components.
        def components_or_self(item: str) -> list[str]:
            if item in get_recipes():
                return get_recipes()[item]
            return [item]
        # Items have the components passed.
        q = q.map(ql.extend({
            'matched_components': ql.idx('items').map(ql.unary(components_or_self)).flatten().unary(count_match_score(components))
        }))
        q = q.filter(ql.idx('matched_components').eq(len(components)))
        
        return q.sort_by(ql.idx('places').unary(sum), True).top(10).eval()
    
    @override
    def render(self, outputs: Any = None) -> str:
        table = Table([
            ItemNameField('Item 1', ql.idx('items.0')),
            ItemNameField('Item 2', ql.idx('items.1')),
            ItemNameField('Item 3', ql.idx('items.2')),
            AvgPlaceField('Avg Place', ql.idx('places')),
            GamesPlayedField('Games', ql.idx('places'))
        ])
        return table.render(outputs)
    
    @override
    def name(self) -> str:
        return "Best in Slot Items for Champion"
    
    @override
    def description(self) -> str:
        return "Returns the 10 most popular 3 item builds for a champion.\nUsage: bis <champion>"
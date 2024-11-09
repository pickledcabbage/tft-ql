from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
import tft.client.meta as meta
from tft.ql.table import AvgPlaceField, GamesPlayedField, ItemNameField, Table
from tft.queries.aliases import get_champ_aliases
from tft.ql.util import avg_place
import tft.ql.expr as ql
from tft.queries.items import get_item_name_map
import tft.interpreter.validation as valid

__all__ = ["BestItems"]

@register(name='bi')
class BestItems(Command):
    """This command takes in a champion name and returns a list of the most
    popular items for that champions by games played."""
    @override
    def validate(self, inputs: list[str]) -> Any:
        return valid.evaluate_validation(valid.IsChampion(), inputs)[0]

    
    @override
    def execute(self, inputs: Any = None) -> Any:
        return ql.query(meta.get_champ_item_data(inputs)).idx(f"{inputs}.items").filter(
            ql.idx('itemName').in_set(get_item_name_map())
        ).sort_by(ql.idx('places').unary(sum), True).top(10).eval()
        
    
    @override
    def render(self, outputs: Any = None) -> str:
        table = Table([
            ItemNameField('Item', ql.idx('itemName')),
            AvgPlaceField('Avg Place', ql.idx('places')),
            GamesPlayedField('Games', ql.idx('places'))
        ])
        return table.render(outputs)
    
    @override
    def name(self) -> str:
        return "Best Items for Champion"

    @override
    def description(self) -> str:
        return "Returns the 10 most popular items for a champion.\nUsage: bi <champion>"
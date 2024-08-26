import tft.ql.expr as ql
import tft.client.meta as meta

from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.ql.table import AvgPlaceField, GamesPlayedField, ItemNameField, Table
from tft.ql.util import avg_place
from tft.queries.aliases import get_champ_aliases
from tft.queries.items import get_item_name_map


@register(name='bis')
class BestInSlotCommand(Command):
    @override
    def validate(self, inputs: list | None = None) -> Any:
        if inputs is None or len(inputs) != 1:
            raise ValidationException(f"Invalid input: {inputs}")
        champ_id = inputs[0]
        if champ_id not in get_champ_aliases():
            raise ValidationException(f"Champion alias not found: {champ_id}")
        return get_champ_aliases()[champ_id]
    
    @override
    def execute(self, inputs: Any = None) -> Any:
        return ql.query(meta.get_champ_item_data(inputs)).idx(f"{inputs}.builds").map(ql.sub({
            'items': ql.idx('buildNames').split('|'),
            'places': ql.idx('places')
        })).filter(ql.all([
            ql.idx('items').map(ql.in_set(get_item_name_map())).unary(all),
            ql.idx('items').len().eq(3)
        ])).sort_by(ql.idx('places').unary(sum), True).top(10).eval()
    
    @override
    def print(self, outputs: Any = None) -> None:
        table = Table([
            ItemNameField('Item 1', ql.idx('items.0')),
            ItemNameField('Item 2', ql.idx('items.1')),
            ItemNameField('Item 3', ql.idx('items.2')),
            AvgPlaceField('Avg Place', ql.idx('places')),
            GamesPlayedField('Games', ql.idx('places'))
        ])
        table.print(outputs)
        # item_name_map = get_item_name_map()
        # for row in outputs:
        #     items = row['items']
        #     print(f"{item_name_map[items[0]]:20} {item_name_map[items[1]]:20} {item_name_map[items[2]]:20} {row['avg_place']:5.2f} {row['games']:8}")
from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
import tft.client.meta as meta
from tft.queries.aliases import get_champ_aliases
from tft.ql.util import avg_place
import tft.ql.expr as ql
from tft.queries.items import get_item_name_map

__all__ = ["BestItems"]

@register(name='bi')
@register(name='best_items')
class BestItems(Command):
    """This command takes in a champion name and returns a list of the most
    popular items for that champions by games played."""
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
        return ql.query(meta.get_champ_item_data(inputs)).idx(f"{inputs}.items").filter(
            ql.idx('itemName').in_set(get_item_name_map())
        ).map(ql.sub({
            'name': ql.idx('itemName').replace(get_item_name_map()),
            "avg_place": ql.idx('places').unary(avg_place),
            "games": ql.idx('places').unary(sum)
        })).sort_by(ql.idx('games'), True).top(10).eval()
        
    
    @override
    def print(self, outputs: Any = None) -> None:
        for row in outputs:
            print(f"{row['name']:30} {row['avg_place']:5.2f} {row['games']:8}")
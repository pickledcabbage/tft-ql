from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.client.meta import MetaTFTClient, MetaTFTApis
import tft.ql.expr as ql

__all__ = ["BestItems"]

@register(name='bi')
class BestItems(Command):
    """This command takes in a champion name and returns a list of the most
    popular items for that champions by games played."""
    @override
    def validate(self, inputs: list | None = None) -> Any:
        client = MetaTFTClient()
        set_data = client.fetch(MetaTFTApis.SET_DATA)
        champ_ids = ql.query(set_data).idx('units').filter(ql.idx('traits').len().gt(0)).map(ql.idx('apiName')).unary(set).eval()
        if inputs is None or len(inputs) != 1:
            raise ValidationException(f"Invalid input: {inputs}")
        champ_id = inputs[0]
        if champ_id not in champ_ids:
            raise ValidationException(f"Champion not found: {champ_id}")
        return inputs

    
    @override
    def execute(self, inputs: list | None = None) -> Any:
        assert inputs is not None
        client = MetaTFTClient()
        champ_item_data = client.fetch_champ(inputs[0])
        def avg_place(places: Any) -> Any:
            tot = sum(places)
            return sum((i+1) * x / tot for i, x in enumerate(places))
        champ_items = ql.query(champ_item_data).idx('items').map(ql.sub({
            'name': ql.idx('itemName'),
            "avg_place": ql.idx('places').unary(avg_place),
            "games": ql.idx('places').unary(sum)
        })).sort_by(ql.idx('games'), True).top(10).eval()

        return champ_items
        
    
    @override
    def print(self, outputs: Any = None) -> None:
        for row in outputs:
            print(f"{row['name']:30} {row['avg_place']:5.2f} {row['games']:8}")
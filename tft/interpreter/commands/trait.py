

from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.ql.table import ChampionNameField, CostField, Table, TraitField
from tft.ql.util import pad_traits
from tft.queries.aliases import get_trait_aliases
from tft.queries.champs import query_champs
import tft.ql.expr as ql


@register(name='trait')
class TraitCommand(Command):
    """Returns all champs of a particular trait."""
    
    @override
    def validate(self, inputs: list | None = None) -> Any:
        if inputs is None:
            raise ValidationException("Inputs cannot by none.")
        if len(inputs) != 1:
            raise ValidationException("trait command takes one only trait.")
        trait_alias = inputs[0]
        if trait_alias not in get_trait_aliases():
            raise ValidationException(f"Invalid trait alias: {trait_alias}")
        return get_trait_aliases()[trait_alias]
    
    @override
    def execute(self, inputs: Any = None) -> Any:
        trait = inputs
        return query_champs().filter(ql.idx('traits').contains(trait)).sort_by(ql.idx('cost')).eval()

    @override
    def print(self, outputs: Any = None) -> None:
        table = Table([
            ChampionNameField('Name', ql.idx('apiName')),
            CostField('Cost', ql.idx('cost')),
            TraitField('Trait 1', ql.idx('traits').unary(pad_traits).idx('0')),
            TraitField('Trait 2', ql.idx('traits').unary(pad_traits).idx('1')),
            TraitField('Trait 3', ql.idx('traits').unary(pad_traits).idx('2'))
        ])
        table.print(outputs)
    
    @override
    def name(self) -> str:
        return "Champions with Trait"
    
    @override
    def description(self) -> None:
        print("Prints all champions and their costs for a specific trait.")
        print("Usage: trait <champion>")
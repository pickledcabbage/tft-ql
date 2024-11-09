

from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.ql.table import ChampionNameField, CostField, Table, TraitField
from tft.ql.util import pad_traits
from tft.queries.aliases import get_trait_aliases
from tft.queries.champs import query_champs
import tft.ql.expr as ql
from tft.queries.traits import query_traits
import tft.interpreter.validation as valid


@register(name='trait')
class TraitCommand(Command):
    """Returns all champs of a particular trait."""
    
    @override
    def validate(self, inputs: list[str]) -> Any:
        # This will work, don't mind the type checking.
        return valid.evaluate_validation(valid.IsTrait(is_hard=False), inputs)[0]

    
    @override
    def execute(self, inputs: Any = None) -> Any:
        trait = inputs
        return {
            'champs': query_champs().filter(ql.idx('traits').contains(trait)).sort_by(ql.idx('cost')).eval(),
            'info': query_traits().filter(ql.idx('name').eq(trait)).only().eval()
        }

    @override
    def render(self, outputs: Any = None) -> str:
        info = outputs['info']
        output = ""
        output += info['name'] + "\n"
        output += f"Champions: {len(outputs['champs'])}\n"
        output += f"Tiers: {', '.join([str(tier) for tier in info['levels']])}\n"
        table = Table([
            ChampionNameField('Name', ql.idx('apiName')),
            CostField('Cost', ql.idx('cost')),
            TraitField('Trait 1', ql.idx('traits').unary(pad_traits).idx('0')),
            TraitField('Trait 2', ql.idx('traits').unary(pad_traits).idx('1')),
            TraitField('Trait 3', ql.idx('traits').unary(pad_traits).idx('2'))
        ])
        output += table.render(outputs)
        return output
    
    @override
    def name(self) -> str:
        return "Champions with Trait"
    
    @override
    def description(self) -> str:
        return "Prints all champions and their costs for a specific trait.\nUsage: trait <trait>"
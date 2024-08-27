

from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.ql.table import AvgPlaceField, ChampionListField, ChampionNameField, CompClusterField, CostField, GamesPlayedField, Table, TraitField
from tft.ql.util import match_score, pad_traits
from tft.queries.aliases import get_champ_aliases, get_trait_aliases
from tft.queries.champs import query_champs
import tft.ql.expr as ql
from tft.queries.comps import query_early_comps
from tft.queries.traits import query_traits


@register(name='early')
class EarlyCommand(Command):
    """Returns the top early comps given a list of champs."""
    
    @override
    def validate(self, inputs: list | None = None) -> Any:
        if inputs is None:
            raise ValidationException('Inputs cannot be none.')
        if len(inputs) > 0:
            try:
                # Check if convertable.
                _first_as_int = int(inputs[0])
                level_filter = inputs[0]
                inputs = inputs[1:]
            except:
                level_filter = None
        else:
            level_filter = None
        
        for champ in inputs:
            if champ not in get_champ_aliases():
                raise ValidationException(f"Champ alias not found: {champ}")
        return level_filter, [get_champ_aliases()[champ] for champ in inputs]
    
    @override
    def execute(self, inputs: Any = None) -> Any:
        level_filter, champs = inputs
        scoring_function = match_score(champs)
        early_comps = query_early_comps()
        if level_filter is not None:
            early_comps = early_comps.filter(ql.idx('level').eq(level_filter))
        early_comps = early_comps.map(ql.extend({
            'match_score': ql.unary(lambda x: scoring_function(x['units']) * 10000000 + x['games'])
        })).sort_by(ql.idx('match_score'), True).top(10).eval()

        return early_comps

    @override
    def print(self, outputs: Any = None) -> None:
        early_comps = outputs
        table = Table([
            CompClusterField('Id', ql.idx('cluster')),
            ChampionListField('Champions', ql.idx('units'), length=65),
            CompClusterField('Lvl', ql.idx('level')), # TODO make basic fields.
            AvgPlaceField('Avg Place', ql.idx('avg_place')),
            GamesPlayedField('Games', ql.idx('games')),
        ])
        table.print(early_comps)
    
    @override
    def name(self) -> str:
        return "Early Comps"
    
    @override
    def description(self) -> None:
        print("Prints all early comps with the given champs. Optional level")
        print("parameter up to 7.")
        print("Usage: early <?level> <champion> <champion> ...")
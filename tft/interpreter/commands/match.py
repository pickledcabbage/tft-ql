

from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.ql.table import AvgPlaceField, ChampionListField, CompClusterField, Field, GamesPlayedField, Table
from tft.ql.util import match_score
from tft.queries.aliases import get_champ_aliases
import tft.ql.expr as ql
from tft.queries.comps import query_comps


@register(name='match')
class MatchCommand(Command):
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
        early_comps = query_comps()
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
            Field('Lvl', ql.idx('level'), 3),
            AvgPlaceField('Avg Place', ql.idx('avg_place')),
            GamesPlayedField('Games', ql.idx('games')),
        ])
        table.print(early_comps)
    
    @override
    def name(self) -> str:
        return "Champ Comp Match"
    
    @override
    def description(self) -> None:
        print("Matches all passed champs to particular comps. Takes in level")
        print("as a parameter to only get comps of that level.")
        print("Usage: match <?level> <champion> <champion> ...")
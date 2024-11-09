

from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.ql.table import AvgPlaceField, ChampionListField, CompClusterField, Field, GamesPlayedField, Table
from tft.ql.util import match_score
from tft.queries.aliases import get_champ_aliases
import tft.ql.expr as ql
from tft.queries.comps import query_comps
import tft.interpreter.validation as valid


@register(name='match')
class MatchCommand(Command):
    """Returns the top early comps given a list of champs."""
    
    @override
    def validate(self, inputs: list[str]) -> Any:
        valid_inputs = valid.evaluate_validation(
            valid.Sequence([
                valid.Optional(valid.IsInteger()),
                valid.Many(valid.IsChampion())
            ]),
            inputs,
            group=True
        )
        # Yes, level filter is a string.
        level_filter = None if len(valid_inputs['integer']) == 0 else valid_inputs['integer'][0]
        return level_filter, valid_inputs['champion']
    
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
    def render(self, outputs: Any = None) -> str:
        early_comps = outputs
        table = Table([
            CompClusterField('Id', ql.idx('cluster')),
            ChampionListField('Champions', ql.idx('units'), length=65),
            Field('Lvl', ql.idx('level'), 3),
            AvgPlaceField('Avg Place', ql.idx('avg_place')),
            GamesPlayedField('Games', ql.idx('games')),
        ])
        return table.render(early_comps)
    
    @override
    def name(self) -> str:
        return "Champ Comp Match"
    
    @override
    def description(self) -> str:
        return "Matches all passed champs to particular comps. Takes in level\nas a parameter to only get comps of that level.\nUsage: match <?level> <champion> <champion> ..."
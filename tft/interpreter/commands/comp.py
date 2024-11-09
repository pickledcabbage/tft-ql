

from typing import Any, override
from tft.client.meta import get_comp_details
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.ql.table import AugmentField, AvgPlaceField, ChampionListField, CompClusterField, Field, GamesPlayedField, PercentField, Table
from tft.ql.util import match_score
from tft.queries.aliases import get_champ_aliases
import tft.ql.expr as ql
from tft.queries.comps import query_comp_details, query_comps


@register(name='comp')
class EarlyCommand(Command):
    """Returns details about a composition."""
    
    @override
    def validate(self, inputs: list | None = None) -> Any:
        comps = get_comp_details()
        if inputs is None:
            raise ValidationException("Inputs cannot be none.")
        if len(inputs) != 1:
            raise ValidationException("Need exactly one composition param.")
        cid = str(inputs[0])
        if cid not in comps:
            raise ValidationException(f"Composition with id {cid} not found.")
        return cid
    
    @override
    def execute(self, inputs: Any = None) -> Any:
        q_comp_details = query_comp_details().idx(f"{inputs}")
        # Get augment info and append percentage.
        q_aug_info = q_comp_details.idx('augments').map(ql.select(['aug', 'count']))
        total_augs = q_aug_info.map(ql.idx('count')).unary(sum).eval()
        q_aug_info = q_aug_info.map(ql.extend({'percent': ql.idx('count').unary(lambda x: x / total_augs)}).select(['aug', 'percent']))

        # Get reroll info and append percentage.
        q_reroll_info = q_comp_details.idx('rerolls').explode('level')
        total_rerolls = q_reroll_info.map(ql.idx('rerolls')).unary(sum).eval()
        q_reroll_info = q_reroll_info.map(ql.extend({'percent': ql.idx('rerolls').unary(lambda x: x / total_rerolls)}).select(['level', 'percent']))

        # Get level info.
        q_level_info = q_comp_details.idx('levels').select(['level', 'stage', 'round'])

        return q_aug_info.top(10).eval()

    @override
    def render(self, outputs: Any = None) -> str:
        table = Table([
            AugmentField('Augment', ql.idx('aug')),
            PercentField('Percent', ql.idx('percent'))
        ])
        return table.render(outputs)
    
    @override
    def name(self) -> str:
        return "Composition Details"
    
    @override
    def description(self) -> str:
        return "Prints details about about a composition.\nUsage: comp <comp/cluster id>"
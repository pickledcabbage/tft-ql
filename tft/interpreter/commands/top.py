

from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.ql.table import AvgPlaceField, ChampionListField, CompClusterField, CompNameField, Field, GamesPlayedField, ItemListField, Table, coerce_champ_name
from tft.ql.util import match_score
from tft.queries.aliases import get_champ_aliases
import tft.ql.expr as ql
from tft.queries.comps import query_comps, query_top_comps
import tft.interpreter.validation as valid
from tft.interpreter.validation import EntityType


@register(name='top')
class TopCommand(Command):
    """Returns the top comps. If given champs, returns top comps with champ."""
    
    @override
    def validate(self, inputs: list[str]) -> Any:
        return valid.evaluate_validation(
            valid.Many(valid.Or([valid.IsChampion(), valid.IsCluster(), valid.IsField()])),
            inputs,
            group=True
        )
    
    @override
    def execute(self, inputs: Any = None) -> Any:
        champs = inputs['champion']
        cluster_id = inputs['cluster_id'] if 'cluster_id' in inputs else None
        filter_field = inputs['field'][0] if 'field' in inputs else None

        scoring_function = match_score(champs)
        top_comps = query_top_comps()
        top_comps = top_comps.filter(ql.idx('units').unary(scoring_function).eq(len(champs)))
        if cluster_id is not None:
            top_comps = top_comps.filter(ql.idx('cluster').in_set(cluster_id))
        if filter_field is not None and filter_field['value'] in ['games', 'avg_place']:
            top_comps = top_comps.sort_by(ql.idx(filter_field['value']), filter_field['direction'] == 'DES')
        else:
            top_comps = top_comps.sort_by(ql.idx('games'), True).top(10)

        return top_comps.eval()

    @override
    def render(self, outputs: Any = None) -> str:
        top_comps = outputs
        id_field = CompClusterField('Id', ql.idx('cluster'), length=5)
        comp_name_field = CompNameField('Name', ql.idx('name'), length=82)
        champ_list_field = ChampionListField('Champions', ql.idx('units'), length=90, stars=ql.idx('stars'))
        avg_place = AvgPlaceField('Avg Place', ql.idx('avg_place'))
        games = GamesPlayedField('Games', ql.idx('games'))
        row_length = 113
        first_div = 90
        second_div = avg_place.length
        third_div = games.length

        output = ""
        output += row_length*'-' + "\n"
        output += f"{'Team Composition':90} | {avg_place.name:{avg_place.length}} | {games.name:{games.length}}" + "\n"
        output += row_length*'-' + "\n"
        for row in top_comps:
            output += f"[{id_field.get(row)}] {comp_name_field.get(row)} | {avg_place.get(row)} | {games.get(row)}" + "\n"
            output += f"{champ_list_field.get(row)} | {avg_place.length * ' '} |" + "\n"
            output += f"{first_div * ' '} | {second_div*' '} |" + "\n"
            for champ in row['builds']:
                champ_name = coerce_champ_name(champ)
                item_list_field = ItemListField('Items', ql.idx(f'builds.{champ}'), length=first_div-17, same_length=23, delim=' ')
                output += f"{champ_name:15}: {item_list_field.get(row)} | {second_div*' '} |" + "\n"
            output += row_length*'-' + "\n"
        return output
    
    @override
    def name(self) -> str:
        return "Top Comps"
    
    @override
    def description(self) -> str:
        return "Matches given champs to top comps.\nUsage: top <champion> <champion> ..."
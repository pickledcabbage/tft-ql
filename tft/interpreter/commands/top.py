

from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.ql.table import AvgPlaceField, ChampionListField, CompClusterField, CompNameField, Field, GamesPlayedField, ItemListField, Table, coerce_champ_name
from tft.ql.util import match_score
from tft.queries.aliases import get_champ_aliases
import tft.ql.expr as ql
from tft.queries.comps import query_comps, query_top_comps


@register(name='top')
class TopCommand(Command):
    """Returns the top comps. If given champs, returns top comps with champ."""
    
    @override
    def validate(self, inputs: list | None = None) -> Any:
        if inputs is None:
            raise ValidationException('Inputs cannot be none.')      
        for champ in inputs:
            if champ not in get_champ_aliases():
                raise ValidationException(f"Champ alias not found: {champ}")
        return [get_champ_aliases()[champ] for champ in inputs]
    
    @override
    def execute(self, inputs: Any = None) -> Any:
        champs = inputs
        scoring_function = match_score(champs)
        top_comps = query_top_comps()
        top_comps = top_comps.filter(ql.idx('units').unary(scoring_function).eq(len(champs))).sort_by(ql.idx('games'), True).top(10).eval()

        return top_comps

    @override
    def print(self, outputs: Any = None) -> None:
        top_comps = outputs
        id_field = CompClusterField('Id', ql.idx('cluster'), length=3)
        comp_name_field = CompNameField('Name', ql.idx('name'), length=84)
        champ_list_field = ChampionListField('Champions', ql.idx('units'), length=90, stars=ql.idx('stars'))
        avg_place = AvgPlaceField('Avg Place', ql.idx('avg_place'))
        games = GamesPlayedField('Games', ql.idx('games'))
        row_length = 113
        first_div = 90
        second_div = avg_place.length
        third_div = games.length
        print(row_length*'-')
        print(f"{'Team Composition':90} | {avg_place.name:{avg_place.length}} | {games.name:{games.length}}")
        print(row_length*'-')
        for row in top_comps:
            print(f"[{id_field.get(row)}] {comp_name_field.get(row)} | {avg_place.get(row)} | {games.get(row)}")
            print(f"{champ_list_field.get(row)} | {avg_place.length * ' '} |")
            print(f"{first_div * ' '} | {second_div*' '} |")
            for champ in row['builds']:
                champ_name = coerce_champ_name(champ)
                item_list_field = ItemListField('Items', ql.idx(f'builds.{champ}'), length=first_div-17, same_length=23, delim=' ')
                print(f"{champ_name:15}: {item_list_field.get(row)} | {second_div*' '} |")
            print(row_length*'-')
    
    @override
    def name(self) -> str:
        return "Top Comps"
    
    @override
    def description(self) -> None:
        print("Matches given champs to top comps.")
        print("Usage: top <champion> <champion> ...")
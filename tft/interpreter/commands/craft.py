

from typing import Any, override
from tft.interpreter.commands.registry import Command, ValidationException, register
from tft.queries.aliases import get_item_aliases
from tft.queries.items import get_item_name_map, query_buildable_items, query_component_items
import copy
import tft.interpreter.validation as valid

@register(name='craft')
class CraftCommand(Command):
    """This commands help the user with crafting items. For components, it
    will print what it crafts into. For completed items it prints the
    components."""

    @override
    def validate(self, inputs: list[str]) -> Any:
        return valid.evaluate_validation(valid.IsItem(), inputs)[0]
    
    @override
    def execute(self, inputs: Any = None) -> Any:
        components = query_component_items().eval()
        buildable_items = query_buildable_items().eval()
        if inputs in components:
            recipes = [item for item in buildable_items.values() if inputs in item['composition']]
            return {
                'name': inputs,
                'recipes': recipes
            }
        else:
            data = copy.deepcopy(buildable_items[inputs])
            data['name'] = inputs
            return data
    
    @override
    def print(self, outputs: Any = None) -> None:
        item_name_map = get_item_name_map()
        if 'recipes' in outputs: # Is component query.
            def get_other(composition):
                return composition[1] if composition[0] == outputs['name'] else composition[0]
            recipes = sorted(outputs['recipes'], key=lambda x: get_other(x['composition']))
            print(item_name_map[outputs['name']])
            for recipe in recipes:
                composition = recipe['composition']
                recipe_name = recipe['name']
                other_item = composition[1] if composition[0] == outputs['name'] else composition[0]
                print(f" + {item_name_map[other_item]:20} -> {recipe_name:20}")
        else:
            unique = '(Unique)' if outputs['unique'] else ''
            print(item_name_map[outputs['name']], unique)
            composition = outputs['composition']
            print(f"{item_name_map[composition[0]]} + {item_name_map[composition[1]]}")
    
    @override
    def name(self) -> str:
        return "Crafting Recipes"

    @override
    def description(self) -> None:
        print("List recipes for components and completed items.")
        print("Usage: craft <item>")


We will be working on a new feature which computes the trait levels for a particular comp.

The function `query_traits` in tft/queries/traits.py pulls data in the followin form:
"""
{'TFT16_Teamup_SingedTeemo': {'name': 'Poison Pals', 'levels': [2]},
 'TFT16_XerathUnique': {'name': 'Ascendant', 'levels': [1]},
 'TFT16_Freljord': {'name': 'Freljord', 'levels': [3, 5, 7]},
 'TFT16_Juggernaut': {'name': 'Juggernaut', 'levels': [2, 4, 6]},
}
"""

Write a function in tft/queries/comp_traits.py which is given an Iterable of champion API IDs. It computes every champions contribution to each trait and computes the level of that trait that is active for the composition. For example having 2 juggernauts activates level 2 of the trait 'TFT16_Juggernaut'. However adding another juggernaut, won't increase it to 3 because the next level starts at 4. This function should return a list of tuples (API ID of the trait and the level of the trait) ordered in descending order by trait level.

After you finishing writing this function. Add it to the TopComp API endpoint in tft/interpreter/server.py and include it in the response for every single composition.

Finally add a new column to the QLToolTopComp which shows all of the traits (and their levels) for the comp. Each trait and level should be on their own line.
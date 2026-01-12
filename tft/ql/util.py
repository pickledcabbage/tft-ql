# Contains useful functions to use with the TFT QL language.
# Mostly just to compute similarity scores.

from collections import defaultdict
from typing import Any, Callable, Iterable

from tft.queries.items import get_components, get_recipes


def splay(m: Any, layer: int = 0, depth: int | None =None) -> None:
    """
    Takes a TFT query and prints it.
    """
    tab = "  "
    if depth is not None and layer > depth:
        return
    if isinstance(m, dict):
        for key in m.keys():
            print(tab * layer + str(key))
            splay(m[key], layer + 1, depth)
    elif isinstance(m, list):
        print(tab * layer + f"[{len(m)}]")
        if len(m) > 0:
            splay(m[0], layer + 1, depth)
    else:
        print(tab * layer + str(m))


# Meta TFT specific.
def avg_place(places: Any) -> Any:
    """
    Given a list of placement counts, computes average placement.
    [4, 6, 8, 10, 8, 6, 4, 10] => 4.714285714285714
    """
    tot = sum(places)
    return sum((i+1) * x / tot for i, x in enumerate(places))


def pad_traits(traits: list[str]) -> list[str]:
    """
    Pads traits list with blank strings.
    """
    new_traits = [trait for trait in traits]
    while len(new_traits) < 3:
        new_traits.append('')
    return new_traits


def match_score(search_params: Iterable[str]) -> Callable[[Iterable[str]], int]:
    """
    Returns a function that computes a similarity score between a set
    of champions and the search params (which is a set of champions).
    """
    comparison_set = set(search_params)
    def compare(other: Iterable[str]) -> int:
        count = 0
        # We set this because there are double poppy builds.
        for item in set(other):
            if item in comparison_set:
                count += 1
        return count
    
    return compare


def count_match_score(search_params: Iterable) -> Callable[[Iterable[str]], int]:
    """
    Returns a function that computes a similarity score between a match
    score set and the search params (which is also a set).
    """
    comparison_dict = defaultdict(int)
    for item in search_params:
        comparison_dict[item] += 1
    
    def compare(other: Iterable) -> int:
        count = 0
        other_comparison_dict = defaultdict(int)
        for item in other:
            other_comparison_dict[item] += 1
        
        for item, val in other_comparison_dict.items():
            count += min(val, comparison_dict[item])
        
        return count
    return compare

def built_from(search_params: Iterable[str]) -> Callable[[Iterable[str]], bool]:
    """
    Returns a function which returns true if a passed list of items can be
    built from search params.
    """

    def compare(items: Iterable[str]) -> bool:
        # First directly match items.
        items_to_match = list(search_params) 
        missing_items = set() # Items we didn't match yet.
        components = get_components()
        recipes = get_recipes()
        for item in items:
            if item in items_to_match:
                items_to_match.remove(item)
            else:
                missing_items.add(item)
        
        # Check if any components are left.
        if any(item not in components for item in items_to_match):
            return False
        
        matched_components = defaultdict(int)
        # Break missing items down.
        for item in missing_items:
            if item not in recipes:
                return False
            for component in recipes[item]:
                matched_components[component] += 1
        # Check if components match.
        for item in items_to_match:
            if item not in matched_components:
                return False
            if matched_components[item] == 0:
                return False
            matched_components[item] -= 1
        
        return True
    
    return compare



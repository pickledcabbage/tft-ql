# Contains useful functions to use with the TFT QL language.
# Mostly just to compute similarity scores.

from collections import defaultdict
from typing import Any, Callable, Iterable


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

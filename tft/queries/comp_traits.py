"""
Module for computing trait levels for compositions.
WRITTEN BY CLAUDE
"""
from collections import Counter
from typing import Iterable

import tft.ql.expr as ql
import tft.client.meta as meta
from tft.queries.traits import query_traits


# Cached mappings
_CHAMP_TO_TRAITS: dict[str, list[str]] | None = None
_SOFT_TO_HARD_TRAITS: dict[str, str] | None = None


def _get_soft_to_hard_traits() -> dict[str, str]:
    """
    Returns a mapping from trait display names to trait API names.
    WRITTEN BY CLAUDE

    Returns:
        dict: Maps display names (e.g., 'Juggernaut') to API names (e.g., 'TFT16_Juggernaut')
    """
    global _SOFT_TO_HARD_TRAITS
    if _SOFT_TO_HARD_TRAITS is None:
        traits = ql.query(meta.get_set_data()).idx('traits').filter(ql.contains('units')).map(ql.sub({
            'apiName': ql.idx('apiName'),
            'name': ql.idx('name'),
        })).eval()
        _SOFT_TO_HARD_TRAITS = {t['name']: t['apiName'] for t in traits}
    return _SOFT_TO_HARD_TRAITS


def _get_champ_to_traits() -> dict[str, list[str]]:
    """
    Returns a mapping from champion API names to their trait API names.
    WRITTEN BY CLAUDE

    Returns:
        dict: Maps champion API names to list of trait API names
    """
    global _CHAMP_TO_TRAITS
    if _CHAMP_TO_TRAITS is None:
        soft_to_hard = _get_soft_to_hard_traits()
        champs = ql.query(meta.get_set_data()).idx('units').filter(ql.idx('traits').len().gt(0)).map(ql.sub({
            'apiName': ql.idx('apiName'),
            'traits': ql.idx('traits'),
        })).eval()
        _CHAMP_TO_TRAITS = {}
        for champ in champs:
            trait_api_names: list[str] = [soft_to_hard.get(t, t) for t in champ['traits']]
            _CHAMP_TO_TRAITS[champ['apiName']] = trait_api_names
    return _CHAMP_TO_TRAITS


def compute_comp_traits(units: Iterable[str]) -> list[tuple[str, int]]:
    """
    Computes active trait levels for a composition.
    WRITTEN BY CLAUDE

    Args:
        units: Iterable of champion API IDs (e.g., ['TFT16_Teemo', 'TFT16_Singed'])

    Returns:
        List of (trait_api_id, active_level) tuples sorted by level descending.
        Only traits with an active level >= 1 are included.
    """
    champ_to_traits = _get_champ_to_traits()
    trait_data = query_traits().eval()

    # Count how many champions contribute to each trait
    trait_counts: Counter[str] = Counter()
    for unit in units:
        unit_traits = champ_to_traits.get(unit, [])
        for trait in unit_traits:
            trait_counts[trait] += 1

    # Determine active level for each trait
    result: list[tuple[str, int]] = []
    for trait_api_id, count in trait_counts.items():
        trait_info = trait_data.get(trait_api_id)
        if not trait_info:
            continue

        levels = trait_info.get('levels', [])
        if not levels:
            continue

        # Find highest level threshold that count meets or exceeds
        active_level = 0
        for level_threshold in levels:
            if count >= level_threshold:
                active_level = level_threshold
            else:
                break

        if active_level > 0:
            result.append((trait_api_id, active_level))

    # Sort by level descending
    result.sort(key=lambda x: x[1], reverse=True)
    return result

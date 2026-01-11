from tft.ql.util import avg_place
from tft.queries.augs import get_aug_name_map
from tft.queries.champs import get_champ_name_map
from tft.queries.items import get_item_name_map
from tft.queries.traits import get_trait_name_map

def coerce_item_name(name_or_uid: str) -> str:
    """
    If the string is a UID, then tries to convert it into a name
    """
    item_name_map = get_item_name_map()
    if name_or_uid not in item_name_map:
        return name_or_uid
    return item_name_map[name_or_uid]

def coerce_champ_name(name_or_uid: str) -> str:
    """
    If the string is a UID, then tries to convert it into a name
    """
    champ_name_map = get_champ_name_map()
    if name_or_uid not in champ_name_map:
        return name_or_uid
    return champ_name_map[name_or_uid]

def coerce_games_played(games_played) -> int:
    """
    If games played is a list, sums up the values.
    """
    if isinstance(games_played, list):
        return sum(games_played)
    return games_played

def coerce_avg_place(places) -> float:
    """
    If places is a list, computes the average of all values in the list.
    """
    if isinstance(places, list):
        return avg_place(places)
    return places

def coerce_trait_name(name_or_uid: str) -> str:
    """
    If the string is a UID, then tries to convert it into a name.
    """
    trait_name_map = get_trait_name_map()
    if name_or_uid in trait_name_map:
        return trait_name_map[name_or_uid]
    return name_or_uid

def coerce_augment_name(name_or_uid: str) -> str:
    """
    If the string is a UID, then tries to convert it into a name.
    """
    aug_name_map = get_aug_name_map()
    if name_or_uid in aug_name_map:
        return aug_name_map[name_or_uid]
    return name_or_uid

def coerce_wildcard(name_or_uid: str) -> str:
    """
    Coerces across UID name maps.
    """
    mappings = [get_aug_name_map(), get_trait_name_map(), get_champ_name_map(), get_item_name_map()]
    for mapping in mappings:
        if name_or_uid in mapping:
            return mapping[name_or_uid]
    return name_or_uid
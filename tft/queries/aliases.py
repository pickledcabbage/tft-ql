ITEM_ALIASES = None
CHAMP_ALIASES = None

def read_map_csv(filename: str) -> dict:
    alias_dict = {}
    with open(filename, 'r') as f:
        for row in f:
            temp = row.strip().split(',')
            uid = temp[0]
            if uid == '':
                continue
            aliases = temp[1:]
            for alias in aliases:
                if alias == '':
                    continue
                assert alias not in alias_dict, f"Double alias found {alias}"
                alias_dict[alias] = uid
    return alias_dict

def get_champ_aliases():
    global CHAMP_ALIASES
    if CHAMP_ALIASES is None:
        CHAMP_ALIASES = read_map_csv('config/champ_aliases.csv')
    return CHAMP_ALIASES

def get_item_aliases():
    global ITEM_ALIASES
    if ITEM_ALIASES is None:
        ITEM_ALIASES = read_map_csv('config/item_aliases.csv')
    return ITEM_ALIASES

# Make sure item and champ aliases don't overlap!
get_item_aliases()
get_champ_aliases()
for alias in CHAMP_ALIASES:
    assert alias not in ITEM_ALIASES, f"Overlapping alias: {alias}"
for alias in ITEM_ALIASES:
    assert alias not in CHAMP_ALIASES, f"Overlapping alias: {alias}"

    
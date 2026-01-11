from tft.config import CHAMP_ALIAS_FILE, ITEM_ALIAS_FILE, TRAIT_ALIAS_FILE

ITEM_ALIASES = None
CHAMP_ALIASES = None
TRAIT_ALIASES = None
HARD_TRAIT_ALIASES = None

def read_map_csv(filename: str) -> dict:
    """
    Takes an alias CSV file and converts it to a dictionary mapping each alias to
    the API name.
    Ex: A row could be as such:
    TFT14_Fiddlesticks,fiddlesticks,fidd,fid
    
    This would create the following alias dictionary entries:
    fiddlesticks -> TFT14_Fiddlesticks
    fidd         -> TFT14_Fiddlesticks
    fid          -> TFT14_Fiddlesticks
    """
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
    """
    Gets the champion aliases and stores them in a global variable.
    """
    global CHAMP_ALIASES
    if CHAMP_ALIASES is None:
        CHAMP_ALIASES = read_map_csv(CHAMP_ALIAS_FILE)
    return CHAMP_ALIASES

def get_item_aliases():
    """
    Gets the item aliases and stores them in a global variable.
    """
    global ITEM_ALIASES
    if ITEM_ALIASES is None:
        ITEM_ALIASES = read_map_csv(ITEM_ALIAS_FILE)
    return ITEM_ALIASES

def get_trait_aliases():
    """
    Gets the trait aliases and stores them in a global variable.
    This one converts to the soft names.
    Ex: frost -> Frost
    Use this one when looking at champs with a trait.
    """
    global TRAIT_ALIASES
    if TRAIT_ALIASES is None:
        TRAIT_ALIASES = read_map_csv(TRAIT_ALIAS_FILE)
    return TRAIT_ALIASES

def get_hard_trait_aliases():
    """
    Gets the hard trait aliases and stores them in a global variable.
    This one converts to the API names.
    Ex: divinicorp -> TFT14_Divinicorp
    """
    global HARD_TRAIT_ALIASES
    if HARD_TRAIT_ALIASES is None:
        HARD_TRAIT_ALIASES = read_map_csv('config/hard_trait_aliases.csv')
    return HARD_TRAIT_ALIASES

# Make sure item and champ aliases don't overlap!
get_item_aliases()
get_champ_aliases()
for alias in CHAMP_ALIASES:
    assert alias not in ITEM_ALIASES, f"Overlapping alias: {alias}"
for alias in ITEM_ALIASES:
    assert alias not in CHAMP_ALIASES, f"Overlapping alias: {alias}"

# Maybe ensure some trait alias guidelines?

def get_alias_file(alias_type: str) -> str:
    """Returns the file path for the given alias type."""
    if alias_type == 'champ':
        return CHAMP_ALIAS_FILE
    elif alias_type == 'item':
        return ITEM_ALIAS_FILE
    elif alias_type == 'trait':
        return TRAIT_ALIAS_FILE
    else:
        raise ValueError(f"Unknown alias type: {alias_type}")

def get_alias_dict(alias_type: str) -> dict:
    """Returns the alias dictionary for the given type."""
    if alias_type == 'champ':
        return get_champ_aliases()
    elif alias_type == 'item':
        return get_item_aliases()
    elif alias_type == 'trait':
        return get_trait_aliases()
    else:
        raise ValueError(f"Unknown alias type: {alias_type}")

def write_aliases_to_file(alias_type: str):
    """Writes all aliases back to the CSV file for the given type."""
    alias_dict = get_alias_dict(alias_type)
    file_path = get_alias_file(alias_type)

    # Invert the dictionary: group aliases by API ID
    api_to_aliases = {}
    for alias, api_id in alias_dict.items():
        if api_id not in api_to_aliases:
            api_to_aliases[api_id] = []
        api_to_aliases[api_id].append(alias)

    # Write to file
    with open(file_path, 'w') as f:
        for api_id, aliases in api_to_aliases.items():
            f.write(f"{api_id},{','.join(aliases)}\n")

def add_alias(api_id: str, alias: str, alias_type: str) -> bool:
    """
    Adds a new alias for the given API ID and type.
    Returns True if successful, False if alias already exists.
    """
    alias = alias.lower().strip()
    alias_dict = get_alias_dict(alias_type)

    if alias in alias_dict:
        return False

    alias_dict[alias] = api_id
    write_aliases_to_file(alias_type)
    return True

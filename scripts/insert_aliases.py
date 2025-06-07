import pymongo

from tft.client.meta import get_comp_data
from tft.queries.aliases import get_champ_aliases, get_item_aliases
import tft.ql.expr as ql
from tft.config import DB

def main():
    """
    Takes local lists of aliases and uploads them to the DB.
    """
    client = pymongo.MongoClient(DB)
    tft_db = client['tft']
    alias_col = tft_db['alias']

    # Schema:
    # set   - TFT set value.
    # alias - Alias to map to a unit.
    # type  - Either 'champ', 'item', or 'trait'
    # value - What the alias maps to.

    # Create an index. This is idempotent.
    alias_col.create_index([('set', pymongo.ASCENDING), ('alias', pymongo.ASCENDING)], unique=True)

    tft_set = ql.query(get_comp_data()).idx("tft_set").eval()

    # Insert champ aliases.
    champ_aliases = get_champ_aliases()
    for alias, value in champ_aliases.items():
        curr = alias_col.find_one({'set': tft_set, 'alias': alias})
        if curr is None:
            alias_col.insert_one({'alias': alias, 'value': value, 'type': 'champ', 'set': tft_set})
    
    # Insert item aliases.
    item_aliases = get_item_aliases()
    for alias, value in item_aliases.items():
        curr = alias_col.find_one({'set': tft_set, 'alias': alias})
        if curr is None:
            alias_col.insert_one({'alias': alias, 'value': value, 'type': 'item', 'set': tft_set})

if __name__ == '__main__':
    main()
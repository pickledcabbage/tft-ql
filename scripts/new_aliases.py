import tft.ql.expr as ql
from tft.client.meta import *
import re
from tft.config import CHAMP_ALIAS_FILE, ITEM_ALIAS_FILE, TRAIT_ALIAS_FILE

def main():
    """
    Creates a new local file with the current set aliases. Resets all aliases.
    """
    create_client(False) # No local cache.
    client = get_client()
    set_data = client.fetch(MetaTFTApis.SET_DATA)
    q2 = ql.query(set_data)

    # Champs.
    champions = q2.idx('units').filter(ql.idx('traits').len().gt(0))
    with open(CHAMP_ALIAS_FILE, 'w') as f:
        for k,v in champions.map(ql.idx('apiName'), ql.idx('en_name')).eval().items():
            f.write(v + ',' + re.sub(r'\W+','',k.lower()) + '\n')
    
    # Items.
    buildable_items = q2.idx('items').filter(ql.idx('composition').len().eq(2))
    component_names = buildable_items.map(ql.idx('composition')).flatten().uniq().eval()
    component_items = q2.idx('items').filter(ql.idx('apiName').in_set(component_names))
    with open(ITEM_ALIAS_FILE, 'w') as f:
        for k,v in buildable_items.map(ql.idx('apiName'), ql.idx('en_name')).eval().items():
            f.write(v + ',' + re.sub(r'\W+','',k.lower()) + '\n')
        for k,v in component_items.map(ql.idx('apiName'), ql.idx('en_name')).eval().items():
            f.write(v + ',' + re.sub(r'\W+','',k.lower()) + '\n')
    
    # Traits.
    traits = q2.idx('traits').filter(ql.contains('units'))
    with open(TRAIT_ALIAS_FILE, 'w') as f:
        for k,v in traits.map(ql.idx('apiName'), ql.idx('name')).eval().items():
            f.write(v + ',' + re.sub(r'\W+','',k.lower()) + '\n')
        


if __name__ == '__main__':
    main()
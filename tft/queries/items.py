import tft.client.meta as meta
import tft.ql.expr as ql
# Easy access to queries and dicts here.

ITEM_NAME_MAP = None

def query_component_items():
    component_names = query_buildable_items().map(ql.idx('composition')).vals().flatten().unary(set).eval()
    return ql.query(meta.get_set_data()).idx('items').filter(ql.idx('apiName').in_set(component_names)).map(ql.sub({
        'name': ql.idx('en_name')
    }), ql.idx('apiName'))

def query_buildable_items():
    return ql.query(meta.get_set_data()).idx('items').filter(ql.idx('composition').len().eq(2)).map(ql.sub({
        'name': ql.idx('en_name'),
        'composition': ql.idx('composition'),
        'unique': ql.idx('unique')
    }), ql.idx('apiName'))

def get_item_name_map():
    global ITEM_NAME_MAP
    if ITEM_NAME_MAP is None:
        ITEM_NAME_MAP = {}
        component_item_map = query_component_items().map(ql.idx('name')).eval()
        buildable_items = query_buildable_items().map(ql.idx('name')).eval()
        for k, v in component_item_map.items():
            ITEM_NAME_MAP[k] = v
        for k,v in buildable_items.items():
            ITEM_NAME_MAP[k] = v
        # One offs.
        ITEM_NAME_MAP['TFT12_Item_Faerie_QueensCrown'] = "Faerie Queen's Crown"
        ITEM_NAME_MAP['TFT_Item_UnstableTreasureChest'] = "Unstable Treasure Chest"
    return ITEM_NAME_MAP

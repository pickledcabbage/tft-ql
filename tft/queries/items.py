from enum import Enum
import tft.client.meta as meta
import tft.ql.expr as ql
# Easy access to queries and dicts here.

ITEM_NAME_MAP = None
COMPLETED_ITEMS = None
COMPONENT_ITEMS = None
RECIPES = None

class ItemType(Enum):
    COMPONENT = 'component'
    COMPLETED = 'completed'
    OTHER = 'other'
    # ARTIFACT = 'artifact'
    # TRAIT = 'trait'

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
        ITEM_NAME_MAP['TFT7_Item_ShimmerscaleMogulsMail'] = "Mogul's Mail"
    return ITEM_NAME_MAP

def get_components():
    global COMPONENT_ITEMS
    if COMPONENT_ITEMS is None:
        COMPONENT_ITEMS = set(query_component_items().keys().eval())
    return COMPONENT_ITEMS

def get_completed_items():
    global COMPLETED_ITEMS
    if COMPLETED_ITEMS is None:
        COMPLETED_ITEMS = set(query_buildable_items().keys().eval())
    return COMPLETED_ITEMS

def get_recipes():
    global RECIPES
    if RECIPES is None:
        RECIPES = query_buildable_items().map(ql.idx('composition')).eval()
    return RECIPES

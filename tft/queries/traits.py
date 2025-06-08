import tft.ql.expr as ql
import tft.client.meta as meta

TRAIT_NAME_MAP = None

def query_traits():
    """
    Returns a query for trait data.
    """
    return ql.query(meta.get_set_data()).idx('traits').map(ql.sub({
        'name': ql.idx('name'),
        'levels': ql.idx('effects').map(ql.idx('minUnits'))
    }), ql.idx('apiName'))

def get_trait_name_map():
    """
    Returns a dictionary mapping all trait API names to human readable names. Caches in a global variable.
    """
    global TRAIT_NAME_MAP
    if TRAIT_NAME_MAP is None:
        TRAIT_NAME_MAP = query_traits().map(ql.idx('name')).eval()
    return TRAIT_NAME_MAP

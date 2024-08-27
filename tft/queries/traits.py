import tft.ql.expr as ql
import tft.client.meta as meta

TRAIT_NAME_MAP = None

def query_traits():
    return ql.query(meta.get_set_data()).idx('traits').map(ql.sub({
        'name': ql.idx('name'),
        'levels': ql.idx('effects').map(ql.idx('minUnits'))
    }), ql.idx('apiName'))

def get_trait_name_map():
    global TRAIT_NAME_MAP
    if TRAIT_NAME_MAP is None:
        TRAIT_NAME_MAP = query_traits().map(ql.idx('name')).eval()
    return TRAIT_NAME_MAP

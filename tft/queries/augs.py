import tft.ql.expr as ql
import tft.client.meta as meta

AUG_NAME_MAP = None

def query_augs():
    return ql.query(meta.get_set_data()).idx('augments')

def get_aug_name_map() -> dict:
    global AUG_NAME_MAP
    if AUG_NAME_MAP is None:
        AUG_NAME_MAP = query_augs().map(ql.idx('en_name'), ql.idx('apiName')).eval()
    return AUG_NAME_MAP
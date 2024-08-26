import tft.ql.expr as ql
import tft.client.meta as meta

CHAMP_NAME_MAP = None

def query_champs():
    return ql.query(meta.get_set_data()).idx('units').filter(ql.idx('traits').len().gt(0))

def get_champ_name_map():
    global CHAMP_NAME_MAP
    if CHAMP_NAME_MAP is None:
        CHAMP_NAME_MAP = query_champs().map(ql.idx('en_name'), ql.idx('apiName')).eval()
    return CHAMP_NAME_MAP
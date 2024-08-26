import tft.ql.expr as ql
import tft.client.meta as meta

def query_traits():
    return ql.query(meta.get_set_data()).idx('units').map(ql.idx('traits')).flatten().uniq()

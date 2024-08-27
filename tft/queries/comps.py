import tft.ql.expr as ql
import tft.client.meta as meta


def query_early_comps():
    return ql.query(meta.get_comp_details()).map(ql.idx('results.early_options').explode("level").map(ql.sub({
        'units': ql.idx('unit_list').split('&'),
        'avg_place': ql.idx('avg'),
        'games': ql.idx('count'),
        'level': ql.idx('level'),
        'win_rate': ql.idx('win') # This is not included in query_comps().
    }))).explode('cluster').sort_by(ql.idx('win_rate'), True)

def query_comps():
    return ql.query(meta.get_comp_details()).map(ql.idx('results.options').explode("level").map(ql.sub({
        'units': ql.idx('units_list').split('&'), # This is differnt from query_early_comps()
        'traits': ql.idx('traits_list').split('&'),
        'avg_place': ql.idx('avg'),
        'games': ql.idx('count'),
        'level': ql.idx('level'),
    }))).explode('cluster').sort_by(ql.idx('win_rate'), True)
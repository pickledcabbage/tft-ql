import tft.ql.expr as ql
import tft.client.meta as meta


def query_comps():
    """
    Returns a query object containing all comps in the dataset.
    """
    return ql.query(meta.get_comp_details()).filter(ql.contains('results')).map(ql.query(), ql.idx('1'), on_key=True).map(ql.idx('results').sub({
        'early': ql.idx('early_options').explode('level').map(ql.sub({
            'units': ql.idx('unit_list').split('&'),
            'avg_place': ql.idx('avg'),
            'games': ql.idx('count'),
            'level': ql.idx('level'),
        })),
        'late': ql.idx('options').explode('level').map(ql.sub({
            'units': ql.idx('units_list').split('&'),
            'avg_place': ql.idx('avg'),
            'games': ql.idx('count'),
            'level': ql.idx('level'),
        }))
    }).values().flatten()).explode('cluster').sort_by(ql.idx('games'), True)

def query_comp_details():
    """
    Returns a query object containing data about a particular comp.
    """
    return ql.query(meta.get_comp_details()).filter(ql.contains('results')).map(ql.query(), ql.idx('1'), on_key=True).map(
        ql.idx('results').select([
            'placements',
            'unit_stats',
            'builds',
            'overall',
            'augments',
            'levels',
            'rerolls'
        ]))

def query_top_comps():
    """
    Returns a query object containing the main build for the top comps.
    """
    return ql.query(meta.get_comp_data()).idx('results.data.cluster_details').map(ql.sub({
        'units': ql.idx('units_string').split(', '),
        'name': ql.idx('name').map(ql.select(['name', 'type'])),
        'games': ql.idx('overall.count'),
        'avg_place': ql.idx('overall.avg'),
        'builds': ql.idx('builds').map(ql.idx('buildName'), ql.idx('unit')),
        'stars': ql.idx('stars')
    })).explode('cluster')
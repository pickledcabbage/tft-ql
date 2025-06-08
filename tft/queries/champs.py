import tft.ql.expr as ql
import tft.client.meta as meta

CHAMP_NAME_MAP = None

def query_champs():
    """
    Gets a query object for all champ data.
    """
    return ql.query(meta.get_set_data()).idx('units').filter(ql.idx('traits').len().gt(0))

def get_champ_name_map():
    """
    Returns a dictionary that maps API names to human readable names. Use for displaying data.
    Ex: TFT12_Yuumi -> Yuumi
    """
    global CHAMP_NAME_MAP
    if CHAMP_NAME_MAP is None:
        CHAMP_NAME_MAP = query_champs().map(ql.idx('en_name'), ql.idx('apiName')).eval()
        # Add one offs here:
        CHAMP_NAME_MAP['TFT12_Yuumi'] = 'Yuumi'
    return CHAMP_NAME_MAP

from enum import Enum
import json
from pathlib import Path
import attrs
import requests
import tft.ql.expr as ql
import multiprocessing
from tft.config import CLUSTER_ID, TFT_SET


class MetaTFTApis(Enum):
    COMPS_DATA = 'comps_data'
    COMP_STATS = 'comp_stats'
    COMP_DETAILS = 'comp_details'
    SET_DATA = 'set_data'
    CHAMP_ITEMS = 'champ_items'

class MetaTFTClientType(Enum):
    # Will not use the memory cache or the disk cache.
    NO_CACHE = 'no_cache' # Not support yet.
    # Will cache the data in memory but not the disk.
    ONLINE_ONLY = 'online'
    # Will only read data from disk.
    OFFLINE_ONLY = 'offline'
    # Will cache the data in memory and also propagate it to disk.
    ONLINE_AND_OFFLINE = 'online_and_offline'

URLS = {
    MetaTFTApis.COMPS_DATA: "https://api-hc.metatft.com/tft-comps-api/comps_data",
    MetaTFTApis.SET_DATA: f"https://data.metatft.com/lookups/{TFT_SET}_latest_en_us.json",
    MetaTFTApis.CHAMP_ITEMS: "https://api-hc.metatft.com/tft-stat-api/unit_detail",
    MetaTFTApis.COMP_DETAILS: "https://api-hc.metatft.com/tft-comps-api/comp_details"
}

# Location to cache data on disk.
CACHE_PATH = 'res/cache/cache.json'

# Singletons for caching data in memory.
CACHE = {}
CHAMP_CACHE = {}
COMP_CACHE = {}
CLIENT = None

@attrs.define
class MetaTFTClient:
    """
    A client for fetching data from metatft.com. It is heavily cached so that we don't constantly make
    expensive API requests. Here are the components:

    In-memory Cache: The is the `CACHE` global variable and the specific ones like `COMP_CACHE`. This
    stores the raw contents of requests made to the website in memory. ONLINE_ONLY and ONLINE_AND_OFFLINE
    make requests and store them in this cache. OFFLINE_ONLY reads a file and writes its contents into
    here and makes no API requests. NO_CACHE ignores this.

    Disk Cache: The file indicated by `CACHE_PATH`. This is loaded on start up by OFFLINE_ONLY, and written
    to if ONLINE_AND_OFFLINE is specified. 
    """

    client_type: MetaTFTClientType = attrs.field(default=MetaTFTClientType.ONLINE_ONLY)

    def __attrs_post_init__(self):
        """Maybe load caches."""
        global CACHE
        global CHAMP_CACHE
        global COMP_CACHE
        path = Path(CACHE_PATH)
        if self.client_type in [MetaTFTClientType.OFFLINE_ONLY] and path.exists():
            with open(path, 'r') as f:
                CACHE = json.load(f)
            if MetaTFTApis.CHAMP_ITEMS in CACHE:
                CHAMP_CACHE = CACHE[MetaTFTApis.CHAMP_ITEMS.value]
            if MetaTFTApis.COMP_DETAILS in CACHE:
                COMP_CACHE = CACHE[MetaTFTApis.COMP_DETAILS.value]

    def fetch(self, api: MetaTFTApis, cluster_id: int = CLUSTER_ID) -> dict:
        global CACHE
        global CHAMP_CACHE
        """
        Fetches given API and returns a dict. Subsequent requests are cached.
        """
        # Check cache for value. No cache options means we never check memory cache.
        if api.value in CACHE and self.client_type not in [MetaTFTClientType.NO_CACHE]:
            return CACHE[api.value]
        
        # Offline only means a file must already exist, so thereforce if its not in the cache, then no file exists.
        if self.client_type in [MetaTFTClientType.OFFLINE_ONLY]:
            print("ERROR: Offline only client was not able to fetch data set.")
            return dict()

        # Perform appropriate lookup.
        if api == MetaTFTApis.CHAMP_ITEMS:
            champ_ids = ql.query(self.fetch(MetaTFTApis.SET_DATA)).idx('units').filter(ql.idx('traits').len().gt(0)).map(ql.idx('apiName')).eval()
            champ_ids = {champ_id for champ_id in champ_ids if champ_id not in CHAMP_CACHE}
            with multiprocessing.Pool(20) as pool:
                all_champ_data = pool.map(self.fetch_champ, champ_ids)
            for champ_id, champ_data in zip(champ_ids, all_champ_data):
                CHAMP_CACHE[champ_id] = champ_data
            data = CHAMP_CACHE
        elif api == MetaTFTApis.COMP_DETAILS:
            results_q = ql.query(self.fetch(MetaTFTApis.COMPS_DATA)).idx('results.data')
            cids = results_q.idx('cluster_details').map(ql.idx('Cluster')).values().eval()
            # internal_cid = results_q.idx('cluster_id').eval()
            # Need internal CID and cluster id to query.
            cids = {str(cid) for cid in cids if cid not in COMP_CACHE}
            with multiprocessing.Pool(20) as pool:
                all_comp_data = pool.map(self.fetch_comp, cids)
            for cid, comp_data in zip(cids, all_comp_data):
                COMP_CACHE[cid] = comp_data
            data = COMP_CACHE
        else:
            data = requests.get(URLS[api]).json()
        
        # Do not add to cache if you are running no cache set up. This ensures no staleness at the cost of speed.
        if self.client_type not in [MetaTFTClientType.NO_CACHE]:
            CACHE[api.value] = data
        
        # Online and offline option stores what we fetched back to disk.
        if self.client_type in [MetaTFTClientType.ONLINE_AND_OFFLINE]:
            path = Path(CACHE_PATH)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                json.dump(CACHE, f)
        return data
        
    
    def fetch_champ(self, champ_id: str) -> dict:
        """Fetches champ data for a particular champion."""
        global CHAMP_CACHE
        if champ_id not in CHAMP_CACHE:
            params = {
                "queue": 1100, # Not sure what this does.
                "patch": "current",
                "rank": "CHALLENGER,DIAMOND,GRANDMASTER,MASTER",
                "permit_filter_adjustment": True, # No clue here either.
                "unit": champ_id
            }
            CHAMP_CACHE[champ_id] = requests.get(URLS[MetaTFTApis.CHAMP_ITEMS], params=params).json()
        return CHAMP_CACHE[champ_id]
    
    def fetch_comp(self, comp_id: str, cluster_id: str = str(CLUSTER_ID)) -> dict:
        global COMP_CACHE
        if comp_id not in COMP_CACHE:
            params = {
                'comp': comp_id,
                'cluster_id': cluster_id,
            }
            COMP_CACHE[comp_id] = requests.get(URLS[MetaTFTApis.COMP_DETAILS], params=params).json()
        return COMP_CACHE[comp_id]

def create_client(client_type: MetaTFTClientType = MetaTFTClientType.ONLINE_ONLY):
    """
    Factory function for creating your own MetaTFT singleton. If the param
    `local_cache` is true, then it pulls from disk if it exists.
    """
    global CLIENT
    CLIENT = MetaTFTClient(client_type)

def get_client():
    """
    Gets or creates a singleton of the MetaTFT client and returns it.
    """
    if CLIENT is not None:
        return CLIENT
    return MetaTFTClient()

def get_set_data():
    """
    Fetches raw JSON set data via MetaTFT client singleton.
    """
    return get_client().fetch(MetaTFTApis.SET_DATA)

def get_comp_data():
    """
    Fetches raw JSON comp data via MetaTFT client singleton.
    """
    return get_client().fetch(MetaTFTApis.COMPS_DATA)

def get_champ_item_data(champ_id: str | None = None):
    """
    Fetches raw JSON chamption specific data via MetaTFT client singleton.
    """
    client = get_client()
    if champ_id is None:
        return client.fetch(MetaTFTApis.CHAMP_ITEMS)
    else:
        return {champ_id: client.fetch_champ(champ_id)}

def get_comp_details(comp_id: str | int | None = None, cluster_id: int = CLUSTER_ID):
    """
    Fetches raw JSON composition (or cluster) data via MetaTFT client singleton.
    """
    client = get_client()
    if comp_id is None:
        return client.fetch(MetaTFTApis.COMP_DETAILS)
    else:
        return {str(comp_id): client.fetch_comp(str(comp_id), str(CLUSTER_ID))}
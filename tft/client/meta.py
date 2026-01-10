
from enum import Enum
import json
from pathlib import Path
import attrs
import requests
import tft.ql.expr as ql
import multiprocessing


class MetaTFTApis(Enum):
    COMPS_DATA = 'comps_data'
    COMP_STATS = 'comp_stats'
    COMP_DETAILS = 'comp_details'
    SET_DATA = 'set_data'
    CHAMP_ITEMS = 'champ_items'

URLS = {
    MetaTFTApis.COMPS_DATA: "https://api-hc.metatft.com/tft-comps-api/comps_data",
    MetaTFTApis.SET_DATA: "https://data.metatft.com/lookups/TFTSet16_latest_en_us.json",
    MetaTFTApis.CHAMP_ITEMS: "https://api-hc.metatft.com/tft-stat-api/unit_detail",
    MetaTFTApis.COMP_DETAILS: "https://api-hc.metatft.com/tft-comps-api/comp_details"
}

CACHE_PATH = 'res/cache/cache.json'

CACHE = {}
CHAMP_CACHE = {}
COMP_CACHE = {}
CLIENT = None

@attrs.define
class MetaTFTClient:
    local_cache: bool = attrs.field(default=False)

    def __attrs_post_init__(self):
        """Maybe load caches."""
        global CACHE
        global CHAMP_CACHE
        global COMP_CACHE
        path = Path(CACHE_PATH)
        if self.local_cache and path.exists():
            with open(path, 'r') as f:
                CACHE = json.load(f)
            if MetaTFTApis.CHAMP_ITEMS in CACHE:
                CHAMP_CACHE = CACHE[MetaTFTApis.CHAMP_ITEMS.value]
            if MetaTFTApis.COMP_DETAILS in CACHE:
                COMP_CACHE = CACHE[MetaTFTApis.COMP_DETAILS.value]

    def fetch(self, api: MetaTFTApis) -> dict:
        global CACHE
        global CHAMP_CACHE
        """Fetches given API and returns a dict. Subsequent requests are cached."""
        if api.value in CACHE:
            return CACHE[api.value]
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
            internal_cid = results_q.idx('cluster_id').eval()
            # Need internal CID and cluster id to query.
            cids = {(internal_cid, str(cid)) for cid in cids if cid not in COMP_CACHE}
            with multiprocessing.Pool(20) as pool:
                all_comp_data = pool.map(self.fetch_comp, cids)
            for cid, comp_data in zip(cids, all_comp_data):
                COMP_CACHE[cid] = comp_data
            data = COMP_CACHE
        else:
            data = requests.get(URLS[api]).json()
        CACHE[api.value] = data
        if self.local_cache:
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
    
    def fetch_comp(self, cid_pair: tuple[str, str]) -> dict:
        internal_cid, cid = cid_pair
        global COMP_CACHE
        if cid not in COMP_CACHE:
            params = {
                'comp': cid,
                'cluster_id': internal_cid
            }
            COMP_CACHE[cid] = requests.get(URLS[MetaTFTApis.COMP_DETAILS], params=params).json()
        return COMP_CACHE[cid]

def create_client(local_cache: bool = False):
    global CLIENT
    CLIENT = MetaTFTClient(local_cache)

def get_client():
    if CLIENT is not None:
        return CLIENT
    return MetaTFTClient()

def get_set_data():
    return get_client().fetch(MetaTFTApis.SET_DATA)

def get_comp_data():
    return get_client().fetch(MetaTFTApis.COMPS_DATA)

def get_champ_item_data(champ_id: str | None = None):
    client = get_client()
    if champ_id is None:
        return client.fetch(MetaTFTApis.CHAMP_ITEMS)
    else:
        return {champ_id: client.fetch_champ(champ_id)}

def get_comp_details(cid: str | int | None = None):
    client = get_client()
    if cid is None:
        return client.fetch(MetaTFTApis.COMP_DETAILS)
    else:
        return {str(cid): client.fetch_comp(str(cid))}

from enum import Enum
import requests
import tft.ql.expr as ql
import multiprocessing


class MetaTFTApis(Enum):
    COMPS_DATA = 'comps_data'
    SET_DATA = 'set_data'
    CHAMP_ITEMS = 'champ_items'

URLS = {
    MetaTFTApis.COMPS_DATA: "https://api2.metatft.com/tft-comps-api/comps_data",
    MetaTFTApis.SET_DATA: "https://data.metatft.com/lookups/TFTSet12_latest_en_us.json",
    MetaTFTApis.CHAMP_ITEMS: "https://api2.metatft.com/tft-stat-api/unit_detail"
}

class MetaTFTClient:
    def fetch(self, api: MetaTFTApis) -> dict:
        """Fetches given API and returns a dict."""
        if api == MetaTFTApis.CHAMP_ITEMS:
            champ_ids = ql.query(self.fetch(MetaTFTApis.SET_DATA)).idx('units').filter(ql.idx('traits').len().gt(0)).map(ql.idx('apiName')).vals().eval()
            with multiprocessing.Pool(20) as pool:
                all_champ_data = pool.map(self.fetch_champ, champ_ids)
            return {champ_id: champ_data for champ_id, champ_data in zip(champ_ids, all_champ_data)}
        return requests.get(URLS[api]).json()
    
    def fetch_champ(self, champ_id: str) -> dict:
        """Fetches champ data for a particular champion."""
        params = {
            "queue": 1100, # Not sure what this does.
            "patch": "current",
            "rank": "CHALLENGER,DIAMOND,GRANDMASTER,MASTER",
            "permit_filter_adjustment": True, # No clue here either.
            "unit": champ_id
        }
        return requests.get(URLS[MetaTFTApis.CHAMP_ITEMS], params=params).json()
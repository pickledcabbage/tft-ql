
from enum import Enum
import requests


class MetaTFTApis(Enum):
    COMPS_DATA = 'comps_data'
    SET_DATA = 'set_data'

URLS = {
    MetaTFTApis.COMPS_DATA: "https://api2.metatft.com/tft-comps-api/comps_data",
    MetaTFTApis.SET_DATA: "https://data.metatft.com/lookups/TFTSet12_latest_en_us.json",
}

class MetaTFTClient:
    def query(self, api: MetaTFTApis) -> dict:
        """Queries given API and returns a dict."""
        return requests.get(URLS[api]).json()
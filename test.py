from typing import Any
from tft.client.meta import MetaTFTClient, MetaTFTApis
from tft.ql.expr import Query
from tft.ql.util import splay

client = MetaTFTClient()

m = client.query(MetaTFTApis.COMPS_DATA)

# q = Query(m).select('hello').eval()
# splay(m)
print(m)

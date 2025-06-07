import pymongo

import tft.ql.expr as ql
from tft.config import DB

def main():
    """
    Creates session and session_events tables in MongoDB.
    """

    client = pymongo.MongoClient(DB)
    tft_db = client['tft']
    session_col = tft_db['session']

    # Sessions schema:
    # ts        - When session started.
    # join_code - Code to join the session through UI.
    # id        - ID of the session. Unique to each temporal session.

    # Create session collection.
    session_col.create_index([('ts', pymongo.DESCENDING)])
    session_col.create_index([('join_code', pymongo.ASCENDING)], unique=True)

    # Session events schema:
    # ts         - When event happened
    # session_id - ID of the session this is associated with.
    # user_id    - A user tag that was used to create this event.
    # tool       - The tool that was used.
    # data       - The data to save.

    # Create session events.
    events_col = tft_db['session_events']
    events_col.create_index([('ts', pymongo.DESCENDING)])

if __name__ == '__main__':
    main()
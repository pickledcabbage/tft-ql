""" Run the interpreter with this command:
poetry run python tft/interpreter/server.py
"""
# Import all commands and registry.
import pymongo
import pandas as pd
import uuid
import time
import attrs
import random
import tft.client.meta as meta
import tft.interpreter.commands.api as commands
from tft.interpreter.commands.registry import ValidationException
import tft.ql.expr as ql

from flask import Flask, request
from flask_cors import CORS, cross_origin

from tft.config import DB, IP, PORT

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

def get_ts() -> pd.Timestamp:
    '''Creates a timestamp to use for database sessions.'''
    return pd.Timestamp.now()

def create_event(session_id: str, user_id: str, tool: str, data: str):
    '''Creates an event for the session.'''
    client = pymongo.MongoClient(DB)['tft']['session_events']
    client.insert_one({
        'ts': int(get_ts().timestamp()),
        'session_id': session_id,
        'user_id': user_id,
        'tool': tool,
        'data': data
    })

@app.route('/set_info')
@cross_origin()
def get_set_info():
    '''Endpoint to fetch set info.'''
    tft_set = ql.query(meta.get_comp_data()).idx('tft_set').eval()

    # Items.
    all_set_data = ql.query(meta.get_set_data())
    items = all_set_data.idx('items').map(ql.sub(
        {
            'apiName': ql.idx('apiName'),
            'composition': ql.idx('composition'),
            'name': ql.idx('name')
        }
    )).eval()

    # Traits.
    traits = all_set_data.idx('traits').filter(ql.contains('units')).map(ql.sub({
        'apiName': ql.idx('apiName'),
        'name': ql.idx('name'),
        'tiers': ql.idx('effects').map(ql.idx('minUnits')),
        'units': ql.idx('units').map(ql.idx('unit'))
    })).eval()
    # The champs data doesn't use the api name for traits.
    soft_to_hard_traits = {x['name']: x['apiName'] for x in traits}

    # Units.
    champs = all_set_data.idx('units').filter(ql.idx('traits').length().gt(0)).map(ql.sub({
        'apiName': ql.idx('apiName'),
        'name': ql.idx('name'),
        'traits': ql.idx('traits').map(ql.replace(soft_to_hard_traits)),
        'cost': ql.idx('cost')
    })).eval()

    return {
        'tft_set': tft_set,
        'items': items,
        'traits': traits,
        'champs': champs
    }

@app.route('/test')
@cross_origin()
def read_root():
    '''Endpoint that runs core interpreter commands while we migrate to a frontend.'''
    query = request.args.get('query')
    session_id = request.args.get('session_id')
    user_id = request.args.get('user_id')

    user_id = user_id if user_id is not None else 'anon'
    if query is None:
        return {'data': ''}
    
    # Old interpreter code.
    inp = query.strip().lower()
    parts = [part for part in inp.split(' ') if part != ''] # We shouldn't break with multiple spaces.
    command_name = parts[0]
    args = parts[1:]

    if command_name not in commands.COMMAND_REGISTRY:
        return {'data': f"Command not found: {command_name}"}
    command = commands.COMMAND_REGISTRY[command_name]

    try:
        validated_outputs = command.validate(args)
        outputs = command.execute(validated_outputs)
        # Store an event.
        if session_id is not None:
            create_event(session_id, user_id, 'QUERY', query)

        return {'data': command.render(outputs)}
    except ValidationException as e:
        return {'error': str(e)}
    # Don't catch.

@app.route('/session/create', methods=['GET'])
@cross_origin()
def create_session():
    '''Creates a session.'''
    ts = get_ts()
    day_ago = ts + pd.Timedelta(days=-1)
    client = pymongo.MongoClient(DB)['tft']['session']
    session = None
    # Try to create session.
    for _ in range(5):
        code = ''.join([str(random.randint(0, 9)) for i in range(4)])
        maybe_session = client.find_one({'join_code': code, 'ts': {'$gt': int(day_ago.timestamp())}})
        if maybe_session is None:
            # Create a session.
            session = {
                'join_code': code,
                'ts': int(ts.timestamp()),
                'id': str(uuid.uuid4()),
            }
            client.insert_one(session)
            break
    if session is None:
        return {
            'connected': False,
            'error': 'Failed to create a session'
        }
    
    return {
        'join_code': session['join_code'],
        'id': session['id'],
        'connected': True
    }

@app.route('/session/<join_code>', methods=['GET'])
@cross_origin()
def join_session(join_code: str):
    '''Joins an existing session.'''
    ts = get_ts()
    day_ago = ts + pd.Timedelta(days=-1)
    client = pymongo.MongoClient(DB)['tft']['session']
    maybe_session = client.find_one({'join_code': join_code, 'ts': {'$gt': int(day_ago.timestamp())}})
    if maybe_session is None:
        return {
            'connected': False
        }
    # Maybe we refresh the session?
    return {
        'id': maybe_session['id'],
        'join_code': join_code,
        'connected': True
    }

@app.route('/session/<session_id>/events', methods=['GET'])
@cross_origin()
def get_session_events(session_id: str):
    '''Gets all events for a session from a particular timestamp.'''
    ts = request.args.get('ts')
    if ts is None:
        return {
            'error': 'No ts passed.'
        }
    ts = int(ts)
    client = pymongo.MongoClient(DB)['tft']['session']
    day_ago = get_ts() + pd.Timedelta(days=-1)
    maybe_session = client.find_one({'id': session_id, 'ts': {'$gt': int(day_ago.timestamp())}})
    if maybe_session is None:
        return {
            'error': 'Session not found.'
        }
    # Only query up to a day ago.
    ts = max(ts, int(day_ago.timestamp()))
    client = pymongo.MongoClient(DB)['tft']['session_events']
    events = [{'user_id': event['user_id'], 'ts': event['ts'], 'tool': event['tool'], 'data': event['data']} for event in client.find({'session_id': session_id, 'ts': {'$gt': ts}})]
    return {
        'events': events,
        'connected': True,
    }

   
@app.route('/alias/<tft_set>/<alias_type>', methods=['GET'])
@cross_origin()
def get_item_aliases(tft_set: str, alias_type: str):
    client = pymongo.MongoClient(DB)['tft']['alias']
    return {
        'aliases': [
            {'alias': i['alias'], 'value': i['value']} for i in client.find({'set': tft_set, 'type': alias_type})
        ]
    }


if __name__ == '__main__':
    # Flask server hates multiprocessing's pool.
    print('Warming caches. Flask server hates multiprocessing otherwise.')
    commands.COMMAND_REGISTRY['warm'].execute()
    print('Caches warmed, starting server.')

    app.run(host=IP, port=PORT)

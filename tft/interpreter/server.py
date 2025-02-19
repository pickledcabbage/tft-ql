""" Run the interpreter with this command:
poetry run python tft/interpreter/server.py
"""
# Import all commands and registry.
import uuid
import time
import attrs
import random
import tft.client.meta as meta
import tft.interpreter.commands.api as commands
from tft.interpreter.commands.registry import ValidationException

from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

# Our session database for now.
SESSIONS = dict()

@attrs.define
class Session:
    join_code: str = attrs.field()
    events: dict[int, tuple[str, str]] = attrs.define()

    # This can't handle simultaneous events, lol.
    def get_events(self, ts: int = 0) -> list[tuple[int, str]]:
        return list(filter(lambda item: item[0] > ts, self.events.items()))
    
    def add_event(self, event: str, id: str) -> int:
        ts = int(time.time())
        self.events[ts] = (event, id)
        return ts
        

def generate_join_code():
    def gen():
        return ''.join([str(random.randint(0, 9)) for i in range(4)])
    # This is inefficient, but works for now.
    join_code = gen()
    while (join_code in SESSIONS):
        join_code = gen()
    return join_code

@app.route('/test')
@cross_origin()
def read_root():
    query = request.args.get('query')
    if query is None:
        return {'data': ''}
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
        return command.render(outputs)
    except ValidationException as e:
        return {'error': str(e)}
    # Don't catch.

@app.route('/session/create', methods=['GET'])
@cross_origin()
def create_session():
    id = str(uuid.uuid4())[:6]
    join_code = generate_join_code()
    SESSIONS[join_code] = Session(join_code=join_code, events=dict())
    return {
        'id': id,
        'join_code': join_code,
        'connected': True,
    }

@app.route('/session/<join_code>', methods=['GET'])
@cross_origin()
def join_session(join_code: str):
    id = str(uuid.uuid4())[:6]
    if join_code not in SESSIONS:
        return {
            'connected': False,
        }
    return {
        'id': id,
        'join_code': join_code,
        'connected': True
    }

@app.route('/session/<join_code>/events', methods=['GET', 'POST'])
@cross_origin()
def get_events(join_code):
    if join_code not in SESSIONS:
            return {
                'connected': False
            }
    if request.method == 'GET':
        ts = request.args.get('ts', type=int)
        if ts is None:
            ts = 0
        return {
            'connected': True,
            'events': SESSIONS[join_code].get_events(ts)
        }
    elif request.method == 'POST':
        data = request.get_json()
        print(data)
        if 'event' not in data:
            return {
                'connected': True,
                'error': 'No event field passed.'
            }
        if 'id' not in data:
            return {
                'connected': True,
                'error': 'No id field passed.'
            }

        ts = SESSIONS[join_code].add_event(data['event'], data['id'])
        return {
            'connected': True,
            'ts': ts,
        }



if __name__ == '__main__':
    # Flask server hates multiprocessing's pool.
    print('Warming caches. Flask server hates multiprocessing otherwise.')
    commands.COMMAND_REGISTRY['warm'].execute()
    print('Caches warmed, starting server.')

    app.run(host='0.0.0.0', port=9000)

""" Run the interpreter with this command:
poetry run python tft/interpreter/server.py
"""
# Import all commands and registry.
import argparse
import json
import tft.client.meta as meta
import tft.interpreter.commands.api as commands
from tft.interpreter.commands.registry import ValidationException

from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/test')
@cross_origin()
def read_root():
    query = request.args.get('query')
    if query is None:
        return {'data': ''}
    print(query)
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
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # Flask server hates multiprocessing's pool.
    print('Warming caches. Flask server hates multiprocessing otherwise.')
    commands.COMMAND_REGISTRY['warm'].execute()
    print('Caches warmed, starting server.')

    app.run(host='0.0.0.0', port=9000)

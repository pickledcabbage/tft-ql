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


if __name__ == '__main__':
    # Flask server hates multiprocessing's pool.
    print('Warming caches. Flask server hates multiprocessing otherwise.')
    commands.COMMAND_REGISTRY['warm'].execute()
    print('Caches warmed, starting server.')

    app.run(host='0.0.0.0', port=9000)

# PROMPT = "\n> "
# BLANK_COMMAND = ''

# class ServerInterpreter:
#     """This is a server that receives data, feeds it into an interpreter
#     and returns back a result."""

#     def run(self):
#         """This function runs the main loop of the command line interpreter."""
#         print("Starting interpreter, use command 'help' for info.")
#         inp = '' # Something that we aren't using.
#         while True:
#             inp = input(PROMPT)
#             inp = inp.strip()
#             if inp == BLANK_COMMAND:
#                 continue
#             elif inp in commands.QUIT_COMMANDS:
#                 break
#             parts = [part for part in inp.split(' ') if part != ''] # We shouldn't break with multiple spaces.
#             command_name = parts[0]
#             args = parts[1:]

#             if command_name not in commands.COMMAND_REGISTRY:
#                 print(f"Command not found: {command_name}")
#                 continue
#             command = commands.COMMAND_REGISTRY[command_name]

#             try:
#                 validated_outputs = command.validate(args)
#                 outputs = command.execute(validated_outputs)
#                 command.print(outputs)
#             except ValidationException as e:
#                 print(e)
#             # except Exception as e:
#             #     print(f"Command unexpectedly failed: {e}")


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(
#         prog='TFT Interpreter',
#         description='Provides helpful commands to play TFT.')
#     parser.add_argument('-l', '--local', action='store_true')
#     args = parser.parse_args()
#     if args.local:
#         # Create a local client.
#         meta.create_client(True)
#     interpreter = Interpreter()
#     interpreter.run()
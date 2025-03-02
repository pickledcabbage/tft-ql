""" Run the interpreter with this command:
poetry run python tft/interpreter/core.py
"""
# Import all commands and registry.
import argparse
import tft.client.meta as meta
import tft.interpreter.commands.api as commands
from tft.interpreter.commands.registry import ValidationException

PROMPT = "\n> "
BLANK_COMMAND = ''

class Interpreter:
    """This is an interpreter for command line commands."""

    def run(self):
        """This function runs the main loop of the command line interpreter."""
        print("Starting interpreter, use command 'help' for info.")
        inp = '' # Something that we aren't using.
        while True:
            inp = input(PROMPT)
            inp = inp.strip()
            if inp == BLANK_COMMAND:
                continue
            elif inp in commands.QUIT_COMMANDS:
                break
            parts = [part for part in inp.split(' ') if part != ''] # We shouldn't break with multiple spaces.
            command_name = parts[0]
            args = parts[1:]

            if command_name not in commands.COMMAND_REGISTRY:
                print(f"Command not found: {command_name}")
                continue
            command = commands.COMMAND_REGISTRY[command_name]

            try:
                validated_outputs = command.validate(args)
                outputs = command.execute(validated_outputs)
                print(command.render(outputs))
            except ValidationException as e:
                print(e)
            # except Exception as e:
            #     print(f"Command unexpectedly failed: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='TFT Interpreter',
        description='Provides helpful commands to play TFT.')
    parser.add_argument('-l', '--local', action='store_true')
    args = parser.parse_args()
    if args.local:
        # Create a local client.
        meta.create_client(True)
    interpreter = Interpreter()
    interpreter.run()


from typing import Any, override
from tft.interpreter.commands.registry import Command, register

__all__ = ["PrintHelloWorld"]

@register(name='hello')
class PrintHelloWorld(Command):
    @override
    def validate(self, inputs=None) -> Any:
        pass

    @override
    def execute(self, inputs=None) -> Any:
        return None
    
    @override
    def print(self, outputs=None) -> None:
        print("Hello world!")
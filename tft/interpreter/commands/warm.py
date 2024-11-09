


from typing import Any, override
import tft.client.meta as meta
from tft.interpreter.commands.registry import Command, ValidationException, register


@register(name='warm')
class WarmUpCommand(Command):
    
    @override
    def validate(self, inputs: list | None = None) -> Any:
        if inputs is None:
            raise ValidationException("Parameter to inputs cannot be none.")
        if len(inputs) != 0:
            raise ValidationException("No params should be passed.")
        return None
    
    @override
    def execute(self, inputs: Any = None) -> Any:
        meta.get_comp_data()
        meta.get_champ_item_data()
        meta.get_set_data()
        meta.get_comp_details()
    
    @override
    def render(self, outputs: Any = None) -> str:
        return 'Caches are warm.'
    
    @override
    def name(self) -> str:
        return "Warmup Caches"
    
    @override
    def description(self) -> str:
        return "This command downloads all info locally, so that futures requests are fast.\nUsage: warm"
        
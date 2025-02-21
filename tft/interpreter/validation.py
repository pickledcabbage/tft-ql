from abc import abstractmethod
from collections import defaultdict
from enum import Enum
from typing import override
import attrs

from tft.interpreter.commands.registry import ValidationException
from tft.queries.aliases import get_champ_aliases, get_hard_trait_aliases, get_item_aliases, get_trait_aliases
from tft.queries.items import ItemType, get_completed_items, get_components

class EntityType(Enum):
    CHAMPION = 'champion'
    ITEM = 'item'
    TRAIT = 'trait'
    INTEGER = 'integer'
    LEVEL = 'level'
    CLUSTER_ID = 'cluster_id'
    FIELD = 'field'

@attrs.define
class Entity:
    entity_type: EntityType = attrs.field()
    value: str = attrs.field()

@attrs.define
class Validation:
    """Base class for validations."""

    @abstractmethod
    def convert(self, inputs: list[str]) -> tuple[list[Entity], None | str, list[str]]:
        """Converts as many of the inputs as possible and return 3 things:
          1. A list of the converted names.
          2. A failure string if it failed to convert anything.
          3. The rest of the input which it failed to convert.
          """
        raise NotImplementedError('A Validation needs to implement convert().')
    
    def represent(self) -> str:
        """Prints the representation of this validation."""
        raise NotImplementedError('A Validation needs a represent() method.')

@attrs.define
class Sequence(Validation):
    validations: list[Validation] = attrs.field()

    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        leftovers = inputs[:]
        output = []
        validation_idx = 0
        while len(leftovers) > 0:
            if validation_idx >= len(self.validations):
                raise ValidationException('Validations exhausted.')
            validation = self.validations[validation_idx]
            converted, error, temp = validation.convert(leftovers)
            leftovers = temp
            if error is not None:
                return output, error, leftovers
            output.extend(converted)
            validation_idx = validation_idx + 1
        return output, None, []
    
    @override
    def represent(self) -> str:
        return ', '.join([validation.represent() for validation in self.validations])

@attrs.define
class Many(Validation):
    validation: Validation = attrs.field()

    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        leftovers = inputs[:]
        output = []
        while len(leftovers) > 0:
            converted, error, temp = self.validation.convert(leftovers)
            leftovers = temp
            if error is not None or len(converted) == 0:
                return output, error, leftovers
            output.extend(converted)
        return output, None, []
    
    @override
    def represent(self) -> str:
        return f"MANY({self.validation.represent()})"

@attrs.define
class Or(Validation):
    validations: list[Validation] = attrs.field()

    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        failure_strings = []
        for validation in self.validations:
            converted, error, leftover = validation.convert(inputs)
            if error is None:
                return converted, None, leftover
            failure_strings.append(error)
        return [], "[OR] None satisfied: " + ', '.join(failure_strings), inputs[:]
    
    @override
    def represent(self) -> str:
        return f"OR({', '.join([validation.represent() for validation in self.validations])})"

@attrs.define
class Optional(Validation):
    validation: Validation = attrs.field()

    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        converted, error, leftover = self.validation.convert(inputs[:])
        if error is not None:
            return [], None, inputs[:]
        return converted, None, leftover
    
    @override
    def represent(self) -> str:
        return f"?{self.validation.represent()}"

@attrs.define
class IsChampion(Validation):
    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        if len(inputs) == 0:
            return [], "No champ name to convert", inputs[:]
        champ = inputs[0]
        if champ not in get_champ_aliases():
            return [], f"Champ alias {champ} not found.", inputs[:]
        return [Entity(EntityType.CHAMPION, get_champ_aliases()[champ])], None, inputs[1:]

    @override
    def represent(self) -> str:
        return "IS_CHAMPION"

@attrs.define
class IsItem(Validation):
    item_type: ItemType | None = attrs.field(default=None)

    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        if len(inputs) == 0:
            return [], "No item name to convert", inputs[:]
        first = inputs[0]
        if first not in get_item_aliases():
            return [], f"Item alias {first} not found.", inputs[:]
        converted_item_name = get_item_aliases()[first]
        if self.item_type is not None and self.item_type == ItemType.COMPLETED:
            if converted_item_name not in get_completed_items():
                raise ValidationException(f"Item alias is not of a completed item: {first}")
        elif self.item_type is not None and self.item_type == ItemType.COMPONENT:
            if converted_item_name not in get_components():
                raise ValidationException(f"Item alias is not of a component: {first}")
        return [Entity(EntityType.ITEM, converted_item_name)], None, inputs[1:]

    @override
    def represent(self) -> str:
        additional_info = ""
        if self.item_type is not None:
            additional_info = f"_{self.item_type.value}"
        return f"IS_ITEM{additional_info}"

@attrs.define
class IsTrait(Validation):
    is_hard: bool = attrs.field(default=True)

    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        if len(inputs) == 0:
            return [], "No trait name to convert", inputs[:]
        first = inputs[0]
        alias_map = get_hard_trait_aliases() if self.is_hard else get_trait_aliases()
        if first not in alias_map:
            return [], f"Trait {'(HARD)' if self.is_hard else '(SOFT)'} alias {first} not found.", inputs[:]
        return [Entity(EntityType.TRAIT, alias_map[first])], None, inputs[1:]

    @override
    def represent(self) -> str:
        return "IS_TRAIT"

@attrs.define
class IsInteger(Validation):
    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        if len(inputs) == 0:
            return [], "No number to convert", inputs[:]
        first = inputs[0]
        try:
            number = int(first)
        except:
            return [], f"Item is not an integer: {first}", inputs[:]
        return [Entity(EntityType.INTEGER, str(number))], None, inputs[1:]

@attrs.define
class IsPrefix(Validation):
    prefix: str = attrs.field()
    val_type: type = attrs.field()
    delim: str = attrs.field()
    entity_type: EntityType = attrs.field()

    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        if len(inputs) == 0:
            return [], "No values to convert", inputs[:]
        first = inputs[0]
        try:
            if first[:len(self.prefix)] != self.prefix:
                raise f'No {self.prefix}'
            values = [self.val_type(i) for i in first[len(self.prefix):].split(',')]
        except:
            return [], f"Value has wrong type: {first}", inputs[:]
        return [Entity(self.entity_type, str(val)) for val in values], None, inputs[1:]


@attrs.define
class IsLevel(Validation):
    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        prefix = IsPrefix('lv:', int, ',', EntityType.LEVEL)
        return prefix.convert(inputs)

@attrs.define
class IsField(Validation): 
    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        if len(inputs) == 0:
            return [], "No number to convert", inputs[:]
        first = inputs[0]
        try:
            if first[:3] not in ['fa:', 'fd:']:
                raise 'No fa: or fd:'
            value = first[3:]
            direction = 'ASC' if first[:3] == 'fa:' else 'DES'
        except:
            return [], f"Item is not a field order: {first}", inputs[:]
        return [Entity(EntityType.FIELD, {'value': value, 'direction': direction})], None, inputs[1:]

@attrs.define
class IsCluster(Validation):
    @override
    def convert(self, inputs: list[str]) -> tuple[list[Entity], str | None, list[str]]:
        prefix = IsPrefix('cid:', int, ',', EntityType.CLUSTER_ID)
        return prefix.convert(inputs)


def evaluate_validation(validation: Validation, inputs: list[str], group: bool = False) -> list[str] | dict[str, list[str]]:
    converted, error, leftover = validation.convert(inputs)
    if error is not None:
        raise ValidationException(error)
    if len(leftover) > 0:
        raise ValidationException(f'Not enough parameters. Parameters should satisfy: {validation.represent()}')
    
    if group:
        output = defaultdict(list)
        for item in converted:
            output[item.entity_type.value].append(item.value)
        return output
    return [item.value for item in converted]
from abc import abstractmethod
from enum import Enum
from typing import Any, Callable, Self, override
from attrs import define, field, evolve
from tft.ql.util import splay

def identity(x: Any) -> Any:
    return x

class TransformType(Enum):
    SINGLE = 'single'
    MULTI_LIST = 'multi_list'
    MULTI_DICT = 'multi_dict'

@define
class Transform:
    @abstractmethod
    def transform(self, _m: dict) -> Any:
        raise NotImplemented('Need to implement transform')

    @abstractmethod
    def get_type(self) -> TransformType:
        return TransformType.SINGLE

@define
class Select(Transform):
    path: list[str] = field(converter=lambda x: x.split('.'))

    @override
    def transform(self, m: dict | list) -> Any:
        assert isinstance(m, dict) or isinstance(m, list), f"Is not of type dict or list: {type(m)}"
        output = m
        for field in self.path:
            if isinstance(output, dict):
                assert field in output, f"No field {field} in path {'.'.join(self.path)}, available keys: {','.join(output.keys())}"
                output = output[field]
            elif isinstance(output, list):
                idx = int(field)
                assert idx < len(output), f"Index {idx} out of range [0,{len(output)})."
                output = output[idx]
            else:
                raise Exception("Can only select on dicts and lists")
        return output

@define
class Map(Transform):
    key_func: Callable[[Any], Any] = field(default=identity)
    # val_func: Callable[[Any], Any] = field(default=identity)
    @override
    def transform(self, m: dict | list) -> dict[Any, Any]:
        if isinstance(m, list):
            return {self.key_func(idx): m[idx] for idx in range(len(m))}
        elif isinstance(m, dict):
            return {self.key_func(key): val for key, val in m.items()}
        else:
            raise Exception(f"Mapping incorrect type: {type(m)}")
    
    @override
    def get_type(self) -> TransformType:
        return TransformType.MULTI_DICT

@define
class Top(Transform):
    num: int = field(default=1)
    reverse: bool = field(default=False)

    @override
    def transform(self, m: dict | list) -> Any:
        assert isinstance(m, list), "Can only use top() on a list"
        return m[0:self.num] if not self.reverse else m[-self.num:]

@define
class Result:
    value: Any | None = field(default=None)
    results: dict | list | None = field(default = None)

    def __attrs_post_init__(self):
        assert self.results is not None or self.value is not None

    def is_val(self) -> bool:
        return self.value is not None
    
    def update(self, transform: Transform) -> None:
        if not self.is_val():
            assert self.results is not None
            if isinstance(self.results, dict):
                for result in self.results.values():
                    result.update(transform)
            elif isinstance(self.results, list):
                for result in self.results:
                    result.update(transform)
            else:
                raise Exception(f"Encounter bad nested result with results type: {type(self.results)}")
        else:
            assert self.value is not None
            t_type = transform.get_type()
            match t_type:
                case TransformType.SINGLE:
                    self.value = transform.transform(self.value)
                case TransformType.MULTI_DICT:
                    temp = transform.transform(self.value)
                    self.value = None
                    self.results = {k: Result(value=v) for k,v in temp.items()}
                case TransformType.MULTI_LIST:
                    temp = transform.transform(self.value)
                    self.value = None
                    self.results = [Result(value=v) for v in temp]
    
    def to_dict(self) -> Any:
        if self.is_val():
            return self.value
        assert self.results is not None
        if isinstance(self.results, dict):
            return {k: v.to_dict() for k, v in self.results.items()}
        return [v.to_dict() for v in self.results]

@define
class Query:
    m: dict = field()
    transforms: list[Transform] = field(factory=list)

    def _evolve(self, transform: Transform) -> Self:
        return evolve(self, m=self.m, transforms=self.transforms + [transform])

    def select(self, path: str) -> Self:
        return self._evolve(Select(path))
    
    def map(self, key_func: Callable[[Any], Any] = identity) -> Self:
        return self._evolve(Map(key_func))
    
    def top(self, num: int = 1, reverse: bool = False) -> Self:
        return self._evolve(Top(num, reverse))
    
    def eval(self) -> Any:
        result = Result(self.m)
        for transform in self.transforms:
            result.update(transform)
        
        return result.to_dict()
    
    def splay(self, depth: int | None = None) -> None:
        splay(self.eval(), depth=depth)
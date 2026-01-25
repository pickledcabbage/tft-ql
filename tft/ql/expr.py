from abc import abstractmethod
from enum import Enum
import json
import copy
from typing import Any, Callable, Iterable, Self, override
from attrs import define, field, evolve
from tft.ql.util import splay
import pandas as pd

def identity(x: Any) -> Any:
    return x

_all = all
_any = any

# Forward declaration.
class Query:
    def eval(self, m: Any) -> Any:
        raise NotImplemented('Need to implement query')

class TransformType(Enum):
    SINGLE = 'single'
    MULTI = 'multi'

@define
class Transform:
    @abstractmethod
    def transform(self, m: Any) -> Any:
        raise NotImplemented('Need to implement transform')

    @abstractmethod
    def get_type(self) -> TransformType:
        return TransformType.SINGLE

@define
class Noop(Transform):
    @override
    def transform(self, m: dict | list) -> Any:
        return m

@define
class Index(Transform):
    path: list[str] = field(converter=lambda x: x.split('.'))

    @override
    def transform(self, m: dict | list) -> Any:
        assert isinstance(m, dict) or isinstance(m, list) or isinstance(m, tuple), f"Is not of type dict or list: {type(m)}"
        output = m
        for field in self.path:
            if isinstance(output, dict):
                assert field in output, f"No field {field} in path {'.'.join(self.path)}, available keys: {','.join(output.keys())}"
                output = output[field]
            elif isinstance(output, list) or isinstance(output, tuple):
                idx = int(field)
                assert idx < len(output), f"Index {idx} out of range [0,{len(output)})."
                output = output[idx]
            else:
                raise Exception("Can only select on dicts, lists, and tuples")
        return output

@define
class Map(Transform):
    query: Query = field(default=Query())
    key_query: Query | None = field(default=None)
    on_key: bool = field(default=False)

    @override
    def transform(self, m: dict | list) -> list | dict:
        if isinstance(m, list):
            if self.key_query is not None:
                if self.on_key:
                    raise Exception("Can only use on_key flag on dicts.")
                return {self.key_query.eval(i): self.query.eval(i) for i in m}
            else:
                return [self.query.eval(i) for i in m]
        elif isinstance(m, dict):
            if self.key_query is not None:
                return {self.key_query.eval(key if self.on_key else val): self.query.eval(val) for key, val in m.items()}
            else:
                return {key: self.query.eval(val) for key, val in m.items()}
        else:
            raise Exception(f"Mapping incorrect type: {type(m)}")

@define
class Top(Transform):
    num: int = field(default=1)
    reverse: bool = field(default=False)

    @override
    def transform(self, m: dict | list) -> Any:
        assert isinstance(m, list), "Can only use top() on a list"
        return m[0:self.num] if not self.reverse else m[-self.num:]

@define
class Split(Transform):
    delim: str = field(default=',')

    @override
    def transform(self, m: Any) -> Any:
        assert isinstance(m, str), "Can only use split() on a string"
        return m.split(self.delim)
    
    # @override
    # def get_type(self) -> TransformType:
    #     return TransformType.MULTI

@define
class SubQuery(Transform):
    query_map: dict[Any, Query] = field()

    def transform(self, m: dict) -> Any:
        output = {}
        for key, query in self.query_map.items():
            output[key] = query.eval(m)
        return output
    
    def get_type(self) -> TransformType:
        return TransformType.SINGLE

@define
class Extend(Transform):
    sub_query: SubQuery = field()

    def transform(self, m: Any) -> Any:
        output = copy.deepcopy(m)
        sub_output = self.sub_query.transform(m)
        for k, v in sub_output.items():
            output[k] = v
        return output

@define
class Explode(Transform):
    to_field: str = field()

    def transform(self, m: Any) -> Any:
        assert isinstance(m, dict), "Can only explode on a dict field"
        output = []
        for field in m.keys():
            if isinstance(m[field], list):
                for item in m[field]:
                    assert isinstance(item, dict), f"Internal item not of type dict: {type(item)}"
                    new_item = copy.deepcopy(item)
                    new_item[self.to_field] = field
                    output.append(new_item)
            elif isinstance(m[field], dict):
                new_item = copy.deepcopy(m[field])
                new_item[self.to_field] = field
                output.append(new_item)
            else:
                assert False, f"Bad internal dict type for explode: {type(m[field])}"
        return output

@define
class LessThan(Transform):
    other: Any = field()

    def transform(self, m: Any) -> bool:
        return m < self.other

@define
class LessThanEqual(Transform):
    other: Any = field()

    def transform(self, m: Any) -> bool:
        return m <= self.other

@define
class GreaterThan(Transform):
    other: Any = field()

    def transform(self, m: Any) -> bool:
        return m > self.other
    
@define
class GreaterThanEqual(Transform):
    other: Any = field()

    def transform(self, m: Any) -> bool:
        return m >= self.other

@define
class Equal(Transform):
    other: Any = field()

    def transform(self, m: Any) -> bool:
        return m == self.other

@define
class NotEqual(Transform):
    other: Any = field()

    def transform(self, m: Any) -> bool:
        return m != self.other

@define
class Negate(Transform):
    def transform(self, m: Any) -> Any:
        return not m

@define
class _Any(Transform):
    queries: Iterable[Query] = field()

    @override
    def transform(self, m: Any) -> bool:
        return _any(query.eval(m) for query in self.queries)

@define
class All(Transform):
    queries: Iterable[Query] = field()

    @override
    def transform(self, m: Any) -> bool:
        return _all(query.eval(m) for query in self.queries)

@define
class Filter(Transform):
    query: Query = field()

    def transform(self, m: Any) -> Any:
        if isinstance(m, list):
            return [val for val in m if bool(self.query.eval(val))]
        elif isinstance(m, dict):
            return {k: v for k, v in m.items() if bool(self.query.eval(v))}
        else:
            raise Exception(f"Can only filter on list or dict: {type(m)}")

    # def get_type(self) -> TransformType:
    #     return TransformType.MULTI

@define
class Length(Transform):
    def transform(self, m: Any) -> Any:
        return len(m)

@define
class Contains(Transform):
    other: Any = field()

    def transform(self, m: Any) -> bool:
        return self.other in m

@define
class InSet(Transform):
    other: Any = field()

    def transform(self, m: Any) -> Any:
        return m in self.other

@define
class Select(Transform):
    fields: Iterable = field()

    def transform(self, m: Any) -> Any:
        if isinstance(m, list):
            return [m[field] for field in self.fields]
        elif isinstance(m ,dict):
            return {field: m[field] for field in self.fields}
        else:
            raise Exception(f"Can only use with on lists and dicts: {type(m)}")

@define
class Replace(Transform):
    mapping: dict = field()

    def transform(self, m: Any) -> Any:
        assert m in self.mapping, f"Value {m} is not in mapping: {self.mapping}"
        return self.mapping[m]

@define
class Flatten(Transform):
    layers: int = field(default=1)

    def transform(self, m: Any) -> list[Any]:
        output = []
        assert isinstance(m, list), "Can only flatten a list"

        def recurse(v, level):
            if level > self.layers:
                output.append(v)
                return
            if not isinstance(v, list):
                output.append(v)
                return
            for i in v:
                recurse(i, level + 1)
        recurse(m, 0)
        return output

@define
class Unique(Transform):
    def transform(self, m: Any) -> list[Any]:
        assert isinstance(m, list), f"Can only use unique on lists: {type(m)}"
        return list(set(m))

@define
class Keys(Transform):
    def transform(self, m: Any) -> list[Any]:
        assert isinstance(m, dict), f"Can only use keys on dicts: {type(m)}"
        return list(m.keys())

@define
class Values(Transform):
    def transform(self, m: Any) -> list[Any]:
        assert isinstance(m, dict), f"Can only use values on dicts: {type(m)}"
        return list(m.values())

@define
class Only(Transform):
    def transform(self, m: Any) -> Any:
        assert len(m) == 1, f"Can only use only() if there is exactly one output"
        assert isinstance(m, list) or isinstance(m, dict), f"Can only use only() on dicts or lists: {type(m)}"
        if isinstance(m, dict):
            return list(m.values())[0]
        return m[0]

@define
class SortBy(Transform):
    query: Query = field()
    reverse: bool = field()

    def transform(self, m: Any) -> Any:
        assert isinstance(m, list), f"Can only sort lists {type(m)}"
        return sorted(m, key=lambda x: self.query.eval(x), reverse=self.reverse)

@define
class Unary(Transform):
    op: Callable[[Any], Any] = field()

    def transform(self, m: Any) -> Any:
        return self.op(m)

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
            self.value = transform.transform(self.value)
    
    def to_dict(self) -> Any:
        if self.is_val():
            return self.value
        assert self.results is not None
        if isinstance(self.results, dict):
            return {k: v.to_dict() for k, v in self.results.items()}
        return [v.to_dict() for v in self.results]

# Should only be used by Query to represent an empty dataset.
class EmptyDataset:
    pass

@define
class BaseQuery(Query):
    m: Any | EmptyDataset = field(factory=EmptyDataset)
    transforms: list[Transform] = field(factory=list)

    def empty(self) -> bool:
        return isinstance(self.m, EmptyDataset)

    def _evolve(self, transform: Transform) -> Self:
        return evolve(self, m=self.m, transforms=self.transforms + [transform])
    

    # START Transforms.
    def noop(self) -> Self:
        return self._evolve(Noop())

    def idx(self, path: str) -> Self:
        return self._evolve(Index(path))
    
    def map(self, query: Query, key_query: Query | None = None, on_key: bool = False) -> Self:
        return self._evolve(Map(query, key_query, on_key))
    
    def top(self, num: int = 1, reverse: bool = False) -> Self:
        return self._evolve(Top(num, reverse))
    
    def split(self, delim: str = ',') -> Self:
        return self._evolve(Split(delim))
    
    def sub(self, sub_queries: dict[Any, Query]) -> Self:
        return self._evolve(SubQuery(sub_queries))

    def extend(self, sub_queries: dict[Any, Query]) -> Self:
        return self._evolve(Extend(SubQuery(sub_queries)))
    
    def explode(self, to_field: str) -> Self:
        return self._evolve(Explode(to_field))
    
    def filter(self, query: Query) -> Self:
        return self._evolve(Filter(query))
    
    def len(self) -> Self:
        return self._evolve(Length())
    
    def length(self) -> Self:
        return self.len()
    
    def select(self, fields: Iterable) -> Self:
        return self._evolve(Select(fields))
    
    def contains(self, other) -> Self:
        return self._evolve(Contains(other))
    
    def in_set(self, other) -> Self:
        return self._evolve(InSet(other))
    
    def flatten(self, layers: int = 1) -> Self:
        return self._evolve(Flatten(layers))
    
    def uniq(self) -> Self:
        return self._evolve(Unique())
    
    def keys(self) -> Self:
        return self._evolve(Keys())
    
    def vals(self) -> Self:
        return self._evolve(Values())
    
    def values(self) -> Self:
        return self.vals()
    
    def only(self) -> Self:
        return self._evolve(Only())
    
    def sort_by(self, query: Query, reverse: bool = False) -> Self:
        return self._evolve(SortBy(query, reverse))
    
    def unary(self, func: Callable) -> Self:
        return self._evolve(Unary(func))
    
    def replace(self, mapping: dict) -> Self:
        return self._evolve(Replace(mapping))
    
    # Comparison ops.
    def lt(self, other) -> Self:
        return self._evolve(LessThan(other))
    
    def le(self, other) -> Self:
        return self._evolve(LessThanEqual(other))
    
    def gt(self, other) -> Self:
        return self._evolve(GreaterThan(other))
    
    def ge(self, other) -> Self:
        return self._evolve(GreaterThanEqual(other))

    def eq(self, other) -> Self:
        return self._evolve(Equal(other))
    
    def ne(self, other) -> Self:
        return self._evolve(Equal(other))
    
    def neg(self) -> Self:
        return self._evolve(Negate())

    # Boolean operators.

    def all(self, queries: Iterable[Query]) -> Self:
        return self._evolve(All(queries))
    
    def any(self, queries: Iterable[Query]) -> Self:
        return self._evolve(_Any(queries))
    

    # END Transforms.
    
    def eval(self, m: Any | None = None) -> Any:
        assert not self.empty() or m is not None, "Need dataset to evaluate on."
        # Passed `m` should override.
        if m is None:
            m = self.m
        result = Result(m)
        for transform in self.transforms:
            result.update(transform)
        
        return result.to_dict()
    
    def splay(self, depth: int | None = None) -> None:
        splay(self.eval(), depth=depth)
    
    def pp(self, indent: int = 2) -> None:
        print(json.dumps(self.eval(), indent=indent))
    
    def to_pandas(self) -> pd.DataFrame:
        return pd.DataFrame(self.eval())

# Public functions
def noop() -> BaseQuery:
    return query().noop()

def query(m: dict | None = None) -> BaseQuery:
    return BaseQuery(m)

def idx(path: str) -> BaseQuery:
    return query().idx(path)

def map(_query: Query, key_query: Query | None = None, on_key: bool = False) -> BaseQuery:
    return query().map(_query, key_query, on_key)

def top(num: int = 1, reverse: bool = False) -> BaseQuery:
    return query().top(num, reverse)

def split(delim: str = ',') -> BaseQuery:
    return query().split(delim)

def sub(sub_queries: dict) -> BaseQuery:
    return query().sub(sub_queries)

def extend(sub_queries: dict) -> BaseQuery:
    return query().extend(sub_queries)

def filter(_query: Query) -> BaseQuery:
    return query().filter(_query)

def length() -> BaseQuery:
    return query().len()

def select(fields: Iterable) -> BaseQuery:
    return query().select(fields)

def contains(other) -> BaseQuery:
    return query().contains(other)

def flatten(layers: int = 1) -> BaseQuery:
    return query().flatten(layers)

def uniq() -> BaseQuery:
    return query().uniq()

def keys() -> BaseQuery:
    return query().keys()

def vals() -> BaseQuery:
    return query().vals()

def neg() -> BaseQuery:
    return query().neg()

def all(queries: Iterable[Query]) -> BaseQuery:
    return query().all(queries)

def any(queries: Iterable[Query]) -> BaseQuery:
    return query().any(queries)

def sort_by(_query: Query, reverse: bool = False) -> BaseQuery:
    return query().sort_by(_query, reverse)

def unary(func: Callable) -> BaseQuery:
    return query().unary(func)

def replace(mapping: dict) -> BaseQuery:
    return query().replace(mapping)

def in_set(other) -> BaseQuery:
    return query().in_set(other)

def only() -> BaseQuery:
    return query().only()

def explode(to_field: str) -> BaseQuery:
    return query().explode(to_field)
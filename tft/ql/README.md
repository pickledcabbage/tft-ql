# QL
QL simply stands for query language and is used to query JSON files effectively. Instead of using loops and imperative programming you can chain functions together to achieve your desired outcome. This makes QL easier to maintain and much more readable. This document serves as a guide on how to use use QL.

## Basics
### `ql.query(dict | None)`
This constructs either a blank query if no params are passed or a query with a base dictionary. This is the basis of QL and functions can be chained to perform operations. If you do not include a param in this function, then you have to pass a parameter to `eval()` or `splay()` otherwise you will be evaluating the query on nothing.

### `.eval(dict | None)`
This evaluates the query on the given dictionary and returns back whatever the operations evaluate to. If the query was constructed without a base dictionary you are required to pass a dictionary when you `eval()`. This is a terminating command, you cannot follow it with more operations.
```
>>> d = {"a":1}
>>> ql.query(d).eval()
{'a': 1}
```
### `.splay(int)`
Splay prints our levels in a dictionary or list and is used for debugging and researching a JSON. You can specifiy how deep you want splay to go. If `splay()` encounters a list, it will print the length of the list for that level and continue with the first item in the list. This is a terminating command, you cannot follow it with more operations.
```
>>> d = {"a": [{"b": 3, "d": 4}], "c": {"e": 5}}
>>> ql.query(d).splay()
a
  [1]
    b
      3
    d
      4
c
  e
    5
```

## Common
### `.idx(str)`
The index operation lets you select a field in a dictionary or list. This can be chained using the delimiter `.` between fields in the path you want to index into.
```
>>> d = {"a": [{"b": 3, "d": 4}], "c": {"e": 5}}
>>> ql.query(d).idx("a.0.b").eval()
3
```

### `.select(list[str])`
The select operation lets you select fields to keep in the dictionary output.
```
>>> d = {"a": 1, "b": 2, "c": 3}
>>> ql.query(d).select(["a", "b"]).eval()
{'a': 1, 'b': 2}
```

### `.map(Query, Callable[[Any] Any] | None)`
The map operator lets you do the same operation across fields in a level and then returns back to the same spot the map was called but with the new result. You can also specific a function that will map the keys to something you prefer.
```
# List (note the key becomes the index)
>>> d = [{"a": 1, "b": 2}, {"a": 3, "b": 4}, {"a": 5, "b":6}]
>>> ql.query(d).map(ql.idx('a')).eval()
{0: 1, 1: 3, 2: 5}

# Dict (key is the field you are mapping)
>>> d = {"x": {"a": 1, "b": 2}, "y":{"a": 3, "b": 4}, "z":{"a": 5, "b":6}}
>>> ql.query(d).map(ql.idx('a')).eval()
{'x': 1, 'y': 3, 'z': 5}
```

### `.top(int, bool)`
The top operator lets you select the first elements of a list. First param indicates how many elements to select and second param indicates if you want to select in reverse order.
```
>>> d = [{"a": 1}, {"b": 2}, {"c": 3}]
>>> ql.query(d).top(2).eval()
[{'a': 1}, {'b': 2}]
```

### `.len()` or `.length()`
Returns the length of the object. Can be used on anything. Very useful for comparison and filtering operators.
```
>>> d = [{"a": 1}, {"b": 2}, {"c": 3}]
>>> ql.query(d).len().eval()
3
```

### `.vals()` or `.values()`
Returns the values in a list for a particular dictionary level.
```
>>> d = {"a": 1, "b": 2, "c": 3}
>>> ql.query(d).vals().eval()
[1, 2, 3]
```

### `.keys()`
Returns the keys in a list for a particular dictionary level.
```
>>> d = {"a": 1, "b": 2, "c": 3}
>>> ql.query(d).keys().eval()
['a', 'b', 'c']
```

### `.uniq()`
Given a list of objects, returns only the unique ones.
```
>>> d = [1, 1, 2, 2, 3, 4]
>>> ql.query(d).uniq().eval()
[1, 2, 3, 4]
```

## Advanced
### `.sub(dict[Any, Query])`
Given a dictionary of keys to queries, returns back a dictionary of keys to each of those queries applied to the current dictionary. No example yet, needs to be fixed.

### `.filter(Query)`
Applies a query to each value in a list or dictionary and only keeps that values for which the query evaluates to true. See logic operators for how to contruct a boolean query.
```
# Only take all values in a list which have fields "a" less than 3.
>>> d = [{"a": 1}, {"a": 2}, {"a": 3}]
>>> ql.query(d).filter(ql.idx('a').lt(3)).eval()
[{'a': 1}, {'a': 2}]
```

## Logic Operator
Work in Progress.
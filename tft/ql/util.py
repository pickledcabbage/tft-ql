from typing import Any


def splay(m: Any, layer: int = 0, depth: int | None =None) -> None:
    tab = "  "
    if depth is not None and layer > depth:
        return
    if isinstance(m, dict):
        for key in m.keys():
            print(tab * layer + str(key))
            splay(m[key], layer + 1, depth)
    elif isinstance(m, list):
        print(tab * layer + f"[{len(m)}]")
        if len(m) > 0:
            splay(m[0], layer + 1, depth)
    else:
        print(tab * layer + str(m))
"""
Built-in functions for DesiLang.
"""

from typing import Any, List, Callable
import sys


class BuiltinFunction:
    """Wrapper for built-in functions."""
    
    def __init__(self, name: str, func: Callable, param_count: int = -1):
        self.name = name
        self.func = func
        self.param_count = param_count  # -1 means variable number of params
    
    def __call__(self, *args):
        if self.param_count >= 0 and len(args) != self.param_count:
            raise TypeError(f"Function '{self.name}' expects {self.param_count} arguments, got {len(args)}")
        return self.func(*args)


def builtin_length(obj: Any) -> int:
    """Get length of a list or string."""
    if isinstance(obj, (list, str)):
        return len(obj)
    raise TypeError(f"length() expects a list or string, got {type(obj).__name__}")


def builtin_append(lst: List, value: Any) -> None:
    """Append value to a list (modifies in place)."""
    if not isinstance(lst, list):
        raise TypeError(f"append() expects a list as first argument, got {type(lst).__name__}")
    lst.append(value)
    return None


def builtin_pop(lst: List, index: int = -1) -> Any:
    """Remove and return item at index (default last)."""
    if not isinstance(lst, list):
        raise TypeError(f"pop() expects a list as first argument, got {type(lst).__name__}")
    if not lst:
        raise IndexError("pop() from empty list")
    return lst.pop(index)


def builtin_insert(lst: List, index: int, value: Any) -> None:
    """Insert value at index."""
    if not isinstance(lst, list):
        raise TypeError(f"insert() expects a list as first argument, got {type(lst).__name__}")
    if not isinstance(index, int):
        raise TypeError(f"insert() expects an integer index, got {type(index).__name__}")
    lst.insert(index, value)
    return None


def builtin_type(obj: Any) -> str:
    """Get type of object as string."""
    if isinstance(obj, bool):
        return "boolean"
    elif isinstance(obj, int):
        return "integer"
    elif isinstance(obj, float):
        return "float"
    elif isinstance(obj, str):
        return "string"
    elif isinstance(obj, list):
        return "list"
    elif callable(obj):
        return "function"
    else:
        return "unknown"


def builtin_str(obj: Any) -> str:
    """Convert object to string."""
    if isinstance(obj, bool):
        return "sahi" if obj else "galat"
    return str(obj)


def builtin_int(obj: Any) -> int:
    """Convert object to integer."""
    try:
        if isinstance(obj, str):
            return int(obj)
        elif isinstance(obj, (int, float, bool)):
            return int(obj)
        else:
            raise TypeError(f"Cannot convert {type(obj).__name__} to integer")
    except ValueError:
        raise TypeError(f"Cannot convert '{obj}' to integer")


def builtin_float(obj: Any) -> float:
    """Convert object to float."""
    try:
        if isinstance(obj, str):
            return float(obj)
        elif isinstance(obj, (int, float, bool)):
            return float(obj)
        else:
            raise TypeError(f"Cannot convert {type(obj).__name__} to float")
    except ValueError:
        raise TypeError(f"Cannot convert '{obj}' to float")


def builtin_input_func(prompt: str = "") -> str:
    """Read input from user."""
    return input(prompt)


def builtin_range(start: int, end: int, step: int = 1) -> List[int]:
    """Generate a list of numbers from start to end (exclusive) with step."""
    if not all(isinstance(x, int) for x in [start, end, step]):
        raise TypeError("range() arguments must be integers")
    return list(range(start, end, step))


def builtin_min(*args) -> Any:
    """Return minimum value."""
    if len(args) == 1 and isinstance(args[0], list):
        return min(args[0])
    return min(args)


def builtin_max(*args) -> Any:
    """Return maximum value."""
    if len(args) == 1 and isinstance(args[0], list):
        return max(args[0])
    return max(args)


def builtin_sum(lst: List) -> float:
    """Sum all numbers in a list."""
    if not isinstance(lst, list):
        raise TypeError(f"sum() expects a list, got {type(lst).__name__}")
    return sum(lst)


def builtin_sort(lst: List, reverse: bool = False) -> List:
    """Return sorted copy of list."""
    if not isinstance(lst, list):
        raise TypeError(f"sort() expects a list, got {type(lst).__name__}")
    return sorted(lst, reverse=reverse)


def builtin_reverse(lst: List) -> List:
    """Return reversed copy of list."""
    if not isinstance(lst, list):
        raise TypeError(f"reverse() expects a list, got {type(lst).__name__}")
    return list(reversed(lst))


def builtin_join(lst: List, separator: str = "") -> str:
    """Join list elements into a string."""
    if not isinstance(lst, list):
        raise TypeError(f"join() expects a list as first argument, got {type(lst).__name__}")
    if not isinstance(separator, str):
        raise TypeError(f"join() expects a string separator, got {type(separator).__name__}")
    return separator.join(str(item) for item in lst)


def builtin_split(string: str, separator: str = " ") -> List[str]:
    """Split string into list."""
    if not isinstance(string, str):
        raise TypeError(f"split() expects a string, got {type(string).__name__}")
    if not isinstance(separator, str):
        raise TypeError(f"split() expects a string separator, got {type(separator).__name__}")
    return string.split(separator)


def builtin_upper(string: str) -> str:
    """Convert string to uppercase."""
    if not isinstance(string, str):
        raise TypeError(f"upper() expects a string, got {type(string).__name__}")
    return string.upper()


def builtin_lower(string: str) -> str:
    """Convert string to lowercase."""
    if not isinstance(string, str):
        raise TypeError(f"lower() expects a string, got {type(string).__name__}")
    return string.lower()


def builtin_replace(string: str, old: str, new: str) -> str:
    """Replace occurrences of old with new in string."""
    if not isinstance(string, str):
        raise TypeError(f"replace() expects a string, got {type(string).__name__}")
    return string.replace(old, new)


# Built-in functions registry
BUILTINS = {
    # List operations
    'length': BuiltinFunction('length', builtin_length, 1),
    'append': BuiltinFunction('append', builtin_append, 2),
    'pop': BuiltinFunction('pop', builtin_pop, -1),
    'insert': BuiltinFunction('insert', builtin_insert, 3),
    'sort': BuiltinFunction('sort', builtin_sort, -1),
    'reverse': BuiltinFunction('reverse', builtin_reverse, 1),
    'join': BuiltinFunction('join', builtin_join, -1),
    'min': BuiltinFunction('min', builtin_min, -1),
    'max': BuiltinFunction('max', builtin_max, -1),
    'sum': BuiltinFunction('sum', builtin_sum, 1),
    
    # String operations
    'split': BuiltinFunction('split', builtin_split, -1),
    'upper': BuiltinFunction('upper', builtin_upper, 1),
    'lower': BuiltinFunction('lower', builtin_lower, 1),
    'replace': BuiltinFunction('replace', builtin_replace, 3),
    
    # Type operations
    'type': BuiltinFunction('type', builtin_type, 1),
    'str': BuiltinFunction('str', builtin_str, 1),
    'int': BuiltinFunction('int', builtin_int, 1),
    'float': BuiltinFunction('float', builtin_float, 1),
    
    # Utility
    'input': BuiltinFunction('input', builtin_input_func, -1),
    'range': BuiltinFunction('range', builtin_range, -1),
}

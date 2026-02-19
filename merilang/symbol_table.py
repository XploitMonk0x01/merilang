"""
Symbol Table for Merilang Semantic Analysis.

Implements a stack-of-hash-maps scoping system used by the SemanticAnalyzer
to track variable / function / class definitions across nested scopes.

Author: Merilang Team
Version: 3.0 - Compiler Front-End
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Symbol kinds
# ---------------------------------------------------------------------------

class SymbolKind(Enum):
    """Classification of a named entity in the symbol table."""
    VARIABLE  = auto()    # maan x = …
    PARAMETER = auto()    # function / lambda parameter
    FUNCTION  = auto()    # kaam name(…) { … }
    CLASS     = auto()    # class Name { … }


# ---------------------------------------------------------------------------
# Type tags (inferred, not declared)
# ---------------------------------------------------------------------------

class MType:
    """Lightweight string-based type tags inferred during analysis.

    These are *not* full type objects – they are coarse tags sufficient for
    the type-checking rules Merilang enforces.

    Constants:
        NUMBER  – int or float literal / expression
        STRING  – string literal / expression
        BOOL    – sach / jhoot boolean
        LIST    – list literal or list-returning built-in
        DICT    – dict literal
        FUNC    – kaam function object
        CLASS   – class value
        NONE    – void (no return value)
        ANY     – unknown / polymorphic (turns off strict checks)
    """
    NUMBER = "number"
    STRING = "string"
    BOOL   = "bool"
    LIST   = "list"
    DICT   = "dict"
    FUNC   = "function"
    CLASS  = "class"
    NONE   = "none"
    ANY    = "any"


# ---------------------------------------------------------------------------
# Symbol record
# ---------------------------------------------------------------------------

@dataclass
class Symbol:
    """A single entry in the symbol table.

    Attributes:
        name:          The identifier text.
        kind:          Whether it is a variable, parameter, function, or class.
        inferred_type: Coarse MType tag inferred from the declaration site.
        line:          Source line of the *first* declaration.
        param_count:   For FUNCTION symbols – the number of declared parameters
                       (used for arity checking at call sites).
    """
    name:          str
    kind:          SymbolKind
    inferred_type: str
    line:          int
    param_count:   Optional[int] = None   # only set for FUNCTION symbols


# ---------------------------------------------------------------------------
# Symbol table (scope)
# ---------------------------------------------------------------------------

class SymbolTable:
    """A single lexical scope implemented as a hash map with an optional parent.

    Scopes are chained: each new block (function body, if-branch, etc.) creates
    a child ``SymbolTable`` that delegates resolution upward to parent scopes.

    Usage::

        global_scope = SymbolTable()
        global_scope.define(Symbol("x", SymbolKind.VARIABLE, MType.NUMBER, 1))

        func_scope = SymbolTable(parent=global_scope)
        func_scope.define(Symbol("y", SymbolKind.PARAMETER, MType.ANY, 3))

        print(func_scope.resolve("x"))   # found in parent
        print(func_scope.resolve("y"))   # found locally
        print(func_scope.resolve("z"))   # None – not found
    """

    def __init__(self, parent: Optional[SymbolTable] = None) -> None:
        self._bindings: Dict[str, Symbol] = {}
        self.parent = parent
        self.depth: int = (parent.depth + 1) if parent is not None else 0

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def define(self, symbol: Symbol) -> None:
        """Add *symbol* to the **current** (innermost) scope.

        Does not check for re-definition; the SemanticAnalyzer is responsible
        for calling ``resolve_local`` first and raising ``RedefinitionError``
        when appropriate.

        Args:
            symbol: The Symbol record to register.
        """
        self._bindings[symbol.name] = symbol

    def resolve(self, name: str) -> Optional[Symbol]:
        """Search for *name* in this scope and all enclosing parent scopes.

        Args:
            name: Identifier to look up.

        Returns:
            The matching ``Symbol`` if found, otherwise ``None``.
        """
        if name in self._bindings:
            return self._bindings[name]
        if self.parent is not None:
            return self.parent.resolve(name)
        return None

    def resolve_local(self, name: str) -> Optional[Symbol]:
        """Search for *name* in the **current scope only** (no parents).

        Used by the SemanticAnalyzer to detect re-declarations in the same
        scope (vs. legitimate shadowing of an outer variable).

        Args:
            name: Identifier to check.

        Returns:
            The ``Symbol`` if it exists in this scope, otherwise ``None``.
        """
        return self._bindings.get(name)

    # ------------------------------------------------------------------
    # Scope stack helpers
    # ------------------------------------------------------------------

    def enter_scope(self) -> SymbolTable:
        """Create and return a new child scope (push).

        The caller should store the returned scope and eventually call
        ``exit_scope()`` on it when the block ends.

        Example::

            scope = scope.enter_scope()
            # … analyse block statements …
            scope = scope.exit_scope()

        Returns:
            A new ``SymbolTable`` whose parent is ``self``.
        """
        return SymbolTable(parent=self)

    def exit_scope(self) -> SymbolTable:
        """Return the parent scope (pop).

        Raises:
            RuntimeError: If called on the global (root) scope.

        Returns:
            The parent ``SymbolTable``.
        """
        if self.parent is None:
            raise RuntimeError("Cannot exit the global scope.")
        return self.parent

    # ------------------------------------------------------------------
    # Introspection / debugging
    # ------------------------------------------------------------------

    def all_names(self) -> List[str]:
        """Return all names visible from this scope (including parent scopes).

        Useful for generating "did you mean?" suggestions.
        """
        names: List[str] = list(self._bindings.keys())
        if self.parent is not None:
            names.extend(self.parent.all_names())
        return names

    def local_names(self) -> List[str]:
        """Return names defined in this scope only."""
        return list(self._bindings.keys())

    def __repr__(self) -> str:  # pragma: no cover
        local = ", ".join(self._bindings.keys())
        return f"SymbolTable(depth={self.depth}, local=[{local}])"

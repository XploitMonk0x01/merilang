"""
Three-Address Code (3AC) IR Node definitions for Merilang.

This module defines the instruction set for the intermediate representation (IR)
that sits between the AST and a future VM / code-generation back-end.

Every instruction is an immutable dataclass.  A ``Temp`` variable has the form
``t0``, ``t1``, … and a ``Label`` has the form ``L0``, ``L1``, …

Author: Merilang Team
Version: 3.0 - Compiler Front-End
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Operand wrappers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Temp:
    """A compiler-generated temporary variable (e.g. ``t0``)."""
    name: str

    def __str__(self) -> str:  # pragma: no cover
        return self.name


@dataclass(frozen=True)
class Label:
    """A jump target label (e.g. ``L0``, ``loop_start_3``)."""
    name: str

    def __str__(self) -> str:  # pragma: no cover
        return self.name


# Operand union – anything that can appear as an operand in a 3AC instruction.
Operand = "str | int | float | bool | Temp | None"


# ---------------------------------------------------------------------------
# Base instruction
# ---------------------------------------------------------------------------

class IRInstr:
    """Abstract base for all IR instructions.

    Not a dataclass itself – subclasses are dataclasses that declare
    ``source_line: int = 1`` as their last (optional) field.  This avoids
    the Python restriction that non-default fields cannot follow default
    ones in a dataclass inheritance chain.
    """
    def __str__(self) -> str:  # pragma: no cover
        return repr(self)



# ---------------------------------------------------------------------------
# Arithmetic / logic / comparison
# ---------------------------------------------------------------------------

@dataclass
class BinOp(IRInstr):
    """``result = left op right``

    Example::

        t2 = t0 + t1   # BinOp(Temp('t2'), '+', Temp('t0'), Temp('t1'))
    """
    result:   Temp
    op:       str
    left:     object       # Temp | literal
    right:    object
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    {self.result} = {self.left} {self.op} {self.right}"


@dataclass
class UnaryOp(IRInstr):
    """``result = op operand``

    Example::

        t1 = - t0   # UnaryOp(Temp('t1'), '-', Temp('t0'))
        t3 = not t2
    """
    result:  Temp
    op:      str
    operand: object
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    {self.result} = {self.op} {self.operand}"


# ---------------------------------------------------------------------------
# Assignment / copy
# ---------------------------------------------------------------------------

@dataclass
class Assign(IRInstr):
    """``result = value``  (load a literal constant into a temp)

    Example::

        t0 = 42         # Assign(Temp('t0'), 42)
        t1 = "hello"
    """
    result: Temp
    value:  object        # literal (int, float, str, bool, None)
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    {self.result} = {repr(self.value)}"


@dataclass
class Copy(IRInstr):
    """``dest = src``  (copy between named variable and temp)

    Used when writing a computed result back to a named variable or reading
    a named variable into a temp.

    Example::

        x = t3          # Copy('x', Temp('t3'))   → named_var = temp
        t4 = x          # Copy(Temp('t4'), 'x')   → temp = named_var
    """
    dest: object    # str (variable name) or Temp
    src:  object    # str (variable name) or Temp
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    {self.dest} = {self.src}"


# ---------------------------------------------------------------------------
# Control flow
# ---------------------------------------------------------------------------

@dataclass
class LabelInstr(IRInstr):
    """Emit a jump target label.

    Example::

        L0:             # LabelInstr(Label('L0'))
    """
    label: Label
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.label}:"


@dataclass
class Jump(IRInstr):
    """Unconditional jump.

    Example::

        GOTO L2         # Jump(Label('L2'))
    """
    target: Label
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    GOTO {self.target}"


@dataclass
class CondJump(IRInstr):
    """Conditional jump: ``IF condition GOTO true_label ELSE false_label``.

    Example::

        IF t0 GOTO L1 ELSE L2
    """
    condition:   object     # Temp or literal bool
    true_label:  Label
    false_label: Label
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    IF {self.condition} GOTO {self.true_label} ELSE {self.false_label}"


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

@dataclass
class FuncLabel(IRInstr):
    """Mark the entry point of a function definition.

    Example::

        FUNC add:       # FuncLabel('add')
    """
    func_name: str
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"FUNC {self.func_name}:"


@dataclass
class Param(IRInstr):
    """Push an argument onto the call stack.

    Example::

        PARAM t0        # Param(Temp('t0'))
    """
    value: object
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    PARAM {self.value}"


@dataclass
class Call(IRInstr):
    """Call a function with *n_args* pre-pushed params; result → *result_temp*.

    Example::

        t3 = CALL add 2     # Call(Temp('t3'), 'add', 2)
    """
    result:    Optional[Temp]   # None if return value is discarded
    func_name: str
    n_args:    int
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        dest = f"{self.result} = " if self.result else ""
        return f"    {dest}CALL {self.func_name} {self.n_args}"


@dataclass
class Return(IRInstr):
    """Return from current function, optionally with a value.

    Example::

        RETURN t2       # Return(Temp('t2'))
        RETURN          # Return(None)
    """
    value: Optional[object]
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        val = f" {self.value}" if self.value is not None else ""
        return f"    RETURN{val}"


# ---------------------------------------------------------------------------
# Object / OOP
# ---------------------------------------------------------------------------

@dataclass
class NewObj(IRInstr):
    """Instantiate a class: ``result = NEW ClassName``.

    Example::

        t5 = NEW Person     # NewObj(Temp('t5'), 'Person')
    """
    result:     Temp
    class_name: str
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    {self.result} = NEW {self.class_name}"


@dataclass
class FieldLoad(IRInstr):
    """Load an object field: ``result = obj.field``.

    Example::

        t6 = t5.naam
    """
    result:     Temp
    obj:        object
    field_name: str
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    {self.result} = {self.obj}.{self.field_name}"


@dataclass
class FieldStore(IRInstr):
    """Store to an object field: ``obj.field = value``.

    Example::

        t5.naam = t0
    """
    obj:        object
    field_name: str
    value:      object
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    {self.obj}.{self.field_name} = {self.value}"


# ---------------------------------------------------------------------------
# List / dict indexing
# ---------------------------------------------------------------------------

@dataclass
class IndexLoad(IRInstr):
    """Load an element: ``result = obj[index]``.

    Example::

        t7 = arr[t0]
    """
    result: Temp
    obj:    object
    index:  object
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    {self.result} = {self.obj}[{self.index}]"


@dataclass
class IndexStore(IRInstr):
    """Store an element: ``obj[index] = value``.

    Example::

        arr[t0] = t1
    """
    obj:   object
    index: object
    value: object
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    {self.obj}[{self.index}] = {self.value}"


# ---------------------------------------------------------------------------
# I / O
# ---------------------------------------------------------------------------

@dataclass
class PrintIR(IRInstr):
    """PRINT one or more values.

    Example::

        PRINT t0, t1
    """
    args: List[object] = field(default_factory=list)
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        joined = ", ".join(str(a) for a in self.args)
        return f"    PRINT {joined}"


@dataclass
class InputIR(IRInstr):
    """Read user input into a named variable.

    Example::

        INPUT name
    """
    var_name: str
    prompt:   Optional[object] = None
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        prompt_str = f" {self.prompt}" if self.prompt is not None else ""
        return f"    INPUT {self.var_name}{prompt_str}"


# ---------------------------------------------------------------------------
# Exception handling
# ---------------------------------------------------------------------------

@dataclass
class ThrowIR(IRInstr):
    """THROW an exception value.

    Example::

        THROW t0
    """
    value: object
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        return f"    THROW {self.value}"


@dataclass
class TryBegin(IRInstr):
    """Mark the beginning of a try block with an associated catch label."""
    catch_label:   Label
    finally_label: Optional[Label] = None
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        fl = f" finally={self.finally_label}" if self.finally_label else ""
        return f"    TRY_BEGIN catch={self.catch_label}{fl}"


@dataclass
class TryEnd(IRInstr):
    """Mark the end of a try block."""
    def __str__(self) -> str:  # pragma: no cover
        return "    TRY_END"


@dataclass
class CatchBegin(IRInstr):
    """Mark the beginning of a catch block; binds exception to *var_name*."""
    var_name: Optional[str]
    source_line: int = 1

    def __str__(self) -> str:  # pragma: no cover
        binding = f" AS {self.var_name}" if self.var_name else ""
        return f"    CATCH{binding}"


# ---------------------------------------------------------------------------
# IR Program container
# ---------------------------------------------------------------------------

@dataclass
class IRProgram:
    """The root container for a compiled program's IR instructions.

    Attributes:
        instructions: Flat, ordered list of all 3AC instructions.
    """
    instructions: List[IRInstr] = field(default_factory=list)

    def append(self, instr: IRInstr) -> None:
        """Append a single instruction."""
        self.instructions.append(instr)

    def extend(self, instrs: List[IRInstr]) -> None:
        """Append multiple instructions."""
        self.instructions.extend(instrs)

    def dump(self) -> str:
        """Return a human-readable listing of all instructions."""
        return "\n".join(str(i) for i in self.instructions)

    def __repr__(self) -> str:  # pragma: no cover
        return f"IRProgram({len(self.instructions)} instructions)"

"""IR optimization passes for Merilang 3AC.

Implemented passes:
- Constant folding
- Dead code elimination (for pure temp-producing instructions)
- Common subexpression elimination (local, expression-level)

Author: Merilang Team
Version: 3.1 - Optimizer Upgrade
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from merilang.ir_nodes import (
    Assign,
    BinOp,
    Call,
    CondJump,
    Copy,
    FieldLoad,
    FieldStore,
    IRInstr,
    IRProgram,
    IndexLoad,
    IndexStore,
    InputIR,
    Jump,
    LabelInstr,
    Param,
    Phi,
    PrintIR,
    Return,
    Temp,
    ThrowIR,
    TryBegin,
    TryEnd,
    CatchBegin,
    UnaryOp,
)
from merilang.ir_dag import optimize_ir_with_dag

COMMUTATIVE_OPS = {"+", "*", "==", "!=", "aur", "ya"}


@dataclass
class OptimizationReport:
    """Counts of applied IR optimizations."""

    constant_folds: int = 0
    dead_instructions_removed: int = 0
    cse_rewrites: int = 0
    dag_rewrites: int = 0


def _is_literal(value: object) -> bool:
    return isinstance(value, (int, float, str, bool)) or value is None


def _temp_name(op: object) -> Optional[str]:
    if isinstance(op, Temp):
        return op.name
    return None


def _eval_binop(op: str, left: object, right: object) -> Tuple[bool, object]:
    try:
        if op == "+":
            return True, left + right
        if op == "-":
            return True, left - right
        if op == "*":
            return True, left * right
        if op == "/":
            # Keep runtime behavior for divide-by-zero.
            if right == 0:
                return False, None
            return True, left / right
        if op == "%":
            if right == 0:
                return False, None
            return True, left % right
        if op == ">":
            return True, left > right
        if op == "<":
            return True, left < right
        if op == ">=":
            return True, left >= right
        if op == "<=":
            return True, left <= right
        if op == "==":
            return True, left == right
        if op == "!=":
            return True, left != right
        if op == "aur":
            return True, bool(left) and bool(right)
        if op == "ya":
            return True, bool(left) or bool(right)
    except Exception:
        return False, None
    return False, None


def _eval_unary(op: str, operand: object) -> Tuple[bool, object]:
    try:
        if op == "-":
            return True, -operand
        if op == "nahi":
            return True, not bool(operand)
    except Exception:
        return False, None
    return False, None


def _read_temps(instr: IRInstr) -> Set[str]:
    reads: Set[str] = set()

    def collect(value: object) -> None:
        if isinstance(value, Temp):
            reads.add(value.name)

    if isinstance(instr, BinOp):
        collect(instr.left)
        collect(instr.right)
    elif isinstance(instr, UnaryOp):
        collect(instr.operand)
    elif isinstance(instr, Copy):
        collect(instr.src)
    elif isinstance(instr, CondJump):
        collect(instr.condition)
    elif isinstance(instr, Param):
        collect(instr.value)
    elif isinstance(instr, Phi):
        for src in instr.sources.values():
            collect(src)
    elif isinstance(instr, Return):
        if instr.value is not None:
            collect(instr.value)
    elif isinstance(instr, PrintIR):
        for arg in instr.args:
            collect(arg)
    elif isinstance(instr, ThrowIR):
        collect(instr.value)
    elif isinstance(instr, FieldStore):
        collect(instr.obj)
        collect(instr.value)
    elif isinstance(instr, FieldLoad):
        collect(instr.obj)
    elif isinstance(instr, IndexStore):
        collect(instr.obj)
        collect(instr.index)
        collect(instr.value)
    elif isinstance(instr, IndexLoad):
        collect(instr.obj)
        collect(instr.index)

    return reads


def _written_temp(instr: IRInstr) -> Optional[str]:
    if isinstance(instr, Assign):
        return instr.result.name
    if isinstance(instr, BinOp):
        return instr.result.name
    if isinstance(instr, UnaryOp):
        return instr.result.name
    if isinstance(instr, Copy) and isinstance(instr.dest, Temp):
        return instr.dest.name
    if isinstance(instr, Phi):
        if isinstance(instr.result, Temp):
            return instr.result.name
        if isinstance(instr.result, str):
            return instr.result
    if isinstance(instr, Call) and instr.result is not None:
        return instr.result.name
    if isinstance(instr, FieldLoad):
        return instr.result.name
    if isinstance(instr, IndexLoad):
        return instr.result.name
    return None


def _is_pure_temp_assignment(instr: IRInstr) -> bool:
    if isinstance(instr, (Assign, BinOp, UnaryOp)):
        return True
    if isinstance(instr, Copy) and isinstance(instr.dest, Temp):
        return True
    if isinstance(instr, Phi) and isinstance(instr.result, Temp):
        return True
    return False


def constant_fold(program: IRProgram) -> Tuple[IRProgram, int]:
    """Fold constant expressions into direct assignments."""
    folded: List[IRInstr] = []
    changes = 0

    for instr in program.instructions:
        if isinstance(instr, BinOp) and _is_literal(instr.left) and _is_literal(instr.right):
            ok, value = _eval_binop(instr.op, instr.left, instr.right)
            if ok:
                folded.append(
                    Assign(result=instr.result, value=value, source_line=instr.source_line)
                )
                changes += 1
                continue

        if isinstance(instr, UnaryOp) and _is_literal(instr.operand):
            ok, value = _eval_unary(instr.op, instr.operand)
            if ok:
                folded.append(
                    Assign(result=instr.result, value=value, source_line=instr.source_line)
                )
                changes += 1
                continue

        folded.append(instr)

    return IRProgram(instructions=folded), changes


def eliminate_dead_temps(program: IRProgram) -> Tuple[IRProgram, int]:
    """Backward liveness DCE for pure temp-producing instructions."""
    used: Set[str] = set()
    out: List[IRInstr] = []
    removed = 0

    for instr in reversed(program.instructions):
        reads = _read_temps(instr)
        wt = _written_temp(instr)

        keep = True
        if wt is not None and wt not in used and _is_pure_temp_assignment(instr):
            keep = False

        if keep:
            if wt is not None:
                used.discard(wt)
            used.update(reads)
            out.append(instr)
        else:
            removed += 1

    out.reverse()
    return IRProgram(instructions=out), removed


def eliminate_common_subexpressions(program: IRProgram) -> Tuple[IRProgram, int]:
    """Local common-subexpression elimination for BinOp instructions."""
    result: List[IRInstr] = []
    expr_to_temp: Dict[Tuple[str, object, object], Temp] = {}
    rewrites = 0

    def barrier(instr: IRInstr) -> bool:
        return isinstance(
            instr,
            (
                LabelInstr,
                Jump,
                CondJump,
                Return,
                ThrowIR,
                Call,
                TryBegin,
                TryEnd,
                CatchBegin,
                Phi,
                InputIR,
                PrintIR,
            ),
        )

    for instr in program.instructions:
        if barrier(instr):
            expr_to_temp.clear()
            result.append(instr)
            continue

        if isinstance(instr, BinOp):
            left = instr.left
            right = instr.right
            if instr.op in COMMUTATIVE_OPS and repr(left) > repr(right):
                left, right = right, left

            key = (instr.op, left, right)
            existing = expr_to_temp.get(key)
            if existing is not None:
                result.append(
                    Copy(dest=instr.result, src=existing, source_line=instr.source_line)
                )
                rewrites += 1
                continue

            expr_to_temp[key] = instr.result

        result.append(instr)

    return IRProgram(instructions=result), rewrites


def optimize_ir(
    program: IRProgram,
    *,
    enable_constant_folding: bool = True,
    enable_dead_code_elimination: bool = True,
    enable_common_subexpression: bool = True,
    enable_dag_local_optimization: bool = True,
) -> Tuple[IRProgram, OptimizationReport]:
    """Run optimization passes and return optimized program + report."""
    report = OptimizationReport()
    current = IRProgram(instructions=list(program.instructions))

    if enable_common_subexpression:
        current, n = eliminate_common_subexpressions(current)
        report.cse_rewrites = n

    if enable_dag_local_optimization:
        current, n = optimize_ir_with_dag(current)
        report.dag_rewrites = n

    if enable_constant_folding:
        current, n = constant_fold(current)
        report.constant_folds = n

    if enable_dead_code_elimination:
        current, n = eliminate_dead_temps(current)
        report.dead_instructions_removed = n

    return current, report

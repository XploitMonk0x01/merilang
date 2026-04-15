"""DAG-based local expression optimization for Merilang IR.

This pass optimizes each basic block independently by building a local DAG/
value-numbering structure for expression reuse.

Author: Merilang Team
Version: 3.2 - DAG Local Optimizer
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from merilang.ir_analysis import BasicBlock, build_basic_blocks
from merilang.ir_nodes import BinOp, Copy, IRInstr, IRProgram, Temp

COMMUTATIVE_OPS = {"+", "*", "==", "!=", "aur", "ya"}


@dataclass
class DAGNode:
    """A local DAG node representing one expression value in a basic block."""

    op: Optional[str]
    left: object
    right: Optional[object]
    result: object


def _canonical_operand(operand: object, aliases: Dict[str, object]) -> object:
    if isinstance(operand, Temp):
        name = operand.name
        if name in aliases:
            return aliases[name]
    return operand


def optimize_basic_block_with_dag(block: BasicBlock) -> Tuple[List[IRInstr], int]:
    """Optimize one block using DAG/value-numbering style expression reuse."""
    optimized: List[IRInstr] = []
    expr_to_result: Dict[Tuple[str, object, object], object] = {}
    aliases: Dict[str, object] = {}
    rewrites = 0

    for instr in block.instructions:
        if not isinstance(instr, BinOp):
            # Maintain simple aliases for direct copies to improve canonicalization.
            if isinstance(instr, Copy) and isinstance(instr.dest, Temp):
                src = _canonical_operand(instr.src, aliases)
                aliases[instr.dest.name] = src
                optimized.append(Copy(dest=instr.dest, src=src, source_line=instr.source_line))
                continue
            optimized.append(instr)
            continue

        left = _canonical_operand(instr.left, aliases)
        right = _canonical_operand(instr.right, aliases)

        if instr.op in COMMUTATIVE_OPS and repr(left) > repr(right):
            left, right = right, left

        key = (instr.op, left, right)
        if key in expr_to_result:
            optimized.append(Copy(dest=instr.result, src=expr_to_result[key], source_line=instr.source_line))
            aliases[instr.result.name] = expr_to_result[key]
            rewrites += 1
            continue

        expr_to_result[key] = instr.result
        aliases[instr.result.name] = instr.result
        optimized.append(BinOp(result=instr.result, op=instr.op, left=left, right=right, source_line=instr.source_line))

    return optimized, rewrites


def optimize_ir_with_dag(program: IRProgram) -> Tuple[IRProgram, int]:
    """Apply local DAG optimization independently to each basic block."""
    blocks = build_basic_blocks(program)
    if not blocks:
        return IRProgram(instructions=[]), 0

    rewrites = 0
    out: List[IRInstr] = []
    for block in blocks:
        optimized_block, n = optimize_basic_block_with_dag(block)
        rewrites += n
        out.extend(optimized_block)

    return IRProgram(instructions=out), rewrites

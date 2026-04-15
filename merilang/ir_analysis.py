"""IR analysis utilities: basic-block construction and control-flow graph.

This module turns a flat 3AC instruction stream into:
- Basic blocks (single-entry, single-exit regions)
- A control-flow graph (CFG) over those blocks

Author: Merilang Team
Version: 3.1 - CFG Upgrade
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from merilang.ir_nodes import (
    IRInstr,
    IRProgram,
    LabelInstr,
    Jump,
    CondJump,
    Return,
    ThrowIR,
)


@dataclass
class BasicBlock:
    """A straight-line block of IR instructions."""

    block_id: int
    start_index: int
    instructions: List[IRInstr] = field(default_factory=list)
    label: Optional[str] = None

    def dump(self) -> str:
        """Pretty-print this block for debugging/reporting."""
        head = f"B{self.block_id}"
        if self.label:
            head += f" ({self.label})"
        lines = [head]
        for instr in self.instructions:
            lines.append(str(instr))
        return "\n".join(lines)


@dataclass
class ControlFlowGraph:
    """Control-flow graph over basic blocks."""

    blocks: List[BasicBlock]
    edges: Dict[int, Set[int]]
    reverse_edges: Dict[int, Set[int]]

    def successors(self, block_id: int) -> Set[int]:
        return self.edges.get(block_id, set())

    def predecessors(self, block_id: int) -> Set[int]:
        return self.reverse_edges.get(block_id, set())

    def dump(self) -> str:
        """Return a human-readable CFG dump."""
        lines: List[str] = []
        for block in self.blocks:
            succ = sorted(self.successors(block.block_id))
            lines.append(f"B{block.block_id} -> {succ}")
            lines.append(block.dump())
            lines.append("")
        return "\n".join(lines).rstrip()


def _label_to_index(instructions: List[IRInstr]) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    for idx, instr in enumerate(instructions):
        if isinstance(instr, LabelInstr):
            mapping[instr.label.name] = idx
    return mapping


def build_basic_blocks(program: IRProgram) -> List[BasicBlock]:
    """Split a flat IR program into basic blocks."""
    instructions = program.instructions
    if not instructions:
        return []

    label_to_idx = _label_to_index(instructions)
    leaders: Set[int] = {0}

    # Every label starts a block.
    for idx, instr in enumerate(instructions):
        if isinstance(instr, LabelInstr):
            leaders.add(idx)

    # Jump targets and post-terminator instructions are leaders.
    for idx, instr in enumerate(instructions):
        if isinstance(instr, Jump):
            target_idx = label_to_idx.get(instr.target.name)
            if target_idx is not None:
                leaders.add(target_idx)
            if idx + 1 < len(instructions):
                leaders.add(idx + 1)
        elif isinstance(instr, CondJump):
            t_idx = label_to_idx.get(instr.true_label.name)
            f_idx = label_to_idx.get(instr.false_label.name)
            if t_idx is not None:
                leaders.add(t_idx)
            if f_idx is not None:
                leaders.add(f_idx)
            if idx + 1 < len(instructions):
                leaders.add(idx + 1)
        elif isinstance(instr, (Return, ThrowIR)):
            if idx + 1 < len(instructions):
                leaders.add(idx + 1)

    sorted_leaders = sorted(leaders)
    blocks: List[BasicBlock] = []

    for block_id, start in enumerate(sorted_leaders):
        end = sorted_leaders[block_id + 1] if block_id + 1 < len(sorted_leaders) else len(instructions)
        block_instrs = instructions[start:end]
        label_name: Optional[str] = None
        if block_instrs and isinstance(block_instrs[0], LabelInstr):
            label_name = block_instrs[0].label.name
        blocks.append(
            BasicBlock(
                block_id=block_id,
                start_index=start,
                instructions=block_instrs,
                label=label_name,
            )
        )

    return blocks


def build_cfg(program: IRProgram) -> ControlFlowGraph:
    """Build a CFG from the given IR program."""
    blocks = build_basic_blocks(program)
    edges: Dict[int, Set[int]] = {b.block_id: set() for b in blocks}
    reverse_edges: Dict[int, Set[int]] = {b.block_id: set() for b in blocks}

    if not blocks:
        return ControlFlowGraph(blocks=blocks, edges=edges, reverse_edges=reverse_edges)

    start_to_block = {b.start_index: b.block_id for b in blocks}
    label_to_block: Dict[str, int] = {}
    for b in blocks:
        if b.label is not None:
            label_to_block[b.label] = b.block_id

    for idx, block in enumerate(blocks):
        if not block.instructions:
            continue

        last = block.instructions[-1]
        succ: Set[int] = set()

        if isinstance(last, Jump):
            bid = label_to_block.get(last.target.name)
            if bid is not None:
                succ.add(bid)
        elif isinstance(last, CondJump):
            t_bid = label_to_block.get(last.true_label.name)
            f_bid = label_to_block.get(last.false_label.name)
            if t_bid is not None:
                succ.add(t_bid)
            if f_bid is not None:
                succ.add(f_bid)
        elif isinstance(last, (Return, ThrowIR)):
            succ = set()
        else:
            if idx + 1 < len(blocks):
                succ.add(blocks[idx + 1].block_id)

        edges[block.block_id] = succ

    for src, dsts in edges.items():
        for dst in dsts:
            reverse_edges.setdefault(dst, set()).add(src)

    # Ensure all block ids are present.
    for b in blocks:
        reverse_edges.setdefault(b.block_id, set())

    return ControlFlowGraph(blocks=blocks, edges=edges, reverse_edges=reverse_edges)

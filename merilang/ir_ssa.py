"""SSA conversion pass for Merilang IR.

Converts a flat 3AC program into an SSA-style IR using CFG information.
The pass performs:
- Versioned renaming for variable/temp definitions
- Merge-point PHI insertion for names with conflicting incoming versions

Author: Merilang Team
Version: 3.2 - SSA Upgrade
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from merilang.ir_analysis import build_cfg
from merilang.ir_nodes import (
    Assign,
    BinOp,
    Call,
    CatchBegin,
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
    UnaryOp,
)


@dataclass
class SSAReport:
    """Summary information for SSA conversion."""

    phi_inserted: int = 0
    definitions_renamed: int = 0


def _is_temp_name(name: str) -> bool:
    return name.startswith("t")


def _materialize_name(base: str, versioned: str) -> object:
    if _is_temp_name(base):
        return Temp(versioned)
    return versioned


def _operand_base(op: object) -> Optional[str]:
    if isinstance(op, Temp):
        return op.name
    if isinstance(op, str):
        return op
    return None


def _read_names(instr: IRInstr) -> Set[str]:
    reads: Set[str] = set()

    def add(v: object) -> None:
        b = _operand_base(v)
        if b is not None:
            reads.add(b)

    if isinstance(instr, BinOp):
        add(instr.left)
        add(instr.right)
    elif isinstance(instr, UnaryOp):
        add(instr.operand)
    elif isinstance(instr, Copy):
        add(instr.src)
    elif isinstance(instr, CondJump):
        add(instr.condition)
    elif isinstance(instr, Param):
        add(instr.value)
    elif isinstance(instr, Return):
        if instr.value is not None:
            add(instr.value)
    elif isinstance(instr, PrintIR):
        for arg in instr.args:
            add(arg)
    elif isinstance(instr, ThrowIR):
        add(instr.value)
    elif isinstance(instr, FieldLoad):
        add(instr.obj)
    elif isinstance(instr, FieldStore):
        add(instr.obj)
        add(instr.value)
    elif isinstance(instr, IndexLoad):
        add(instr.obj)
        add(instr.index)
    elif isinstance(instr, IndexStore):
        add(instr.obj)
        add(instr.index)
        add(instr.value)

    return reads


def _write_names(instr: IRInstr) -> Set[str]:
    writes: Set[str] = set()

    def add(v: object) -> None:
        b = _operand_base(v)
        if b is not None:
            writes.add(b)

    if isinstance(instr, Assign):
        add(instr.result)
    elif isinstance(instr, BinOp):
        add(instr.result)
    elif isinstance(instr, UnaryOp):
        add(instr.result)
    elif isinstance(instr, Copy):
        add(instr.dest)
    elif isinstance(instr, Call) and instr.result is not None:
        add(instr.result)
    elif isinstance(instr, FieldLoad):
        add(instr.result)
    elif isinstance(instr, IndexLoad):
        add(instr.result)
    elif isinstance(instr, InputIR):
        add(instr.var_name)

    return writes


def _rename_operand(op: object, current: Dict[str, str]) -> object:
    base = _operand_base(op)
    if base is None:
        return op
    versioned = current.get(base, f"{base}_0")
    return _materialize_name(base, versioned)


def _rename_instruction_reads(instr: IRInstr, current: Dict[str, str]) -> IRInstr:
    if isinstance(instr, BinOp):
        return BinOp(
            result=instr.result,
            op=instr.op,
            left=_rename_operand(instr.left, current),
            right=_rename_operand(instr.right, current),
            source_line=instr.source_line,
        )
    if isinstance(instr, UnaryOp):
        return UnaryOp(
            result=instr.result,
            op=instr.op,
            operand=_rename_operand(instr.operand, current),
            source_line=instr.source_line,
        )
    if isinstance(instr, Copy):
        return Copy(
            dest=instr.dest,
            src=_rename_operand(instr.src, current),
            source_line=instr.source_line,
        )
    if isinstance(instr, CondJump):
        return CondJump(
            condition=_rename_operand(instr.condition, current),
            true_label=instr.true_label,
            false_label=instr.false_label,
            source_line=instr.source_line,
        )
    if isinstance(instr, Param):
        return Param(value=_rename_operand(instr.value, current), source_line=instr.source_line)
    if isinstance(instr, Return):
        val = _rename_operand(instr.value, current) if instr.value is not None else None
        return Return(value=val, source_line=instr.source_line)
    if isinstance(instr, PrintIR):
        return PrintIR(args=[_rename_operand(a, current) for a in instr.args], source_line=instr.source_line)
    if isinstance(instr, ThrowIR):
        return ThrowIR(value=_rename_operand(instr.value, current), source_line=instr.source_line)
    if isinstance(instr, FieldLoad):
        return FieldLoad(
            result=instr.result,
            obj=_rename_operand(instr.obj, current),
            field_name=instr.field_name,
            source_line=instr.source_line,
        )
    if isinstance(instr, FieldStore):
        return FieldStore(
            obj=_rename_operand(instr.obj, current),
            field_name=instr.field_name,
            value=_rename_operand(instr.value, current),
            source_line=instr.source_line,
        )
    if isinstance(instr, IndexLoad):
        return IndexLoad(
            result=instr.result,
            obj=_rename_operand(instr.obj, current),
            index=_rename_operand(instr.index, current),
            source_line=instr.source_line,
        )
    if isinstance(instr, IndexStore):
        return IndexStore(
            obj=_rename_operand(instr.obj, current),
            index=_rename_operand(instr.index, current),
            value=_rename_operand(instr.value, current),
            source_line=instr.source_line,
        )

    return instr


def _rename_definition_target(
    instr: IRInstr,
    current: Dict[str, str],
    counters: Dict[str, int],
) -> Tuple[IRInstr, int]:
    renamed = 0

    def fresh(base: str) -> str:
        counters[base] += 1
        return f"{base}_{counters[base]}"

    if isinstance(instr, Assign):
        base = instr.result.name
        new_name = fresh(base)
        current[base] = new_name
        renamed += 1
        return Assign(result=Temp(new_name), value=instr.value, source_line=instr.source_line), renamed

    if isinstance(instr, BinOp):
        base = instr.result.name
        new_name = fresh(base)
        current[base] = new_name
        renamed += 1
        return BinOp(
            result=Temp(new_name),
            op=instr.op,
            left=instr.left,
            right=instr.right,
            source_line=instr.source_line,
        ), renamed

    if isinstance(instr, UnaryOp):
        base = instr.result.name
        new_name = fresh(base)
        current[base] = new_name
        renamed += 1
        return UnaryOp(
            result=Temp(new_name),
            op=instr.op,
            operand=instr.operand,
            source_line=instr.source_line,
        ), renamed

    if isinstance(instr, Copy):
        base = _operand_base(instr.dest)
        if base is None:
            return instr, renamed
        new_name = fresh(base)
        current[base] = new_name
        renamed += 1
        return Copy(
            dest=_materialize_name(base, new_name),
            src=instr.src,
            source_line=instr.source_line,
        ), renamed

    if isinstance(instr, Call) and instr.result is not None:
        base = instr.result.name
        new_name = fresh(base)
        current[base] = new_name
        renamed += 1
        return Call(
            result=Temp(new_name),
            func_name=instr.func_name,
            n_args=instr.n_args,
            source_line=instr.source_line,
        ), renamed

    if isinstance(instr, FieldLoad):
        base = instr.result.name
        new_name = fresh(base)
        current[base] = new_name
        renamed += 1
        return FieldLoad(
            result=Temp(new_name),
            obj=instr.obj,
            field_name=instr.field_name,
            source_line=instr.source_line,
        ), renamed

    if isinstance(instr, IndexLoad):
        base = instr.result.name
        new_name = fresh(base)
        current[base] = new_name
        renamed += 1
        return IndexLoad(
            result=Temp(new_name),
            obj=instr.obj,
            index=instr.index,
            source_line=instr.source_line,
        ), renamed

    if isinstance(instr, InputIR):
        base = instr.var_name
        new_name = fresh(base)
        current[base] = new_name
        renamed += 1
        return InputIR(var_name=new_name, prompt=instr.prompt, source_line=instr.source_line)

    return instr, renamed


def convert_to_ssa(program: IRProgram) -> Tuple[IRProgram, SSAReport]:
    """Convert IR program to SSA form using CFG merge information."""
    cfg = build_cfg(program)
    if not cfg.blocks:
        return IRProgram(instructions=[]), SSAReport()

    report = SSAReport()
    counters: Dict[str, int] = defaultdict(int)
    out_versions: Dict[int, Dict[str, str]] = {}

    renamed_blocks: Dict[int, List[IRInstr]] = {}
    ordered_ids = [b.block_id for b in cfg.blocks]

    for bid in ordered_ids:
        block = cfg.blocks[bid]
        preds = sorted(cfg.predecessors(bid))

        incoming: Dict[str, str] = {}
        if preds:
            keys: Set[str] = set()
            for p in preds:
                keys.update(out_versions.get(p, {}).keys())

            for name in sorted(keys):
                versions = {
                    out_versions[p][name]
                    for p in preds
                    if name in out_versions.get(p, {})
                }
                if len(versions) == 1:
                    incoming[name] = next(iter(versions))

        current = dict(incoming)

        phi_instrs: List[IRInstr] = []
        if preds:
            keys: Set[str] = set()
            for p in preds:
                keys.update(out_versions.get(p, {}).keys())
            for name in sorted(keys):
                versions = {
                    out_versions[p][name]
                    for p in preds
                    if name in out_versions.get(p, {})
                }
                if len(versions) > 1:
                    counters[name] += 1
                    new_name = f"{name}_{counters[name]}"
                    current[name] = new_name
                    sources = {
                        f"B{p}": _materialize_name(name, out_versions[p].get(name, f"{name}_0"))
                        for p in preds
                    }
                    phi_instrs.append(
                        Phi(
                            result=_materialize_name(name, new_name),
                            sources=sources,
                            source_line=block.instructions[0].source_line if block.instructions else 1,
                        )
                    )
                    report.phi_inserted += 1

        body: List[IRInstr] = []
        inserted_phi = False

        for instr in block.instructions:
            if isinstance(instr, LabelInstr):
                body.append(instr)
                if not inserted_phi and phi_instrs:
                    body.extend(phi_instrs)
                    inserted_phi = True
                continue

            renamed_reads = _rename_instruction_reads(instr, current)
            renamed_full, ndefs = _rename_definition_target(renamed_reads, current, counters)
            report.definitions_renamed += ndefs
            body.append(renamed_full)

        if not inserted_phi and phi_instrs:
            body = phi_instrs + body

        renamed_blocks[bid] = body
        out_versions[bid] = dict(current)

    flat: List[IRInstr] = []
    for bid in ordered_ids:
        flat.extend(renamed_blocks[bid])

    return IRProgram(instructions=flat), report

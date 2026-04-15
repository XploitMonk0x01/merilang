"""Advanced compiler feature tests (CFG, optimizer, backpatching, runtime frames)."""

from merilang.ast_nodes_enhanced import (
    AssignmentNode,
    BinaryOpNode,
    BooleanNode,
    DictNode,
    ListNode,
    NumberNode,
    ProgramNode,
)
from merilang.interpreter_enhanced import Interpreter, UserFunction
from merilang.ir_analysis import build_basic_blocks, build_cfg
from merilang.ir_generator import IRGenerator
from merilang.ir_nodes import (
    Assign,
    CondJump,
    Copy,
    IRProgram,
    Jump,
    Label,
    LabelInstr,
    Return,
    Temp,
    BinOp,
    Phi,
)
from merilang.ir_optimizer import optimize_ir
from merilang.ir_dag import optimize_ir_with_dag
from merilang.ir_ssa import convert_to_ssa


def test_cfg_basic_blocks_for_branching_program() -> None:
    program = IRProgram(
        instructions=[
            Assign(result=Temp("t0"), value=True, source_line=1),
            CondJump(
                condition=Temp("t0"),
                true_label=Label("L_true"),
                false_label=Label("L_false"),
                source_line=1,
            ),
            LabelInstr(label=Label("L_true"), source_line=2),
            Assign(result=Temp("t1"), value=1, source_line=2),
            Jump(target=Label("L_end"), source_line=2),
            LabelInstr(label=Label("L_false"), source_line=3),
            Assign(result=Temp("t2"), value=0, source_line=3),
            LabelInstr(label=Label("L_end"), source_line=4),
            Return(value=None, source_line=4),
        ]
    )

    blocks = build_basic_blocks(program)
    cfg = build_cfg(program)

    assert len(blocks) == 4
    assert cfg.successors(0) == {1, 2}
    assert cfg.successors(1) == {3}
    assert cfg.successors(2) == {3}
    assert cfg.successors(3) == set()


def test_ir_optimizer_constant_fold_and_dead_code_elimination() -> None:
    program = IRProgram(
        instructions=[
            BinOp(result=Temp("t0"), op="+", left=2, right=3, source_line=1),
            Copy(dest="x", src=Temp("t0"), source_line=1),
            Assign(result=Temp("t_dead"), value=999, source_line=2),
        ]
    )

    optimized, report = optimize_ir(program)

    assert report.constant_folds >= 1
    assert report.dead_instructions_removed >= 1
    assert all(
        not (isinstance(i, Assign) and i.result.name == "t_dead")
        for i in optimized.instructions
    )


def test_ir_generator_short_circuit_uses_backpatched_control_flow() -> None:
    ast = ProgramNode(
        statements=[
            AssignmentNode(
                name="x",
                value=BinaryOpNode(
                    operator="aur",
                    left=BooleanNode(True, line=1),
                    right=BooleanNode(False, line=1),
                    line=1,
                ),
                line=1,
            )
        ],
        line=1,
    )

    gen = IRGenerator()
    ir = gen.generate(ast)

    cond_jumps = [i for i in ir.instructions if isinstance(i, CondJump)]
    assert len(cond_jumps) >= 2
    assert any(isinstance(i, LabelInstr) and i.label.name.startswith("bool_true_") for i in ir.instructions)
    assert any(isinstance(i, LabelInstr) and i.label.name.startswith("bool_false_") for i in ir.instructions)


def test_activation_record_lifecycle_for_function_call() -> None:
    interp = Interpreter()
    seen_depth = {"value": 0}

    original = interp.visit_NumberNode

    def visit_number_spy(node: NumberNode):
        seen_depth["value"] = max(seen_depth["value"], len(interp.activation_records))
        return original(node)

    interp.visit_NumberNode = visit_number_spy  # type: ignore[assignment]

    func = UserFunction(
        name="probe",
        parameters=["a"],
        body=[NumberNode(123, line=1)],
        closure=interp.current_env,
    )

    result = interp._call_user_function(func, [1], line=1)

    assert result is None
    assert seen_depth["value"] == 1
    assert len(interp.activation_records) == 0


def test_ssa_conversion_inserts_phi_for_merge_block() -> None:
    program = IRProgram(
        instructions=[
            Assign(result=Temp("t0"), value=True, source_line=1),
            CondJump(
                condition=Temp("t0"),
                true_label=Label("L_true"),
                false_label=Label("L_false"),
                source_line=1,
            ),
            LabelInstr(label=Label("L_true"), source_line=2),
            Copy(dest="x", src=Temp("t0"), source_line=2),
            Jump(target=Label("L_join"), source_line=2),
            LabelInstr(label=Label("L_false"), source_line=3),
            Assign(result=Temp("t1"), value=0, source_line=3),
            Copy(dest="x", src=Temp("t1"), source_line=3),
            LabelInstr(label=Label("L_join"), source_line=4),
            Copy(dest=Temp("t2"), src="x", source_line=4),
            Return(value=Temp("t2"), source_line=4),
        ]
    )

    ssa_program, report = convert_to_ssa(program)
    assert report.phi_inserted >= 1
    assert any(isinstance(i, Phi) for i in ssa_program.instructions)


def test_dag_local_optimizer_reuses_expression_inside_block() -> None:
    program = IRProgram(
        instructions=[
            BinOp(result=Temp("t0"), op="+", left=Temp("a"), right=Temp("b"), source_line=1),
            BinOp(result=Temp("t1"), op="+", left=Temp("a"), right=Temp("b"), source_line=2),
        ]
    )

    optimized, rewrites = optimize_ir_with_dag(program)

    assert rewrites >= 1
    assert isinstance(optimized.instructions[1], Copy)


def test_runtime_stack_and_heap_models_are_explicitly_maintained() -> None:
    interp = Interpreter()

    # Heap allocations through AST visitors.
    list_node = ListNode(elements=[NumberNode(1, line=1), NumberNode(2, line=1)], line=1)
    dict_node = DictNode(pairs=[(NumberNode(1, line=1), NumberNode(2, line=1))], line=1)

    list_value = interp.visit_ListNode(list_node)
    dict_value = interp.visit_DictNode(dict_node)

    assert isinstance(list_value, list)
    assert isinstance(dict_value, dict)

    # Stack allocations through function calls.
    func = UserFunction(
        name="probe_runtime",
        parameters=["a"],
        body=[NumberNode(7, line=1)],
        closure=interp.current_env,
    )
    interp._call_user_function(func, [3], line=1)

    snapshot = interp.runtime_memory_snapshot()
    assert snapshot["stack_depth"] == 0
    assert snapshot["heap"]["total"] >= 2

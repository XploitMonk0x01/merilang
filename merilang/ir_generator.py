"""
IR Generator for Merilang – AST to Three-Address Code (3AC).

This module walks the AST produced by the parser and flattens it into a
linear sequence of ``IRInstr`` objects (defined in ``ir_nodes.py``).

Design goals:
  * Each complex sub-expression becomes a chain of temporaries (t0, t1, …).
  * Control flow becomes labels + unconditional / conditional jumps.
  * Functions become label-delimited blocks with PARAM / CALL / RETURN.
  * The resulting ``IRProgram`` can be pretty-printed, further optimised, or
    fed to a VM / code-generator back-end.

Author: Merilang Team
Version: 3.0 - Compiler Front-End
"""

from __future__ import annotations

from typing import List, Optional

from merilang.ast_nodes_enhanced import (
    ASTNode, ProgramNode, NumberNode, StringNode, BooleanNode,
    ListNode, DictNode, VariableNode, AssignmentNode,
    BinaryOpNode, UnaryOpNode, ParenthesizedNode,
    IfNode, WhileNode, ForNode, BreakNode, ContinueNode,
    FunctionDefNode, FunctionCallNode, ReturnNode, LambdaNode,
    ClassDefNode, NewObjectNode, MethodCallNode, PropertyAccessNode,
    PropertyAssignmentNode, ThisNode, SuperNode,
    TryNode, ThrowNode, PrintNode, InputNode, ImportNode,
    IndexNode, IndexAssignmentNode,
)
from merilang.ir_nodes import (
    IRInstr, IRProgram, Temp, Label,
    Assign, BinOp, UnaryOp, Copy,
    LabelInstr, Jump, CondJump,
    FuncLabel, Param, Call, Return,
    NewObj, FieldLoad, FieldStore,
    IndexLoad, IndexStore,
    PrintIR, InputIR,
    ThrowIR, TryBegin, TryEnd, CatchBegin,
)


# ---------------------------------------------------------------------------
# Counter helpers
# ---------------------------------------------------------------------------

class _TempGen:
    """Generates monotonically increasing temporary variable names."""

    def __init__(self) -> None:
        self._count = 0

    def fresh(self) -> Temp:
        t = Temp(f"t{self._count}")
        self._count += 1
        return t


class _LabelGen:
    """Generates monotonically increasing jump-label names."""

    def __init__(self) -> None:
        self._count = 0

    def fresh(self, hint: str = "L") -> Label:
        lbl = Label(f"{hint}{self._count}")
        self._count += 1
        return lbl


# ---------------------------------------------------------------------------
# IR Generator
# ---------------------------------------------------------------------------

class IRGenerator:
    """Translate a Merilang AST into a flat list of 3AC instructions.

    Usage::

        gen = IRGenerator()
        ir  = gen.generate(program_node)
        print(ir.dump())

    The ``generate()`` method returns an ``IRProgram`` whose ``instructions``
    list is a flat, ordered 3AC representation suitable for optimisation or
    VM execution.

    Attributes:
        _program:   The ``IRProgram`` being built.
        _temps:     Fresh temporary generator.
        _labels:    Fresh label generator.
        _break_stack:
            Stack of labels to jump to when ``ruk`` (break) is encountered.
        _continue_stack:
            Stack of labels to jump to when ``age_badho`` (continue) is seen.
    """

    def __init__(self) -> None:
        self._program:        IRProgram  = IRProgram()
        self._temps:          _TempGen   = _TempGen()
        self._labels:         _LabelGen  = _LabelGen()
        self._break_stack:    List[Label] = []
        self._continue_stack: List[Label] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, node: ProgramNode) -> IRProgram:
        """Translate *node* into an ``IRProgram`` and return it.

        Args:
            node: Root ``ProgramNode`` from the parser.

        Returns:
            An ``IRProgram`` containing the full 3AC instruction sequence.
        """
        self._visit(node)
        return self._program

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit(self, instr: IRInstr) -> None:
        """Append a single instruction to the program."""
        self._program.append(instr)

    def _fresh_temp(self) -> Temp:
        return self._temps.fresh()

    def _fresh_label(self, hint: str = "L") -> Label:
        return self._labels.fresh(hint)

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def _visit(self, node: ASTNode) -> Optional[object]:
        """Dispatch to a type-specific visitor; return the result operand."""
        method = f"_visit_{type(node).__name__}"
        visitor = getattr(self, method, self._visit_generic)
        return visitor(node)

    def _visit_generic(self, node: ASTNode) -> None:  # pragma: no cover
        """No-op fallback for unhandled node types."""
        pass

    # ------------------------------------------------------------------
    # Literals
    # ------------------------------------------------------------------

    def _visit_NumberNode(self, node: NumberNode) -> Temp:
        t = self._fresh_temp()
        self._emit(Assign(source_line=node.line, result=t, value=node.value))
        return t

    def _visit_StringNode(self, node: StringNode) -> Temp:
        t = self._fresh_temp()
        self._emit(Assign(source_line=node.line, result=t, value=node.value))
        return t

    def _visit_BooleanNode(self, node: BooleanNode) -> Temp:
        t = self._fresh_temp()
        self._emit(Assign(source_line=node.line, result=t, value=node.value))
        return t

    def _visit_ListNode(self, node: ListNode) -> Temp:
        # Emit each element, then a special CALL to the list constructor.
        elem_temps = [self._visit(e) for e in node.elements]
        for et in elem_temps:
            self._emit(Param(source_line=node.line, value=et))
        t = self._fresh_temp()
        self._emit(Call(source_line=node.line, result=t,
                        func_name="__list__", n_args=len(node.elements)))
        return t

    def _visit_DictNode(self, node: DictNode) -> Temp:
        for key, val in node.pairs:
            kt = self._visit(key)
            vt = self._visit(val)
            self._emit(Param(source_line=node.line, value=kt))
            self._emit(Param(source_line=node.line, value=vt))
        t = self._fresh_temp()
        self._emit(Call(source_line=node.line, result=t,
                        func_name="__dict__", n_args=len(node.pairs) * 2))
        return t

    # ------------------------------------------------------------------
    # Variables
    # ------------------------------------------------------------------

    def _visit_VariableNode(self, node: VariableNode) -> Temp:
        """Load a named variable into a fresh temporary."""
        t = self._fresh_temp()
        self._emit(Copy(source_line=node.line, dest=t, src=node.name))
        return t

    def _visit_AssignmentNode(self, node: AssignmentNode) -> None:
        val_temp = self._visit(node.value)
        self._emit(Copy(source_line=node.line, dest=node.name, src=val_temp))

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def _visit_BinaryOpNode(self, node: BinaryOpNode) -> Temp:
        """Emit sub-expressions then the BinOp instruction.

        Example:
            ``x = a + b * c``
            → ``t0 = b``, ``t1 = c``, ``t2 = t0 * t1``,
              ``t3 = a``, ``t4 = t3 + t2``, ``x = t4``
        """
        left_temp  = self._visit(node.left)
        right_temp = self._visit(node.right)
        result     = self._fresh_temp()
        self._emit(BinOp(
            source_line=node.line,
            result=result,
            op=node.operator,
            left=left_temp,
            right=right_temp,
        ))
        return result

    def _visit_UnaryOpNode(self, node: UnaryOpNode) -> Temp:
        operand = self._visit(node.operand)
        result  = self._fresh_temp()
        self._emit(UnaryOp(
            source_line=node.line,
            result=result,
            op=node.operator,
            operand=operand,
        ))
        return result

    def _visit_ParenthesizedNode(self, node: ParenthesizedNode) -> object:
        return self._visit(node.expression)

    # ------------------------------------------------------------------
    # Control Flow
    # ------------------------------------------------------------------

    def _visit_IfNode(self, node: IfNode) -> None:
        """Emit the standard if-elif-else ladder using labels and jumps.

        Structure::

            <condition>
            IF cond GOTO then_L ELSE elif0_L (or else_L / end_L)
            then_L:
              <then body>
              GOTO end_L
            elif0_L:
              <elif cond>
              IF … (chain continues)
            else_L:
              <else body>
            end_L:
        """
        then_label = self._fresh_label("then_")
        end_label  = self._fresh_label("if_end_")

        # Build a list of (cond_temp?, label) pairs for elif chains + else.
        # We'll generate them left-to-right.
        elif_labels = [self._fresh_label("elif_") for _ in node.elif_branches]
        else_label  = self._fresh_label("else_") if node.else_branch is not None else None

        # ---- main condition ----
        cond_temp = self._visit(node.condition)
        first_false = elif_labels[0] if elif_labels else (else_label or end_label)
        self._emit(CondJump(
            source_line=node.line,
            condition=cond_temp,
            true_label=then_label,
            false_label=first_false,
        ))

        # ---- then branch ----
        self._emit(LabelInstr(source_line=node.line, label=then_label))
        for stmt in node.then_branch:
            self._visit(stmt)
        self._emit(Jump(source_line=node.line, target=end_label))

        # ---- elif branches ----
        for idx, (elif_cond, elif_body) in enumerate(node.elif_branches):
            self._emit(LabelInstr(source_line=node.line, label=elif_labels[idx]))
            ec_temp = self._visit(elif_cond)
            next_false = (elif_labels[idx + 1] if idx + 1 < len(elif_labels)
                          else (else_label or end_label))
            next_true  = self._fresh_label("elif_body_")
            self._emit(CondJump(
                source_line=node.line,
                condition=ec_temp,
                true_label=next_true,
                false_label=next_false,
            ))
            self._emit(LabelInstr(source_line=node.line, label=next_true))
            for stmt in elif_body:
                self._visit(stmt)
            self._emit(Jump(source_line=node.line, target=end_label))

        # ---- else branch ----
        if node.else_branch is not None:
            self._emit(LabelInstr(source_line=node.line, label=else_label))  # type: ignore[arg-type]
            for stmt in node.else_branch:
                self._visit(stmt)

        self._emit(LabelInstr(source_line=node.line, label=end_label))

    def _visit_WhileNode(self, node: WhileNode) -> None:
        """Emit a while loop with labelled entry and exit.

        Structure::

            loop_start_L:
              <condition>
              IF cond GOTO loop_body_L ELSE loop_end_L
            loop_body_L:
              <body>
              GOTO loop_start_L
            loop_end_L:
        """
        loop_start = self._fresh_label("while_start_")
        loop_body  = self._fresh_label("while_body_")
        loop_end   = self._fresh_label("while_end_")

        self._break_stack.append(loop_end)
        self._continue_stack.append(loop_start)

        self._emit(LabelInstr(source_line=node.line, label=loop_start))
        cond_temp = self._visit(node.condition)
        self._emit(CondJump(
            source_line=node.line,
            condition=cond_temp,
            true_label=loop_body,
            false_label=loop_end,
        ))
        self._emit(LabelInstr(source_line=node.line, label=loop_body))
        for stmt in node.body:
            self._visit(stmt)
        self._emit(Jump(source_line=node.line, target=loop_start))
        self._emit(LabelInstr(source_line=node.line, label=loop_end))

        self._break_stack.pop()
        self._continue_stack.pop()

    def _visit_ForNode(self, node: ForNode) -> None:
        """Emit a for-in loop using an internal iterator protocol.

        Lowered as::

            iter_t = CALL __iter__ iterable
            loop_start:
              has_next_t = CALL __has_next__ iter_t
              IF has_next_t GOTO loop_body ELSE loop_end
            loop_body:
              var = CALL __next__ iter_t
              <body>
              GOTO loop_start
            loop_end:
        """
        iter_t    = self._fresh_temp()
        has_t     = self._fresh_temp()
        loop_start = self._fresh_label("for_start_")
        loop_body  = self._fresh_label("for_body_")
        loop_end   = self._fresh_label("for_end_")

        iterable_t = self._visit(node.iterable)
        self._emit(Param(source_line=node.line, value=iterable_t))
        self._emit(Call(source_line=node.line, result=iter_t,
                        func_name="__iter__", n_args=1))

        self._break_stack.append(loop_end)
        self._continue_stack.append(loop_start)

        self._emit(LabelInstr(source_line=node.line, label=loop_start))
        self._emit(Param(source_line=node.line, value=iter_t))
        self._emit(Call(source_line=node.line, result=has_t,
                        func_name="__has_next__", n_args=1))
        self._emit(CondJump(
            source_line=node.line,
            condition=has_t,
            true_label=loop_body,
            false_label=loop_end,
        ))

        self._emit(LabelInstr(source_line=node.line, label=loop_body))
        next_t = self._fresh_temp()
        self._emit(Param(source_line=node.line, value=iter_t))
        self._emit(Call(source_line=node.line, result=next_t,
                        func_name="__next__", n_args=1))
        self._emit(Copy(source_line=node.line, dest=node.variable, src=next_t))
        for stmt in node.body:
            self._visit(stmt)
        self._emit(Jump(source_line=node.line, target=loop_start))
        self._emit(LabelInstr(source_line=node.line, label=loop_end))

        self._break_stack.pop()
        self._continue_stack.pop()

    def _visit_BreakNode(self, node: BreakNode) -> None:
        if self._break_stack:
            self._emit(Jump(source_line=node.line, target=self._break_stack[-1]))

    def _visit_ContinueNode(self, node: ContinueNode) -> None:
        if self._continue_stack:
            self._emit(Jump(source_line=node.line, target=self._continue_stack[-1]))

    # ------------------------------------------------------------------
    # Functions
    # ------------------------------------------------------------------

    def _visit_FunctionDefNode(self, node: FunctionDefNode) -> None:
        """Emit the function's IR block: FuncLabel → body → RETURN."""
        self._emit(FuncLabel(source_line=node.line, func_name=node.name))
        # Parameters are received via a calling convention – they are simply
        # named variables available in the function body.
        for stmt in node.body:
            self._visit(stmt)
        # Implicit void return at end.
        self._emit(Return(source_line=node.line, value=None))

    def _visit_ReturnNode(self, node: ReturnNode) -> None:
        val = self._visit(node.value) if node.value is not None else None
        self._emit(Return(source_line=node.line, value=val))

    def _visit_FunctionCallNode(self, node: FunctionCallNode) -> Temp:
        for arg in node.arguments:
            arg_temp = self._visit(arg)
            self._emit(Param(source_line=node.line, value=arg_temp))
        result = self._fresh_temp()
        self._emit(Call(source_line=node.line, result=result,
                        func_name=node.name, n_args=len(node.arguments)))
        return result

    def _visit_LambdaNode(self, node: LambdaNode) -> Temp:
        """Emit an anonymous function as an auto-named FUNC block."""
        func_name = f"__lambda_{id(node)}__"
        end_label = self._fresh_label("lambda_end_")
        # Jump over the lambda body at definition time.
        self._emit(Jump(source_line=node.line, target=end_label))
        self._emit(FuncLabel(source_line=node.line, func_name=func_name))
        body_t = self._visit(node.body)
        self._emit(Return(source_line=node.line, value=body_t))
        self._emit(LabelInstr(source_line=node.line, label=end_label))
        # The runtime will bind this closure to a temp.
        t = self._fresh_temp()
        self._emit(Assign(source_line=node.line, result=t, value=func_name))
        return t

    # ------------------------------------------------------------------
    # OOP
    # ------------------------------------------------------------------

    def _visit_ClassDefNode(self, node: ClassDefNode) -> None:
        lbl = self._fresh_label(f"class_{node.name}_")
        end_lbl = self._fresh_label(f"class_{node.name}_end_")
        self._emit(Jump(source_line=node.line, target=end_lbl))
        self._emit(LabelInstr(source_line=node.line, label=lbl))
        for method in node.methods:
            self._visit_FunctionDefNode(method)
        self._emit(LabelInstr(source_line=node.line, label=end_lbl))

    def _visit_NewObjectNode(self, node: NewObjectNode) -> Temp:
        t = self._fresh_temp()
        self._emit(NewObj(source_line=node.line, result=t,
                          class_name=node.class_name))
        # Call __init__ with arguments.
        for arg in node.arguments:
            arg_t = self._visit(arg)
            self._emit(Param(source_line=node.line, value=arg_t))
        init_result = self._fresh_temp()
        self._emit(Call(source_line=node.line, result=init_result,
                        func_name=f"{node.class_name}.__init__",
                        n_args=len(node.arguments)))
        return t

    def _visit_MethodCallNode(self, node: MethodCallNode) -> Temp:
        obj_t = self._visit(node.object)
        # Implicit 'self' param.
        self._emit(Param(source_line=node.line, value=obj_t))
        for arg in node.arguments:
            arg_t = self._visit(arg)
            self._emit(Param(source_line=node.line, value=arg_t))
        result = self._fresh_temp()
        self._emit(Call(source_line=node.line, result=result,
                        func_name=node.method_name,
                        n_args=len(node.arguments) + 1))
        return result

    def _visit_PropertyAccessNode(self, node: PropertyAccessNode) -> Temp:
        obj_t  = self._visit(node.object)
        result = self._fresh_temp()
        self._emit(FieldLoad(source_line=node.line, result=result,
                             obj=obj_t, field_name=node.property_name))
        return result

    def _visit_PropertyAssignmentNode(self, node: PropertyAssignmentNode) -> None:
        obj_t = self._visit(node.object)
        val_t = self._visit(node.value)
        self._emit(FieldStore(source_line=node.line, obj=obj_t,
                              field_name=node.property_name, value=val_t))

    def _visit_ThisNode(self, node: ThisNode) -> Temp:
        t = self._fresh_temp()
        self._emit(Copy(source_line=node.line, dest=t, src="__self__"))
        return t

    def _visit_SuperNode(self, node: SuperNode) -> Temp:
        for arg in node.arguments:
            arg_t = self._visit(arg)
            self._emit(Param(source_line=node.line, value=arg_t))
        result = self._fresh_temp()
        self._emit(Call(source_line=node.line, result=result,
                        func_name=f"__super__.{node.method_name}",
                        n_args=len(node.arguments)))
        return result

    # ------------------------------------------------------------------
    # Error Handling
    # ------------------------------------------------------------------

    def _visit_TryNode(self, node: TryNode) -> None:
        catch_label   = self._fresh_label("catch_")
        finally_label = self._fresh_label("finally_") if node.finally_block else None
        end_label     = self._fresh_label("try_end_")

        self._emit(TryBegin(source_line=node.line,
                            catch_label=catch_label,
                            finally_label=finally_label))
        for stmt in node.try_block:
            self._visit(stmt)
        self._emit(TryEnd(source_line=node.line))
        self._emit(Jump(source_line=node.line,
                        target=finally_label or end_label))

        self._emit(LabelInstr(source_line=node.line, label=catch_label))
        self._emit(CatchBegin(source_line=node.line, var_name=node.exception_var))
        if node.catch_block:
            for stmt in node.catch_block:
                self._visit(stmt)
        self._emit(Jump(source_line=node.line,
                        target=finally_label or end_label))

        if finally_label and node.finally_block:
            self._emit(LabelInstr(source_line=node.line, label=finally_label))
            for stmt in node.finally_block:
                self._visit(stmt)

        self._emit(LabelInstr(source_line=node.line, label=end_label))

    def _visit_ThrowNode(self, node: ThrowNode) -> None:
        val_t = self._visit(node.exception)
        self._emit(ThrowIR(source_line=node.line, value=val_t))

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------

    def _visit_PrintNode(self, node: PrintNode) -> None:
        arg_temps = [self._visit(a) for a in node.arguments]
        self._emit(PrintIR(source_line=node.line, args=arg_temps))

    def _visit_InputNode(self, node: InputNode) -> None:
        prompt = self._visit(node.prompt) if node.prompt else None
        self._emit(InputIR(source_line=node.line,
                           var_name=node.variable, prompt=prompt))

    def _visit_ImportNode(self, node: ImportNode) -> None:
        # Lowered to a runtime call.
        mod_t = self._fresh_temp()
        self._emit(Assign(source_line=node.line,
                          result=mod_t, value=node.module_name))
        self._emit(Param(source_line=node.line, value=mod_t))
        self._emit(Call(source_line=node.line, result=None,
                        func_name="__import__", n_args=1))

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def _visit_IndexNode(self, node: IndexNode) -> Temp:
        obj_t   = self._visit(node.object)
        index_t = self._visit(node.index)
        result  = self._fresh_temp()
        self._emit(IndexLoad(source_line=node.line, result=result,
                             obj=obj_t, index=index_t))
        return result

    def _visit_IndexAssignmentNode(self, node: IndexAssignmentNode) -> None:
        obj_t   = self._visit(node.object)
        index_t = self._visit(node.index)
        val_t   = self._visit(node.value)
        self._emit(IndexStore(source_line=node.line, obj=obj_t,
                              index=index_t, value=val_t))

    # ------------------------------------------------------------------
    # Program root
    # ------------------------------------------------------------------

    def _visit_ProgramNode(self, node: ProgramNode) -> None:
        for stmt in node.statements:
            self._visit(stmt)

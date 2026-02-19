"""
Semantic Analyzer for Merilang.

Performs a static analysis pass over the AST *before* the interpreter runs,
catching errors that are syntactically valid but semantically wrong:

  * Undefined variables / functions at use sites
  * Type-checking of binary and unary operations on known-type operands
  * Function call arity (argument count vs. parameter count)
  * Re-declaration of a name in the same scope

The analyzer uses the SymbolTable (stack-of-hash-maps) from symbol_table.py
for scope tracking and returns a (possibly empty) list of SemanticError
instances. The caller decides whether to abort execution.

Author: Merilang Team
Version: 3.0 - Compiler Front-End
"""

from __future__ import annotations

import difflib
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
from merilang.symbol_table import MType, Symbol, SymbolKind, SymbolTable
from merilang.errors_enhanced import (
    SemanticError, TypeCheckError, UndefinedNameError, RedefinitionError,
    MeriLangError,
)


# ---------------------------------------------------------------------------
# Type-checking rules for binary operators
# ---------------------------------------------------------------------------

# Maps (left_type, op, right_type) → True  means always valid.
# Maps (left_type, op, right_type) → False means always a type error.
# When a pair is absent the check is skipped (i.e. treated as dynamic).
_NUMERIC_OPS = {"+", "-", "*", "/", "%", ">", "<", ">=", "<="}
_EQUALITY_OPS = {"==", "!="}
_LOGICAL_OPS = {"aur", "ya"}

# Operations that are valid between two STRINGs
_STRING_VALID_OPS = {"+", "==", "!="}


def _check_binary_types(
    op: str, left: str, right: str, line: int
) -> Optional[TypeCheckError]:
    """Return a TypeCheckError if *op* is illegal for *left* × *right*.

    Only fires when *both* operand types are known (not MType.ANY).

    Args:
        op:    Operator string ("+", "-", "aur", etc.)
        left:  MType tag for the left operand.
        right: MType tag for the right operand.
        line:  Source line for error reporting.

    Returns:
        ``TypeCheckError`` if the operation is invalid, ``None`` otherwise.
    """
    if left == MType.ANY or right == MType.ANY:
        return None  # dynamic – skip static check

    if op in _NUMERIC_OPS:
        if left == MType.NUMBER and right == MType.NUMBER:
            return None   # valid
        if left == MType.STRING and right == MType.STRING and op == "+":
            return None   # string concatenation is fine
        return TypeCheckError.invalid_operation(op, left, right, line)

    if op in _EQUALITY_OPS:
        return None   # equality always OK between any types

    if op in _LOGICAL_OPS:
        # Both sides should be bool; warn but allow for now.
        return None

    return None   # unrecognised op – leave to interpreter


def _check_unary_type(
    op: str, operand_type: str, line: int
) -> Optional[TypeCheckError]:
    """Return a TypeCheckError if *op* is illegal for *operand_type*.

    Args:
        op:           Unary operator ("-" or "nahi").
        operand_type: MType tag.
        line:         Source line.

    Returns:
        ``TypeCheckError`` or ``None``.
    """
    if operand_type == MType.ANY:
        return None
    if op == "-" and operand_type != MType.NUMBER:
        return TypeCheckError.unary_invalid(op, operand_type, line)
    if op == "nahi" and operand_type != MType.BOOL:
        return TypeCheckError.unary_invalid(op, operand_type, line)
    return None


# ---------------------------------------------------------------------------
# SemanticAnalyzer
# ---------------------------------------------------------------------------

class SemanticAnalyzer:
    """Visitor-based static analyser for Merilang ASTs.

    Walk the AST produced by the parser, maintaining a ``SymbolTable`` scope
    stack and collecting ``SemanticError`` instances.  The interpreter is only
    invoked if ``errors`` is empty after ``analyze()`` returns.

    Usage::

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(program_node)
        if errors:
            for e in errors:
                print(e)
        else:
            interpreter.execute(program_node)

    Attributes:
        errors:       All errors collected during the analysis pass.
        scope:        The current innermost ``SymbolTable``.
        _in_function: Stack of function names (for return-outside-function checks).
        _in_loop:     Depth counter for break/continue validity.
    """

    def __init__(self) -> None:
        self.errors: List[SemanticError] = []
        self.scope: SymbolTable = SymbolTable()   # global scope
        self._function_stack: List[str] = []
        self._in_loop: int = 0
        self._class_stack: List[str] = []

        # Pre-populate global scope with built-in functions so they resolve.
        self._register_builtins()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def analyze(self, node: ProgramNode) -> List[SemanticError]:
        """Run the full analysis pass and return all collected errors.

        Args:
            node: The root ``ProgramNode`` returned by the parser.

        Returns:
            (Possibly empty) list of ``SemanticError`` instances.
        """
        self._visit(node)
        return self.errors

    # ------------------------------------------------------------------
    # Built-in function registration
    # ------------------------------------------------------------------

    def _register_builtins(self) -> None:
        """Seed the global symbol table with known built-in names."""
        builtins = [
            # I/O
            ("print",   0),  # variadic – arity bypass via ANY
            ("input",   1),
            # Type conversions
            ("str",     1),
            ("int",     1),
            ("float",   1),
            ("bool",    1),
            ("type",    1),
            # List operations
            ("length",  1),
            ("append",  2),
            ("pop",     2),
            ("insert",  3),
            ("sort",    1),
            ("reverse", 1),
            ("sum",     1),
            ("min",     1),
            ("max",     1),
            # String operations
            ("upper",   1),
            ("lower",   1),
            ("split",   2),
            ("join",    2),
            ("replace", 3),
            # Math
            ("abs",     1),
            ("round",   2),
            # Range
            ("range",   1),
        ]
        for name, arity in builtins:
            sym = Symbol(
                name=name,
                kind=SymbolKind.FUNCTION,
                inferred_type=MType.ANY,
                line=0,
                param_count=arity,
            )
            self.scope.define(sym)

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def _visit(self, node: ASTNode) -> str:
        """Dispatch to the appropriate ``_visit_*`` method.

        Args:
            node: Any AST node.

        Returns:
            The inferred ``MType`` tag for the node (useful for type checking).
        """
        method_name = f"_visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self._visit_generic)
        return visitor(node)

    def _visit_generic(self, node: ASTNode) -> str:
        """Fallback visitor: traverse children if the node has a ``body``."""
        # Try to visit any list-of-nodes field we recognise.
        for attr in ("statements", "body", "then_branch", "else_branch",
                     "try_block", "catch_block", "finally_block", "elements"):
            val = getattr(node, attr, None)
            if isinstance(val, list):
                for child in val:
                    if isinstance(child, ASTNode):
                        self._visit(child)
        return MType.ANY

    # ------------------------------------------------------------------
    # Error helpers
    # ------------------------------------------------------------------

    def _error(self, err: SemanticError) -> None:
        self.errors.append(err)

    def _similar_names(self, name: str) -> List[str]:
        """Find up to 3 names in scope similar to *name* (for suggestions)."""
        all_names = self.scope.all_names()
        return difflib.get_close_matches(name, all_names, n=3, cutoff=0.6)

    # ------------------------------------------------------------------
    # Visitors – Literals
    # ------------------------------------------------------------------

    def _visit_NumberNode(self, node: NumberNode) -> str:
        return MType.NUMBER

    def _visit_StringNode(self, node: StringNode) -> str:
        return MType.STRING

    def _visit_BooleanNode(self, node: BooleanNode) -> str:
        return MType.BOOL

    def _visit_ListNode(self, node: ListNode) -> str:
        for elem in node.elements:
            self._visit(elem)
        return MType.LIST

    def _visit_DictNode(self, node: DictNode) -> str:
        for key, val in node.pairs:
            self._visit(key)
            self._visit(val)
        return MType.DICT

    # ------------------------------------------------------------------
    # Visitors – Variables
    # ------------------------------------------------------------------

    def _visit_VariableNode(self, node: VariableNode) -> str:
        sym = self.scope.resolve(node.name)
        if sym is None:
            self._error(UndefinedNameError(
                name=node.name,
                line=node.line,
                similar_names=self._similar_names(node.name),
            ))
            return MType.ANY
        return sym.inferred_type

    def _visit_AssignmentNode(self, node: AssignmentNode) -> str:
        val_type = self._visit(node.value)

        # Check if already declared in *this* scope (re-declaration).
        existing = self.scope.resolve_local(node.name)
        if existing is not None and existing.kind == SymbolKind.VARIABLE:
            # Re-assignment to existing variable is allowed; skip.
            # Update inferred type so downstream checks use fresh info.
            existing.inferred_type  # (immutable dataclass – just note it)
        else:
            # New declaration.
            self.scope.define(Symbol(
                name=node.name,
                kind=SymbolKind.VARIABLE,
                inferred_type=val_type,
                line=node.line,
            ))
        return val_type

    # ------------------------------------------------------------------
    # Visitors – Operations
    # ------------------------------------------------------------------

    def _visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left_type  = self._visit(node.left)
        right_type = self._visit(node.right)

        err = _check_binary_types(node.operator, left_type, right_type, node.line)
        if err:
            self._error(err)

        # Determine result type.
        if node.operator in {">", "<", ">=", "<=", "==", "!=", "aur", "ya"}:
            return MType.BOOL
        if left_type == MType.NUMBER and right_type == MType.NUMBER:
            return MType.NUMBER
        if left_type == MType.STRING and right_type == MType.STRING:
            return MType.STRING
        return MType.ANY

    def _visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        operand_type = self._visit(node.operand)
        err = _check_unary_type(node.operator, operand_type, node.line)
        if err:
            self._error(err)
        if node.operator == "-":
            return MType.NUMBER
        if node.operator == "nahi":
            return MType.BOOL
        return MType.ANY

    def _visit_ParenthesizedNode(self, node: ParenthesizedNode) -> str:
        return self._visit(node.expression)

    # ------------------------------------------------------------------
    # Visitors – Control Flow
    # ------------------------------------------------------------------

    def _visit_IfNode(self, node: IfNode) -> str:
        self._visit(node.condition)

        self.scope = self.scope.enter_scope()
        for stmt in node.then_branch:
            self._visit(stmt)
        self.scope = self.scope.exit_scope()

        for elif_cond, elif_body in node.elif_branches:
            self._visit(elif_cond)
            self.scope = self.scope.enter_scope()
            for stmt in elif_body:
                self._visit(stmt)
            self.scope = self.scope.exit_scope()

        if node.else_branch is not None:
            self.scope = self.scope.enter_scope()
            for stmt in node.else_branch:
                self._visit(stmt)
            self.scope = self.scope.exit_scope()

        return MType.NONE

    def _visit_WhileNode(self, node: WhileNode) -> str:
        self._visit(node.condition)
        self._in_loop += 1
        self.scope = self.scope.enter_scope()
        for stmt in node.body:
            self._visit(stmt)
        self.scope = self.scope.exit_scope()
        self._in_loop -= 1
        return MType.NONE

    def _visit_ForNode(self, node: ForNode) -> str:
        self._visit(node.iterable)
        self._in_loop += 1
        self.scope = self.scope.enter_scope()
        # Bind the loop variable.
        self.scope.define(Symbol(
            name=node.variable,
            kind=SymbolKind.VARIABLE,
            inferred_type=MType.ANY,
            line=node.line,
        ))
        for stmt in node.body:
            self._visit(stmt)
        self.scope = self.scope.exit_scope()
        self._in_loop -= 1
        return MType.NONE

    def _visit_BreakNode(self, node: BreakNode) -> str:
        if self._in_loop == 0:
            self._error(SemanticError(
                message_en="'ruk' (break) used outside a loop",
                message_hi="'ruk' (ब्रेक) लूप के बाहर उपयोग किया गया",
                line=node.line,
            ))
        return MType.NONE

    def _visit_ContinueNode(self, node: ContinueNode) -> str:
        if self._in_loop == 0:
            self._error(SemanticError(
                message_en="'age_badho' (continue) used outside a loop",
                message_hi="'age_badho' लूप के बाहर उपयोग किया गया",
                line=node.line,
            ))
        return MType.NONE

    # ------------------------------------------------------------------
    # Visitors – Functions
    # ------------------------------------------------------------------

    def _visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        # Register the function name in the enclosing scope.
        existing = self.scope.resolve_local(node.name)
        if existing is not None:
            self._error(RedefinitionError(
                name=node.name,
                original_line=existing.line,
                line=node.line,
            ))
        else:
            self.scope.define(Symbol(
                name=node.name,
                kind=SymbolKind.FUNCTION,
                inferred_type=MType.FUNC,
                line=node.line,
                param_count=len(node.parameters),
            ))

        # Analyse the body in a new scope.
        self._function_stack.append(node.name)
        self.scope = self.scope.enter_scope()
        for param in node.parameters:
            self.scope.define(Symbol(
                name=param,
                kind=SymbolKind.PARAMETER,
                inferred_type=MType.ANY,
                line=node.line,
            ))
        for stmt in node.body:
            self._visit(stmt)
        self.scope = self.scope.exit_scope()
        self._function_stack.pop()
        return MType.FUNC

    def _visit_ReturnNode(self, node: ReturnNode) -> str:
        if not self._function_stack:
            self._error(SemanticError(
                message_en="'wapas' (return) used outside a function",
                message_hi="'wapas' (रिटर्न) फंक्शन के बाहर उपयोग किया गया",
                line=node.line,
            ))
        if node.value is not None:
            return self._visit(node.value)
        return MType.NONE

    def _visit_FunctionCallNode(self, node: FunctionCallNode) -> str:
        sym = self.scope.resolve(node.name)
        if sym is None:
            self._error(UndefinedNameError(
                name=node.name,
                line=node.line,
                similar_names=self._similar_names(node.name),
            ))
        else:
            # Arity check (skip for variadic built-ins stored with param_count=0).
            if (sym.kind in (SymbolKind.FUNCTION,) and
                    sym.param_count is not None and
                    sym.param_count != 0 and
                    len(node.arguments) != sym.param_count):
                self._error(SemanticError(
                    message_en=(
                        f"Function '{node.name}' expects {sym.param_count} "
                        f"argument(s), got {len(node.arguments)}"
                    ),
                    message_hi=(
                        f"फंक्शन '{node.name}' को {sym.param_count} "
                        f"तर्क(ों) की ज़रूरत है, मिले {len(node.arguments)}"
                    ),
                    line=node.line,
                ))
        # Visit arguments regardless.
        for arg in node.arguments:
            self._visit(arg)
        return MType.ANY

    def _visit_LambdaNode(self, node: LambdaNode) -> str:
        self.scope = self.scope.enter_scope()
        for param in node.parameters:
            self.scope.define(Symbol(
                name=param,
                kind=SymbolKind.PARAMETER,
                inferred_type=MType.ANY,
                line=node.line,
            ))
        self._visit(node.body)
        self.scope = self.scope.exit_scope()
        return MType.FUNC

    # ------------------------------------------------------------------
    # Visitors – OOP
    # ------------------------------------------------------------------

    def _visit_ClassDefNode(self, node: ClassDefNode) -> str:
        existing = self.scope.resolve_local(node.name)
        if existing is not None:
            self._error(RedefinitionError(
                name=node.name,
                original_line=existing.line,
                line=node.line,
            ))
        else:
            self.scope.define(Symbol(
                name=node.name,
                kind=SymbolKind.CLASS,
                inferred_type=MType.CLASS,
                line=node.line,
            ))

        if node.parent is not None:
            parent_sym = self.scope.resolve(node.parent)
            if parent_sym is None:
                self._error(UndefinedNameError(
                    name=node.parent,
                    line=node.line,
                    similar_names=self._similar_names(node.parent),
                ))

        self._class_stack.append(node.name)
        self.scope = self.scope.enter_scope()
        for method in node.methods:
            self._visit_FunctionDefNode(method)
        self.scope = self.scope.exit_scope()
        self._class_stack.pop()
        return MType.CLASS

    def _visit_NewObjectNode(self, node: NewObjectNode) -> str:
        sym = self.scope.resolve(node.class_name)
        if sym is None:
            self._error(UndefinedNameError(
                name=node.class_name,
                line=node.line,
                similar_names=self._similar_names(node.class_name),
            ))
        for arg in node.arguments:
            self._visit(arg)
        return MType.ANY

    def _visit_MethodCallNode(self, node: MethodCallNode) -> str:
        self._visit(node.object)
        for arg in node.arguments:
            self._visit(arg)
        return MType.ANY

    def _visit_PropertyAccessNode(self, node: PropertyAccessNode) -> str:
        self._visit(node.object)
        return MType.ANY

    def _visit_PropertyAssignmentNode(self, node: PropertyAssignmentNode) -> str:
        self._visit(node.object)
        self._visit(node.value)
        return MType.NONE

    def _visit_ThisNode(self, node: ThisNode) -> str:
        if not self._class_stack:
            self._error(SemanticError(
                message_en="'yeh' (this) used outside a class method",
                message_hi="'yeh' क्लास मेथड के बाहर उपयोग किया गया",
                line=node.line,
            ))
        return MType.ANY

    def _visit_SuperNode(self, node: SuperNode) -> str:
        if not self._class_stack:
            self._error(SemanticError(
                message_en="'upar' (super) used outside a class method",
                message_hi="'upar' क्लास मेथड के बाहर उपयोग किया गया",
                line=node.line,
            ))
        for arg in node.arguments:
            self._visit(arg)
        return MType.ANY

    # ------------------------------------------------------------------
    # Visitors – Error Handling
    # ------------------------------------------------------------------

    def _visit_TryNode(self, node: TryNode) -> str:
        self.scope = self.scope.enter_scope()
        for stmt in node.try_block:
            self._visit(stmt)
        self.scope = self.scope.exit_scope()

        if node.catch_block is not None:
            self.scope = self.scope.enter_scope()
            if node.exception_var:
                self.scope.define(Symbol(
                    name=node.exception_var,
                    kind=SymbolKind.VARIABLE,
                    inferred_type=MType.ANY,
                    line=node.line,
                ))
            for stmt in node.catch_block:
                self._visit(stmt)
            self.scope = self.scope.exit_scope()

        if node.finally_block is not None:
            self.scope = self.scope.enter_scope()
            for stmt in node.finally_block:
                self._visit(stmt)
            self.scope = self.scope.exit_scope()

        return MType.NONE

    def _visit_ThrowNode(self, node: ThrowNode) -> str:
        self._visit(node.exception)
        return MType.NONE

    # ------------------------------------------------------------------
    # Visitors – I/O
    # ------------------------------------------------------------------

    def _visit_PrintNode(self, node: PrintNode) -> str:
        for arg in node.arguments:
            self._visit(arg)
        return MType.NONE

    def _visit_InputNode(self, node: InputNode) -> str:
        # Bind the variable in the current scope.
        if self.scope.resolve_local(node.variable) is None:
            self.scope.define(Symbol(
                name=node.variable,
                kind=SymbolKind.VARIABLE,
                inferred_type=MType.STRING,   # input() always returns a string
                line=node.line,
            ))
        if node.prompt is not None:
            self._visit(node.prompt)
        return MType.NONE

    def _visit_ImportNode(self, node: ImportNode) -> str:
        # Can't fully resolve at static time; just note the name.
        return MType.NONE

    # ------------------------------------------------------------------
    # Visitors – Indexing
    # ------------------------------------------------------------------

    def _visit_IndexNode(self, node: IndexNode) -> str:
        self._visit(node.object)
        self._visit(node.index)
        return MType.ANY

    def _visit_IndexAssignmentNode(self, node: IndexAssignmentNode) -> str:
        self._visit(node.object)
        self._visit(node.index)
        self._visit(node.value)
        return MType.NONE

    # ------------------------------------------------------------------
    # Visitors – Program root
    # ------------------------------------------------------------------

    def _visit_ProgramNode(self, node: ProgramNode) -> str:
        for stmt in node.statements:
            self._visit(stmt)
        return MType.NONE

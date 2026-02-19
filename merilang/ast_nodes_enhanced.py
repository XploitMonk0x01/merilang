"""
Enhanced AST nodes for MeriLang Phase 2.

Adds support for:
- Parenthesized expressions
- Unary operators (-, nahi)
- Lambda functions
- Dictionary literals
- Enhanced type annotations

Author: MeriLang Team
Version: 2.0 - Phase 2
"""

from typing import Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class ASTNode:
    """Base class for all AST nodes.
    
    All AST nodes track their line number for error reporting.
    """
    def __init__(self, line: int = 1):
        self.line = line
    
    def __repr__(self) -> str:
        """Default repr for debugging."""
        return f"{self.__class__.__name__}(line={self.line})"


# ============================================================================
# Literals
# ============================================================================

@dataclass
class NumberNode(ASTNode):
    """Represents a number literal (integer or float).
    
    Examples:
        42 -> NumberNode(42)
        3.14 -> NumberNode(3.14)
        -10 -> NumberNode(-10)
    """
    value: Union[int, float]
    line: int = 1
    
    def __repr__(self) -> str:
        return f"NumberNode({self.value}, line={self.line})"


@dataclass
class StringNode(ASTNode):
    """Represents a string literal.
    
    Examples:
        "hello" -> StringNode("hello")
        'world' -> StringNode("world")
    """
    value: str
    line: int = 1
    
    def __repr__(self) -> str:
        return f"StringNode({repr(self.value)}, line={self.line})"


@dataclass
class BooleanNode(ASTNode):
    """Represents a boolean literal.
    
    Keywords:
        sach -> BooleanNode(True)
        jhoot -> BooleanNode(False)
    """
    value: bool
    line: int = 1
    
    def __repr__(self) -> str:
        return f"BooleanNode({self.value}, line={self.line})"


@dataclass
class ListNode(ASTNode):
    """Represents a list literal.
    
    Examples:
        [1, 2, 3] -> ListNode([NumberNode(1), NumberNode(2), NumberNode(3)])
        [] -> ListNode([])
    """
    elements: List[ASTNode] = field(default_factory=list)
    line: int = 1
    
    def __repr__(self) -> str:
        return f"ListNode({len(self.elements)} elements, line={self.line})"


@dataclass
class DictNode(ASTNode):
    """Represents a dictionary literal.
    
    Examples:
        {name: "Ahmed", age: 25} -> DictNode([("name", StringNode("Ahmed")), ...])
        {} -> DictNode([])
    """
    pairs: List[tuple[ASTNode, ASTNode]] = field(default_factory=list)
    line: int = 1
    
    def __repr__(self) -> str:
        return f"DictNode({len(self.pairs)} pairs, line={self.line})"


# ============================================================================
# Variables
# ============================================================================

@dataclass
class VariableNode(ASTNode):
    """Represents a variable reference.
    
    Examples:
        x -> VariableNode("x")
        count -> VariableNode("count")
    """
    name: str
    line: int = 1
    
    def __repr__(self) -> str:
        return f"VariableNode({self.name}, line={self.line})"


@dataclass
class AssignmentNode(ASTNode):
    """Represents variable assignment.
    
    Examples:
        maan x = 10 -> AssignmentNode("x", NumberNode(10))
        x = 20 -> AssignmentNode("x", NumberNode(20))
    """
    name: str
    value: ASTNode
    line: int = 1
    
    def __repr__(self) -> str:
        return f"AssignmentNode({self.name} = ..., line={self.line})"


# ============================================================================
# Operations
# ============================================================================

class BinaryOperator(Enum):
    """Binary operators with precedence levels."""
    # Arithmetic (precedence 10)
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    
    # Comparison (precedence 5)
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER = ">"
    LESS = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    
    # Logical (precedence 3)
    AND = "aur"  # and
    OR = "ya"    # or


class UnaryOperator(Enum):
    """Unary operators."""
    NEGATE = "-"      # Arithmetic negation: -x
    NOT = "nahi"      # Logical NOT: nahi x


@dataclass
class BinaryOpNode(ASTNode):
    """Represents binary operations.
    
    Examples:
        x + y -> BinaryOpNode("+", VariableNode("x"), VariableNode("y"))
        a == b -> BinaryOpNode("==", VariableNode("a"), VariableNode("b"))
    """
    operator: str
    left: ASTNode
    right: ASTNode
    line: int = 1
    
    def __repr__(self) -> str:
        return f"BinaryOpNode({self.operator}, line={self.line})"


@dataclass
class UnaryOpNode(ASTNode):
    """Represents unary operations.
    
    Examples:
        -x -> UnaryOpNode("-", VariableNode("x"))
        nahi flag -> UnaryOpNode("nahi", VariableNode("flag"))
    """
    operator: str
    operand: ASTNode
    line: int = 1
    
    def __repr__(self) -> str:
        return f"UnaryOpNode({self.operator}, line={self.line})"


@dataclass
class ParenthesizedNode(ASTNode):
    """Represents a parenthesized expression.
    
    Used to explicitly group expressions and control precedence.
    
    Examples:
        (x + y) * z -> ParenthesizedNode(BinaryOpNode("+", x, y))
    """
    expression: ASTNode
    line: int = 1
    
    def __repr__(self) -> str:
        return f"ParenthesizedNode(..., line={self.line})"


# ============================================================================
# Control Flow
# ============================================================================

@dataclass
class IfNode(ASTNode):
    """Represents if-else statement.
    
    Examples:
        agar x > 10 { ... } -> IfNode(BinaryOpNode(">", x, 10), [...], None)
        agar x > 10 { ... } warna { ... } -> IfNode(..., [...], [...])
    """
    condition: ASTNode
    then_branch: List[ASTNode]
    elif_branches: List[tuple[ASTNode, List[ASTNode]]] = field(default_factory=list)
    else_branch: Optional[List[ASTNode]] = None
    line: int = 1
    
    def __repr__(self) -> str:
        return f"IfNode(line={self.line})"


@dataclass
class WhileNode(ASTNode):
    """Represents while loop.
    
    Examples:
        jab_tak x < 10 { ... } -> WhileNode(BinaryOpNode("<", x, 10), [...])
    """
    condition: ASTNode
    body: List[ASTNode]
    line: int = 1
    
    def __repr__(self) -> str:
        return f"WhileNode(line={self.line})"


@dataclass
class ForNode(ASTNode):
    """Represents for loop over iterable.
    
    Examples:
        bar_bar x in [1, 2, 3] { ... } -> ForNode("x", ListNode([...]), [...])
    """
    variable: str
    iterable: ASTNode
    body: List[ASTNode]
    line: int = 1
    
    def __repr__(self) -> str:
        return f"ForNode({self.variable} in ..., line={self.line})"


@dataclass
class BreakNode(ASTNode):
    """Represents break statement (ruk)."""
    line: int = 1
    
    def __repr__(self) -> str:
        return f"BreakNode(line={self.line})"


@dataclass
class ContinueNode(ASTNode):
    """Represents continue statement (age_badho)."""
    line: int = 1
    
    def __repr__(self) -> str:
        return f"ContinueNode(line={self.line})"


# ============================================================================
# Functions
# ============================================================================

@dataclass
class FunctionDefNode(ASTNode):
    """Represents function definition.
    
    Examples:
        kaam add(a, b) { wapas a + b } -> FunctionDefNode("add", ["a", "b"], [...])
    """
    name: str
    parameters: List[str]
    body: List[ASTNode]
    line: int = 1
    
    def __repr__(self) -> str:
        return f"FunctionDefNode({self.name}, params={len(self.parameters)}, line={self.line})"


@dataclass
class FunctionCallNode(ASTNode):
    """Represents function call.
    
    Examples:
        add(5, 3) -> FunctionCallNode("add", [NumberNode(5), NumberNode(3)])
        likho("hello") -> FunctionCallNode("likho", [StringNode("hello")])
    """
    name: str
    arguments: List[ASTNode]
    line: int = 1
    
    def __repr__(self) -> str:
        return f"FunctionCallNode({self.name}, args={len(self.arguments)}, line={self.line})"


@dataclass
class ReturnNode(ASTNode):
    """Represents return statement.
    
    Examples:
        wapas 42 -> ReturnNode(NumberNode(42))
        wapas -> ReturnNode(None)
    """
    value: Optional[ASTNode] = None
    line: int = 1
    
    def __repr__(self) -> str:
        has_value = "with value" if self.value else "void"
        return f"ReturnNode({has_value}, line={self.line})"


@dataclass
class LambdaNode(ASTNode):
    """Represents lambda (anonymous) function.
    
    Examples:
        lambada x: x * 2 -> LambdaNode(["x"], BinaryOpNode("*", x, 2))
    """
    parameters: List[str]
    body: ASTNode  # Single expression
    line: int = 1
    
    def __repr__(self) -> str:
        return f"LambdaNode(params={len(self.parameters)}, line={self.line})"


# ============================================================================
# Object-Oriented Programming
# ============================================================================

@dataclass
class ClassDefNode(ASTNode):
    """Represents class definition.
    
    Examples:
        class Person { ... } -> ClassDefNode("Person", None, [...])
        class Student badhaao Person { ... } -> ClassDefNode("Student", "Person", [...])
    """
    name: str
    parent: Optional[str]
    methods: List[FunctionDefNode]
    line: int = 1
    
    def __repr__(self) -> str:
        parent_info = f" extends {self.parent}" if self.parent else ""
        return f"ClassDefNode({self.name}{parent_info}, line={self.line})"


@dataclass
class NewObjectNode(ASTNode):
    """Represents object instantiation.
    
    Examples:
        naya Person("Ahmed", 25) -> NewObjectNode("Person", [StringNode("Ahmed"), NumberNode(25)])
    """
    class_name: str
    arguments: List[ASTNode]
    line: int = 1
    
    def __repr__(self) -> str:
        return f"NewObjectNode({self.class_name}, line={self.line})"


@dataclass
class MethodCallNode(ASTNode):
    """Represents method call on object.
    
    Examples:
        person.greet() -> MethodCallNode(VariableNode("person"), "greet", [])
        obj.method(arg) -> MethodCallNode(..., "method", [arg])
    """
    object: ASTNode
    method_name: str
    arguments: List[ASTNode]
    line: int = 1
    
    def __repr__(self) -> str:
        return f"MethodCallNode(..., {self.method_name}, line={self.line})"


@dataclass
class PropertyAccessNode(ASTNode):
    """Represents property access on object.
    
    Examples:
        person.name -> PropertyAccessNode(VariableNode("person"), "name")
    """
    object: ASTNode
    property_name: str
    line: int = 1
    
    def __repr__(self) -> str:
        return f"PropertyAccessNode(..., {self.property_name}, line={self.line})"


@dataclass
class PropertyAssignmentNode(ASTNode):
    """Represents property assignment on object.
    
    Examples:
        yeh.name = "Ahmed" -> PropertyAssignmentNode(ThisNode(), "name", StringNode("Ahmed"))
    """
    object: ASTNode
    property_name: str
    value: ASTNode
    line: int = 1
    
    def __repr__(self) -> str:
        return f"PropertyAssignmentNode(..., {self.property_name} = ..., line={self.line})"


@dataclass
class ThisNode(ASTNode):
    """Represents 'yeh' (this/self) keyword."""
    line: int = 1
    
    def __repr__(self) -> str:
        return f"ThisNode(line={self.line})"


@dataclass
class SuperNode(ASTNode):
    """Represents 'upar' (super) keyword for parent class method calls.
    
    Examples:
        upar.greet() -> SuperNode("greet", [])
    """
    method_name: str
    arguments: List[ASTNode]
    line: int = 1
    
    def __repr__(self) -> str:
        return f"SuperNode({self.method_name}, line={self.line})"


# ============================================================================
# Error Handling
# ============================================================================

@dataclass
class TryNode(ASTNode):
    """Represents try-catch-finally block.
    
    Examples:
        koshish { ... } pakdo e { ... } -> TryNode([...], "e", [...], None)
        koshish { ... } pakdo e { ... } akhir { ... } -> TryNode([...], "e", [...], [...])
    """
    try_block: List[ASTNode]
    exception_var: Optional[str]
    catch_block: Optional[List[ASTNode]]
    finally_block: Optional[List[ASTNode]]
    line: int = 1
    
    def __repr__(self) -> str:
        return f"TryNode(line={self.line})"


@dataclass
class ThrowNode(ASTNode):
    """Represents throw statement.
    
    Examples:
        fenko "Error occurred" -> ThrowNode(StringNode("Error occurred"))
    """
    exception: ASTNode
    line: int = 1
    
    def __repr__(self) -> str:
        return f"ThrowNode(line={self.line})"


# ============================================================================
# I/O and Special
# ============================================================================

@dataclass
class PrintNode(ASTNode):
    """Represents print statement.
    
    Examples:
        likho("hello") -> PrintNode([StringNode("hello")])
        likho(x, y, z) -> PrintNode([...])
    """
    arguments: List[ASTNode]
    line: int = 1
    
    def __repr__(self) -> str:
        return f"PrintNode({len(self.arguments)} args, line={self.line})"


@dataclass
class InputNode(ASTNode):
    """Represents input statement.
    
    Examples:
        padho name -> InputNode("name")
    """
    variable: str
    prompt: Optional[ASTNode] = None
    line: int = 1
    
    def __repr__(self) -> str:
        return f"InputNode({self.variable}, line={self.line})"


@dataclass
class ImportNode(ASTNode):
    """Represents module import.
    
    Examples:
        lao "mylib" -> ImportNode("mylib")
    """
    module_name: str
    line: int = 1
    
    def __repr__(self) -> str:
        return f"ImportNode({self.module_name}, line={self.line})"


@dataclass
class ProgramNode(ASTNode):
    """Represents the entire program (root node).
    
    Examples:
        shuru ... khatam -> ProgramNode([...])
    """
    statements: List[ASTNode]
    line: int = 1
    
    def __repr__(self) -> str:
        return f"ProgramNode({len(self.statements)} statements, line={self.line})"


# ============================================================================
# Index/Subscription
# ============================================================================

@dataclass
class IndexNode(ASTNode):
    """Represents array/dict indexing.
    
    Examples:
        arr[0] -> IndexNode(VariableNode("arr"), NumberNode(0))
        dict["key"] -> IndexNode(VariableNode("dict"), StringNode("key"))
    """
    object: ASTNode
    index: ASTNode
    line: int = 1
    
    def __repr__(self) -> str:
        return f"IndexNode(...[...], line={self.line})"


@dataclass
class IndexAssignmentNode(ASTNode):
    """Represents index assignment.
    
    Examples:
        arr[0] = 42 -> IndexAssignmentNode(VariableNode("arr"), NumberNode(0), NumberNode(42))
    """
    object: ASTNode
    index: ASTNode
    value: ASTNode
    line: int = 1
    
    def __repr__(self) -> str:
        return f"IndexAssignmentNode(...[...] = ..., line={self.line})"

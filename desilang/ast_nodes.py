"""
Abstract Syntax Tree (AST) node classes for DesiLang.
Using classes instead of dictionaries for type safety and clarity.
"""

from typing import Any, List, Optional
from dataclasses import dataclass


class ASTNode:
    """Base class for all AST nodes."""
    def __init__(self, line: int = 1):
        self.line = line


# Literals
@dataclass
class NumberNode(ASTNode):
    """Represents a number literal (int or float)."""
    value: int | float
    line: int = 1


@dataclass
class StringNode(ASTNode):
    """Represents a string literal."""
    value: str
    line: int = 1


@dataclass
class BooleanNode(ASTNode):
    """Represents a boolean literal (sahi/galat)."""
    value: bool
    line: int = 1


@dataclass
class ListNode(ASTNode):
    """Represents a list literal."""
    elements: List[ASTNode]
    line: int = 1


# Variables
@dataclass
class VariableNode(ASTNode):
    """Represents a variable reference."""
    name: str
    line: int = 1


@dataclass
class AssignmentNode(ASTNode):
    """Represents variable assignment: x = value"""
    name: str
    value: ASTNode
    line: int = 1


# Binary Operations
@dataclass
class BinaryOpNode(ASTNode):
    """Represents binary operations: left op right"""
    operator: str  # +, -, *, /, %, >, <, >=, <=, ==, !=
    left: ASTNode
    right: ASTNode
    line: int = 1


@dataclass
class UnaryOpNode(ASTNode):
    """Represents unary operations: op value"""
    operator: str  # - (negation), ! (not)
    operand: ASTNode
    line: int = 1


# Control Flow
@dataclass
class IfNode(ASTNode):
    """Represents if-else statement."""
    condition: ASTNode
    then_branch: List[ASTNode]
    else_branch: Optional[List[ASTNode]] = None
    line: int = 1


@dataclass
class WhileNode(ASTNode):
    """Represents while loop."""
    condition: ASTNode
    body: List[ASTNode]
    line: int = 1


@dataclass
class ForNode(ASTNode):
    """Represents for loop: chalao var se start tak end"""
    variable: str
    start: ASTNode
    end: ASTNode
    body: List[ASTNode]
    line: int = 1


# Functions
@dataclass
class FunctionDefNode(ASTNode):
    """Represents function definition."""
    name: str
    parameters: List[str]
    body: List[ASTNode]
    line: int = 1


@dataclass
class FunctionCallNode(ASTNode):
    """Represents function call."""
    name: str
    arguments: List[ASTNode]
    line: int = 1


@dataclass
class ReturnNode(ASTNode):
    """Represents return statement."""
    value: Optional[ASTNode] = None
    line: int = 1


# I/O Operations
@dataclass
class PrintNode(ASTNode):
    """Represents print statement: dikhao"""
    expression: ASTNode
    line: int = 1


@dataclass
class InputNode(ASTNode):
    """Represents input statement: padho"""
    variable: str
    line: int = 1


# List Operations
@dataclass
class IndexAccessNode(ASTNode):
    """Represents list index access: list[index]"""
    list_expr: ASTNode
    index: ASTNode
    line: int = 1


@dataclass
class IndexAssignmentNode(ASTNode):
    """Represents list index assignment: list[index] = value"""
    list_name: str
    index: ASTNode
    value: ASTNode
    line: int = 1


# Program
@dataclass
class ProgramNode(ASTNode):
    """Represents the entire program."""
    statements: List[ASTNode]
    line: int = 1


# Import
@dataclass
class ImportNode(ASTNode):
    """Represents import statement: lao"""
    filename: str
    line: int = 1


# OOP - Classes and Objects
@dataclass
class ClassDefNode(ASTNode):
    """Represents a class definition: class ClassName"""
    name: str
    parent: Optional[str]  # For inheritance
    methods: List['FunctionDefNode']
    properties: List[str]  # Property names initialized in constructor
    line: int = 1


@dataclass
class NewObjectNode(ASTNode):
    """Represents object instantiation: naya ClassName(args)"""
    class_name: str
    arguments: List[ASTNode]
    line: int = 1


@dataclass
class MethodCallNode(ASTNode):
    """Represents method call: object.method(args)"""
    object_expr: ASTNode  # Can be variable or another expression
    method_name: str
    arguments: List[ASTNode]
    line: int = 1


@dataclass
class PropertyAccessNode(ASTNode):
    """Represents property access: object.property"""
    object_expr: ASTNode
    property_name: str
    line: int = 1


@dataclass
class PropertyAssignmentNode(ASTNode):
    """Represents property assignment: object.property = value"""
    object_expr: ASTNode
    property_name: str
    value: ASTNode
    line: int = 1


@dataclass
class ThisNode(ASTNode):
    """Represents 'yeh' (this) keyword"""
    line: int = 1


@dataclass
class SuperNode(ASTNode):
    """Represents 'upar' (super) for parent method calls"""
    method_name: str
    arguments: List[ASTNode]
    line: int = 1


# Error Handling
@dataclass
class TryNode(ASTNode):
    """Represents try-catch-finally block"""
    try_block: List[ASTNode]
    catch_var: Optional[str]  # Variable name to bind exception
    catch_block: List[ASTNode]
    finally_block: Optional[List[ASTNode]]
    line: int = 1


@dataclass
class ThrowNode(ASTNode):
    """Represents throw statement: fenko"""
    expression: ASTNode  # Error message or object
    line: int = 1

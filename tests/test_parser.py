"""
Unit tests for DesiLang parser.
"""

import pytest
from merilang.lexer import tokenize
from merilang.parser import Parser
from merilang.ast_nodes import *
from merilang.errors import ParserError


def parse_code(code: str) -> ProgramNode:
    """Helper to tokenize and parse code."""
    tokens = tokenize(code)
    parser = Parser(tokens)
    return parser.parse()


def test_parse_assignment():
    """Test parsing variable assignment."""
    code = "shuru x = 42 khatam"
    ast = parse_code(code)
    
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], AssignmentNode)
    assert ast.statements[0].name == 'x'
    assert isinstance(ast.statements[0].value, NumberNode)
    assert ast.statements[0].value.value == 42


def test_parse_print():
    """Test parsing print statement."""
    code = 'shuru dikhao "Hello" khatam'
    ast = parse_code(code)
    
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], PrintNode)
    assert isinstance(ast.statements[0].expression, StringNode)


def test_parse_arithmetic():
    """Test parsing arithmetic expressions."""
    code = "shuru x = 1 + 2 * 3 khatam"
    ast = parse_code(code)
    
    assignment = ast.statements[0]
    assert isinstance(assignment.value, BinaryOpNode)
    
    # Should be: 1 + (2 * 3) due to precedence
    assert assignment.value.operator == '+'
    assert isinstance(assignment.value.right, BinaryOpNode)
    assert assignment.value.right.operator == '*'


def test_parse_parentheses():
    """Test parsing parenthesized expressions."""
    code = "shuru x = (1 + 2) * 3 khatam"
    ast = parse_code(code)
    
    assignment = ast.statements[0]
    # Should be: (1 + 2) * 3
    assert assignment.value.operator == '*'
    assert isinstance(assignment.value.left, BinaryOpNode)
    assert assignment.value.left.operator == '+'


def test_parse_comparison():
    """Test parsing comparison operators."""
    code = "shuru x = 5 > 3 khatam"
    ast = parse_code(code)
    
    assignment = ast.statements[0]
    assert isinstance(assignment.value, BinaryOpNode)
    assert assignment.value.operator == '>'


def test_parse_if_statement():
    """Test parsing if statement."""
    code = """
shuru
agar x > 5 {
    dikhao "Big"
} bas
khatam
    """.strip()
    
    ast = parse_code(code)
    
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], IfNode)
    assert len(ast.statements[0].then_branch) == 1


def test_parse_if_else():
    """Test parsing if-else statement."""
    code = """
shuru
agar x > 5 {
    dikhao "Big"
} warna {
    dikhao "Small"
} bas
khatam
    """.strip()
    
    ast = parse_code(code)
    
    if_node = ast.statements[0]
    assert isinstance(if_node, IfNode)
    assert len(if_node.then_branch) == 1
    assert if_node.else_branch is not None
    assert len(if_node.else_branch) == 1


def test_parse_while_loop():
    """Test parsing while loop."""
    code = """
shuru
jabtak x < 10 {
    dikhao x
} band
khatam
    """.strip()
    
    ast = parse_code(code)
    
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], WhileNode)
    assert len(ast.statements[0].body) == 1


def test_parse_for_loop():
    """Test parsing for loop."""
    code = """
shuru
chalao i se 0 tak 10 {
    dikhao i
}
khatam
    """.strip()
    
    ast = parse_code(code)
    
    assert len(ast.statements) == 1
    for_node = ast.statements[0]
    assert isinstance(for_node, ForNode)
    assert for_node.variable == 'i'
    assert isinstance(for_node.start, NumberNode)
    assert isinstance(for_node.end, NumberNode)


def test_parse_function_def():
    """Test parsing function definition."""
    code = """
shuru
vidhi add(a, b) {
    vapas a + b
} samapt
khatam
    """.strip()
    
    ast = parse_code(code)
    
    assert len(ast.statements) == 1
    func_def = ast.statements[0]
    assert isinstance(func_def, FunctionDefNode)
    assert func_def.name == 'add'
    assert func_def.parameters == ['a', 'b']
    assert len(func_def.body) == 1


def test_parse_function_call():
    """Test parsing function call."""
    code = """
shuru
bulayo print_hello()
khatam
    """.strip()
    
    ast = parse_code(code)
    
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], FunctionCallNode)
    assert ast.statements[0].name == 'print_hello'
    assert len(ast.statements[0].arguments) == 0


def test_parse_function_call_with_args():
    """Test parsing function call with arguments."""
    code = """
shuru
bulayo add(1, 2)
khatam
    """.strip()
    
    ast = parse_code(code)
    
    call_node = ast.statements[0]
    assert isinstance(call_node, FunctionCallNode)
    assert call_node.name == 'add'
    assert len(call_node.arguments) == 2


def test_parse_list_literal():
    """Test parsing list literal."""
    code = "shuru mylist = [1, 2, 3] khatam"
    ast = parse_code(code)
    
    assignment = ast.statements[0]
    assert isinstance(assignment.value, ListNode)
    assert len(assignment.value.elements) == 3


def test_parse_list_access():
    """Test parsing list index access."""
    code = "shuru x = mylist[0] khatam"
    ast = parse_code(code)
    
    assignment = ast.statements[0]
    assert isinstance(assignment.value, IndexAccessNode)


def test_parse_list_assignment():
    """Test parsing list index assignment."""
    code = "shuru mylist[0] = 42 khatam"
    ast = parse_code(code)
    
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], IndexAssignmentNode)
    assert ast.statements[0].list_name == 'mylist'


def test_parse_unary_minus():
    """Test parsing unary negation."""
    code = "shuru x = -5 khatam"
    ast = parse_code(code)
    
    assignment = ast.statements[0]
    assert isinstance(assignment.value, UnaryOpNode)
    assert assignment.value.operator == '-'


def test_parse_return_statement():
    """Test parsing return statement."""
    code = """
shuru
vidhi get_five() {
    vapas 5
} samapt
khatam
    """.strip()
    
    ast = parse_code(code)
    
    func_def = ast.statements[0]
    assert len(func_def.body) == 1
    assert isinstance(func_def.body[0], ReturnNode)
    assert isinstance(func_def.body[0].value, NumberNode)


def test_parse_import():
    """Test parsing import statement."""
    code = 'shuru lao "mylib.desilang" khatam'
    ast = parse_code(code)
    
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], ImportNode)
    assert ast.statements[0].filename == "mylib.desilang"


def test_parse_input():
    """Test parsing input statement."""
    code = "shuru padho x khatam"
    ast = parse_code(code)
    
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], InputNode)
    assert ast.statements[0].variable == 'x'


def test_parse_error_missing_end():
    """Test error when khatam is missing."""
    code = "shuru x = 42"
    
    with pytest.raises(ParserError):
        parse_code(code)


def test_parse_error_invalid_assignment():
    """Test error on invalid assignment."""
    code = "shuru x = khatam"
    
    with pytest.raises(ParserError):
        parse_code(code)


def test_parse_empty_program():
    """Test parsing empty program."""
    code = "shuru khatam"
    ast = parse_code(code)
    
    assert len(ast.statements) == 0


def test_parse_nested_if():
    """Test parsing nested if statements."""
    code = """
shuru
agar x > 0 {
    agar x > 10 {
        dikhao "Very big"
    } bas
} bas
khatam
    """.strip()
    
    ast = parse_code(code)
    
    outer_if = ast.statements[0]
    assert isinstance(outer_if, IfNode)
    assert len(outer_if.then_branch) == 1
    
    inner_if = outer_if.then_branch[0]
    assert isinstance(inner_if, IfNode)

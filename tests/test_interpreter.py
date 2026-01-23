"""
Unit tests for DesiLang interpreter.
"""

import pytest
from io import StringIO
import sys
from desilang.lexer import tokenize
from desilang.parser import Parser
from desilang.interpreter import Interpreter
from desilang.errors import DivisionByZeroError, NameError as DesiNameError, TypeError as DesiTypeError


def run_code(code: str, capture_output=True):
    """Helper to tokenize, parse, and interpret code."""
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    
    if capture_output:
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            interpreter.execute(ast)
            output = captured_output.getvalue()
            return output, interpreter
        finally:
            sys.stdout = old_stdout
    else:
        interpreter.execute(ast)
        return None, interpreter


def test_interpret_assignment():
    """Test variable assignment."""
    code = "shuru x = 42 khatam"
    _, interp = run_code(code)
    
    assert interp.global_env.get('x') == 42


def test_interpret_print_number():
    """Test printing a number."""
    code = "shuru dikhao 42 khatam"
    output, _ = run_code(code)
    
    assert output.strip() == "42"


def test_interpret_print_string():
    """Test printing a string."""
    code = 'shuru dikhao "Hello World" khatam'
    output, _ = run_code(code)
    
    assert output.strip() == "Hello World"


def test_interpret_print_variable():
    """Test printing a variable."""
    code = """
shuru
x = 42
dikhao x
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "42"


def test_interpret_arithmetic():
    """Test arithmetic operations."""
    code = """
shuru
a = 5 + 3
b = 10 - 2
c = 4 * 3
d = 15 / 3
e = 17 % 5
dikhao a
dikhao b
dikhao c
dikhao d
dikhao e
khatam
    """.strip()
    
    output, _ = run_code(code)
    lines = output.strip().split('\n')
    
    assert lines[0] == "8"
    assert lines[1] == "8"
    assert lines[2] == "12"
    assert lines[3] == "5"  # Integer division
    assert lines[4] == "2"


def test_interpret_comparison():
    """Test comparison operators."""
    code = """
shuru
a = 5 > 3
b = 5 < 3
c = 5 >= 5
d = 5 <= 4
e = 5 == 5
f = 5 != 3
dikhao a
dikhao b
dikhao c
dikhao d
dikhao e
dikhao f
khatam
    """.strip()
    
    output, _ = run_code(code)
    lines = output.strip().split('\n')
    
    assert lines[0] == "sahi"
    assert lines[1] == "galat"
    assert lines[2] == "sahi"
    assert lines[3] == "galat"
    assert lines[4] == "sahi"
    assert lines[5] == "sahi"


def test_interpret_if_statement():
    """Test if statement."""
    code = """
shuru
x = 10
agar x > 5 {
    dikhao "Big"
} bas
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "Big"


def test_interpret_if_else():
    """Test if-else statement."""
    code = """
shuru
x = 3
agar x > 5 {
    dikhao "Big"
} warna {
    dikhao "Small"
} bas
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "Small"


def test_interpret_while_loop():
    """Test while loop."""
    code = """
shuru
x = 0
jabtak x < 3 {
    dikhao x
    x = x + 1
} band
khatam
    """.strip()
    
    output, _ = run_code(code)
    lines = output.strip().split('\n')
    
    assert lines == ["0", "1", "2"]


def test_interpret_for_loop():
    """Test for loop."""
    code = """
shuru
chalao i se 0 tak 3 {
    dikhao i
}
khatam
    """.strip()
    
    output, _ = run_code(code)
    lines = output.strip().split('\n')
    
    assert lines == ["0", "1", "2"]


def test_interpret_function():
    """Test function definition and call."""
    code = """
shuru
vidhi greet(name) {
    dikhao name
} samapt

bulayo greet("Alice")
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "Alice"


def test_interpret_function_return():
    """Test function with return value."""
    code = """
shuru
vidhi add(a, b) {
    vapas a + b
} samapt

result = add(5, 3)
dikhao result
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "8"


def test_interpret_list():
    """Test list creation and access."""
    code = """
shuru
mylist = [1, 2, 3]
dikhao mylist[0]
dikhao mylist[1]
dikhao mylist[2]
khatam
    """.strip()
    
    output, _ = run_code(code)
    lines = output.strip().split('\n')
    
    assert lines == ["1", "2", "3"]


def test_interpret_list_assignment():
    """Test list element assignment."""
    code = """
shuru
mylist = [1, 2, 3]
mylist[1] = 99
dikhao mylist[1]
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "99"


def test_interpret_builtin_length():
    """Test built-in length function."""
    code = """
shuru
mylist = [1, 2, 3, 4, 5]
n = length(mylist)
dikhao n
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "5"


def test_interpret_builtin_append():
    """Test built-in append function."""
    code = """
shuru
mylist = [1, 2]
append(mylist, 3)
dikhao mylist
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "[1, 2, 3]"


def test_interpret_string_concatenation():
    """Test string concatenation."""
    code = """
shuru
s = "Hello" + " " + "World"
dikhao s
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "Hello World"


def test_interpret_boolean():
    """Test boolean values."""
    code = """
shuru
a = sahi
b = galat
dikhao a
dikhao b
khatam
    """.strip()
    
    output, _ = run_code(code)
    lines = output.strip().split('\n')
    
    assert lines[0] == "sahi"
    assert lines[1] == "galat"


def test_interpret_unary_minus():
    """Test unary negation."""
    code = """
shuru
x = -5
dikhao x
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "-5"


def test_interpret_nested_function():
    """Test nested function scopes."""
    code = """
shuru
x = 10

vidhi outer() {
    x = 20
    vidhi inner() {
        vapas x
    } samapt
    vapas inner()
} samapt

result = outer()
dikhao result
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "20"


def test_interpret_recursion():
    """Test recursive function."""
    code = """
shuru
vidhi factorial(n) {
    agar n <= 1 {
        vapas 1
    } bas
    vapas n * factorial(n - 1)
} samapt

result = factorial(5)
dikhao result
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "120"


def test_error_division_by_zero():
    """Test division by zero error."""
    code = "shuru x = 10 / 0 khatam"
    
    with pytest.raises(DivisionByZeroError):
        run_code(code)


def test_error_undefined_variable():
    """Test undefined variable error."""
    code = "shuru dikhao undefined_var khatam"
    
    with pytest.raises(DesiNameError):
        run_code(code)


def test_error_type_mismatch():
    """Test type error in operation."""
    code = 'shuru x = "hello" - 5 khatam'
    
    with pytest.raises(DesiTypeError):
        run_code(code)


def test_float_division():
    """Test float division."""
    code = """
shuru
x = 7.0 / 2.0
dikhao x
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "3.5"


def test_operator_precedence():
    """Test operator precedence."""
    code = """
shuru
x = 2 + 3 * 4
dikhao x
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "14"


def test_parentheses_precedence():
    """Test parentheses override precedence."""
    code = """
shuru
x = (2 + 3) * 4
dikhao x
khatam
    """.strip()
    
    output, _ = run_code(code)
    assert output.strip() == "20"

"""
Integration tests for MeriLang - test complete programs.
"""

import pytest
from io import StringIO
import sys
from merilang.lexer import tokenize
from merilang.parser import Parser
from merilang.interpreter import Interpreter


def run_program(code: str):
    """Run a complete MeriLang program and capture output."""
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        interpreter.execute(ast)
        output = captured_output.getvalue()
        return output
    finally:
        sys.stdout = old_stdout


def test_hello_world():
    """Test classic Hello World program."""
    code = """
shuru
dikhao "Hello World"
khatam
    """.strip()
    
    output = run_program(code)
    assert output.strip() == "Hello World"


def test_factorial():
    """Test factorial calculation."""
    code = """
shuru
vidhi factorial(n) {
    agar n <= 1 {
        vapas 1
    } bas
    vapas n * factorial(n - 1)
} samapt

dikhao factorial(5)
dikhao factorial(10)
khatam
    """.strip()
    
    output = run_program(code)
    lines = output.strip().split('\n')
    
    assert lines[0] == "120"
    assert lines[1] == "3628800"


def test_fizzbuzz():
    """Test FizzBuzz program."""
    code = """
shuru
chalao i se 1 tak 16 {
    agar i % 15 == 0 {
        dikhao "FizzBuzz"
    } warna {
        agar i % 3 == 0 {
            dikhao "Fizz"
        } warna {
            agar i % 5 == 0 {
                dikhao "Buzz"
            } warna {
                dikhao i
            } bas
        } bas
    } bas
}
khatam
    """.strip()
    
    output = run_program(code)
    lines = output.strip().split('\n')
    
    expected = ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", 
                "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]
    
    assert lines == expected


def test_fibonacci():
    """Test Fibonacci sequence."""
    code = """
shuru
vidhi fib(n) {
    agar n <= 1 {
        vapas n
    } bas
    vapas fib(n - 1) + fib(n - 2)
} samapt

chalao i se 0 tak 10 {
    dikhao fib(i)
}
khatam
    """.strip()
    
    output = run_program(code)
    lines = [int(line) for line in output.strip().split('\n')]
    
    expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    assert lines == expected


def test_list_operations():
    """Test various list operations."""
    code = """
shuru
numbers = [1, 2, 3, 4, 5]

// Add elements
append(numbers, 6)
append(numbers, 7)

// Print all elements
chalao i se 0 tak length(numbers) {
    dikhao numbers[i]
}

// Modify element
numbers[3] = 99
dikhao numbers[3]

// Get sum
total = sum(numbers)
dikhao total
khatam
    """.strip()
    
    output = run_program(code)
    lines = output.strip().split('\n')
    
    assert lines[0:7] == ["1", "2", "3", "4", "5", "6", "7"]
    assert lines[7] == "99"
    assert lines[8] == "122"  # 1+2+3+99+5+6+7


def test_string_manipulation():
    """Test string operations."""
    code = """
shuru
s1 = "hello"
s2 = "world"

// Concatenation
greeting = s1 + " " + s2
dikhao greeting

// Upper/lower
dikhao upper(s1)
dikhao lower("HELLO")

// Length
dikhao length(greeting)
khatam
    """.strip()
    
    output = run_program(code)
    lines = output.strip().split('\n')
    
    assert lines[0] == "hello world"
    assert lines[1] == "HELLO"
    assert lines[2] == "hello"
    assert lines[3] == "11"


def test_nested_loops():
    """Test nested loops."""
    code = """
shuru
chalao i se 1 tak 4 {
    chalao j se 1 tak 4 {
        product = i * j
        dikhao product
    }
}
khatam
    """.strip()
    
    output = run_program(code)
    lines = [int(line) for line in output.strip().split('\n')]
    
    expected = [1, 2, 3, 2, 4, 6, 3, 6, 9]
    assert lines == expected


def test_complex_conditionals():
    """Test complex conditional logic."""
    code = """
shuru
vidhi classify(x) {
    agar x > 100 {
        vapas "large"
    } warna {
        agar x > 50 {
            vapas "medium"
        } warna {
            agar x > 0 {
                vapas "small"
            } warna {
                vapas "non-positive"
            } bas
        } bas
    } bas
} samapt

dikhao classify(150)
dikhao classify(75)
dikhao classify(25)
dikhao classify(-5)
khatam
    """.strip()
    
    output = run_program(code)
    lines = output.strip().split('\n')
    
    assert lines == ["large", "medium", "small", "non-positive"]


def test_higher_order_function():
    """Test function returning function."""
    code = """
shuru
vidhi make_adder(x) {
    vidhi add(y) {
        vapas x + y
    } samapt
    vapas add
} samapt

add5 = make_adder(5)
result = add5(10)
dikhao result
khatam
    """.strip()
    
    output = run_program(code)
    assert output.strip() == "15"


def test_sorting():
    """Test list sorting."""
    code = """
shuru
numbers = [5, 2, 8, 1, 9, 3]
sorted_nums = sort(numbers)

chalao i se 0 tak length(sorted_nums) {
    dikhao sorted_nums[i]
}
khatam
    """.strip()
    
    output = run_program(code)
    lines = [int(line) for line in output.strip().split('\n')]
    
    assert lines == [1, 2, 3, 5, 8, 9]


def test_prime_numbers():
    """Test prime number finder."""
    code = """
shuru
vidhi is_prime(n) {
    agar n < 2 {
        vapas galat
    } bas
    
    chalao i se 2 tak n {
        agar n % i == 0 {
            vapas galat
        } bas
    }
    
    vapas sahi
} samapt

// Find primes up to 20
chalao num se 2 tak 21 {
    agar is_prime(num) {
        dikhao num
    } bas
}
khatam
    """.strip()
    
    output = run_program(code)
    lines = [int(line) for line in output.strip().split('\n')]
    
    expected_primes = [2, 3, 5, 7, 11, 13, 17, 19]
    assert lines == expected_primes


def test_variable_scoping():
    """Test variable scoping rules."""
    code = """
shuru
x = 10

vidhi test() {
    x = 20
    dikhao x
} samapt

dikhao x
bulayo test()
dikhao x
khatam
    """.strip()
    
    output = run_program(code)
    lines = output.strip().split('\n')
    
    assert lines == ["10", "20", "20"]


def test_mixed_types():
    """Test operations with mixed types."""
    code = """
shuru
// Number to string conversion
x = str(42)
dikhao x

// String to number conversion
y = int("123")
dikhao y

// Type checking
dikhao type(42)
dikhao type("hello")
dikhao type(sahi)
dikhao type([1, 2, 3])
khatam
    """.strip()
    
    output = run_program(code)
    lines = output.strip().split('\n')
    
    assert lines[0] == "42"
    assert lines[1] == "123"
    assert lines[2] == "integer"
    assert lines[3] == "string"
    assert lines[4] == "boolean"
    assert lines[5] == "list"

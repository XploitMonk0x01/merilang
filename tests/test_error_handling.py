"""
Unit tests for error handling features in DesiLang.
Tests try-catch-finally blocks and throw statements.
"""

import pytest
from desilang.lexer import tokenize
from desilang.parser import Parser
from desilang.interpreter import Interpreter, DesiException
from desilang.errors import DivisionByZeroError


def test_basic_try_catch():
    """Test basic try-catch block."""
    code = """
    shuru
    koshish {
        fenko "Error happened"
    }
    pakdo err {
        dikhao "Caught error"
    }
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    # Should execute without raising exception
    interpreter.execute(ast)


def test_throw_and_catch():
    """Test throwing and catching custom exception."""
    code = """
    shuru
    result = "not set"
    
    koshish {
        fenko "Custom error message"
        result = "should not reach"
    }
    pakdo e {
        result = "caught"
    }
    
    dikhao result
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    result = interpreter.global_env.get('result')
    assert result == "caught"


def test_finally_block():
    """Test that finally block always executes."""
    code = """
    shuru
    cleanup = "not done"
    
    koshish {
        dikhao "In try"
    }
    pakdo {
        dikhao "In catch"
    }
    akhir {
        cleanup = "done"
    }
    
    dikhao cleanup
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    cleanup = interpreter.global_env.get('cleanup')
    assert cleanup == "done"


def test_finally_after_exception():
    """Test finally block executes even after exception."""
    code = """
    shuru
    status = "initial"
    
    koshish {
        fenko "Error"
        status = "try"
    }
    pakdo {
        status = "catch"
    }
    akhir {
        status = "finally"
    }
    
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    status = interpreter.global_env.get('status')
    assert status == "finally"


def test_exception_variable_binding():
    """Test that exception is bound to variable in catch."""
    code = """
    shuru
    msg = ""
    
    koshish {
        fenko "Error message"
    }
    pakdo error {
        msg = error
    }
    
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    msg = interpreter.global_env.get('msg')
    assert "Error message" in str(msg)


def test_nested_try_catch():
    """Test nested try-catch blocks."""
    code = """
    shuru
    outer = "no"
    inner = "no"
    
    koshish {
        koshish {
            fenko "Inner error"
        }
        pakdo {
            inner = "yes"
        }
        
        fenko "Outer error"
    }
    pakdo {
        outer = "yes"
    }
    
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    outer = interpreter.global_env.get('outer')
    inner = interpreter.global_env.get('inner')
    
    assert outer == "yes"
    assert inner == "yes"


def test_try_without_exception():
    """Test try block that completes without exception."""
    code = """
    shuru
    result = "initial"
    caught = galat
    
    koshish {
        result = "success"
    }
    pakdo {
        caught = sahi
    }
    
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    result = interpreter.global_env.get('result')
    caught = interpreter.global_env.get('caught')
    
    assert result == "success"
    assert caught == False


def test_catch_division_by_zero():
    """Test catching built-in division by zero error."""
    code = """
    shuru
    result = "ok"
    
    koshish {
        x = 10 / 0
    }
    pakdo err {
        result = "caught division error"
    }
    
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    result = interpreter.global_env.get('result')
    assert result == "caught division error"


def test_multiple_throws():
    """Test multiple throw statements."""
    code = """
    shuru
    count = 0
    
    koshish {
        count = count + 1
        fenko "First"
    }
    pakdo {
        count = count + 1
    }
    
    koshish {
        count = count + 1
        fenko "Second"
    }
    pakdo {
        count = count + 1
    }
    
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    count = interpreter.global_env.get('count')
    assert count == 4


def test_uncaught_exception():
    """Test that uncaught exception propagates."""
    code = """
    shuru
    fenko "Uncaught error"
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    
    with pytest.raises(DesiException):
        interpreter.execute(ast)


def test_finally_without_catch():
    """Test try-finally without catch block."""
    code = """
    shuru
    cleanup = galat
    
    koshish {
        dikhao "In try"
    }
    pakdo {
        dikhao "Won't reach"
    }
    akhir {
        cleanup = sahi
    }
    
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    cleanup = interpreter.global_env.get('cleanup')
    assert cleanup == True

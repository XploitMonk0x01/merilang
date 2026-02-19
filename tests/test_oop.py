"""
Unit tests for OOP features in MeriLang.
Tests classes, objects, inheritance, methods, and properties.
"""

import pytest
from merilang.lexer import tokenize
from merilang.parser import Parser
from merilang.interpreter import Interpreter


def test_simple_class():
    """Test basic class definition and instantiation."""
    code = """
    shuru
    class Vyakti {
        vidhi __init__(naam) {
            yeh.naam = naam
        }
        samapt
        
        vidhi namaskar() {
            dikhao yeh.naam
        }
        samapt
    }
    
    obj = naya Vyakti("Rajesh")
    obj.namaskar()
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    # Should execute without error
    interpreter.execute(ast)


def test_class_with_properties():
    """Test class with multiple properties."""
    code = """
    shuru
    class Gaadi {
        vidhi __init__(naam, rang) {
            yeh.naam = naam
            yeh.rang = rang
        }
        samapt
    }
    
    car = naya Gaadi("Maruti", "Laal")
    dikhao car.naam
    dikhao car.rang
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)


def test_inheritance():
    """Test class inheritance with badhaao."""
    code = """
    shuru
    class Janwar {
        vidhi __init__(naam) {
            yeh.naam = naam
        }
        samapt
        
        vidhi bolo() {
            dikhao "Main ek janwar hoon"
        }
        samapt
    }
    
    class Kutta badhaao Janwar {
        vidhi bolo() {
            dikhao "Bhow bhow!"
        }
        samapt
    }
    
    dog = naya Kutta("Tommy")
    dog.bolo()
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)


def test_super_call():
    """Test calling parent method with upar."""
    code = """
    shuru
    class Parent {
        vidhi greet() {
            dikhao "Hello from parent"
        }
        samapt
    }
    
    class Child badhaao Parent {
        vidhi greet() {
            upar.greet()
            dikhao "Hello from child"
        }
        samapt
    }
    
    c = naya Child()
    c.greet()
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)


def test_method_with_return():
    """Test method that returns a value."""
    code = """
    shuru
    class Calculator {
        vidhi add(a, b) {
            vapas a + b
        }
        samapt
    }
    
    calc = naya Calculator()
    result = calc.add(5, 3)
    dikhao result
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    # Verify result
    result = interpreter.global_env.get('result')
    assert result == 8


def test_property_modification():
    """Test modifying object properties."""
    code = """
    shuru
    class Counter {
        vidhi __init__() {
            yeh.count = 0
        }
        samapt
        
        vidhi increment() {
            yeh.count = yeh.count + 1
        }
        samapt
    }
    
    c = naya Counter()
    c.increment()
    c.increment()
    dikhao c.count
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    c = interpreter.global_env.get('c')
    assert c.properties['count'] == 2


def test_multiple_instances():
    """Test multiple instances of same class."""
    code = """
    shuru
    class Person {
        vidhi __init__(naam, umar) {
            yeh.naam = naam
            yeh.umar = umar
        }
        samapt
    }
    
    p1 = naya Person("Amit", 25)
    p2 = naya Person("Priya", 30)
    
    dikhao p1.naam
    dikhao p2.naam
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    p1 = interpreter.global_env.get('p1')
    p2 = interpreter.global_env.get('p2')
    
    assert p1.properties['naam'] == "Amit"
    assert p2.properties['naam'] == "Priya"


def test_this_in_method():
    """Test using 'yeh' (this) in methods."""
    code = """
    shuru
    class Test {
        vidhi __init__(value) {
            yeh.value = value
        }
        samapt
        
        vidhi get_value() {
            vapas yeh.value
        }
        samapt
    }
    
    t = naya Test(42)
    result = t.get_value()
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    result = interpreter.global_env.get('result')
    assert result == 42


def test_nested_inheritance():
    """Test multi-level inheritance."""
    code = """
    shuru
    class A {
        vidhi method_a() {
            vapas "A"
        }
        samapt
    }
    
    class B badhaao A {
        vidhi method_b() {
            vapas "B"
        }
        samapt
    }
    
    class C badhaao B {
        vidhi method_c() {
            vapas "C"
        }
        samapt
    }
    
    obj = naya C()
    r1 = obj.method_a()
    r2 = obj.method_b()
    r3 = obj.method_c()
    khatam
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    r1 = interpreter.global_env.get('r1')
    r2 = interpreter.global_env.get('r2')
    r3 = interpreter.global_env.get('r3')
    
    assert r1 == "A"
    assert r2 == "B"
    assert r3 == "C"

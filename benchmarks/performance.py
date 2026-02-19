"""
Performance Benchmarks for MeriLang.

Measures execution speed for various language features.
"""

import time
from typing import Callable, Tuple
from MeriLang.parser_enhanced import parse_MeriLang
from MeriLang.interpreter_enhanced import Interpreter


def benchmark(name: str, code: str, iterations: int = 1000) -> Tuple[float, float]:
    """
    Benchmark a code snippet.
    
    Args:
        name: Benchmark name
        code: MeriLang code to benchmark
        iterations: Number of iterations
        
    Returns:
        Tuple of (total_time, time_per_iteration)
    """
    # Parse once
    ast = parse_MeriLang(code)
    
    # Warm up
    interpreter = Interpreter()
    interpreter.execute(ast)
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        interpreter = Interpreter()
        interpreter.execute(ast)
    end = time.perf_counter()
    
    total_time = end - start
    per_iteration = total_time / iterations
    
    print(f"{name:40} {per_iteration*1000:8.3f} ms/iter  ({iterations} iterations)")
    return total_time, per_iteration


def run_benchmarks():
    """Run all benchmarks."""
    print("=" * 80)
    print("MeriLang Performance Benchmarks")
    print("=" * 80)
    print()
    
    # Arithmetic
    print("ARITHMETIC OPERATIONS:")
    benchmark("Simple addition", "maan x = 1 + 2")
    benchmark("Complex expression", "maan x = (1 + 2) * 3 - 4 / 2")
    benchmark("Float operations", "maan x = 3.14 * 2.5 + 1.0")
    print()
    
    # Variables
    print("VARIABLE OPERATIONS:")
    benchmark("Variable assignment", "maan x = 42")
    benchmark("Variable read", """
maan x = 42
maan y = x
""")
    benchmark("Variable update", """
maan x = 10
x = x + 1
""")
    print()
    
    # Control flow
    print("CONTROL FLOW:")
    benchmark("Simple if", """
maan x = 10
agar x > 5 {
    maan y = x * 2
}
""", iterations=500)
    
    benchmark("If-else", """
maan x = 10
agar x > 15 {
    maan y = 1
} warna {
    maan y = 2
}
""", iterations=500)
    
    benchmark("While loop (10 iterations)", """
maan i = 0
jab_tak i < 10 {
    i = i + 1
}
""", iterations=100)
    print()
    
    # Functions
    print("FUNCTION OPERATIONS:")
    benchmark("Function definition", """
kaam add(a, b) {
    wapas a + b
}
""", iterations=500)
    
    benchmark("Function call", """
kaam double(x) {
    wapas x * 2
}
maan result = double(5)
""", iterations=500)
    
    benchmark("Recursive function (fib 10)", """
kaam fib(n) {
    agar n <= 1 {
        wapas n
    }
    wapas fib(n - 1) + fib(n - 2)
}
maan result = fib(10)
""", iterations=10)
    print()
    
    # Lists
    print("LIST OPERATIONS:")
    benchmark("List creation", "maan arr = [1, 2, 3, 4, 5]")
    benchmark("List access", """
maan arr = [1, 2, 3, 4, 5]
maan x = arr[2]
""")
    benchmark("List iteration", """
maan arr = [1, 2, 3, 4, 5]
bar_bar x in arr {
    maan y = x * 2
}
""", iterations=100)
    print()
    
    # Dictionaries
    print("DICTIONARY OPERATIONS:")
    benchmark("Dict creation", 'maan d = {"x": 10, "y": 20}')
    benchmark("Dict access", """
maan d = {"x": 10, "y": 20}
maan val = d["x"]
""")
    print()
    
    # Lambdas
    print("LAMBDA OPERATIONS:")
    benchmark("Lambda definition", "maan f = lambada x: x * 2")
    benchmark("Lambda call", """
maan double = lambada x: x * 2
maan result = double(10)
""")
    print()
    
    # Built-ins
    print("BUILT-IN FUNCTIONS:")
    benchmark("lambai (length)", """
maan arr = [1, 2, 3, 4, 5]
maan len = lambai(arr)
""")
    benchmark("yog (sum)", """
maan arr = [1, 2, 3, 4, 5]
maan total = yog(arr)
""")
    print()
    
    # Complex programs
    print("COMPLEX PROGRAMS:")
    benchmark("Factorial (10)", """
kaam factorial(n) {
    agar n <= 1 {
        wapas 1
    }
    wapas n * factorial(n - 1)
}
maan result = factorial(10)
""", iterations=50)
    
    benchmark("List processing", """
maan numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
maan total = 0
bar_bar x in numbers {
    agar x % 2 == 0 {
        total = total + x
    }
}
""", iterations=50)
    
    print()
    print("=" * 80)
    print("Benchmarks complete!")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmarks()

# MeriLang 🇮🇳

A desi toy programming language built with Python.

[![Version](https://img.shields.io/badge/version-1.0.2-blue.svg)](https://github.com/XploitMonk0x01/merilang)
[![PyPI](https://img.shields.io/pypi/v/merilang.svg)](https://pypi.org/project/merilang/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)

## Features ✨

- **Simple Syntax**: Easy-to-learn syntax with meri keywords
- **Full Programming Language**: Variables, functions, loops, conditionals, and more
- **Object-Oriented Programming**: Classes, inheritance, methods, and properties
- **Error Handling**: Try-catch-finally blocks for robust error management
- **Interactive REPL**: Test code snippets interactively
- **Helpful Error Messages**: Clear error messages with line numbers
- **Built-in Functions**: Rich standard library for common operations
- **File I/O**: Read and write files
- **Module System**: Import and reuse code across files
- **Web Playground**: Browser-based code editor and runner

## Installation 📦

### Using pip (Recommended)

```bash
pip install merilang
```

### From Source

```bash
git clone https://github.com/XploitMonk0x01/merilang.git
cd merilang
pip install -e .
```

## Quick Start 🚀

### Hello World

Create a file `hello.meri`:

```MeriLang
shuru
dikhao "Hello, World!"
khatam
```

Run it:

```bash
merilang hello.meri
# or
ml hello.meri
```

### Interactive REPL

```bash
merilang
# or
ml
```

```
MeriLang v1.0.1 Interactive REPL
Type 'exit' or press Ctrl+C to quit

>>> x = 42
>>> dikhao x
42
>>> dikhao x * 2
84
```

## Language Syntax 📝

### Program Structure

Every MeriLang program starts with `shuru` (begin) and ends with `khatam` (end):

```MeriLang
shuru
// Your code here
khatam
```

### Comments

```MeriLang
// Single-line comments start with //
```

### Variables

```MeriLang
shuru
x = 42              // Integer
pi = 3.14           // Float
naam = "Rajwant"    // String
is_valid = sahi     // Boolean (true)
is_false = galat    // Boolean (false)
khatam
```

### Data Types

- **Numbers**: `42`, `3.14`
- **Strings**: `"Hello"`, `"नमस्ते"`
- **Booleans**: `sahi` (true), `galat` (false)
- **Lists**: `[1, 2, 3]`, `["a", "b", "c"]`

### Operators

**Arithmetic:**

- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `%` Modulo

**Comparison:**

- `>` Greater than
- `<` Less than
- `>=` Greater than or equal
- `<=` Less than or equal
- `==` Equal to
- `!=` Not equal to

### Print Statement

```MeriLang
shuru
dikhao "Hello"      // Print string
dikhao 42           // Print number
dikhao x            // Print variable
dikhao x + y        // Print expression
khatam
```

### Input

```MeriLang
shuru
dikhao "Enter your name:"
padho naam
dikhao "Hello, " + naam
khatam
```

### Conditionals

```MeriLang
shuru
age = 25

agar age >= 18 {
    dikhao "Adult"
} warna {
    dikhao "Minor"
} bas
khatam
```

### Loops

**For Loop:**

```MeriLang
shuru
chalao i se 0 tak 5 {
    dikhao i
}
khatam
```

**While Loop:**

```MeriLang
shuru
count = 0
jabtak count < 5 {
    dikhao count
    count = count + 1
} band
khatam
```

### Functions

```MeriLang
shuru
// Function definition
vidhi add(a, b) {
    vapas a + b
} samapt

// Function call
result = add(5, 3)
dikhao result

// Or use bulayo keyword
bulayo add(10, 20)
khatam
```

### Lists

```MeriLang
shuru
// Create list
numbers = [1, 2, 3, 4, 5]

// Access element
dikhao numbers[0]

// Modify element
numbers[1] = 99

// Add element
append(numbers, 6)

// List operations
dikhao length(numbers)
dikhao sum(numbers)
dikhao max(numbers)
dikhao min(numbers)

sorted_nums = sort(numbers)
reversed_nums = reverse(numbers)
khatam
```

### Built-in Functions

**List Operations:**

- `length(list)` - Get length
- `append(list, value)` - Add element
- `pop(list, index)` - Remove and return element
- `insert(list, index, value)` - Insert at index
- `sort(list)` - Return sorted copy
- `reverse(list)` - Return reversed copy
- `sum(list)` - Sum all elements
- `min(list/args)` - Get minimum
- `max(list/args)` - Get maximum

**String Operations:**

- `upper(string)` - Convert to uppercase
- `lower(string)` - Convert to lowercase
- `split(string, separator)` - Split into list
- `join(list, separator)` - Join list into string
- `replace(string, old, new)` - Replace substring

**Type Operations:**

- `type(value)` - Get type name
- `str(value)` - Convert to string
- `int(value)` - Convert to integer
- `float(value)` - Convert to float

**I/O Operations:**

- `input(prompt)` - Read user input
- `likho "file.txt" content` - Write to file
- `padho_file("file.txt")` - Read from file

### File I/O

```MeriLang
shuru
// Write to file
likho "output.txt" "Hello, MeriLang!"

// Read from file
content = padho_file("output.txt")
dikhao content
khatam
```

### Importing Modules

```MeriLang
// mylib.meri
shuru
vidhi helper_function(x) {
    vapas x * 2
} samapt
khatam

// main.meri
shuru
lao "mylib"
result = helper_function(21)
dikhao result
khatam
```

### Object-Oriented Programming

```MeriLang
shuru

// Define a class
class Person {
    vidhi __init__(naam, umar) {
        yeh.naam = naam
        yeh.umar = umar
    }
    samapt

    vidhi greet() {
        dikhao "Namaste, "
        dikhao yeh.naam
    }
    samapt
}

// Create instance
p = naya Person("Rajesh", 25)
p.greet()

// Access property
dikhao p.naam

// Inheritance
class Student badhaao Person {
    vidhi __init__(naam, umar, school) {
        yeh.naam = naam
        yeh.umar = umar
        yeh.school = school
    }
    samapt

    vidhi study() {
        dikhao yeh.naam
        dikhao " is studying"
    }
    samapt
}

s = naya Student("Priya", 20, "Delhi University")
s.greet()      // Inherited method
s.study()      // Own method

khatam
```

### Error Handling

```MeriLang
shuru

// Try-catch-finally
koshish {
    x = 10 / 0  // This will fail
}
pakdo err {
    dikhao "Error: "
    dikhao err
}
akhir {
    dikhao "Cleanup done"
}

// Throw custom exceptions
vidhi validate_age(age) {
    agar age < 0 {
        fenko "Age cannot be negative"
    }
    bas
    vapas sahi
}
samapt

koshish {
    validate_age(-5)
}
pakdo err {
    dikhao "Validation error: "
    dikhao err
}

khatam
```

## Examples 📚

See the [examples](examples/) directory for complete programs:

### Basic Examples

1. [Hello World](examples/01_hello_world.meri)
2. [Variables](examples/02_variables.meri)
3. [Conditionals](examples/03_conditionals.meri)
4. [Loops](examples/04_loops.meri)
5. [Functions](examples/05_functions.meri)
6. [FizzBuzz](examples/06_fizzbuzz.meri)
7. [Fibonacci](examples/07_fibonacci.meri)
8. [Lists](examples/08_lists.meri)
9. [Prime Numbers](examples/09_primes.meri)
10. [String Operations](examples/10_strings.meri)

### Advanced Examples (OOP & Error Handling)

11. [Basic Class](examples/11_basic_class.meri) - Class definition and objects
12. [Inheritance](examples/12_inheritance.meri) - Class inheritance with `badhaao`
13. [Bank Account](examples/13_bank_account.meri) - Real-world OOP example
14. [Error Handling](examples/14_error_handling.meri) - Try-catch-finally patterns
15. [Complete OOP + Errors](examples/15_complete_oop_errors.meri) - Advanced combination

## CLI Usage 💻

```bash
# Run a script
merilang script.meri
# or use short alias
ml script.meri

# Start REPL (interactive mode)
merilang
ml

# Show version
merilang --version
ml --version

# Show help
merilang --help
ml --help
```

## Development 🛠️

### Running Tests

```bash
# Install development dependencies
pip install pytest

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=MeriLang --cov-report=html

# Run specific test file
pytest tests/test_lexer.py -v
```

### Project Structure

```
merilang/
├── merilang/              # Main package
│   ├── __init__.py
│   ├── lexer_enhanced.py  # Tokenizer
│   ├── parser_enhanced.py # Parser
│   ├── ast_nodes_enhanced.py # AST node definitions
│   ├── interpreter_enhanced.py # Interpreter
│   ├── environment.py     # Environment management
│   ├── errors_enhanced.py # Error classes
│   └── cli.py            # Command-line interface
├── tests/                # Comprehensive test suite (172+ tests)
│   ├── test_lexer_enhanced.py
│   ├── test_parser_enhanced.py
│   ├── test_interpreter_enhanced.py
│   ├── test_oop.py
│   ├── test_error_handling.py
│   └── test_integration.py
├── examples/             # 25+ example programs (.meri files)
├── benchmarks/           # Performance benchmarks
├── docs/                # Documentation
│   ├── TUTORIAL.md      # Comprehensive tutorial
│   └── API.md           # API documentation
└── pyproject.toml       # Package configuration
```

## Keyword Reference 🔤

| English      | MeriLang  | Usage                  |
| ------------ | --------- | ---------------------- |
| Begin        | `shuru`   | Program start          |
| End          | `khatam`  | Program end            |
| Print        | `dikhao`  | Output statement       |
| Input        | `padho`   | Read input             |
| If           | `agar`    | Conditional            |
| Else         | `warna`   | Alternative branch     |
| End If       | `bas`     | Close if block         |
| While        | `jabtak`  | While loop             |
| End While    | `band`    | Close while loop       |
| For          | `chalao`  | For loop               |
| From         | `se`      | Loop start             |
| To           | `tak`     | Loop end               |
| Function     | `vidhi`   | Define function/method |
| Return       | `vapas`   | Return value           |
| End Function | `samapt`  | Close function         |
| Call         | `bulayo`  | Call function          |
| True         | `sahi`    | Boolean true           |
| False        | `galat`   | Boolean false          |
| Import       | `lao`     | Import module          |
| Write        | `likho`   | Write to file          |
| Class        | `class`   | Define class           |
| New          | `naya`    | Create object          |
| This         | `yeh`     | Current instance       |
| Extends      | `badhaao` | Inherit from class     |
| Super        | `upar`    | Call parent method     |
| Try          | `koshish` | Try block              |
| Catch        | `pakdo`   | Catch exception        |
| Finally      | `akhir`   | Finally block          |
| Throw        | `fenko`   | Throw exception        |

## Error Handling 🚨

MeriLang provides helpful error messages with line numbers:

```

Line 5, Column 12: Undefined variable: 'xyz'
Line 8: Division by zero
Line 12: Expected '=' after identifier

```

You can also handle errors gracefully with try-catch:

```MeriLang
koshish {
    risky_operation()
}
pakdo err {
    dikhao "Error handled: "
    dikhao err
}
```

## Documentation 📖

🌐 **[Official Documentation Website](https://xploitmonk0x01.github.io/merilang/)**

For comprehensive guides, see:

- **[TUTORIAL.md](docs/TUTORIAL.md)** - Complete beginner-friendly tutorial
- **[API.md](docs/API.md)** - API documentation and advanced features
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap 🗺️

- [x] Full lexer and parser
- [x] Interpreter with scopes
- [x] Functions and recursion
- [x] Lists and data structures
- [x] File I/O and modules
- [x] Object-Oriented Programming (classes, inheritance, methods)
- [x] Error handling (try-catch-finally, exceptions)
- [x] Comprehensive test suite
- [x] CLI and REPL
- [x] Web playground
- [x] Documentation website
- [ ] Package manager
- [ ] Debugger with breakpoints
- [ ] Standard library expansion
- [ ] IDE extensions (VS Code, etc.)
- [ ] Compiled mode (faster execution)

## Credits 💖

Inspired by educational programming languages and the need for culturally relevant learning tools.

## Support ⭐

If you like MeriLang, please give it a star on GitHub!

---

Made with ❤️ for the meri community

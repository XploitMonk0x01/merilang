# DesiLang API Documentation

Complete API reference for DesiLang modules and functions.

---

## Table of Contents

1. [Lexer API](#lexer-api)
2. [Parser API](#parser-api)
3. [Interpreter API](#interpreter-api)
4. [Environment API](#environment-api)
5. [Error System](#error-system)
6. [Built-in Functions](#built-in-functions)
7. [AST Nodes](#ast-nodes)

---

## Lexer API

### Module: `desilang.lexer_enhanced`

The lexer tokenizes DesiLang source code.

#### Class: `Lexer`

```python
class Lexer:
    def __init__(self, code: str, language: str = "en") -> None:
        """
        Initialize lexer with source code.

        Args:
            code: Source code to tokenize
            language: Error message language ("en" or "hi")
        """
```

**Methods:**

```python
def tokenize(self) -> List[Token]:
    """
    Tokenize entire source code.

    Returns:
        List of Token objects

    Raises:
        LexerError: On invalid characters or syntax
    """
```

#### Class: `Token`

```python
@dataclass
class Token:
    type: TokenType           # Token type enum
    value: Any                # Token value (str, int, float, None)
    line: int                 # Line number (1-indexed)
    column: int               # Column number (1-indexed)
```

#### Enum: `TokenType`

All token types:

```python
class TokenType(Enum):
    # Literals
    NUMBER = "NUMBER"          # Integer or float
    STRING = "STRING"          # String literal
    SACH = "SACH"             # true
    JHOOT = "JHOOT"           # false

    # Identifiers & Keywords
    IDENTIFIER = "IDENTIFIER"  # Variable names
    MAAN = "MAAN"             # let (variable declaration)
    KAAM = "KAAM"             # function
    WAPAS = "WAPAS"           # return

    # Control Flow
    AGAR = "AGAR"             # if
    WARNA = "WARNA"           # else
    AGARLENA = "AGARLENA"     # else if
    JAB_TAK = "JAB_TAK"       # while
    BAR_BAR = "BAR_BAR"       # for each
    RUK = "RUK"               # break
    AGE_BADHO = "AGE_BADHO"   # continue

    # OOP
    CLASS = "CLASS"           # class
    NAYA = "NAYA"             # new
    YEH = "YEH"               # this/self
    BADHAAO = "BADHAAO"       # extends
    UPAR = "UPAR"             # super

    # Error Handling
    KOSHISH = "KOSHISH"       # try
    PAKDO = "PAKDO"           # catch
    FENKO = "FENKO"           # throw
    AKHIR = "AKHIR"           # finally

    # Operators
    PLUS = "PLUS"             # +
    MINUS = "MINUS"           # -
    MULTIPLY = "MULTIPLY"     # *
    DIVIDE = "DIVIDE"         # /
    MODULO = "MODULO"         # %
    EQUALS = "EQUALS"         # =
    EQUAL_EQUAL = "EQUAL_EQUAL"     # ==
    NOT_EQUAL = "NOT_EQUAL"         # !=
    LESS = "LESS"             # <
    GREATER = "GREATER"       # >
    LESS_EQUAL = "LESS_EQUAL"       # <=
    GREATER_EQUAL = "GREATER_EQUAL" # >=

    # Logical
    AUR = "AUR"               # and
    YA = "YA"                 # or
    NAHI = "NAHI"             # not

    # Delimiters
    LPAREN = "LPAREN"         # (
    RPAREN = "RPAREN"         # )
    LBRACE = "LBRACE"         # {
    RBRACE = "RBRACE"         # }
    LBRACKET = "LBRACKET"     # [
    RBRACKET = "RBRACKET"     # ]
    COMMA = "COMMA"           # ,
    DOT = "DOT"               # .
    COLON = "COLON"           # :
    SEMICOLON = "SEMICOLON"   # ;

    # Special
    LAMBADA = "LAMBADA"       # lambda
    IN = "IN"                 # in
    EOF = "EOF"               # End of file
```

**Example Usage:**

```python
from desilang.lexer_enhanced import Lexer

code = 'maan x = 10'
lexer = Lexer(code)
tokens = lexer.tokenize()

for token in tokens:
    print(f"{token.type}: {token.value}")
# Output:
# MAAN: maan
# IDENTIFIER: x
# EQUALS: =
# NUMBER: 10
# EOF: None
```

---

## Parser API

### Module: `desilang.parser_enhanced`

The parser builds an Abstract Syntax Tree (AST) from tokens.

#### Class: `Parser`

```python
class Parser:
    def __init__(
        self,
        tokens: List[Token],
        language: str = "en"
    ) -> None:
        """
        Initialize parser with tokens.

        Args:
            tokens: List of Token objects from lexer
            language: Error message language ("en" or "hi")
        """
```

**Methods:**

```python
def parse(self) -> List[ASTNode]:
    """
    Parse tokens into AST.

    Returns:
        List of AST nodes (statements)

    Raises:
        ParserError: On syntax errors
    """
```

**Example Usage:**

```python
from desilang.lexer_enhanced import Lexer
from desilang.parser_enhanced import Parser

code = '''
maan x = 10
likho(x)
'''

lexer = Lexer(code)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

print(ast)  # List of AST nodes
```

---

## Interpreter API

### Module: `desilang.interpreter_enhanced`

The interpreter executes AST nodes.

#### Class: `Interpreter`

```python
class Interpreter:
    def __init__(
        self,
        language: str = "en",
        env: Optional[Environment] = None
    ) -> None:
        """
        Initialize interpreter.

        Args:
            language: Error message language ("en" or "hi")
            env: Optional custom environment (default: global)
        """
```

**Methods:**

```python
def interpret(self, nodes: List[ASTNode]) -> Any:
    """
    Execute AST nodes.

    Args:
        nodes: List of AST nodes to execute

    Returns:
        Result of last expression (if any)

    Raises:
        RuntimeError: On execution errors
        DivisionByZeroError: On division by zero
    """

def visit(self, node: ASTNode) -> Any:
    """
    Visit and execute single AST node.

    Args:
        node: AST node to execute

    Returns:
        Node execution result
    """
```

**Example Usage:**

```python
from desilang.lexer_enhanced import Lexer
from desilang.parser_enhanced import Parser
from desilang.interpreter_enhanced import Interpreter

code = '''
maan x = 10
maan y = 20
wapas x + y
'''

lexer = Lexer(code)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
result = interpreter.interpret(ast)

print(result)  # 30
```

---

## Environment API

### Module: `desilang.environment`

Environment manages variable scopes and built-in functions.

#### Class: `Environment`

```python
class Environment:
    def __init__(
        self,
        parent: Optional["Environment"] = None,
        language: str = "en"
    ) -> None:
        """
        Initialize environment.

        Args:
            parent: Parent environment (for nested scopes)
            language: Error message language
        """
```

**Methods:**

```python
def define(self, name: str, value: Any) -> None:
    """
    Define new variable.

    Args:
        name: Variable name
        value: Variable value
    """

def get(self, name: str, line: int, column: int) -> Any:
    """
    Get variable value.

    Args:
        name: Variable name
        line: Line number for errors
        column: Column number for errors

    Returns:
        Variable value

    Raises:
        RuntimeError: If variable undefined
    """

def set(
    self,
    name: str,
    value: Any,
    line: int,
    column: int
) -> None:
    """
    Update existing variable.

    Args:
        name: Variable name
        value: New value
        line: Line number for errors
        column: Column number for errors

    Raises:
        RuntimeError: If variable undefined
    """

def child_scope(self) -> "Environment":
    """
    Create child environment (nested scope).

    Returns:
        New Environment with self as parent
    """
```

**Built-in Functions:**

The global environment includes these built-in functions:

```python
# Output
likho(*args)                 # Print values

# Type Conversion
ank(value)                   # Convert to int
dashamlav(value)             # Convert to float
shabd(value)                 # Convert to string
prakar(value)                # Get type name

# List Operations
lambai(collection)           # Length
jodo(list, item)             # Append
nikalo(list)                 # Pop
disha(start, end=None)       # Range

# Math Operations
yog(numbers)                 # Sum
nyuntam(numbers)             # Minimum
adhiktam(numbers)            # Maximum
nirpeksha(value)             # Absolute value

# Dictionary Operations
kunji(dict)                  # Get keys
mul(dict)                    # Get values
```

**Example Usage:**

```python
from desilang.environment import Environment

env = Environment()

# Define variable
env.define("x", 10)

# Get variable
value = env.get("x", line=1, column=1)
print(value)  # 10

# Update variable
env.set("x", 20, line=1, column=1)

# Create nested scope
child_env = env.child_scope()
child_env.define("y", 30)

# Access built-in
likho = env.get("likho", 1, 1)
likho("Hello")  # Prints: Hello
```

---

## Error System

### Module: `desilang.errors_enhanced`

Bilingual error system with English and Hindi messages.

#### Base Class: `DesiLangError`

```python
class DesiLangError(Exception):
    def __init__(
        self,
        message_en: str,
        message_hi: str,
        line: int,
        column: int,
        language: str = "en"
    ) -> None:
        """
        Base error class.

        Args:
            message_en: English error message
            message_hi: Hindi error message
            line: Line number where error occurred
            column: Column number where error occurred
            language: Display language ("en" or "hi")
        """
```

#### Error Types

**LexerError**: Tokenization errors

```python
# Invalid character
LexerError.invalid_character(char, line, column, language)

# Unterminated string
LexerError.unterminated_string(line, column, language)
```

**ParserError**: Syntax errors

```python
# Unexpected token
ParserError.unexpected_token(
    expected: str,
    got: str,
    line: int,
    column: int,
    language: str
)

# Expected identifier
ParserError.expected_identifier(line, column, language)
```

**RuntimeError**: Execution errors

```python
# Undefined variable
RuntimeError.undefined_variable(name, line, column, language)

# Not a function
RuntimeError.not_a_function(name, line, column, language)

# Wrong argument count
RuntimeError.wrong_argument_count(
    expected: int,
    got: int,
    line: int,
    column: int,
    language: str
)
```

**DivisionByZeroError**: Division by zero

```python
DivisionByZeroError(line, column, language)
```

**Example Usage:**

```python
from desilang.errors_enhanced import RuntimeError

try:
    raise RuntimeError.undefined_variable("x", 5, 10, "en")
except RuntimeError as e:
    print(e)
    # Line 5, Column 10: Undefined variable 'x'
```

---

## Built-in Functions

Complete reference for all built-in functions.

### Output Functions

#### `likho(*args)`

Print values to console.

```desilang
likho("Hello")
likho("Sum:", 10 + 20)
likho(x, y, z)
```

**Parameters:**

- `*args`: Any number of values

**Returns:** `None`

---

### Type Conversion

#### `ank(value)`

Convert to integer.

```desilang
maan x = ank("42")      // 42
maan y = ank(3.7)       // 3
maan z = ank(sach)      // 1
```

**Parameters:**

- `value`: Value to convert

**Returns:** `int`

**Raises:** Error if conversion fails

---

#### `dashamlav(value)`

Convert to float.

```desilang
maan x = dashamlav("3.14")   // 3.14
maan y = dashamlav(42)       // 42.0
```

**Parameters:**

- `value`: Value to convert

**Returns:** `float`

**Raises:** Error if conversion fails

---

#### `shabd(value)`

Convert to string.

```desilang
maan x = shabd(42)          // "42"
maan y = shabd(3.14)        // "3.14"
maan z = shabd(sach)        // "sach"
```

**Parameters:**

- `value`: Value to convert

**Returns:** `str`

---

#### `prakar(value)`

Get type name.

```desilang
likho(prakar(42))           // "int"
likho(prakar(3.14))         // "float"
likho(prakar("hello"))      // "str"
likho(prakar([1, 2, 3]))    // "list"
likho(prakar({"a": 1}))     // "dict"
```

**Parameters:**

- `value`: Value to check

**Returns:** `str` (type name)

---

### List Functions

#### `lambai(collection)`

Get length of list, string, or dict.

```desilang
likho(lambai([1, 2, 3]))      // 3
likho(lambai("hello"))         // 5
likho(lambai({"a": 1}))        // 1
```

**Parameters:**

- `collection`: List, string, or dict

**Returns:** `int` (length)

---

#### `jodo(list, item)`

Append item to list.

```desilang
maan nums = [1, 2, 3]
jodo(nums, 4)
likho(nums)  // [1, 2, 3, 4]
```

**Parameters:**

- `list`: List to modify
- `item`: Item to append

**Returns:** `None`

---

#### `nikalo(list)`

Remove and return last item.

```desilang
maan nums = [1, 2, 3]
maan last = nikalo(nums)
likho(last)  // 3
likho(nums)  // [1, 2]
```

**Parameters:**

- `list`: List to modify

**Returns:** Removed item

**Raises:** Error if list empty

---

#### `disha(start, end=None)`

Create range of numbers.

```desilang
maan a = disha(5)         // [0, 1, 2, 3, 4]
maan b = disha(2, 6)      // [2, 3, 4, 5]
maan c = disha(1, 10)     // [1, 2, ..., 9]
```

**Parameters:**

- `start`: Start value (or end if only arg)
- `end`: End value (optional)

**Returns:** `list` of integers

**Note:** Range is `[start, end)` (excludes end)

---

### Math Functions

#### `yog(numbers)`

Sum of numbers.

```desilang
likho(yog([1, 2, 3, 4]))    // 10
likho(yog([]))              // 0
```

**Parameters:**

- `numbers`: List of numbers

**Returns:** `int` or `float` (sum)

---

#### `nyuntam(numbers)`

Minimum value.

```desilang
likho(nyuntam([5, 2, 8, 1]))   // 1
```

**Parameters:**

- `numbers`: List of numbers

**Returns:** Minimum value

**Raises:** Error if list empty

---

#### `adhiktam(numbers)`

Maximum value.

```desilang
likho(adhiktam([5, 2, 8, 1]))  // 8
```

**Parameters:**

- `numbers`: List of numbers

**Returns:** Maximum value

**Raises:** Error if list empty

---

#### `nirpeksha(value)`

Absolute value.

```desilang
likho(nirpeksha(-5))     // 5
likho(nirpeksha(3.14))   // 3.14
```

**Parameters:**

- `value`: Number

**Returns:** `int` or `float` (absolute value)

---

### Dictionary Functions

#### `kunji(dict)`

Get dictionary keys.

```desilang
maan data = {"a": 1, "b": 2}
maan keys = kunji(data)
likho(keys)  // ["a", "b"]
```

**Parameters:**

- `dict`: Dictionary

**Returns:** `list` of keys

---

#### `mul(dict)`

Get dictionary values.

```desilang
maan data = {"a": 1, "b": 2}
maan values = mul(data)
likho(values)  // [1, 2]
```

**Parameters:**

- `dict`: Dictionary

**Returns:** `list` of values

---

## AST Nodes

### Module: `desilang.ast_nodes_enhanced`

All AST node types.

#### Base: `ASTNode`

```python
@dataclass
class ASTNode:
    line: int      # Line number
    column: int    # Column number
```

#### Literals

```python
@dataclass
class NumberNode(ASTNode):
    value: Union[int, float]

@dataclass
class StringNode(ASTNode):
    value: str

@dataclass
class BooleanNode(ASTNode):
    value: bool
```

#### Variables

```python
@dataclass
class VariableNode(ASTNode):
    name: str

@dataclass
class AssignmentNode(ASTNode):
    name: str
    value: ASTNode
```

#### Operators

```python
@dataclass
class BinaryOpNode(ASTNode):
    left: ASTNode
    operator: str  # +, -, *, /, %, ==, !=, <, >, <=, >=
    right: ASTNode

@dataclass
class UnaryOpNode(ASTNode):
    operator: str  # -, nahi
    operand: ASTNode
```

#### Control Flow

```python
@dataclass
class IfNode(ASTNode):
    condition: ASTNode
    then_body: List[ASTNode]
    else_body: Optional[List[ASTNode]]

@dataclass
class WhileNode(ASTNode):
    condition: ASTNode
    body: List[ASTNode]

@dataclass
class ForNode(ASTNode):
    variable: str
    iterable: ASTNode
    body: List[ASTNode]
```

#### Functions

```python
@dataclass
class FunctionDefNode(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]

@dataclass
class FunctionCallNode(ASTNode):
    name: ASTNode
    arguments: List[ASTNode]

@dataclass
class ReturnNode(ASTNode):
    value: Optional[ASTNode]

@dataclass
class LambdaNode(ASTNode):
    params: List[str]
    body: ASTNode
```

#### Classes

```python
@dataclass
class ClassDefNode(ASTNode):
    name: str
    superclass: Optional[str]
    methods: List[FunctionDefNode]

@dataclass
class NewNode(ASTNode):
    class_name: str
    arguments: List[ASTNode]
```

#### Collections

```python
@dataclass
class ListNode(ASTNode):
    elements: List[ASTNode]

@dataclass
class DictNode(ASTNode):
    pairs: List[Tuple[ASTNode, ASTNode]]

@dataclass
class IndexNode(ASTNode):
    object: ASTNode
    index: ASTNode
```

#### Error Handling

```python
@dataclass
class TryNode(ASTNode):
    try_body: List[ASTNode]
    error_var: Optional[str]
    catch_body: List[ASTNode]
    finally_body: Optional[List[ASTNode]]

@dataclass
class ThrowNode(ASTNode):
    value: ASTNode
```

---

## Complete Example

Putting it all together:

```python
from desilang.lexer_enhanced import Lexer
from desilang.parser_enhanced import Parser
from desilang.interpreter_enhanced import Interpreter

# Source code
code = '''
kaam factorial(n) {
    agar n <= 1 {
        wapas 1
    }
    wapas n * factorial(n - 1)
}

maan result = factorial(5)
likho("Factorial of 5 is:", result)
'''

# Tokenize
lexer = Lexer(code, language="en")
tokens = lexer.tokenize()

# Parse
parser = Parser(tokens, language="en")
ast = parser.parse()

# Execute
interpreter = Interpreter(language="en")
interpreter.interpret(ast)

# Output: Factorial of 5 is: 120
```

---

## Integration Guide

### Using DesiLang in Python

```python
from desilang import run_code

# Simple execution
result = run_code('maan x = 10\nwapas x * 2')
print(result)  # 20

# With custom environment
from desilang.environment import Environment

env = Environment()
env.define("custom_var", 42)

result = run_code('wapas custom_var + 8', env=env)
print(result)  # 50
```

### Error Handling

```python
from desilang import run_code
from desilang.errors_enhanced import DesiLangError

try:
    result = run_code('maan x = 10 / 0')
except DesiLangError as e:
    print(f"Error at line {e.line}, col {e.column}: {e}")
```

---

## Advanced Topics

### Custom Built-ins

Add your own built-in functions:

```python
from desilang.environment import Environment
from desilang.interpreter_enhanced import Interpreter

def custom_function(x, y):
    return x ** y

env = Environment()
env.define("power", custom_function)

interpreter = Interpreter(env=env)
# Now you can use power() in DesiLang code
```

### Language Switching

Switch between English and Hindi errors:

```python
from desilang.lexer_enhanced import Lexer

# English errors
lexer_en = Lexer(code, language="en")

# Hindi errors
lexer_hi = Lexer(code, language="hi")
```

---

## Reference Links

- [Tutorial](TUTORIAL.md) - Beginner guide
- [Examples](../examples/) - Code examples
- [GitHub](https://github.com/XploitMonk0x01/merilang) - Source code

---

**API Version**: 2.0.0  
**Last Updated**: 2024

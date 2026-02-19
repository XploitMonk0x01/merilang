# Merilang — Developer Guide

> **Version:** 3.0 (Compiler Front-End)  
> **Location:** `merilang/` package directory  
> A step-by-step reference for every module, how they connect, and how source code flows through the full pipeline.

---

## Table of Contents

1. [Directory Overview](#1-directory-overview)
2. [The Compilation Pipeline](#2-the-compilation-pipeline)
3. [Module Reference (step by step)](#3-module-reference)
   - [errors_enhanced.py](#31-errors_enhancedpy)
   - [lexer_enhanced.py](#32-lexer_enhancedpy)
   - [ast_nodes_enhanced.py](#33-ast_nodes_enhancedpy)
   - [parser_enhanced.py](#34-parser_enhancedpy)
   - [symbol_table.py](#35-symbol_tablepy)
   - [semantic_analyzer.py](#36-semantic_analyzerpy)
   - [ir_nodes.py](#37-ir_nodespy)
   - [ir_generator.py](#38-ir_generatorpy)
   - [environment.py](#39-environmentpy)
   - [interpreter_enhanced.py](#310-interpreter_enhancedpy)
   - [cli.py](#311-clipy)
   - [\_\_init\_\_.py](#312-__init__py)
   - [\_\_main\_\_.py](#313-__main__py)
4. [Data Flow Diagram](#4-data-flow-diagram)
5. [Keyword Reference](#5-keyword-reference)
6. [Error Hierarchy](#6-error-hierarchy)
7. [Adding a New Language Feature](#7-adding-a-new-language-feature)

---

## 1. Directory Overview

```
merilang/
├── __init__.py            # Public API / re-exports
├── __main__.py            # python -m merilang entry point
├── cli.py                 # Argument parsing + pipeline orchestration
│
├── errors_enhanced.py     # All exception classes (bilingual EN + HI)
│
├── lexer_enhanced.py      # Source → Token list  (Phase 1)
├── ast_nodes_enhanced.py  # AST node dataclasses (shared by Parser & IR)
├── parser_enhanced.py     # Token list → AST     (Phase 2)
│
├── symbol_table.py        # Scope stack for semantic analysis
├── semantic_analyzer.py   # AST → error list     (Phase 3)
│
├── ir_nodes.py            # 3AC instruction dataclasses
├── ir_generator.py        # AST → IR program     (Phase 4, optional)
│
├── environment.py         # Runtime variable scoping
└── interpreter_enhanced.py# AST → execution      (Phase 5)
```

---

## 2. The Compilation Pipeline

Every time you run a Merilang script the following five phases execute **in order**:

```
 ┌──────────┐    tokens    ┌────────┐    AST     ┌──────────┐
 │  Lexer   │ ──────────▶ │ Parser │ ──────────▶ │ Semantic │
 └──────────┘             └────────┘             │ Analyzer │
                                                 └────┬─────┘
                  optional IR dump ◀── IRGenerator ◀──┘
                                                      │
                                               ┌──────▼──────┐
                                               │ Interpreter │
                                               └─────────────┘
```

| Phase | Input | Output | Module |
|-------|-------|--------|--------|
| **1. Lex** | Raw source string | `List[Token]` | `lexer_enhanced.py` |
| **2. Parse** | `List[Token]` | `ProgramNode` (AST) | `parser_enhanced.py` |
| **3. Analyse** | `ProgramNode` | `List[SemanticError]` | `semantic_analyzer.py` |
| **4. IR Gen** *(optional)* | `ProgramNode` | `IRProgram` | `ir_generator.py` |
| **5. Interpret** | `ProgramNode` | Side effects / output | `interpreter_enhanced.py` |

Phases 1–3 are **always** run. Phase 4 is triggered by `--ir`. Phase 5 runs only if phases 1–3 are error-free.

---

## 3. Module Reference

---

### 3.1 `errors_enhanced.py`

**Purpose:** Central hub for all exception classes. Every other module imports from here.

**Key classes:**

| Class | Role |
|---|---|
| `MeriLangError` | Base class — carries `message_en`, `message_hi`, `line`, `column`, `suggestion_en/hi` |
| `LexerError` | Bad character / unterminated string |
| `LexerErrorCollection` | Wraps multiple `LexerError`s for panic-mode batch reporting |
| `ParserError` | Syntax error; has factory methods `expected_token()`, `missing_token()`, `invalid_syntax()` |
| `ParserErrorCollection` | Wraps multiple `ParserError`s |
| `SemanticError` | Base for static analysis errors |
| `TypeCheckError` | Illegal type combination (e.g. `"hello" - 5`) |
| `UndefinedNameError` | Variable/function used before declaration |
| `RedefinitionError` | Name declared twice in the same scope |
| `RuntimeError` | Base for runtime failures |
| `ErrorLanguage` | Enum: `ENGLISH`, `HINDI`, `BILINGUAL` — controls message formatting |

**How `MeriLangError.format_message()` works:**

```
ErrorLanguage.ENGLISH   → English message only
ErrorLanguage.HINDI     → Hindi message only
ErrorLanguage.BILINGUAL → English first, Hindi below (default)
```

---

### 3.2 `lexer_enhanced.py`

**Purpose:** Turns raw source text into a flat list of `Token` objects. The first phase of the pipeline.

**Key types:**

```python
@dataclass
class Token:
    type:   TokenType   # e.g. TokenType.LET, TokenType.NUMBER
    value:  Any         # literal value or raw string
    line:   int         # 1-indexed source line
    column: int
```

**How tokenisation works (step by step):**

1. `Lexer.__init__(source)` — stores source, resets position/line/column counters and `self.errors = []`.
2. `Lexer.tokenize()` loops over every character:
   - **Whitespace** → `skip_whitespace()` (advances position)
   - `//` → `skip_comment()` (reads to end of line)
   - `\n` → advance and continue
   - Digit → `read_number()` → produces `NUMBER` token
   - `"` or `'` → `read_string()` → produces `STRING` token
   - Letter / `_` / Hindi Unicode (≥ 0x0900) → `read_identifier_or_keyword()` — keyword lookup via the `KEYWORDS` dict produces named token types; unknown identifiers become `IDENTIFIER`
   - Known operator chars → `read_operator()` — tries two-char ops first, then single-char
   - **Unknown char** → `_record_error()` — appended to `self.errors`, character is skipped (**panic-mode**)
3. Appends `EOF` token.
4. If `self.errors` is non-empty → raises `LexerErrorCollection` with all errors.

**Public helpers:**

```python
tokenize(source)        # raises on any error
tokenize_safe(source)   # returns (tokens, list_of_lex_errors) — never raises
```

**Merilang keyword → TokenType map (examples):**

| Source | TokenType |
|---|---|
| `maan` | `LET` |
| `likho` | `PRINT` |
| `kaam` | `FUNCTION` |
| `agar` | `IF` |
| `warna` | `ELSE` |
| `jab_tak` | `WHILE` |
| `har` | `FOR` |
| `wapas` | `RETURN` |
| `sach` / `jhoot` | `TRUE` / `FALSE` |
| `ruk` | `BREAK` |
| `age_badho` | `CONTINUE` |
| `koshish` / `pakad` | `TRY` / `CATCH` |
| `uchalo` | `THROW` |
| `nahi` | `NOT` |
| `aur` / `ya` | `AND` / `OR` |

---

### 3.3 `ast_nodes_enhanced.py`

**Purpose:** Defines all **Abstract Syntax Tree node** dataclasses. These are the data structures that carry the parsed meaning of your program; they are consumed by the parser (produced), the semantic analyzer, the IR generator, and the interpreter (all consumed).

**Base class:**

```python
class ASTNode:
    line: int   # every node stores its source line
```

**Node categories:**

| Category | Key nodes |
|---|---|
| **Literals** | `NumberNode`, `StringNode`, `BooleanNode`, `NoneNode` |
| **Collections** | `ListNode`, `DictNode` |
| **Variables** | `VariableNode`, `AssignmentNode` |
| **Operations** | `BinaryOpNode(operator, left, right)`, `UnaryOpNode(operator, operand)` |
| **Control flow** | `IfNode(condition, then_branch, elif_branches, else_branch)`, `WhileNode`, `ForNode`, `BreakNode`, `ContinueNode` |
| **Functions** | `FunctionDefNode(name, parameters, body)`, `FunctionCallNode(name, arguments)`, `ReturnNode`, `LambdaNode` |
| **OOP** | `ClassDefNode(name, parent, methods)`, `NewObjectNode`, `MethodCallNode`, `PropertyAccessNode`, `PropertyAssignmentNode`, `ThisNode`, `SuperNode` |
| **Exceptions** | `TryNode(try_block, exception_var, catch_block, finally_block)`, `ThrowNode` |
| **I/O** | `PrintNode(arguments)`, `InputNode(variable, prompt)` |
| **Misc** | `IndexNode`, `IndexAssignmentNode`, `ImportNode`, `ParenthesizedNode` |

---

### 3.4 `parser_enhanced.py`

**Purpose:** Converts the flat token list from the lexer into a tree of `ASTNode` objects. Uses **recursive descent** — each grammar rule is one method.

**Class:** `Parser(tokens, error_language=ErrorLanguage.ENGLISH)`

**How parsing works (step by step):**

1. `Parser.__init__` — stores tokens, sets cursor `pos = 0`, initialises `self.errors = []`.
2. `Parser.parse()` — top-level loop; calls `parse_statement()` until `EOF`.
   - Each call is wrapped in `try/except ParserError`:
     - On success → appends the returned `ASTNode` to `program.statements`
     - On error → appends error to `self.errors`, calls `synchronize()` to skip forward to a safe boundary
3. If `self.errors` → raises `ParserErrorCollection`.

**`synchronize()` — panic-mode recovery:**

After a parse error the parser fast-forwards past tokens until it reaches one of:
`}`, `khatam`, `EOF`, `agar`, `jab_tak`, `kaam`, `wapas`, `koshish`

This lets the parser continue and report multiple errors per run instead of stopping at the first one.

**Grammar hierarchy (lowest → highest precedence):**

```
parse_statement
  └─ parse_expression
       └─ parse_logical_or
            └─ parse_logical_and
                 └─ parse_equality
                      └─ parse_comparison
                           └─ parse_addition
                                └─ parse_multiplication
                                     └─ parse_unary
                                          └─ parse_postfix
                                               └─ parse_primary
```

**Helper methods:**

```python
self.current_token      # peek without consuming
self.advance()          # consume and return current token
self.match(type)        # consume if type matches, else False
self.expect(type)       # consume or raise ParserError
```

---

### 3.5 `symbol_table.py`

**Purpose:** A **stack-of-hash-maps** scope manager used during semantic analysis. Tracks every declared name and its type/kind.

**Key classes:**

```python
class SymbolKind(Enum):
    VARIABLE, PARAMETER, FUNCTION, CLASS

class MType:                    # string constants (not a real type system)
    NUMBER, STRING, BOOL, LIST, DICT, FUNC, CLASS, NONE, ANY

@dataclass
class Symbol:
    name: str
    kind: SymbolKind
    inferred_type: str          # MType constant
    line: int
    param_count: Optional[int]  # set for FUNCTION symbols

class SymbolTable:
    def define(symbol)          # add to current scope
    def resolve(name)           # walk scope chain upward
    def resolve_local(name)     # current scope only (re-declaration check)
    def enter_scope()           # push → returns child SymbolTable
    def exit_scope()            # pop → returns parent SymbolTable
    def all_names()             # all visible names (for "did you mean?" hints)
```

**Scoping example:**

```
Global scope
├── x: VARIABLE (number)
└── add: FUNCTION (param_count=2)
    └── Function scope (child)
        ├── a: PARAMETER
        └── b: PARAMETER
```

---

### 3.6 `semantic_analyzer.py`

**Purpose:** Walks the AST **before** interpretation, collecting logical errors that the parser cannot detect.

**What it checks:**

| Check | Error raised |
|---|---|
| Variable used before `maan` declaration | `UndefinedNameError` |
| Function called before `kaam` definition | `UndefinedNameError` + "did you mean?" suggestion |
| `ruk` / `age_badho` outside a loop | `SemanticError` |
| `wapas` outside a `kaam` | `SemanticError` |
| `yeh` / `upar` outside a class method | `SemanticError` |
| Re-declaring a name in the same scope | `RedefinitionError` |
| Arithmetic on string — e.g. `"x" - 5` | `TypeCheckError` |
| Wrong argument count to a function | `SemanticError` |
| Parent class not defined | `UndefinedNameError` |

**How it works (step by step):**

1. `SemanticAnalyzer()` creates a global `SymbolTable` and pre-populates it with built-in functions (`likho`, `input`, `length`, `range`, …)
2. `analyzer.analyze(program_node)` → calls `_visit(program_node)`
3. `_visit(node)` dispatches by class name: `_visit_NumberNode`, `_visit_IfNode`, etc.
4. Each visitor:
   - Recurses into child nodes
   - Calls `scope.enter_scope()` / `scope.exit_scope()` around blocks
   - Returns an `MType` tag (used by parent for type inference)
   - Calls `self._error(SemanticError(...))` for any violation — **non-fatal**, analysis continues
5. After the full walk, `analyze()` returns `self.errors` (empty = clean)

**Type checking rules:**

```
NUMBER op NUMBER  → always valid for arithmetic ops
STRING + STRING   → valid (concatenation)
STRING - NUMBER   → TypeCheckError
nahi NUMBER       → TypeCheckError  (nahi = logical NOT)
- STRING          → TypeCheckError  (unary minus on string)
```

---

### 3.7 `ir_nodes.py`

**Purpose:** Defines the **Three-Address Code (3AC)** instruction set as immutable dataclasses. Each instruction has at most one operation and two operands.

**Helper types:**

```python
@dataclass(frozen=True)
class Temp:   name: str    # compiler temp: t0, t1, t2 …
class Label:  name: str    # jump target:   L0, loop_start_3 …
```

**Instruction catalogue:**

| Class | Meaning | Example dump |
|---|---|---|
| `Assign` | `result = literal` | `t0 = 42` |
| `Copy` | `dest = src` | `x = t3` |
| `BinOp` | `result = l op r` | `t2 = t0 + t1` |
| `UnaryOp` | `result = op x` | `t1 = - t0` |
| `LabelInstr` | Label declaration | `loop_start_0:` |
| `Jump` | Unconditional jump | `GOTO loop_start_0` |
| `CondJump` | Conditional branch | `IF t3 GOTO L1 ELSE L2` |
| `FuncLabel` | Function entry | `FUNC add:` |
| `Param` | Push argument | `PARAM t0` |
| `Call` | Call function | `t5 = CALL add 2` |
| `Return` | Return from function | `RETURN t5` |
| `NewObj` | Instantiate class | `t6 = NEW Person` |
| `FieldLoad` | Read property | `t7 = t6.naam` |
| `FieldStore` | Write property | `t6.naam = t0` |
| `IndexLoad` | Read index | `t8 = arr[t0]` |
| `IndexStore` | Write index | `arr[t0] = t1` |
| `PrintIR` | Print values | `PRINT t0, t1` |
| `InputIR` | Read input | `INPUT naam` |
| `ThrowIR` | Throw exception | `THROW t0` |
| `TryBegin` | Begin try block | `TRY_BEGIN catch=L4` |
| `TryEnd` | End try block | `TRY_END` |
| `CatchBegin` | Begin catch | `CATCH AS err` |

**Container:**

```python
@dataclass
class IRProgram:
    instructions: List[IRInstr]
    def append(instr)     # add one instruction
    def dump() -> str     # human-readable listing (used by --ir flag)
```

---

### 3.8 `ir_generator.py`

**Purpose:** Walks the AST (same visitor pattern as the semantic analyzer) and emits a flat list of 3AC instructions into an `IRProgram`.

**Helper generators:**

```python
class _TempGen:   # yields t0, t1, t2 …
class _LabelGen:  # yields named labels: while_start_0, if_true_1 …
```

**How IR generation works (step by step):**

1. `IRGenerator()` creates a fresh `_TempGen`, `_LabelGen`, and an empty `IRProgram`.
2. `gen.generate(program_node)` → walks via `_emit(node)` dispatch.
3. **Expressions** lower into temporary assignments:
   ```
   maan x = 3 + 4
   ─────────────────
   t0 = 3
   t1 = 4
   t2 = t0 + t1
   x  = t2
   ```
4. **Control flow** becomes labels + jumps:
   ```
   jab_tak i < 10 { ... }
   ──────────────────────────
   while_start_0:
       t0 = i < 10
       IF t0 GOTO while_body_1 ELSE while_end_2
   while_body_1:
       ...
       GOTO while_start_0
   while_end_2:
   ```
5. **Functions** are wrapped in `FuncLabel` / `Return`:
   ```
   kaam add(a, b) { wapas a + b }
   ────────────────────────────────
   FUNC add:
       t0 = a + b
       RETURN t0
   ```
6. `_emit(node)` returns the `Temp` that holds the result of that sub-expression (or `None` for statements).

> **Note:** The IR is currently diagnostic / display-only. The interpreter still runs from the original AST. The IR provides a stable foundation for a future bytecode compiler or optimizer.

---

### 3.9 `environment.py`

**Purpose:** Runtime variable scoping used by the interpreter. Separate from `SymbolTable` — this one holds **values** not types, and operates at execution time.

```python
class Environment:
    bindings: Dict[str, Any]   # name → value
    parent:   Optional[Environment]
    MAX_RECURSION_DEPTH = 1000

    def define(name, value)   # create in current scope
    def get(name)             # walk chain upward, raise NameError if missing
    def set(name, value)      # update existing binding in any scope
    def create_child()        # push new scope (called on function entry)
```

**Difference from SymbolTable:**

| | `SymbolTable` | `Environment` |
|---|---|---|
| Phase | Compile-time (semantic analysis) | Runtime (interpretation) |
| Stores | Type tags + metadata | Actual Python values |
| Errors | `SemanticError` subclasses | `RuntimeError` subclasses |

---

### 3.10 `interpreter_enhanced.py`

**Purpose:** Executes the program by walking the AST and evaluating each node. The final and most complex phase.

**Class:** `Interpreter(debug=False)`

**How interpretation works:**

1. `interpreter.execute(program_node)` → iterates `program_node.statements`, calling `self.visit(stmt)`.
2. `visit(node)` dispatches by class name (same visitor pattern as semantic analyzer).
3. Statements return `None`; expressions return a Python value.
4. Scope is managed via `Environment`:
   - Block entry → `env = env.create_child()`
   - Block exit → `env = env.parent`
5. Functions are stored as `MeriLangFunction` objects in the environment and called later.
6. Classes are stored as `MeriLangClass` objects; `new Foo()` creates a `MeriLangInstance`.

**Control flow exceptions (internal):**

The interpreter uses Python exceptions for internal control flow signals — they are **not** error conditions:

```python
class BreakSignal(Exception): ...
class ContinueSignal(Exception): ...
class ReturnSignal(Exception):
    value: Any
class ThrowSignal(Exception):
    value: Any
```

These propagate up the call stack until caught by the corresponding loop/function/try handler.

**Built-in functions available at runtime:**

`likho` (print), `input`, `length`, `append`, `pop`, `sort`, `range`, `str`, `int`, `float`, `bool`, `type`, `abs`, `round`, `upper`, `lower`, `split`, `join`, `replace`, and more.

---

### 3.11 `cli.py`

**Purpose:** The command-line entry point. Wires all phases together and exposes flags to the user.

**Sub-commands:**

```
merilang run <file> [--debug] [--ir] [--no-semantic]
merilang repl        [--ir] [--no-semantic]
merilang version
```

**`_run_pipeline(code, ...)` — the core orchestrator:**

```python
# Phase 1 — Lex
tokens, lex_errors = tokenize_safe(code)
# (print lex_errors if any, but continue)

# Phase 2 — Parse
ast = Parser(tokens).parse()         # raises ParserErrorCollection on error

# Phase 3 — Semantic (skipped with --no-semantic)
errors = SemanticAnalyzer().analyze(ast)
if errors: return 1                   # abort before executing

# Phase 4 — IR (only with --ir flag)
if emit_ir:
    print(IRGenerator().generate(ast).dump())

# Phase 5 — Interpret
Interpreter().execute(ast)
```

**REPL specifics:**  
The REPL creates a **single persistent `Interpreter` instance** so variables defined in one line are available in the next. Each line is evaluated through the full pipeline independently.

---

### 3.12 `__init__.py`

**Purpose:** The public API of the `merilang` package. Anything you need when using Merilang as a library is importable from here.

```python
from merilang import (
    # Lexer
    tokenize, tokenize_safe, Token,
    # Parser
    Parser,
    # Interpreter
    Interpreter,
    # Semantic analysis
    SemanticAnalyzer, SymbolTable, Symbol, SymbolKind, MType,
    # IR
    IRGenerator, IRProgram,
    # Errors
    MeriLangError, LexerError, ParserError,
    LexerErrorCollection, ParserErrorCollection,
    SemanticError, TypeCheckError, UndefinedNameError, RedefinitionError,
    ErrorLanguage,
)
```

**Version:** `__version__ = "3.0.0"`

---

### 3.13 `__main__.py`

**Purpose:** Allows running Merilang as a Python module.

```bash
python -m merilang run script.meri
```

It simply imports and calls `cli.main()`.

---

## 4. Data Flow Diagram

```
                      ┌─────────────────────────────┐
                      │         Source Code          │
                      │   "maan x = 3 + 4"           │
                      └──────────────┬──────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  lexer_enhanced.py   │
                          │  Lexer.tokenize()    │
                          │                      │
                          │  unknown chars →     │
                          │  _record_error()     │ ← panic-mode
                          └──────────┬──────────┘
                                     │ List[Token]
                          ┌──────────▼──────────┐
                          │  parser_enhanced.py  │
                          │  Parser.parse()      │
                          │                      │
                          │  parse errors →      │
                          │  synchronize()       │ ← panic-mode
                          └──────────┬──────────┘
                                     │ ProgramNode (AST)
                    ┌────────────────┼────────────────┐
                    │                │                 │
         ┌──────────▼──────┐ ┌───────▼──────┐ ┌──────▼──────────┐
         │ symbol_table.py │ │semantic_      │ │ ir_generator.py │
         │ SymbolTable     │◀│ analyzer.py   │ │ IRGenerator     │
         │ (scope stack)   │ │ SemanticAnal. │ │ (optional)      │
         └─────────────────┘ └───────┬───────┘ └──────┬──────────┘
                                     │ errors          │ IRProgram
                               if [] │                 │ .dump() → stdout
                                     │
                          ┌──────────▼──────────┐
                          │ environment.py       │
                          │ Environment          │◀─┐
                          │ (runtime scopes)     │  │
                          └──────────┬──────────┘  │
                                     │              │ scope chain
                          ┌──────────▼──────────┐  │
                          │interpreter_enhanced  │──┘
                          │ Interpreter.execute()│
                          └──────────┬──────────┘
                                     │
                                  stdout
```

---

## 5. Keyword Reference

| Merilang | Meaning | Python equiv. |
|---|---|---|
| `maan x = …` | Variable declaration | `x = …` |
| `likho(…)` | Print | `print(…)` |
| `likho_online(…)` | Print without newline | `print(…, end="")` |
| `poocho(…)` | Input | `input(…)` |
| `agar … { }` | if | `if …:` |
| `warna_agar … { }` | elif | `elif …:` |
| `warna { }` | else | `else:` |
| `jab_tak … { }` | while | `while …:` |
| `har x mein list { }` | for-each | `for x in list:` |
| `ruk` | break | `break` |
| `age_badho` | continue | `continue` |
| `kaam name(…) { }` | function def | `def name(…):` |
| `wapas …` | return | `return …` |
| `lambda(…) → expr` | lambda | `lambda …: expr` |
| `class Name { }` | class | `class Name:` |
| `naya Name(…)` | create object | `Name(…)` |
| `yeh` | this/self | `self` |
| `upar(…)` | super | `super().__init__(…)` |
| `koshish { }` | try | `try:` |
| `pakad e { }` | catch | `except e:` |
| `aakhir { }` | finally | `finally:` |
| `uchalo …` | throw | `raise …` |
| `sach` / `jhoot` | true / false | `True` / `False` |
| `khaali` | null | `None` |
| `nahi` | logical NOT | `not` |
| `aur` / `ya` | AND / OR | `and` / `or` |

---

## 6. Error Hierarchy

```
MeriLangError
├── LexerError
│   └── LexerErrorCollection         ← batch: multiple lex errors
├── ParserError
│   └── ParserErrorCollection        ← batch: multiple parse errors
├── SemanticError                    ← base for static analysis
│   ├── TypeCheckError               ← "hello" - 5
│   ├── UndefinedNameError           ← use before declare
│   └── RedefinitionError            ← name declared twice
└── RuntimeError                     ← execution failures
    ├── TypeError
    ├── NameError
    ├── DivisionByZeroError
    ├── IndexError
    ├── AttributeError
    ├── RecursionError
    ├── FileIOError
    ├── ImportError
    └── UserException                ← uchalo (throw)
```

---

## 7. Adding a New Language Feature

Follow these steps when adding a new statement or expression to Merilang:

### Step 1 — Add the keyword (if needed)
In `lexer_enhanced.py`, add to the `KEYWORDS` dict:
```python
"naya_kw": TokenType.NEW_KEYWORD,
```
Add the new `TokenType` variant too.

### Step 2 — Add an AST node
In `ast_nodes_enhanced.py`:
```python
@dataclass
class MyFeatureNode(ASTNode):
    some_field: ASTNode
    line: int = 1
```

### Step 3 — Parse it
In `parser_enhanced.py`, inside `parse_statement()` (or `parse_primary()` for expressions):
```python
if self.match(TokenType.NEW_KEYWORD):
    return self.parse_my_feature()
```
Write `parse_my_feature()` using the existing `self.expect()` / `self.match()` helpers.

### Step 4 — Analyse it
In `semantic_analyzer.py`, add a visitor:
```python
def _visit_MyFeatureNode(self, node: MyFeatureNode) -> str:
    self._visit(node.some_field)
    # add scope / type checks here
    return MType.ANY
```

### Step 5 — Generate IR (optional)
In `ir_generator.py`:
```python
def _emit_MyFeatureNode(self, node: MyFeatureNode) -> Optional[Temp]:
    val = self._emit(node.some_field)
    # emit IR instructions
    return val
```

### Step 6 — Interpret it
In `interpreter_enhanced.py`:
```python
def visit_MyFeatureNode(self, node: MyFeatureNode) -> Any:
    value = self.visit(node.some_field)
    # execute the feature
    return result
```

### Step 7 — Verify
Run the smoke tests:
```bash
python tests/smoke_test_pipeline.py
```

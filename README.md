# Merilang 🇮🇳

**A desi-flavoured programming language with a full compiler front-end — built in Python.**

[![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)](https://github.com/XploitMonk0x01/merilang)
[![PyPI](https://img.shields.io/pypi/v/merilang.svg)](https://pypi.org/project/merilang/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)

---

## What's New in v3.2 🆕

Merilang has graduated from a basic interpreter to a **full compiler front-end**:

| Phase                    | What it does                                                                |
| ------------------------ | --------------------------------------------------------------------------- |
| 🔍 **Panic-mode Lexer**  | Collects _all_ bad characters instead of stopping at the first one          |
| 🌳 **Panic-mode Parser** | Synchronises after errors and reports _all_ syntax problems in one pass     |
| 🔬 **Semantic Analyser** | Static type-checking, scope resolution, arity checks — before any code runs |
| 📐 **IR Generator**      | Lowers the AST to Three-Address Code (3AC) viewable with `--ir`             |
| 🚀 **Interpreter**       | Unchanged tree-walking execution on the verified AST                        |

---

## Features ✨

- **Desi Keywords** — write code in Hindi-inspired syntax (`maan`, `likho`, `kaam`, …)
- **Panic-mode Error Recovery** — see every mistake in one run, not one at a time
- **Static Semantic Analysis** — undefined names, type mismatches and arity errors caught _before_ execution
- **IR Dump** — inspect the generated Three-Address Code with `--ir`
- **CFG + Basic Blocks** — inspect control flow using `--cfg`
- **IR Optimizer** — constant folding, dead code elimination, CSE, and DAG local optimization via `--opt-ir`
- **SSA Conversion** — convert IR to SSA form (with PHI nodes) using `--ssa`
- **Full OOP** — classes, inheritance, `yeh` (this), `upar` (super)
- **Exception Handling** — `koshish` / `pakad` / `aakhir` (try / catch / finally)
- **Explicit Runtime Memory Model** — runtime stack + heap objects beyond basic activation records
- **Interactive REPL** — persistent state across lines, `--ir` mode available
- **Bilingual Errors** — every error message in English _and_ Hindi

---

## Installation 📦

### From PyPI (recommended)

```bash
pip install merilang
```

### From source

```bash
git clone https://github.com/XploitMonk0x01/merilang.git
cd merilang
pip install -e .
```

---

## Quick Start 🚀

### Hello World

Create `hello.meri`:

```
maan naam = "Duniya"
likho("Namaste, " + naam + "!")
```

Run it:

```bash
merilang run hello.meri
```

Output:

```
Namaste, Duniya!
```

### Interactive REPL

```bash
merilang repl
```

```
Merilang v3.2.0 Interactive REPL
>>> maan x = 10
>>> maan y = 32
>>> likho(x + y)
42
>>> niklo
Alvida! 👋
```

---

## Language Syntax 📝

### Comments

```
// This is a comment
```

### Variables

```
maan x = 42          // number
maan pi = 3.14       // float
maan naam = "Ravi"   // string
maan flag = sach     // boolean true
maan other = jhoot   // boolean false
maan nothing = khaali // null / None
```

### Operators

| Category   | Operators                          |
| ---------- | ---------------------------------- |
| Arithmetic | `+` `-` `*` `/` `%`                |
| Comparison | `==` `!=` `>` `<` `>=` `<=`        |
| Logical    | `aur` (and) `ya` (or) `nahi` (not) |

### Print & Input

```
likho("Hello!")                    // print with newline
likho_online("Enter name: ")       // print without newline
poocho naam "What is your name? "  // read input into 'naam'
```

### Conditionals

```
maan umar = 20

agar umar >= 18 {
    likho("Adult")
} warna_agar umar >= 13 {
    likho("Teen")
} warna {
    likho("Child")
}
```

### Loops

**While loop:**

```
maan i = 0
jab_tak i < 5 {
    likho(i)
    maan i = i + 1
}
```

**For-each loop:**

```
maan nums = [1, 2, 3, 4, 5]
har n mein nums {
    likho(n)
}
```

**Break & Continue:**

```
jab_tak sach {
    agar x > 10 { ruk }        // break
    agar x == 5 { age_badho }  // continue
    maan x = x + 1
}
```

### Functions

```
kaam jodo(a, b) {
    wapas a + b
}

maan hasil = jodo(3, 4)
likho(hasil)   // 7
```

**Lambda:**

```
maan double = lambda(x) -> x * 2
likho(double(21))   // 42
```

### Lists & Dicts

```
maan fruits = ["apple", "mango", "guava"]
likho(fruits[0])           // apple
likho(length(fruits))      // 3
append(fruits, "banana")

maan person = {"naam": "Raj", "umar": 25}
likho(person["naam"])      // Raj
```

### Object-Oriented Programming

```
class Insaan {
    kaam __init__(naam, umar) {
        yeh.naam = naam
        yeh.umar = umar
    }

    kaam parichay() {
        likho("Mera naam " + yeh.naam + " hai.")
    }
}

class Chaatra extends Insaan {
    kaam __init__(naam, umar, school) {
        upar(naam, umar)
        yeh.school = school
    }

    kaam padhai() {
        likho(yeh.naam + " padh raha hai.")
    }
}

maan c = naya Chaatra("Aryan", 18, "IIT")
c.parichay()   // Mera naam Aryan hai.
c.padhai()     // Aryan padh raha hai.
```

### Exception Handling

```
koshish {
    maan x = 10 / 0
} pakad galti {
    likho("Error: " + galti)
} aakhir {
    likho("Always runs.")
}

// Throw your own
kaam check_age(umar) {
    agar umar < 0 {
        uchalo "Umar negative nahi ho sakti!"
    }
    wapas sach
}
```

---

## CLI Reference 💻

```bash
# Run a script
merilang run script.meri

# Run with debug output (tokens + AST)
merilang run script.meri --debug

# Show Three-Address Code IR before running
merilang run script.meri --ir

# Show CFG / basic blocks
merilang run script.meri --cfg

# Optimize IR (constant folding + DCE + CSE + DAG local optimization)
merilang run script.meri --opt-ir

# Convert to SSA and print SSA IR (with PHI nodes)
merilang run script.meri --ssa

# Skip semantic analysis (faster, less safe)
merilang run script.meri --no-semantic

# Interactive REPL
merilang repl
merilang repl --ir           # show IR for each line
merilang repl --cfg --opt-ir --ssa

# Show version
merilang version
merilang --version
```

---

## Built-in Functions 🔧

| Function                         | Description                  |
| -------------------------------- | ---------------------------- |
| `likho(...)`                     | Print values                 |
| `poocho(var, prompt)`            | Read user input              |
| `length(x)`                      | Length of list or string     |
| `append(list, val)`              | Add element to list          |
| `pop(list, idx)`                 | Remove & return element      |
| `insert(list, idx, val)`         | Insert at index              |
| `sort(list)`                     | Return sorted copy           |
| `reverse(list)`                  | Return reversed copy         |
| `sum(list)`                      | Sum of elements              |
| `min(list)` / `max(list)`        | Minimum / Maximum            |
| `upper(s)` / `lower(s)`          | String case conversion       |
| `split(s, sep)`                  | Split string → list          |
| `join(list, sep)`                | Join list → string           |
| `replace(s, old, new)`           | Replace in string            |
| `str(x)` / `int(x)` / `float(x)` | Type conversion              |
| `bool(x)` / `type(x)`            | Type conversion / inspection |
| `abs(x)` / `round(x, n)`         | Math helpers                 |
| `range(n)`                       | List `[0 … n-1]`             |

---

## Project Structure 🗂️

```
merilang/
├── merilang/
│   ├── __init__.py              # Public API (v3.2.0)
│   ├── __main__.py              # python -m merilang
│   ├── cli.py                   # Arg parsing + pipeline wiring
│   ├── errors_enhanced.py       # All error classes (bilingual)
│   ├── lexer_enhanced.py        # Phase 1 — tokeniser (panic-mode)
│   ├── ast_nodes_enhanced.py    # AST node dataclasses
│   ├── parser_enhanced.py       # Phase 2 — recursive-descent parser
│   ├── symbol_table.py          # Scope manager for semantic analysis
│   ├── semantic_analyzer.py     # Phase 3 — static analyser
│   ├── ir_nodes.py              # 3AC instruction dataclasses
│   ├── ir_generator.py          # Phase 4 — AST → IR lowering
│   ├── ir_analysis.py           # Basic blocks + CFG builder
│   ├── ir_dag.py                # DAG local expression optimizer
│   ├── ir_optimizer.py          # Global IR optimization pipeline
│   ├── ir_ssa.py                # SSA conversion pass (PHI insertion)
│   ├── environment.py           # Runtime variable scoping
│   └── interpreter_enhanced.py  # Phase 5 — tree-walking interpreter
├── tests/
│   └── smoke_test_pipeline.py   # Full pipeline smoke tests
├── examples/                    # .meri example programs
├── Guide.md                     # In-depth developer guide
├── pyproject.toml               # PEP 517/518 packaging config
└── setup.py                     # Legacy build compat shim
```

> **Full developer reference:** [Guide.md](Guide.md)

---

## Keyword Reference 🔤

| Concept      | Merilang                | Python                  |
| ------------ | ----------------------- | ----------------------- |
| Variable     | `maan x = …`            | `x = …`                 |
| Print        | `likho(…)`              | `print(…)`              |
| Input        | `poocho var "prompt"`   | `var = input("prompt")` |
| If           | `agar … { }`            | `if …:`                 |
| Elif         | `warna_agar … { }`      | `elif …:`               |
| Else         | `warna { }`             | `else:`                 |
| While        | `jab_tak … { }`         | `while …:`              |
| For-each     | `har x mein list { }`   | `for x in list:`        |
| Break        | `ruk`                   | `break`                 |
| Continue     | `age_badho`             | `continue`              |
| Function     | `kaam name(…) { }`      | `def name(…):`          |
| Return       | `wapas …`               | `return …`              |
| Lambda       | `lambda(x) -> expr`     | `lambda x: expr`        |
| Class        | `class Name { }`        | `class Name:`           |
| Inherit      | `class A extends B { }` | `class A(B):`           |
| New object   | `naya Name(…)`          | `Name(…)`               |
| This         | `yeh`                   | `self`                  |
| Super        | `upar(…)`               | `super().__init__(…)`   |
| Try          | `koshish { }`           | `try:`                  |
| Catch        | `pakad e { }`           | `except e:`             |
| Finally      | `aakhir { }`            | `finally:`              |
| Throw        | `uchalo …`              | `raise …`               |
| True / False | `sach` / `jhoot`        | `True` / `False`        |
| Null         | `khaali`                | `None`                  |
| Not          | `nahi`                  | `not`                   |
| And / Or     | `aur` / `ya`            | `and` / `or`            |

---

## Error System 🚨

Merilang reports errors in **English + Hindi** with line/column positions. In v3.2 all errors from a single run are reported together (panic-mode), so you fix all issues at once.

```
[LexerError]  Line 4, Col 9: Unexpected character: '@'
[ParseError]  Line 8, Col 1: Expected expression, got 'EOF'
[SemanticError] Line 12: Undefined name 'resutl' — did you mean 'result'?
[TypeCheckError] Line 15: Cannot apply '-' to string and number
```

---

## Roadmap 🗺️

- [x] Lexer + parser
- [x] Tree-walking interpreter
- [x] OOP (classes, inheritance)
- [x] Exception handling
- [x] Interactive REPL
- [x] **Panic-mode error recovery** _(v3.0)_
- [x] **Semantic analysis pass** _(v3.0)_
- [x] **IR / Three-Address Code generation** _(v3.0)_
- [x] **Basic blocks + CFG**
- [x] **SSA conversion pass**
- [x] **DAG local expression optimization**
- [x] **Explicit stack/heap runtime model**
- [ ] Bytecode compiler & VM
- [ ] Standard library expansion
- [ ] VS Code extension
- [ ] Debugger with breakpoints
- [ ] Package manager

---

## Contributing 🤝

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

See [Guide.md](Guide.md) for a step-by-step walkthrough of how to add a new language feature.

---

## License 📄

MIT — see [LICENSE](LICENSE).

---

Made with ❤️ for the desi developer community

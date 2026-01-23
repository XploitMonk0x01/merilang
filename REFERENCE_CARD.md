# DesiLang Quick Reference Card

## Program Structure

```desilang
shuru           // Begin program
// code here
khatam          // End program
```

## Comments

```desilang
// Single-line comment
```

## Variables

```desilang
x = 42                  // Integer
pi = 3.14              // Float
name = "Rajwant"       // String
is_valid = sahi        // Boolean (true)
is_false = galat       // Boolean (false)
items = [1, 2, 3]      // List
```

## Operators

### Arithmetic

```desilang
a + b           // Addition
a - b           // Subtraction
a * b           // Multiplication
a / b           // Division
a % b           // Modulo
-a              // Negation
(a + b) * c     // Parentheses
```

### Comparison

```desilang
a > b           // Greater than
a < b           // Less than
a >= b          // Greater than or equal
a <= b          // Less than or equal
a == b          // Equal to
a != b          // Not equal to
```

## Control Flow

### If-Else

```desilang
agar condition {
    // if true
} bas

agar condition {
    // if true
} warna {
    // if false
} bas
```

### While Loop

```desilang
jabtak condition {
    // loop body
} band
```

### For Loop

```desilang
chalao i se start tak end {
    // loop body
}
```

## Functions

### Definition

```desilang
vidhi name(param1, param2) {
    // function body
    vapas result
} samapt
```

### Calling

```desilang
result = name(arg1, arg2)
bulayo name(arg1, arg2)
```

## I/O

### Print

```desilang
dikhao "Hello"
dikhao variable
dikhao expression
```

### Input

```desilang
padho variable
```

### File I/O

```desilang
likho "file.txt" content
content = padho_file("file.txt")
```

## Lists

### Basic Operations

```desilang
list = [1, 2, 3]        // Create
element = list[0]       // Access
list[1] = 99            // Modify
```

### Built-in Functions

```desilang
length(list)            // Get length
append(list, value)     // Add element
pop(list)               // Remove last
sort(list)              // Sort
reverse(list)           // Reverse
sum(list)               // Sum all
min(list)               // Minimum
max(list)               // Maximum
```

## String Functions

```desilang
upper(string)           // To uppercase
lower(string)           // To lowercase
split(string, sep)      // Split to list
join(list, sep)         // Join list
replace(str, old, new)  // Replace
length(string)          // String length
```

## Type Functions

```desilang
type(value)             // Get type
str(value)              // To string
int(value)              // To integer
float(value)            // To float
```

## Modules

```desilang
lao "filename"          // Import module
```

## Keywords Reference

| Keyword  | English      | Usage         |
| -------- | ------------ | ------------- |
| `shuru`  | begin        | Start program |
| `khatam` | end          | End program   |
| `dikhao` | show/print   | Print output  |
| `padho`  | read         | Read input    |
| `agar`   | if           | Conditional   |
| `warna`  | else         | Alternative   |
| `bas`    | enough/stop  | End if        |
| `jabtak` | until        | While loop    |
| `band`   | close/stop   | End while     |
| `chalao` | run          | For loop      |
| `se`     | from         | Loop start    |
| `tak`    | until        | Loop end      |
| `vidhi`  | method       | Function def  |
| `bulayo` | call         | Call function |
| `vapas`  | return       | Return value  |
| `samapt` | finished     | End function  |
| `sahi`   | correct/true | Boolean true  |
| `galat`  | wrong/false  | Boolean false |
| `lao`    | bring        | Import        |
| `likho`  | write        | Write file    |

## Complete Example

```desilang
shuru
// Factorial function
vidhi factorial(n) {
    agar n <= 1 {
        vapas 1
    } bas
    vapas n * factorial(n - 1)
} samapt

// Calculate and print
chalao i se 1 tak 6 {
    result = factorial(i)
    dikhao "Factorial of " + str(i) + " = " + str(result)
}
khatam
```

## Common Patterns

### Loop over list

```desilang
chalao i se 0 tak length(mylist) {
    dikhao mylist[i]
}
```

### Find maximum

```desilang
max_val = max(list)
```

### Check even/odd

```desilang
agar num % 2 == 0 {
    dikhao "Even"
} warna {
    dikhao "Odd"
} bas
```

### String concatenation

```desilang
result = "Hello" + " " + "World"
```

### Type conversion

```desilang
num_str = str(42)       // "42"
num = int("42")         // 42
```

## Operator Precedence (High to Low)

1. Parentheses `()`
2. Unary minus `-`
3. Multiply, Divide, Modulo `*`, `/`, `%`
4. Add, Subtract `+`, `-`
5. Comparison `>`, `<`, `>=`, `<=`, `==`, `!=`

## CLI Commands

```bash
# Run script
python -m desilang run script.dl

# Debug mode
python -m desilang run script.dl --debug

# Interactive REPL
python -m desilang repl

# Version
python -m desilang version

# Help
python -m desilang --help
```

---

**DesiLang v1.0.0** | Made with ❤️ for learning

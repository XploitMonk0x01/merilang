# OOP and Error Handling in DesiLang

## Table of Contents

1. [Object-Oriented Programming](#object-oriented-programming)
2. [Error Handling](#error-handling)
3. [Best Practices](#best-practices)
4. [Examples](#examples)

---

## Object-Oriented Programming

DesiLang supports full object-oriented programming with classes, inheritance, methods, and properties.

### Classes

#### Defining a Class

```desilang
class ClassName {
    vidhi __init__(parameters) {
        // Constructor code
        yeh.property = value
    }
    samapt

    vidhi method_name(parameters) {
        // Method code
    }
    samapt
}
```

**Keywords:**

- `class` - Declares a class
- `vidhi` - Defines a method (function inside class)
- `yeh` - Refers to current instance (like `this` in other languages)

#### Example:

```desilang
shuru

class Person {
    vidhi __init__(naam, umar) {
        yeh.naam = naam
        yeh.umar = umar
    }
    samapt

    vidhi greet() {
        dikhao "Hello, I am "
        dikhao yeh.naam
    }
    samapt
}

khatam
```

### Creating Objects

Use `naya` keyword to instantiate a class:

```desilang
person = naya Person("Rajesh", 25)
```

### Accessing Properties and Methods

```desilang
// Access property
dikhao person.naam

// Call method
person.greet()

// Modify property
person.umar = 26
```

### Constructor (`__init__`)

The special method `__init__` is called when creating a new object:

```desilang
class Car {
    vidhi __init__(brand, model, year) {
        yeh.brand = brand
        yeh.model = model
        yeh.year = year
    }
    samapt
}

car = naya Car("Maruti", "Swift", 2023)
```

### Inheritance

Use `badhaao` keyword to inherit from a parent class:

```desilang
class ParentClass {
    vidhi parent_method() {
        dikhao "Parent method"
    }
    samapt
}

class ChildClass badhaao ParentClass {
    vidhi child_method() {
        dikhao "Child method"
    }
    samapt
}

child = naya ChildClass()
child.parent_method()  // Inherited
child.child_method()    // Own method
```

### Super (Parent Method Calls)

Use `upar` to call parent class methods:

```desilang
class Animal {
    vidhi speak() {
        dikhao "Animal sound"
    }
    samapt
}

class Dog badhaao Animal {
    vidhi speak() {
        upar.speak()  // Call parent method
        dikhao "Woof!"
    }
    samapt
}

dog = naya Dog()
dog.speak()
// Output:
// Animal sound
// Woof!
```

### The `yeh` Keyword

`yeh` refers to the current instance and is used to:

- Access instance properties: `yeh.property`
- Call instance methods: `yeh.method()`
- Set properties: `yeh.property = value`

```desilang
class Counter {
    vidhi __init__() {
        yeh.count = 0
    }
    samapt

    vidhi increment() {
        yeh.count = yeh.count + 1
    }
    samapt

    vidhi get_count() {
        vapas yeh.count
    }
    samapt
}

c = naya Counter()
c.increment()
c.increment()
dikhao c.get_count()  // 2
```

### Method Return Values

Methods can return values using `vapas`:

```desilang
class Calculator {
    vidhi add(a, b) {
        vapas a + b
    }
    samapt

    vidhi multiply(a, b) {
        vapas a * b
    }
    samapt
}

calc = naya Calculator()
result = calc.add(5, 3)
dikhao result  // 8
```

### Complete OOP Example

```desilang
shuru

class BankAccount {
    vidhi __init__(account_no, name, balance) {
        yeh.account_no = account_no
        yeh.name = name
        yeh.balance = balance
    }
    samapt

    vidhi deposit(amount) {
        yeh.balance = yeh.balance + amount
        dikhao "Deposited: "
        dikhao amount
    }
    samapt

    vidhi withdraw(amount) {
        agar amount > yeh.balance {
            dikhao "Insufficient funds"
            vapas galat
        }
        bas

        yeh.balance = yeh.balance - amount
        dikhao "Withdrawn: "
        dikhao amount
        vapas sahi
    }
    samapt

    vidhi get_balance() {
        vapas yeh.balance
    }
    samapt
}

account = naya BankAccount("ACC001", "Rajesh", 10000)
account.deposit(5000)
account.withdraw(3000)
dikhao "Current balance: "
dikhao account.get_balance()

khatam
```

---

## Error Handling

DesiLang provides robust error handling with try-catch-finally blocks.

### Try-Catch-Finally

**Syntax:**

```desilang
koshish {
    // Code that might fail
}
pakdo variable_name {
    // Error handling code
}
akhir {
    // Always executes (optional)
}
```

**Keywords:**

- `koshish` - Try block (attempt)
- `pakdo` - Catch block (catch)
- `akhir` - Finally block (end/finally)
- `fenko` - Throw exception (throw)

### Basic Try-Catch

```desilang
shuru

koshish {
    x = 10 / 0  // This will fail
}
pakdo err {
    dikhao "Error occurred: "
    dikhao err
}

khatam
```

### Throwing Exceptions

Use `fenko` to throw custom exceptions:

```desilang
vidhi validate_age(age) {
    agar age < 0 {
        fenko "Age cannot be negative"
    }
    bas

    agar age > 150 {
        fenko "Invalid age"
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
```

### Catching Specific Errors

The catch block receives the error message as a variable:

```desilang
koshish {
    result = 10 / 0
}
pakdo error_message {
    dikhao "Caught error: "
    dikhao error_message
}
```

### Finally Block

The `akhir` (finally) block always executes, regardless of whether an error occurred:

```desilang
file_open = galat

koshish {
    file_open = sahi
    dikhao "Processing file..."
    fenko "File error"
}
pakdo err {
    dikhao "Error: "
    dikhao err
}
akhir {
    agar file_open {
        dikhao "Closing file"
    }
    bas
}
```

### Nested Try-Catch

```desilang
koshish {
    dikhao "Outer try"

    koshish {
        dikhao "Inner try"
        fenko "Inner error"
    }
    pakdo {
        dikhao "Inner catch"
    }

    fenko "Outer error"
}
pakdo {
    dikhao "Outer catch"
}
```

### Built-in Errors

DesiLang automatically throws errors for:

- **Division by zero**: `x / 0`
- **Index out of bounds**: `list[999]`
- **Type errors**: Invalid operations
- **Name errors**: Undefined variables
- **File I/O errors**: File operations

All these can be caught with try-catch:

```desilang
koshish {
    numbers = [1, 2, 3]
    dikhao numbers[10]  // Index error
}
pakdo err {
    dikhao "List index error: "
    dikhao err
}
```

### Error Handling with Functions

```desilang
vidhi divide(a, b) {
    koshish {
        vapas a / b
    }
    pakdo err {
        dikhao "Cannot divide: "
        dikhao err
        vapas 0
    }
}
samapt

result = divide(10, 0)  // Returns 0 instead of crashing
```

### Complete Error Handling Example

```desilang
shuru

vidhi safe_operation(operation, a, b) {
    koshish {
        agar operation == "add" {
            vapas a + b
        }
        bas

        agar operation == "divide" {
            agar b == 0 {
                fenko "Division by zero"
            }
            bas
            vapas a / b
        }
        bas

        fenko "Unknown operation"
    }
    pakdo err {
        dikhao "Operation failed: "
        dikhao err
        vapas 0
    }
}
samapt

// Test various operations
dikhao safe_operation("add", 5, 3)      // 8
dikhao safe_operation("divide", 10, 2)  // 5
dikhao safe_operation("divide", 10, 0)  // Error, returns 0
dikhao safe_operation("unknown", 1, 2)  // Error, returns 0

khatam
```

---

## Best Practices

### OOP Best Practices

1. **Use meaningful class names**: `Person`, `BankAccount`, `Vehicle`
2. **Initialize all properties in `__init__`**
3. **Use `yeh` for all instance properties and methods**
4. **Keep methods focused and small**
5. **Use inheritance for "is-a" relationships**
6. **Document what each method does**

### Error Handling Best Practices

1. **Catch specific errors when possible**
2. **Always clean up resources in `akhir` block**
3. **Provide meaningful error messages with `fenko`**
4. **Don't catch errors silently - at least log them**
5. **Validate input early**
6. **Use try-catch for external operations** (file I/O, user input)

### Combined OOP + Error Handling

```desilang
class SafeList {
    vidhi __init__() {
        yeh.items = []
    }
    samapt

    vidhi add(item) {
        koshish {
            length(yeh.items)  // Validate it's a list
            append(yeh.items, item)
            vapas sahi
        }
        pakdo err {
            dikhao "Failed to add item"
            vapas galat
        }
    }
    samapt

    vidhi get(index) {
        koshish {
            vapas yeh.items[index]
        }
        pakdo {
            dikhao "Index out of bounds"
            vapas 0
        }
    }
    samapt
}
```

---

## Examples

See the following example files for complete demonstrations:

1. **`11_basic_class.dl`** - Basic class definition and usage
2. **`12_inheritance.dl`** - Inheritance with `badhaao` and `upar`
3. **`13_bank_account.dl`** - Real-world OOP example
4. **`14_error_handling.dl`** - Try-catch-finally patterns
5. **`15_complete_oop_errors.dl`** - Combined OOP and error handling

---

## Quick Reference

### OOP Keywords

| Keyword   | Purpose             | Example                      |
| --------- | ------------------- | ---------------------------- |
| `class`   | Define a class      | `class Person { }`           |
| `naya`    | Create instance     | `p = naya Person()`          |
| `yeh`     | Current instance    | `yeh.name = "Raj"`           |
| `badhaao` | Inherit from parent | `class Child badhaao Parent` |
| `upar`    | Call parent method  | `upar.method()`              |
| `vidhi`   | Define method       | `vidhi greet() { }`          |

### Error Handling Keywords

| Keyword   | Purpose         | Example             |
| --------- | --------------- | ------------------- |
| `koshish` | Try block       | `koshish { code }`  |
| `pakdo`   | Catch block     | `pakdo err { }`     |
| `akhir`   | Finally block   | `akhir { cleanup }` |
| `fenko`   | Throw exception | `fenko "error"`     |

---

**DesiLang** now supports full object-oriented programming with robust error handling! 🎉

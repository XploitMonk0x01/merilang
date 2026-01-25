# DesiLang Tutorial - Learn Programming in Hindustani

Welcome to DesiLang! This tutorial will teach you programming using Hindustani keywords.

---

## Chapter 1: Getting Started

### Your First Program

Let's start with the classic "Hello World":

```desilang
likho("Hello, World!")
```

**What this does:**

- `likho()` means "print" - it displays text on screen
- Text goes inside quotes: `"Hello, World!"`

**Try it**: Save as `hello.meri` and run:

```bash
python -m desilang hello.meri
```

---

## Chapter 2: Variables

### Storing Values

Variables store data you can use later:

```desilang
maan name = "Ahmed"
maan age = 25
maan city = "Delhi"

likho(name)
likho(age)
```

**Keywords:**

- `maan` = "let" (declare a variable)
- Variable names can be anything: `name`, `age`, `myNumber`

### Numbers

```desilang
maan score = 100
maan price = 49.99
maan total = score + price

likho(total)  // Outputs: 149.99
```

**Number types:**

- **Integers**: `42`, `100`, `-5`
- **Floats**: `3.14`, `49.99`, `0.5`

### Strings

```desilang
maan greeting = "Namaste"
maan farewell = "Khuda Hafiz"
maan full = greeting + " aur " + farewell

likho(full)  // Outputs: Namaste aur Khuda Hafiz
```

**String operations:**

- **Concatenate**: `"Hello" + " " + "World"`
- **Length**: `lambai("Hello")` → `5`

---

## Chapter 3: Math Operations

### Arithmetic

```desilang
maan a = 10
maan b = 3

likho(a + b)   // Addition: 13
likho(a - b)   // Subtraction: 7
likho(a * b)   // Multiplication: 30
likho(a / b)   // Division: 3.333...
likho(a % b)   // Modulo (remainder): 1
```

### Comparison

```desilang
maan x = 10
maan y = 20

likho(x == y)  // Equal: jhoot (false)
likho(x != y)  // Not equal: sach (true)
likho(x < y)   // Less than: sach
likho(x > y)   // Greater than: jhoot
likho(x <= y)  // Less or equal: sach
likho(x >= y)  // Greater or equal: jhoot
```

### Parentheses for Order

```desilang
maan result = (2 + 3) * 4
likho(result)  // 20, not 14!
```

---

## Chapter 4: Control Flow

### If Statements

```desilang
maan temperature = 35

agar temperature > 30 {
    likho("It's hot outside!")
}
```

**Keywords:**

- `agar` = "if"
- Condition goes after `agar`
- Code inside `{ }` runs if condition is `sach` (true)

### If-Else

```desilang
maan age = 18

agar age >= 18 {
    likho("You can vote")
} warna {
    likho("Too young to vote")
}
```

**Keywords:**

- `warna` = "else"
- Runs if condition is `jhoot` (false)

### Multiple Conditions

```desilang
maan score = 75

agar score >= 90 {
    likho("Grade: A")
} agarlena score >= 75 {
    likho("Grade: B")
} agarlena score >= 60 {
    likho("Grade: C")
} warna {
    likho("Grade: F")
}
```

**Keywords:**

- `agarlena` = "else if"
- Checks conditions in order

---

## Chapter 5: Loops

### While Loop

```desilang
maan count = 1

jab_tak count <= 5 {
    likho(count)
    count = count + 1
}

// Outputs: 1, 2, 3, 4, 5
```

**Keywords:**

- `jab_tak` = "while" (while/as long as)
- Loop continues while condition is `sach`

### For Loop (Iteration)

```desilang
maan fruits = ["Apple", "Banana", "Mango"]

bar_bar fruit in fruits {
    likho(fruit)
}

// Outputs:
// Apple
// Banana
// Mango
```

**Keywords:**

- `bar_bar` = "for each" (iterate/repeat)
- `in` = iterate over a list

### Break and Continue

```desilang
maan i = 0

jab_tak i < 10 {
    i = i + 1

    agar i == 5 {
        age_badho  // Skip 5
    }

    agar i == 8 {
        ruk  // Stop at 8
    }

    likho(i)
}

// Outputs: 1, 2, 3, 4, 6, 7
```

**Keywords:**

- `ruk` = "break" (stop loop)
- `age_badho` = "continue" (skip to next iteration)

---

## Chapter 6: Lists

### Creating Lists

```desilang
maan numbers = [1, 2, 3, 4, 5]
maan names = ["Ali", "Sara", "Ahmed"]
maan mixed = [1, "hello", 3.14, sach]

likho(numbers)
```

### Accessing Elements

```desilang
maan fruits = ["Apple", "Banana", "Mango"]

likho(fruits[0])  // First: Apple
likho(fruits[1])  // Second: Banana
likho(fruits[2])  // Third: Mango
```

**Note**: Lists start at index 0!

### Modifying Lists

```desilang
maan numbers = [1, 2, 3]

numbers[1] = 99      // Change second element
likho(numbers)       // [1, 99, 3]

jodo(numbers, 4)     // Append 4
likho(numbers)       // [1, 99, 3, 4]

maan removed = nikalo(numbers)  // Remove last
likho(removed)       // 4
likho(numbers)       // [1, 99, 3]
```

**Built-in functions:**

- `jodo(list, item)` = append
- `nikalo(list)` = pop (remove last)
- `lambai(list)` = length

---

## Chapter 7: Functions

### Defining Functions

```desilang
kaam greet(name) {
    likho("Hello, " + name + "!")
}

greet("Ahmed")
greet("Sara")

// Outputs:
// Hello, Ahmed!
// Hello, Sara!
```

**Keywords:**

- `kaam` = "function" (work/task)
- `wapas` = "return"

### Functions with Return

```desilang
kaam add(a, b) {
    wapas a + b
}

maan result = add(5, 3)
likho(result)  // 8
```

### Multiple Parameters

```desilang
kaam describe_person(name, age, city) {
    likho(name + " is " + ank(age) + " years old")
    likho("Lives in " + city)
}

describe_person("Ahmed", 25, "Karachi")
```

### Recursion

```desilang
kaam factorial(n) {
    agar n <= 1 {
        wapas 1
    }
    wapas n * factorial(n - 1)
}

likho(factorial(5))  // 120
```

---

## Chapter 8: Lambdas (Anonymous Functions)

### Simple Lambdas

```desilang
maan double = lambada x: x * 2

likho(double(5))   // 10
likho(double(21))  // 42
```

**Keywords:**

- `lambada` = "lambda" (anonymous function)
- Syntax: `lambada parameters: expression`

### Multiple Parameters

```desilang
maan add = lambada a, b: a + b
maan multiply = lambada x, y: x * y

likho(add(3, 7))       // 10
likho(multiply(4, 5))  // 20
```

### Using with Lists

```desilang
maan numbers = [1, 2, 3, 4, 5]
maan square = lambada x: x * x

// Manually apply to each
bar_bar num in numbers {
    likho(square(num))
}

// Outputs: 1, 4, 9, 16, 25
```

---

## Chapter 9: Dictionaries

### Creating Dictionaries

```desilang
maan person = {
    "name": "Ahmed",
    "age": 25,
    "city": "Delhi"
}

likho(person)
```

### Accessing Values

```desilang
maan person = {"name": "Sara", "age": 22}

likho(person["name"])  // Sara
likho(person["age"])   // 22
```

### Modifying Dictionaries

```desilang
maan scores = {"math": 85, "science": 90}

// Add or update
scores["english"] = 88
scores["math"] = 92

likho(scores)
// {"math": 92, "science": 90, "english": 88}
```

### Dictionary Functions

```desilang
maan data = {"a": 1, "b": 2, "c": 3}

maan keys = kunji(data)       // Get keys
maan values = mul(data)       // Get values

likho(keys)    // ["a", "b", "c"]
likho(values)  // [1, 2, 3]
```

**Built-in functions:**

- `kunji(dict)` = keys
- `mul(dict)` = values

---

## Chapter 10: Object-Oriented Programming

### Defining Classes

```desilang
class Person {
    kaam __init__(name, age) {
        yeh.name = name
        yeh.age = age
    }

    kaam greet() {
        likho("Hello, I'm " + yeh.name)
    }
}

maan person = naya Person("Ahmed", 25)
person.greet()
```

**Keywords:**

- `class` = class definition
- `naya` = "new" (create object)
- `yeh` = "this/self"
- `__init__` = constructor

### Properties and Methods

```desilang
class Student {
    kaam __init__(name, grade) {
        yeh.name = name
        yeh.grade = grade
    }

    kaam display_info() {
        likho("Name: " + yeh.name)
        likho("Grade: " + ank(yeh.grade))
    }
}

maan student = naya Student("Sara", 85)
student.display_info()
```

### Inheritance

```desilang
class Animal {
    kaam __init__(name) {
        yeh.name = name
    }

    kaam speak() {
        likho(yeh.name + " makes a sound")
    }
}

class Dog badhaao Animal {
    kaam speak() {
        likho(yeh.name + " barks!")
    }
}

maan dog = naya Dog("Buddy")
dog.speak()  // Buddy barks!
```

**Keywords:**

- `badhaao` = "extends" (inheritance)
- `upar` = "super" (parent class)

---

## Chapter 11: Error Handling

### Try-Catch

```desilang
koshish {
    maan result = 10 / 0
} pakdo error {
    likho("Error: " + error)
}
```

**Keywords:**

- `koshish` = "try" (attempt)
- `pakdo` = "catch"
- `fenko` = "throw"
- `akhir` = "finally"

### Throwing Errors

```desilang
kaam divide(a, b) {
    agar b == 0 {
        fenko "Cannot divide by zero!"
    }
    wapas a / b
}

koshish {
    maan result = divide(10, 0)
} pakdo error {
    likho("Error occurred: " + error)
}
```

### Finally Block

```desilang
koshish {
    likho("Trying something risky...")
    maan result = 10 / 2
} pakdo error {
    likho("Error: " + error)
} akhir {
    likho("This always runs!")
}
```

---

## Chapter 12: Built-in Functions

### Type Conversion

```desilang
maan text = "123"
maan number = ank(text)      // String to int
maan decimal = dashamlav("3.14")  // String to float
maan str = shabd(42)         // Number to string

likho(prakar(number))   // "int"
likho(prakar(decimal))  // "float"
```

**Functions:**

- `ank()` = int (convert to integer)
- `dashamlav()` = float (convert to float)
- `shabd()` = str (convert to string)
- `prakar()` = type (get type name)

### List Functions

```desilang
maan numbers = [5, 2, 8, 1, 9]

likho(lambai(numbers))   // Length: 5
likho(nyuntam(numbers))  // Min: 1
likho(adhiktam(numbers)) // Max: 9
likho(yog(numbers))      // Sum: 25
```

**Functions:**

- `lambai()` = len (length)
- `nyuntam()` = min (minimum)
- `adhiktam()` = max (maximum)
- `yog()` = sum (total)
- `nirpeksha()` = abs (absolute value)

### Range

```desilang
maan nums = disha(5)       // [0, 1, 2, 3, 4]
maan range1 = disha(2, 6)  // [2, 3, 4, 5]

bar_bar i in disha(1, 4) {
    likho(i)
}
// Outputs: 1, 2, 3
```

---

## Chapter 13: Complete Examples

### Example 1: FizzBuzz

```desilang
bar_bar i in disha(1, 21) {
    agar i % 15 == 0 {
        likho("FizzBuzz")
    } agarlena i % 3 == 0 {
        likho("Fizz")
    } agarlena i % 5 == 0 {
        likho("Buzz")
    } warna {
        likho(i)
    }
}
```

### Example 2: Fibonacci

```desilang
kaam fibonacci(n) {
    agar n <= 1 {
        wapas n
    }
    wapas fibonacci(n - 1) + fibonacci(n - 2)
}

bar_bar i in disha(10) {
    likho(fibonacci(i))
}
```

### Example 3: Prime Numbers

```desilang
kaam is_prime(n) {
    agar n < 2 {
        wapas jhoot
    }

    bar_bar i in disha(2, n) {
        agar n % i == 0 {
            wapas jhoot
        }
    }

    wapas sach
}

bar_bar num in disha(2, 20) {
    agar is_prime(num) {
        likho(num)
    }
}
```

### Example 4: Student Grade Calculator

```desilang
class Student {
    kaam __init__(name, scores) {
        yeh.name = name
        yeh.scores = scores
    }

    kaam average() {
        maan total = yog(yeh.scores)
        maan count = lambai(yeh.scores)
        wapas total / count
    }

    kaam grade() {
        maan avg = yeh.average()

        agar avg >= 90 {
            wapas "A"
        } agarlena avg >= 80 {
            wapas "B"
        } agarlena avg >= 70 {
            wapas "C"
        } agarlena avg >= 60 {
            wapas "D"
        } warna {
            wapas "F"
        }
    }

    kaam display() {
        likho("Student: " + yeh.name)
        likho("Average: " + shabd(yeh.average()))
        likho("Grade: " + yeh.grade())
    }
}

maan student = naya Student("Ahmed", [85, 90, 78, 92])
student.display()
```

---

## Quick Reference

### Keywords

| Hindustani  | English   | Usage               |
| ----------- | --------- | ------------------- |
| `maan`      | let/const | Declare variable    |
| `likho`     | print     | Display output      |
| `agar`      | if        | Conditional         |
| `warna`     | else      | Alternative         |
| `agarlena`  | else if   | Multiple conditions |
| `jab_tak`   | while     | Loop while true     |
| `bar_bar`   | for each  | Iterate over list   |
| `ruk`       | break     | Exit loop           |
| `age_badho` | continue  | Skip iteration      |
| `kaam`      | function  | Define function     |
| `wapas`     | return    | Return value        |
| `lambada`   | lambda    | Anonymous function  |
| `class`     | class     | Define class        |
| `naya`      | new       | Create object       |
| `yeh`       | this/self | Current object      |
| `badhaao`   | extends   | Inheritance         |
| `upar`      | super     | Parent class        |
| `koshish`   | try       | Try block           |
| `pakdo`     | catch     | Catch error         |
| `fenko`     | throw     | Throw error         |
| `akhir`     | finally   | Finally block       |
| `sach`      | true      | Boolean true        |
| `jhoot`     | false     | Boolean false       |
| `aur`       | and       | Logical AND         |
| `ya`        | or        | Logical OR          |
| `nahi`      | not       | Logical NOT         |

### Built-in Functions

| Function      | Purpose     | Example                    |
| ------------- | ----------- | -------------------------- |
| `lambai()`    | Length      | `lambai([1,2,3])` → 3      |
| `yog()`       | Sum         | `yog([1,2,3])` → 6         |
| `nyuntam()`   | Min         | `nyuntam([3,1,2])` → 1     |
| `adhiktam()`  | Max         | `adhiktam([3,1,2])` → 3    |
| `ank()`       | To int      | `ank("42")` → 42           |
| `dashamlav()` | To float    | `dashamlav("3.14")` → 3.14 |
| `shabd()`     | To string   | `shabd(42)` → "42"         |
| `prakar()`    | Type        | `prakar(42)` → "int"       |
| `disha()`     | Range       | `disha(5)` → [0,1,2,3,4]   |
| `jodo()`      | Append      | `jodo(list, item)`         |
| `nikalo()`    | Pop         | `nikalo(list)`             |
| `kunji()`     | Dict keys   | `kunji(dict)`              |
| `mul()`       | Dict values | `mul(dict)`                |
| `nirpeksha()` | Absolute    | `nirpeksha(-5)` → 5        |

---

## Next Steps

Now that you've learned DesiLang basics:

1. **Practice**: Write your own programs
2. **Experiment**: Try combining different features
3. **Build**: Create real projects (calculator, game, etc.)
4. **Share**: Help others learn!

**Happy coding! / Khush Coding!** 🚀

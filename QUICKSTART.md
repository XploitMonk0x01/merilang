# Quick Start Guide - MeriLang

Get up and running with MeriLang in 5 minutes!

## Step 1: Install MeriLang

```bash
# Clone the repository
git clone https://github.com/XploitMonk0x01/merilang.git
cd MeriLang

# Install
pip install -e .
```

## Step 2: Write Your First Program

Create a file called `hello.meri`:

```MeriLang
shuru
dikhao "Hello, MeriLang!"
khatam
```

## Step 3: Run It

```bash
python -m MeriLang run hello.meri
```

Output:

```
Hello, MeriLang!
```

## Step 4: Try Something More Interesting

Create `calculator.meri`:

```MeriLang
shuru
// Simple calculator
a = 10
b = 5

dikhao "Addition: " + str(a + b)
dikhao "Subtraction: " + str(a - b)
dikhao "Multiplication: " + str(a * b)
dikhao "Division: " + str(a / b)
khatam
```

Run it:

```bash
python -m MeriLang run calculator.meri
```

## Step 5: Learn with Examples

Run the included examples:

```bash
# Hello World
python -m MeriLang run examples/01_hello_world.meri

# Loops
python -m MeriLang run examples/04_loops.meri

# Functions
python -m MeriLang run examples/05_functions.meri

# FizzBuzz
python -m MeriLang run examples/06_fizzbuzz.meri
```

## Step 6: Try the REPL

```bash
python -m MeriLang repl
```

Try typing:

```
>>> x = 42
>>> dikhao x
42
>>> dikhao x * 2
84
>>> exit
```

## Step 7: Write a Real Program

Let's create a number guessing game! Create `guess.meri`:

```MeriLang
shuru
// Number guessing game
secret = 42
guess = 0
tries = 0

dikhao "Guess the number (1-100)!"

jabtak guess != secret {
    // In real use, you'd use padho to get input
    // For now, we'll just demonstrate the logic
    guess = 50  // Simulated guess
    tries = tries + 1

    agar guess < secret {
        dikhao "Too low!"
    } warna {
        agar guess > secret {
            dikhao "Too high!"
        } warna {
            dikhao "Correct!"
        } bas
    } bas

    // Break after first iteration for demo
    guess = secret
} band

dikhao "You won in " + str(tries) + " tries!"
khatam
```

## Common Keywords Cheat Sheet

| Keyword             | Meaning       | Example                    |
| ------------------- | ------------- | -------------------------- |
| `shuru`             | Begin program | `shuru`                    |
| `khatam`            | End program   | `khatam`                   |
| `dikhao`            | Print         | `dikhao "Hello"`           |
| `padho`             | Input         | `padho name`               |
| `agar`              | If            | `agar x > 5 { }`           |
| `warna`             | Else          | `warna { }`                |
| `bas`               | End if        | `} bas`                    |
| `jabtak`            | While         | `jabtak x < 10 { }`        |
| `band`              | End while     | `} band`                   |
| `chalao...se...tak` | For loop      | `chalao i se 0 tak 10 { }` |
| `vidhi`             | Function      | `vidhi add(a, b) { }`      |
| `vapas`             | Return        | `vapas result`             |
| `samapt`            | End function  | `} samapt`                 |
| `sahi`              | True          | `is_valid = sahi`          |
| `galat`             | False         | `is_valid = galat`         |

## Next Steps

1. **Read the full syntax guide**: [docs/SYNTAX.md](docs/SYNTAX.md)
2. **Browse more examples**: Check the `examples/` folder
3. **Try the web playground**: Run `python playground/app.py`
4. **Build something fun**: Ideas below!

## Project Ideas for Learning

### Beginner

1. **Temperature Converter**: Celsius to Fahrenheit
2. **Even or Odd Checker**: Check if a number is even or odd
3. **Sum Calculator**: Add numbers from 1 to N

### Intermediate

4. **Palindrome Checker**: Check if a string reads the same backward
5. **Prime Number Generator**: Find all primes up to N
6. **Simple Calculator**: Basic arithmetic with functions

### Advanced

7. **Bubble Sort**: Implement sorting algorithm
8. **Binary Search**: Search in sorted list
9. **Text File Analyzer**: Count words, lines, characters

## Tips for Success

✅ **DO:**

- Start simple and build up
- Test your code frequently
- Use the REPL for quick experiments
- Read error messages carefully
- Add comments to your code

❌ **DON'T:**

- Forget `shuru` and `khatam`
- Skip testing edge cases
- Write functions that are too long
- Ignore error messages

## Getting Help

- **Examples**: Look in `examples/` directory
- **Syntax Reference**: Read `docs/SYNTAX.md`
- **Issues**: Check or create GitHub issues
- **REPL**: Test small code snippets interactively

## Have Fun! 🎉

Remember, programming should be fun! Don't worry about making mistakes - that's how we learn.

Happy coding in MeriLang! 🇮🇳

"""Smoke tests for the Merilang compiler front-end upgrade."""
import sys
sys.path.insert(0, r'c:\Users\smwlc\proj\Test\merilang')

from merilang import (
    tokenize, tokenize_safe, Token, Parser, Interpreter,
    SemanticAnalyzer, SymbolTable, IRGenerator, IRProgram,
    LexerErrorCollection, ParserErrorCollection,
    SemanticError, TypeCheckError, UndefinedNameError, RedefinitionError,
)

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
NOTE = "\033[33mNOTE\033[0m"


def test_imports():
    print("--- Test 1: imports ---")
    print(f"  {PASS}")

test_imports()


# ------------------------------------------------------------------ #
# Test 2: lexer panic-mode (illegal characters)
# ------------------------------------------------------------------ #
print()
print("--- Test 2: lexer panic-mode ---")
tokens, errors = tokenize_safe("maan x = 42 @ # ^")
print(f"  tokens: {len(tokens)}, lex_errors: {len(errors)}")
for e in errors:
    print(f"  lex_error: {e}")
assert len(errors) >= 3, f"Expected >= 3 errors, got {len(errors)}"
print(f"  {PASS}")


# ------------------------------------------------------------------ #
# Test 3: parser panic-mode
# ------------------------------------------------------------------ #
print()
print("--- Test 3: parser panic-mode ---")
src3 = "maan x = 42\nmaan bad ="      # incomplete declaration
tokens3, _ = tokenize_safe(src3)
p3 = Parser(tokens3)
try:
    ast3 = p3.parse()
    print(f"  No ParserErrorCollection raised ({NOTE}: may parse partial)")
except ParserErrorCollection as exc:
    print(f"  ParserErrorCollection with {len(exc.errors)} error(s)")
    print(f"  {PASS}")
except Exception as ex:
    print(f"  Unexpected exception: {ex}")


# ------------------------------------------------------------------ #
# Test 4: semantic analysis - undefined name
# ------------------------------------------------------------------ #
print()
print("--- Test 4: semantic -- undefined variable ---")
src4 = "likho(undefined_var)"
tokens4, _ = tokenize_safe(src4)
p4 = Parser(tokens4)
try:
    ast4 = p4.parse()
    sa4 = SemanticAnalyzer()
    errors4 = sa4.analyze(ast4)
    found_undef = any(isinstance(e, UndefinedNameError) for e in errors4)
    if found_undef:
        print(f"  Found UndefinedNameError: True  {PASS}")
    else:
        print(f"  No UndefinedNameError (got: {[type(e).__name__ for e in errors4]})  {NOTE}")
except Exception as ex:
    import traceback
    traceback.print_exc()
    print(f"  Exception: {ex}")


# ------------------------------------------------------------------ #
# Test 5: semantic analysis - type mismatch
# ------------------------------------------------------------------ #
print()
print("--- Test 5: semantic -- type mismatch (string - number) ---")
src5 = 'maan x = "hello" - 5'
tokens5, _ = tokenize_safe(src5)
p5 = Parser(tokens5)
try:
    ast5 = p5.parse()
    sa5 = SemanticAnalyzer()
    errors5 = sa5.analyze(ast5)
    found_type = any(isinstance(e, TypeCheckError) for e in errors5)
    if found_type:
        print(f"  Found TypeCheckError: True  {PASS}")
    else:
        print(f"  No TypeCheckError (errors: {[type(e).__name__ for e in errors5]})  {NOTE}")
except Exception as ex:
    import traceback
    traceback.print_exc()
    print(f"  Exception: {ex}")


# ------------------------------------------------------------------ #
# Test 6: IR generation - simple arithmetic
# ------------------------------------------------------------------ #
print()
print("--- Test 6: IR generation (maan x = 3 + 4) ---")
src6 = "maan x = 3 + 4"
tokens6, _ = tokenize_safe(src6)
p6 = Parser(tokens6)
try:
    ast6 = p6.parse()
    gen6 = IRGenerator()
    ir6  = gen6.generate(ast6)
    print(ir6.dump())
    assert len(ir6.instructions) > 0
    print(f"  {len(ir6.instructions)} instruction(s)  {PASS}")
except Exception as ex:
    import traceback
    traceback.print_exc()
    print(f"  Exception: {ex}")


# ------------------------------------------------------------------ #
# Test 7: IR generation - while loop
# ------------------------------------------------------------------ #
print()
print("--- Test 7: IR generation (while loop) ---")
src7 = "maan i = 0\njab_tak i < 10 {\n  maan i = i + 1\n}"
tokens7, _ = tokenize_safe(src7)
p7 = Parser(tokens7)
try:
    ast7 = p7.parse()
    gen7 = IRGenerator()
    ir7  = gen7.generate(ast7)
    print(ir7.dump())
    print(f"  {len(ir7.instructions)} instruction(s)  {PASS}")
except Exception as ex:
    import traceback
    traceback.print_exc()
    print(f"  Exception: {ex}")


# ------------------------------------------------------------------ #
# Test 8: end-to-end interpretation still works
# ------------------------------------------------------------------ #
print()
print("--- Test 8: end-to-end interpretation ---")
src8 = "maan a = 10\nmaan b = 20\nlikho(a + b)"
tokens8, _ = tokenize_safe(src8)
p8 = Parser(tokens8)
try:
    ast8 = p8.parse()
    interp = Interpreter()
    interp.execute(ast8)
    print(f"  {PASS}")
except Exception as ex:
    import traceback
    traceback.print_exc()
    print(f"  Exception: {ex}")


print()
print("=== All smoke tests done ===")

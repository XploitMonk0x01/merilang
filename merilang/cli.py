"""
Command-line interface for Merilang.

Pipeline:
    Source → Lexer (panic-mode) → Parser (panic-mode) → SemanticAnalyzer → [IRGenerator] → Interpreter
"""

import argparse
import sys
import os
from pathlib import Path

try:
    from termcolor import colored
except ImportError:
    def colored(text, color=None, on_color=None, attrs=None):
        return text

from . import __version__
from .lexer_enhanced import tokenize_safe
from .parser_enhanced import Parser
from .interpreter_enhanced import Interpreter
from .semantic_analyzer import SemanticAnalyzer
from .ir_generator import IRGenerator
from .errors_enhanced import (
    MeriLangError,
    LexerErrorCollection,
    ParserErrorCollection,
    SemanticError,
    ErrorLanguage,
)
from .ast_nodes_enhanced import AssignmentNode, PrintNode


# ---------------------------------------------------------------------------
# Error printer
# ---------------------------------------------------------------------------

def _print_banner(title: str, colour: str = "cyan") -> None:
    print(colored(f"\n=== {title} ===", colour))


def _print_desi_error(err: MeriLangError, label: str = "Error") -> None:
    """Pretty-print any DesiLangError (or subclass) to stderr."""
    kind = err.__class__.__name__
    print(colored(f"\n[{label}] {kind}: {err.format_message()}", "red", attrs=["bold"]),
          file=sys.stderr)


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

def _run_pipeline(
    code: str,
    *,
    filepath: str = "<stdin>",
    debug: bool = False,
    run_semantic: bool = True,
    emit_ir: bool = False,
    error_language: ErrorLanguage = ErrorLanguage.ENGLISH,
    interpreter: "Interpreter | None" = None,
) -> int:
    """Execute the full compiler front-end + interpreter pipeline.

    Args:
        code:         Source code string.
        filepath:     Display name used in error messages.
        debug:        Print tokens and AST.
        run_semantic: Run the SemanticAnalyzer pass.
        emit_ir:      Dump the IR listing before execution.
        error_language: Language for bilingual error messages.
        interpreter:  Pre-created Interpreter instance (used by REPL to share state).

    Returns:
        Exit code (0 = success, 1 = error).
    """
    # ------------------------------------------------------------------ #
    # Phase 1 – Lexing (panic-mode)
    # ------------------------------------------------------------------ #
    if debug:
        _print_banner("Tokenizing")

    tokens, lex_errors = tokenize_safe(code)

    if debug:
        for tok in tokens:
            print(f"  {tok}")

    if lex_errors:
        for le in lex_errors:
            print(colored(f"\n[LexerError] {le}", "red", attrs=["bold"]), file=sys.stderr)
        # Lex errors are non-fatal for the pipeline (tokens up to the bad char
        # are still valid).  Surface them but continue.

    # ------------------------------------------------------------------ #
    # Phase 2 – Parsing (panic-mode)
    # ------------------------------------------------------------------ #
    if debug:
        _print_banner("Parsing")

    try:
        parser = Parser(tokens, error_language=error_language)
        ast = parser.parse()
    except ParserErrorCollection as exc:
        for pe in exc.errors:
            print(colored(f"\n[ParseError] {pe}", "red", attrs=["bold"]), file=sys.stderr)
        return 1

    if debug:
        print(colored(f"\nAST:\n{ast}", "yellow"))

    # ------------------------------------------------------------------ #
    # Phase 3 – Semantic Analysis
    # ------------------------------------------------------------------ #
    if run_semantic:
        if debug:
            _print_banner("Semantic Analysis")

        analyzer = SemanticAnalyzer()
        sem_errors = analyzer.analyze(ast)

        if sem_errors:
            for se in sem_errors:
                print(colored(f"\n[SemanticError] {se}", "red", attrs=["bold"]),
                      file=sys.stderr)
            return 1

        if debug:
            print(colored("  Semantic analysis passed.", "green"))

    # ------------------------------------------------------------------ #
    # Phase 4 – IR Generation (optional)
    # ------------------------------------------------------------------ #
    if emit_ir:
        _print_banner("Intermediate Representation (3AC)", "magenta")
        gen = IRGenerator()
        ir  = gen.generate(ast)
        print(ir.dump())
        print()   # blank line before execution output

    # ------------------------------------------------------------------ #
    # Phase 5 – Interpretation
    # ------------------------------------------------------------------ #
    if debug:
        _print_banner("Executing")

    if interpreter is None:
        interpreter = Interpreter()

    try:
        interpreter.execute(ast)
    except MeriLangError as exc:
        _print_desi_error(exc, label="RuntimeError")
        return 1

    return 0


# ---------------------------------------------------------------------------
# File runner
# ---------------------------------------------------------------------------

def run_file(
    filepath: str,
    *,
    debug: bool = False,
    semantic: bool = True,
    emit_ir: bool = False,
) -> int:
    """Run a Merilang source file end-to-end.

    Args:
        filepath: Path to a ``.meri`` (or any text) file.
        debug:    Enable verbose token / AST / section output.
        semantic: Run the semantic analysis pass (default True).
        emit_ir:  Print the IR listing before executing.

    Returns:
        Exit code.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            code = fh.read()
    except FileNotFoundError:
        print(colored(f"\nError: File not found: {filepath}", "red", attrs=["bold"]),
              file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(colored("\n\nExecution interrupted by user", "yellow"))
        return 130
    except Exception as exc:
        print(colored(f"\nInternal error reading file: {exc}", "red", attrs=["bold"]),
              file=sys.stderr)
        return 1

    try:
        return _run_pipeline(
            code,
            filepath=filepath,
            debug=debug,
            run_semantic=semantic,
            emit_ir=emit_ir,
        )
    except KeyboardInterrupt:
        print(colored("\n\nExecution interrupted by user", "yellow"))
        return 130
    except Exception as exc:   # pragma: no cover – unexpected internal error
        print(colored(f"\nInternal error: {exc}", "red", attrs=["bold"]), file=sys.stderr)
        if debug:
            import traceback
            traceback.print_exc()
        return 1


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

def run_repl(*, semantic: bool = True, emit_ir: bool = False) -> int:
    """Interactive Read-Eval-Print Loop.

    Maintains a single ``Interpreter`` instance across lines so variables
    declared in one session step are visible in subsequent ones.

    Args:
        semantic: Run semantic analysis before each statement.
        emit_ir:  Print IR for each statement.

    Returns:
        Exit code (always 0).
    """
    print(colored(f"Merilang v{__version__} Interactive REPL", "green", attrs=["bold"]))
    flags = []
    if semantic:
        flags.append("semantic-on")
    if emit_ir:
        flags.append("ir-on")
    if flags:
        print(colored(f"  [{', '.join(flags)}]", "cyan"))
    print(colored("Type 'niklo' or press Ctrl+C to quit\n", "cyan"))

    interpreter = Interpreter()

    while True:
        try:
            line = input(colored(">>> ", "blue", attrs=["bold"]))
        except (KeyboardInterrupt, EOFError):
            print(colored("\nAlvida! 👋", "green"))
            break

        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower() in {"niklo", "exit", "quit"}:
            print(colored("Alvida! 👋", "green"))
            break

        _run_pipeline(
            stripped,
            filepath="<repl>",
            debug=False,
            run_semantic=semantic,
            emit_ir=emit_ir,
            interpreter=interpreter,
        )

    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """Parse CLI arguments and dispatch to the appropriate action."""
    arg_parser = argparse.ArgumentParser(
        prog="merilang",
        description="Merilang – a desi-inspired programming language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  merilang run script.meri            Run a Merilang script
  merilang run script.meri --debug    Run with debug output (tokens + AST)
  merilang run script.meri --ir       Print 3AC IR before running
  merilang run script.meri --no-semantic  Skip semantic analysis
  merilang repl                       Start interactive REPL
  merilang repl --ir                  REPL with IR output
  merilang version                    Show version information
        """,
    )

    arg_parser.add_argument("--version", action="version",
                            version=f"Merilang {__version__}")

    subparsers = arg_parser.add_subparsers(dest="command", help="Sub-command")

    # ---- run ----
    run_p = subparsers.add_parser("run", help="Run a Merilang script file")
    run_p.add_argument("file", help="Path to .meri script")
    run_p.add_argument("--debug", action="store_true",
                       help="Print tokens, AST, and section banners")
    run_p.add_argument("--ir", action="store_true",
                       help="Print Three-Address Code IR before executing")
    run_p.add_argument("--no-semantic", action="store_true",
                       help="Skip the semantic analysis pass (faster, less safe)")

    # ---- repl ----
    repl_p = subparsers.add_parser("repl", help="Start interactive REPL")
    repl_p.add_argument("--ir", action="store_true",
                        help="Show IR output for each evaluated expression")
    repl_p.add_argument("--no-semantic", action="store_true",
                        help="Skip semantic analysis in REPL")

    # ---- version ----
    subparsers.add_parser("version", help="Show version information")

    args = arg_parser.parse_args()

    if args.command == "run":
        return run_file(
            args.file,
            debug=args.debug,
            semantic=not args.no_semantic,
            emit_ir=args.ir,
        )

    if args.command == "repl":
        return run_repl(
            semantic=not args.no_semantic,
            emit_ir=args.ir,
        )

    if args.command == "version":
        print(f"Merilang {__version__}")
        print(f"Python {sys.version}")
        return 0

    # No command – show help.
    arg_parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

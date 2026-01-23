"""
Command-line interface for DesiLang interpreter.
"""

import argparse
import sys
import os
from pathlib import Path
try:
    from termcolor import colored
except ImportError:
    # Fallback if termcolor is not installed
    def colored(text, color=None, on_color=None, attrs=None):
        return text

from . import __version__
from .lexer import tokenize
from .parser import Parser
from .interpreter import Interpreter
from .errors import DesiLangError


def print_error(error: DesiLangError) -> None:
    """Print formatted error message."""
    error_type = error.__class__.__name__
    print(colored(f"\n{error_type}: {error.format_message()}", "red", attrs=["bold"]), file=sys.stderr)


def run_file(filepath: str, debug: bool = False) -> int:
    """Run a DesiLang file."""
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        if debug:
            print(colored("=== Tokenizing ===", "cyan"))
        
        # Tokenize
        tokens = tokenize(code)
        
        if debug:
            for token in tokens:
                print(token)
            print(colored("\n=== Parsing ===", "cyan"))
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        if debug:
            print(colored(f"\nAST: {ast}", "yellow"))
            print(colored("\n=== Executing ===", "cyan"))
        
        # Interpret
        interpreter = Interpreter(debug=debug)
        interpreter.execute(ast)
        
        return 0
    
    except DesiLangError as e:
        print_error(e)
        return 1
    except FileNotFoundError:
        print(colored(f"\nError: File not found: {filepath}", "red", attrs=["bold"]), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(colored("\n\nExecution interrupted by user", "yellow"))
        return 130
    except Exception as e:
        print(colored(f"\nInternal error: {str(e)}", "red", attrs=["bold"]), file=sys.stderr)
        if debug:
            import traceback
            traceback.print_exc()
        return 1


def run_repl() -> int:
    """Run interactive REPL."""
    print(colored(f"DesiLang v{__version__} Interactive REPL", "green", attrs=["bold"]))
    print(colored("Type 'exit' or press Ctrl+C to quit\n", "cyan"))
    
    interpreter = Interpreter()
    
    # REPL doesn't require shuru/khatam
    while True:
        try:
            # Read
            line = input(colored(">>> ", "blue", attrs=["bold"]))
            
            if line.strip().lower() in ['exit', 'quit']:
                print(colored("Alvida! 👋", "green"))
                break
            
            if not line.strip():
                continue
            
            # Wrap in program structure for parsing
            code = f"shuru\n{line}\nkhatam"
            
            # Evaluate
            try:
                tokens = tokenize(code)
                parser = Parser(tokens)
                ast = parser.parse()
                
                # Execute
                for stmt in ast.statements:
                    result = interpreter.visit(stmt)
                    # Print non-None expression results
                    if result is not None and not isinstance(stmt, (AssignmentNode, PrintNode)):
                        print(colored(f"=> {result}", "yellow"))
            
            except DesiLangError as e:
                print_error(e)
            except Exception as e:
                print(colored(f"Error: {str(e)}", "red"), file=sys.stderr)
        
        except KeyboardInterrupt:
            print(colored("\nAlvida! 👋", "green"))
            break
        except EOFError:
            print(colored("\nAlvida! 👋", "green"))
            break
    
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='desilang',
        description='DesiLang - A desi-inspired toy programming language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  desilang run script.dl                Run a DesiLang script
  desilang run script.dl --debug        Run with debug output
  desilang repl                         Start interactive REPL
  desilang version                      Show version information
  
For more information, visit: https://github.com/desilang/desilang
        """
    )
    
    parser.add_argument('--version', action='version', version=f'DesiLang {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a DesiLang script file')
    run_parser.add_argument('file', help='Path to DesiLang script file')
    run_parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    # REPL command
    repl_parser = subparsers.add_parser('repl', help='Start interactive REPL')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'run':
        return run_file(args.file, debug=args.debug)
    
    elif args.command == 'repl':
        return run_repl()
    
    elif args.command == 'version':
        print(f"DesiLang {__version__}")
        print(f"Python {sys.version}")
        return 0
    
    else:
        # No command provided, show help
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())

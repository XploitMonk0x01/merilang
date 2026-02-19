"""
Merilang – a desi-inspired programming language.

Version: 3.0.0 (Compiler Front-End)
Author:  Merilang Community
License: MIT
"""

__version__ = "3.0.0"
__author__  = "Merilang Community"

# ---------------------------------------------------------------------------
# Core pipeline (enhanced / canonical stack)
# ---------------------------------------------------------------------------
from .lexer_enhanced     import tokenize, tokenize_safe, Token
from .parser_enhanced    import Parser
from .interpreter_enhanced import Interpreter

# ---------------------------------------------------------------------------
# New compiler passes
# ---------------------------------------------------------------------------
from .symbol_table      import SymbolTable, Symbol, SymbolKind, MType
from .semantic_analyzer import SemanticAnalyzer
from .ir_nodes          import IRProgram
from .ir_generator      import IRGenerator

# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------
from .errors_enhanced import (
    MeriLangError, LexerError, ParserError,
    LexerErrorCollection, ParserErrorCollection,
    SemanticError, TypeCheckError, UndefinedNameError, RedefinitionError,
    ErrorLanguage,
)

__all__ = [
    # Lexer
    "tokenize", "tokenize_safe", "Token",
    # Parser
    "Parser",
    # Interpreter
    "Interpreter",
    # Semantic analysis
    "SemanticAnalyzer", "SymbolTable", "Symbol", "SymbolKind", "MType",
    # IR
    "IRGenerator", "IRProgram",
    # Errors
    "MeriLangError", "LexerError", "ParserError",
    "LexerErrorCollection", "ParserErrorCollection",
    "SemanticError", "TypeCheckError", "UndefinedNameError", "RedefinitionError",
    "ErrorLanguage",
    # Meta
    "__version__", "__author__",
]

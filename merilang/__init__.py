"""
Merilang – a desi-inspired programming language.

Version: 3.2.0 (Compiler Front-End)
Author:  Merilang Community
License: MIT
"""

__version__ = "3.2.0"
__author__  = "Merilang Community"

# ---------------------------------------------------------------------------
# Core pipeline (enhanced / canonical stack)
# ---------------------------------------------------------------------------
from .lexer_enhanced     import tokenize, tokenize_safe, Token
from .parser_enhanced    import Parser
from .interpreter_enhanced import (
    Interpreter,
    ActivationRecord,
    RuntimeStack,
    RuntimeHeap,
    HeapObject,
)

# ---------------------------------------------------------------------------
# New compiler passes
# ---------------------------------------------------------------------------
from .symbol_table      import SymbolTable, Symbol, SymbolKind, MType
from .semantic_analyzer import SemanticAnalyzer
from .ir_nodes          import IRProgram
from .ir_generator      import IRGenerator
from .ir_analysis       import BasicBlock, ControlFlowGraph, build_basic_blocks, build_cfg
from .ir_optimizer      import OptimizationReport, optimize_ir
from .ir_dag            import DAGNode, optimize_ir_with_dag
from .ir_ssa            import SSAReport, convert_to_ssa

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
    "Interpreter", "ActivationRecord", "RuntimeStack", "RuntimeHeap", "HeapObject",
    # Semantic analysis
    "SemanticAnalyzer", "SymbolTable", "Symbol", "SymbolKind", "MType",
    # IR
    "IRGenerator", "IRProgram",
    "BasicBlock", "ControlFlowGraph", "build_basic_blocks", "build_cfg",
    "OptimizationReport", "optimize_ir",
    "DAGNode", "optimize_ir_with_dag",
    "SSAReport", "convert_to_ssa",
    # Errors
    "MeriLangError", "LexerError", "ParserError",
    "LexerErrorCollection", "ParserErrorCollection",
    "SemanticError", "TypeCheckError", "UndefinedNameError", "RedefinitionError",
    "ErrorLanguage",
    # Meta
    "__version__", "__author__",
]

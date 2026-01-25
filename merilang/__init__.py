"""
DesiLang - A desi-inspired toy programming language interpreter.

Version: 1.0.0
Author: DesiLang Community
License: MIT
"""

__version__ = "1.0.0"
__author__ = "DesiLang Community"

from .lexer import tokenize, Token
from .parser import Parser
from .interpreter import Interpreter
from .errors import merilangError

__all__ = ["tokenize", "Token", "Parser", "Interpreter", "DesiLangError"]

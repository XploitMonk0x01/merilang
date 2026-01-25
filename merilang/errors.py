"""
Custom exception classes for DesiLang with helpful error messages.
"""

from typing import Optional


class DesiLangError(Exception):
    """Base exception for all DesiLang errors."""
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        """Format error message with line/column info."""
        if self.line is not None:
            location = f"Line {self.line}"
            if self.column is not None:
                location += f", Column {self.column}"
            return f"{location}: {self.message}"
        return self.message


class LexerError(DesiLangError):
    """Error during tokenization."""
    pass


class ParserError(DesiLangError):
    """Error during parsing."""
    pass


class RuntimeError(DesiLangError):
    """Error during interpretation/execution."""
    pass


class TypeError(RuntimeError):
    """Type mismatch error."""
    pass


class NameError(RuntimeError):
    """Undefined variable/function error."""
    pass


class DivisionByZeroError(RuntimeError):
    """Division by zero error."""
    pass


class IndexError(RuntimeError):
    """List index out of bounds."""
    pass


class FileIOError(RuntimeError):
    """File I/O operation error."""
    pass

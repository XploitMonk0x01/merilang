"""
Enhanced Lexer for DesiLang - Production version with regex optimization.

This module provides tokenization functionality for DesiLang source code,
converting text into a stream of tokens for the parser. Uses regex patterns
for efficient scanning and supports Unicode characters for Hindi/Urdu text.

Author: DesiLang Team
Version: 2.0
"""

import re
from typing import List, Optional, Tuple
from enum import Enum, auto
from dataclasses import dataclass
from .errors import LexerError


class TokenType(Enum):
    """Enumeration of all token types in DesiLang.
    
    This enum defines every possible token type that the lexer can produce,
    organized by category for clarity.
    """
    
    # Literals
    NUMBER = auto()         # 42, 3.14, -10
    STRING = auto()         # "hello", 'world'
    BOOLEAN = auto()        # sach (true), jhoot (false)
    
    # Identifiers and Keywords
    IDENTIFIER = auto()     # variable/function names
    
    # Keywords - Program Structure
    START = auto()          # shuru (begin)
    END = auto()            # khatam (end)
    
    # Keywords - I/O
    PRINT = auto()          # likho (print)
    INPUT = auto()          # padho (read/input)
    
    # Keywords - Variables
    LET = auto()            # maan (let/const)
    
    # Keywords - Control Flow
    IF = auto()             # agar (if)
    ELSE = auto()           # warna (else)
    ELSEIF = auto()         # agarlena (else if)
    WHILE = auto()          # jab_tak (while)
    FOR = auto()            # bar_bar (for)
    IN = auto()             # in (for iteration)
    BREAK = auto()          # ruk (break)
    CONTINUE = auto()       # age_badho (continue)
    
    # Keywords - Functions
    FUNCTION = auto()       # kaam (function/work)
    RETURN = auto()         # wapas (return)
    LAMBDA = auto()         # lambada (lambda/anonymous function)
    
    # Keywords - OOP
    CLASS = auto()          # class
    NEW = auto()            # naya (new)
    THIS = auto()           # yeh (this/self)
    EXTENDS = auto()        # badhaao (extends)
    SUPER = auto()          # upar (super)
    
    # Keywords - Error Handling
    TRY = auto()            # koshish (try/attempt)
    CATCH = auto()          # pakdo (catch)
    THROW = auto()          # fenko (throw)
    FINALLY = auto()        # akhir (finally/end)
    
    # Keywords - Logical Operators
    AND = auto()            # aur (and)
    OR = auto()             # ya (or)
    NOT = auto()            # nahi (not)
    
    # Operators - Arithmetic
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    
    # Operators - Comparison
    GREATER = auto()        # >
    LESS = auto()           # <
    GREATER_EQUAL = auto()  # >=
    LESS_EQUAL = auto()     # <=
    EQUAL = auto()          # ==
    NOT_EQUAL = auto()      # !=
    
    # Operators - Assignment
    ASSIGN = auto()         # =
    
    # Delimiters
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    COMMA = auto()          # ,
    DOT = auto()            # . (for method calls/property access)
    COLON = auto()          # : (for dict/type hints in future)
    
    # Special
    NEWLINE = auto()        # Line break (can be significant)
    EOF = auto()            # End of file


@dataclass(frozen=True)
class Token:
    """Represents a single token in the source code.
    
    Attributes:
        type: The type of token (from TokenType enum)
        value: The literal value (for numbers, strings, identifiers, etc.)
        line: Line number in source code (1-indexed)
        column: Column number in source code (1-indexed)
        
    Examples:
        >>> Token(TokenType.NUMBER, 42, 1, 5)
        Token(NUMBER, 42, line=1, col=5)
        
        >>> Token(TokenType.IDENTIFIER, "count", 3, 10)
        Token(IDENTIFIER, 'count', line=3, col=10)
    """
    
    type: TokenType
    value: Optional[any] = None
    line: int = 1
    column: int = 1
    
    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        if self.value is not None:
            return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"
        return f"Token({self.type.name}, line={self.line}, col={self.column})"


# Keyword mappings: Hindi/Urdu keywords to token types
KEYWORDS = {
    # Program structure
    'shuru': TokenType.START,
    'khatam': TokenType.END,
    
    # I/O
    'likho': TokenType.PRINT,
    'padho': TokenType.INPUT,
    
    # Variables
    'maan': TokenType.LET,
    
    # Control flow
    'agar': TokenType.IF,
    'warna': TokenType.ELSE,
    'agarlena': TokenType.ELSEIF,
    'jab_tak': TokenType.WHILE,
    'bar_bar': TokenType.FOR,
    'in': TokenType.IN,
    'ruk': TokenType.BREAK,
    'age_badho': TokenType.CONTINUE,
    
    # Functions
    'kaam': TokenType.FUNCTION,
    'wapas': TokenType.RETURN,
    'lambada': TokenType.LAMBDA,
    
    # Booleans
    'sach': TokenType.BOOLEAN,      # true
    'jhoot': TokenType.BOOLEAN,     # false
    
    # Logical operators
    'aur': TokenType.AND,
    'ya': TokenType.OR,
    'nahi': TokenType.NOT,
    
    # OOP
    'class': TokenType.CLASS,
    'naya': TokenType.NEW,
    'yeh': TokenType.THIS,
    'badhaao': TokenType.EXTENDS,
    'upar': TokenType.SUPER,
    
    # Error handling
    'koshish': TokenType.TRY,
    'pakdo': TokenType.CATCH,
    'fenko': TokenType.THROW,
    'akhir': TokenType.FINALLY,
}


class Lexer:
    """Enhanced lexer with regex-based tokenization for DesiLang.
    
    This lexer converts source code into tokens using efficient regex patterns.
    It handles Unicode characters for Hindi/Urdu text, string escapes, and
    provides detailed error messages with line/column information.
    
    Attributes:
        code: The source code to tokenize
        pos: Current position in the code
        line: Current line number (1-indexed)
        column: Current column number (1-indexed)
        tokens: List of tokens produced
        
    Example:
        >>> lexer = Lexer('maan x = 42\\nlikho(x)')
        >>> tokens = lexer.tokenize()
        >>> print(tokens[0])
        Token(LET, 'maan', line=1, col=1)
    """
    
    # Regex patterns for tokens (compiled for performance)
    PATTERNS = {
        'NUMBER': re.compile(r'\d+\.?\d*'),  # 42, 3.14
        'STRING': re.compile(r'"([^"\\\\]|\\\\.)*"|\'([^\'\\\\]|\\\\.)*\''),  # "str" or 'str'
        'IDENTIFIER': re.compile(r'[a-zA-Z_\u0900-\u097F][a-zA-Z0-9_\u0900-\u097F]*'),  # Unicode support
        'WHITESPACE': re.compile(r'[ \t]+'),
        'NEWLINE': re.compile(r'\n'),
        'COMMENT': re.compile(r'//[^\n]*'),  # Single-line comment
    }
    
    # Two-character operators (must check before single-char)
    TWO_CHAR_OPS = {
        '==': TokenType.EQUAL,
        '!=': TokenType.NOT_EQUAL,
        '>=': TokenType.GREATER_EQUAL,
        '<=': TokenType.LESS_EQUAL,
    }
    
    # Single-character operators and delimiters
    SINGLE_CHAR_TOKENS = {
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.MULTIPLY,
        '/': TokenType.DIVIDE,
        '%': TokenType.MODULO,
        '>': TokenType.GREATER,
        '<': TokenType.LESS,
        '=': TokenType.ASSIGN,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        '{': TokenType.LBRACE,
        '}': TokenType.RBRACE,
        '[': TokenType.LBRACKET,
        ']': TokenType.RBRACKET,
        ',': TokenType.COMMA,
        '.': TokenType.DOT,
        ':': TokenType.COLON,
    }
    
    def __init__(self, code: str):
        """Initialize the lexer with source code.
        
        Args:
            code: Source code string to tokenize
        """
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def error(self, message: str) -> None:
        """Raise a lexer error with current position.
        
        Args:
            message: Error description
            
        Raises:
            LexerError: Always raised with formatted message
        """
        raise LexerError(message, self.line, self.column)
    
    def current_char(self) -> Optional[str]:
        """Get current character without advancing.
        
        Returns:
            Current character or None if at end of file
        """
        if self.pos >= len(self.code):
            return None
        return self.code[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek ahead at a character without advancing.
        
        Args:
            offset: How many characters to look ahead (default: 1)
            
        Returns:
            Character at peek position or None if out of bounds
        """
        peek_pos = self.pos + offset
        if peek_pos >= len(self.code):
            return None
        return self.code[peek_pos]
    
    def advance(self, count: int = 1) -> None:
        """Move forward by count characters, updating line/column.
        
        Args:
            count: Number of characters to advance (default: 1)
        """
        for _ in range(count):
            if self.pos < len(self.code):
                if self.code[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1
    
    def match_pattern(self, pattern: re.Pattern) -> Optional[str]:
        """Try to match a regex pattern at current position.
        
        Args:
            pattern: Compiled regex pattern to match
            
        Returns:
            Matched string if successful, None otherwise
        """
        match = pattern.match(self.code, self.pos)
        if match:
            return match.group(0)
        return None
    
    def skip_whitespace(self) -> None:
        """Skip spaces and tabs (but not newlines)."""
        while self.match_pattern(self.PATTERNS['WHITESPACE']):
            matched = self.match_pattern(self.PATTERNS['WHITESPACE'])
            if matched:
                self.advance(len(matched))
    
    def skip_comment(self) -> None:
        """Skip single-line comment (// to end of line)."""
        matched = self.match_pattern(self.PATTERNS['COMMENT'])
        if matched:
            self.advance(len(matched))
    
    def read_number(self) -> Token:
        """Read a number token (integer or float).
        
        Returns:
            Token with NUMBER type and numeric value
            
        Example:
            '42' -> Token(NUMBER, 42)
            '3.14' -> Token(NUMBER, 3.14)
        """
        start_line, start_col = self.line, self.column
        matched = self.match_pattern(self.PATTERNS['NUMBER'])
        
        if not matched:
            self.error("Expected number")
        
        self.advance(len(matched))
        
        # Convert to int or float
        if '.' in matched:
            value = float(matched)
        else:
            value = int(matched)
        
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_string(self) -> Token:
        """Read a string token with escape sequence support.
        
        Returns:
            Token with STRING type and unescaped string value
            
        Raises:
            LexerError: If string is unterminated
            
        Example:
            '"hello"' -> Token(STRING, 'hello')
            '"line1\\nline2"' -> Token(STRING, 'line1\nline2')
        """
        start_line, start_col = self.line, self.column
        quote = self.current_char()  # " or '
        
        if quote not in ('"', "'"):
            self.error("Expected string")
        
        self.advance()  # Skip opening quote
        chars = []
        
        while self.current_char() and self.current_char() != quote:
            if self.current_char() == '\\':
                # Handle escape sequences
                self.advance()
                next_char = self.current_char()
                
                if next_char == 'n':
                    chars.append('\n')
                elif next_char == 't':
                    chars.append('\t')
                elif next_char == 'r':
                    chars.append('\r')
                elif next_char == '\\':
                    chars.append('\\')
                elif next_char == quote:
                    chars.append(quote)
                elif next_char == '0':
                    chars.append('\0')
                else:
                    # Unknown escape, keep as-is
                    chars.append(next_char if next_char else '')
                
                if next_char:
                    self.advance()
            else:
                chars.append(self.current_char())
                self.advance()
        
        if self.current_char() != quote:
            self.error(f"Unterminated string (missing closing {quote})")
        
        self.advance()  # Skip closing quote
        
        return Token(TokenType.STRING, ''.join(chars), start_line, start_col)
    
    def read_identifier_or_keyword(self) -> Token:
        """Read an identifier or keyword token.
        
        Returns:
            Token with IDENTIFIER type or appropriate keyword type
            
        Example:
            'count' -> Token(IDENTIFIER, 'count')
            'agar' -> Token(IF, 'agar')
            'sach' -> Token(BOOLEAN, True)
        """
        start_line, start_col = self.line, self.column
        matched = self.match_pattern(self.PATTERNS['IDENTIFIER'])
        
        if not matched:
            self.error("Expected identifier")
        
        self.advance(len(matched))
        
        # Check if it's a keyword
        if matched in KEYWORDS:
            token_type = KEYWORDS[matched]
            
            # Special handling for booleans
            if token_type == TokenType.BOOLEAN:
                value = True if matched == 'sach' else False
                return Token(TokenType.BOOLEAN, value, start_line, start_col)
            
            return Token(token_type, matched, start_line, start_col)
        
        # It's an identifier
        return Token(TokenType.IDENTIFIER, matched, start_line, start_col)
    
    def read_operator(self) -> Token:
        """Read an operator token (two-char or single-char).
        
        Returns:
            Token with appropriate operator type
            
        Raises:
            LexerError: If character is not a valid operator
        """
        start_line, start_col = self.line, self.column
        
        # Try two-character operators first
        two_char = self.code[self.pos:self.pos+2]
        if two_char in self.TWO_CHAR_OPS:
            self.advance(2)
            return Token(self.TWO_CHAR_OPS[two_char], two_char, start_line, start_col)
        
        # Try single-character operators
        char = self.current_char()
        if char in self.SINGLE_CHAR_TOKENS:
            self.advance()
            return Token(self.SINGLE_CHAR_TOKENS[char], char, start_line, start_col)
        
        self.error(f"Unexpected character: '{char}'")
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code.
        
        Returns:
            List of tokens including final EOF token
            
        Raises:
            LexerError: On any tokenization error
            
        Example:
            >>> lexer = Lexer('maan x = 42')
            >>> tokens = lexer.tokenize()
            >>> [t.type.name for t in tokens]
            ['LET', 'IDENTIFIER', 'ASSIGN', 'NUMBER', 'EOF']
        """
        self.tokens = []
        
        while self.pos < len(self.code):
            # Skip whitespace and comments
            self.skip_whitespace()
            
            if self.current_char() is None:
                break
            
            # Skip comments
            if self.current_char() == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue
            
            # Handle newlines
            if self.current_char() == '\n':
                # Newlines can be significant in some contexts
                # For now, we skip them (Python-style)
                self.advance()
                continue
            
            # Numbers
            if self.current_char() and self.current_char().isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Strings
            if self.current_char() in ('"', "'"):
                self.tokens.append(self.read_string())
                continue
            
            # Identifiers and keywords
            if self.current_char() and (self.current_char().isalpha() or 
                                       self.current_char() == '_' or
                                       ord(self.current_char()) >= 0x0900):  # Unicode Hindi
                self.tokens.append(self.read_identifier_or_keyword())
                continue
            
            # Operators and delimiters
            if self.current_char():
                self.tokens.append(self.read_operator())
                continue
            
            # Should not reach here
            self.error(f"Unexpected character: '{self.current_char()}'")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        
        return self.tokens


def tokenize(code: str) -> List[Token]:
    """Convenience function to tokenize source code.
    
    Args:
        code: Source code string
        
    Returns:
        List of tokens
        
    Raises:
        LexerError: On tokenization error
        
    Example:
        >>> tokens = tokenize('maan x = 42')
        >>> print(tokens[0].type.name)
        'LET'
    """
    lexer = Lexer(code)
    return lexer.tokenize()

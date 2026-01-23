"""
Enhanced Lexer for DesiLang - Production version.
Tokenizes source code into a stream of tokens for the parser.
"""

from typing import List, Optional
from enum import Enum, auto
from .errors import LexerError


class TokenType(Enum):
    """Enumeration of all token types in DesiLang."""
    # Literals
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    
    # Identifiers and Keywords
    IDENTIFIER = auto()
    
    # Keywords - Program Structure
    START = auto()          # shuru
    END = auto()            # khatam
    
    # Keywords - I/O
    PRINT = auto()          # dikhao
    INPUT = auto()          # padho
    
    # Keywords - Control Flow
    IF = auto()             # agar
    ELSE = auto()           # warna
    ENDIF = auto()          # bas
    WHILE = auto()          # jabtak
    ENDWHILE = auto()       # band
    FOR = auto()            # chalao
    FROM = auto()           # se
    TO = auto()             # tak
    
    # Keywords - Functions
    FUNCTION = auto()       # vidhi
    CALL = auto()           # bulayo
    RETURN = auto()         # vapas
    ENDFUNC = auto()        # samapt
    
    # Keywords - File I/O
    WRITE_FILE = auto()     # likho
    READ_FILE = auto()      # padho_file
    IMPORT = auto()         # lao
    
    # Keywords - OOP
    CLASS = auto()          # class
    NEW = auto()            # naya
    THIS = auto()           # yeh
    EXTENDS = auto()        # badhaao
    SUPER = auto()          # upar
    
    # Keywords - Error Handling
    TRY = auto()            # koshish
    CATCH = auto()          # pakdo
    THROW = auto()          # fenko
    FINALLY = auto()        # akhir
    
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
    DOT = auto()            # . (for method calls)
    
    # Special
    NEWLINE = auto()
    EOF = auto()


class Token:
    """Represents a single token in the source code."""
    
    def __init__(self, type_: TokenType, value: Optional[any] = None, line: int = 1, column: int = 1):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self) -> str:
        if self.value is not None:
            return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"
        return f"Token({self.type.name}, {self.line}:{self.column})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value


# Keyword mappings
KEYWORDS = {
    'shuru': TokenType.START,
    'khatam': TokenType.END,
    'dikhao': TokenType.PRINT,
    'padho': TokenType.INPUT,
    'agar': TokenType.IF,
    'warna': TokenType.ELSE,
    'bas': TokenType.ENDIF,
    'jabtak': TokenType.WHILE,
    'band': TokenType.ENDWHILE,
    'chalao': TokenType.FOR,
    'se': TokenType.FROM,
    'tak': TokenType.TO,
    'vidhi': TokenType.FUNCTION,
    'bulayo': TokenType.CALL,
    'vapas': TokenType.RETURN,
    'samapt': TokenType.ENDFUNC,
    'sahi': TokenType.BOOLEAN,     # true
    'galat': TokenType.BOOLEAN,    # false
    'likho': TokenType.WRITE_FILE,
    'padho_file': TokenType.READ_FILE,
    'lao': TokenType.IMPORT,
    # OOP keywords
    'class': TokenType.CLASS,
    'naya': TokenType.NEW,
    'yeh': TokenType.THIS,
    'badhaao': TokenType.EXTENDS,
    'upar': TokenType.SUPER,
    # Error handling keywords
    'koshish': TokenType.TRY,
    'pakdo': TokenType.CATCH,
    'fenko': TokenType.THROW,
    'akhir': TokenType.FINALLY,
}


class Lexer:
    """Tokenizes DesiLang source code."""
    
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def error(self, message: str) -> None:
        """Raise a lexer error with current position."""
        raise LexerError(message, self.line, self.column)
    
    def current_char(self) -> Optional[str]:
        """Get current character without advancing."""
        if self.pos >= len(self.code):
            return None
        return self.code[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek ahead at a character."""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.code):
            return None
        return self.code[peek_pos]
    
    def advance(self) -> Optional[str]:
        """Move to next character and return current."""
        char = self.current_char()
        if char is not None:
            self.pos += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        return char
    
    def skip_whitespace(self) -> None:
        """Skip whitespace except newlines (which can be significant)."""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self) -> None:
        """Skip single-line comment (// to end of line)."""
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> Token:
        """Read a number (integer or float)."""
        start_line = self.line
        start_col = self.column
        num_str = ''
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    self.error("Multiple decimal points in number")
                has_dot = True
                num_str += self.advance()
            else:
                num_str += self.advance()
        
        if has_dot:
            value = float(num_str)
        else:
            value = int(num_str)
        
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_string(self) -> Token:
        """Read a string literal (double-quoted)."""
        start_line = self.line
        start_col = self.column
        
        self.advance()  # Skip opening quote
        string_val = ''
        
        while self.current_char() and self.current_char() != '"':
            if self.current_char() == '\n':
                self.error("Unterminated string literal")
            if self.current_char() == '\\':
                self.advance()
                # Handle escape sequences
                escape_char = self.current_char()
                if escape_char == 'n':
                    string_val += '\n'
                elif escape_char == 't':
                    string_val += '\t'
                elif escape_char == '\\':
                    string_val += '\\'
                elif escape_char == '"':
                    string_val += '"'
                else:
                    string_val += escape_char
                self.advance()
            else:
                string_val += self.advance()
        
        if not self.current_char():
            self.error("Unterminated string literal")
        
        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, string_val, start_line, start_col)
    
    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_line = self.line
        start_col = self.column
        ident = ''
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            ident += self.advance()
        
        # Check if it's a keyword
        token_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        
        # Handle boolean keywords specially
        if token_type == TokenType.BOOLEAN:
            value = (ident == 'sahi')  # True if 'sahi', False if 'galat'
            return Token(token_type, value, start_line, start_col)
        
        return Token(token_type, ident, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code."""
        while self.current_char():
            # Skip whitespace
            if self.current_char() in ' \t\r':
                self.skip_whitespace()
                continue
            
            # Handle newlines
            if self.current_char() == '\n':
                self.advance()
                continue
            
            # Skip comments
            if self.current_char() == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue
            
            # Numbers
            if self.current_char().isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Strings
            if self.current_char() == '"':
                self.tokens.append(self.read_string())
                continue
            
            # Identifiers and keywords
            if self.current_char().isalpha() or self.current_char() == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Two-character operators
            char = self.current_char()
            next_char = self.peek_char()
            start_line = self.line
            start_col = self.column
            
            if char == '>' and next_char == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', start_line, start_col))
                continue
            
            if char == '<' and next_char == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', start_line, start_col))
                continue
            
            if char == '=' and next_char == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.EQUAL, '==', start_line, start_col))
                continue
            
            if char == '!' and next_char == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', start_line, start_col))
                continue
            
            # Single-character tokens
            single_char_tokens = {
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
            }
            
            if char in single_char_tokens:
                token_type = single_char_tokens[char]
                self.advance()
                self.tokens.append(Token(token_type, char, start_line, start_col))
                continue
            
            # Unknown character
            self.error(f"Illegal character: '{char}'")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens


def tokenize(code: str) -> List[Token]:
    """Convenience function to tokenize code."""
    lexer = Lexer(code)
    return lexer.tokenize()

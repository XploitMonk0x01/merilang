"""
Unit tests for DesiLang lexer.
"""

import pytest
from merilang.lexer import tokenize, Token, TokenType, LexerError


def test_tokenize_basic_program():
    """Test tokenizing a basic program."""
    code = """
shuru
x = 42
dikhao x
khatam
    """.strip()
    
    tokens = tokenize(code)
    
    assert tokens[0].type == TokenType.START
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == 'x'
    assert tokens[2].type == TokenType.ASSIGN
    assert tokens[3].type == TokenType.NUMBER
    assert tokens[3].value == 42
    assert tokens[4].type == TokenType.IDENTIFIER
    assert tokens[5].type == TokenType.PRINT
    assert tokens[6].type == TokenType.IDENTIFIER
    assert tokens[7].type == TokenType.END
    assert tokens[8].type == TokenType.EOF


def test_tokenize_numbers():
    """Test tokenizing integers and floats."""
    code = "shuru x = 123 y = 45.67 khatam"
    tokens = tokenize(code)
    
    assert tokens[3].type == TokenType.NUMBER
    assert tokens[3].value == 123
    assert isinstance(tokens[3].value, int)
    
    assert tokens[7].type == TokenType.NUMBER
    assert tokens[7].value == 45.67
    assert isinstance(tokens[7].value, float)


def test_tokenize_strings():
    """Test tokenizing string literals."""
    code = 'shuru naam = "Rajwant" khatam'
    tokens = tokenize(code)
    
    assert tokens[3].type == TokenType.STRING
    assert tokens[3].value == "Rajwant"


def test_tokenize_string_escapes():
    """Test string escape sequences."""
    code = r'shuru s = "Hello\nWorld\t!" khatam'
    tokens = tokenize(code)
    
    assert tokens[3].type == TokenType.STRING
    assert tokens[3].value == "Hello\nWorld\t!"


def test_tokenize_operators():
    """Test tokenizing all operators."""
    code = "shuru a = 1 + 2 - 3 * 4 / 5 % 6 khatam"
    tokens = tokenize(code)
    
    operators = [t for t in tokens if t.type in [
        TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY,
        TokenType.DIVIDE, TokenType.MODULO
    ]]
    
    assert len(operators) == 5


def test_tokenize_comparison_operators():
    """Test comparison operators."""
    code = "shuru x = 1 > 2 x = 1 < 2 x = 1 >= 2 x = 1 <= 2 x = 1 == 2 x = 1 != 2 khatam"
    tokens = tokenize(code)
    
    comparisons = [t for t in tokens if t.type in [
        TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL,
        TokenType.LESS_EQUAL, TokenType.EQUAL, TokenType.NOT_EQUAL
    ]]
    
    assert len(comparisons) == 6


def test_tokenize_booleans():
    """Test boolean literals."""
    code = "shuru a = sahi b = galat khatam"
    tokens = tokenize(code)
    
    bool_tokens = [t for t in tokens if t.type == TokenType.BOOLEAN]
    
    assert len(bool_tokens) == 2
    assert bool_tokens[0].value == True
    assert bool_tokens[1].value == False


def test_tokenize_keywords():
    """Test keyword tokenization."""
    code = "shuru agar warna bas jabtak band chalao vidhi vapas samapt khatam"
    tokens = tokenize(code)
    
    expected_types = [
        TokenType.START, TokenType.IF, TokenType.ELSE, TokenType.ENDIF,
        TokenType.WHILE, TokenType.ENDWHILE, TokenType.FOR,
        TokenType.FUNCTION, TokenType.RETURN, TokenType.ENDFUNC, TokenType.END
    ]
    
    for i, expected_type in enumerate(expected_types):
        assert tokens[i].type == expected_type


def test_tokenize_delimiters():
    """Test delimiter tokens."""
    code = "shuru f ( x , y ) { } [ 1 , 2 ] khatam"
    tokens = tokenize(code)
    
    delimiters = [t for t in tokens if t.type in [
        TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE,
        TokenType.LBRACKET, TokenType.RBRACKET, TokenType.COMMA
    ]]
    
    assert len(delimiters) == 10


def test_tokenize_comments():
    """Test comment handling."""
    code = """
shuru
// This is a comment
x = 42  // Another comment
dikhao x
khatam
    """.strip()
    
    tokens = tokenize(code)
    
    # Comments should be ignored
    comment_tokens = [t for t in tokens if 'comment' in str(t).lower()]
    assert len(comment_tokens) == 0


def test_tokenize_line_tracking():
    """Test that line numbers are tracked correctly."""
    code = """shuru
x = 1
y = 2
khatam"""
    
    tokens = tokenize(code)
    
    assert tokens[0].line == 1  # shuru
    assert tokens[1].line == 2  # x
    assert tokens[4].line == 3  # y


def test_tokenize_unterminated_string():
    """Test error on unterminated string."""
    code = 'shuru s = "unterminated khatam'
    
    with pytest.raises(LexerError) as exc_info:
        tokenize(code)
    
    assert "string" in str(exc_info.value).lower()


def test_tokenize_illegal_character():
    """Test error on illegal character."""
    code = "shuru x @ 42 khatam"
    
    with pytest.raises(LexerError) as exc_info:
        tokenize(code)
    
    assert "illegal" in str(exc_info.value).lower()


def test_tokenize_empty_program():
    """Test tokenizing empty program."""
    code = "shuru khatam"
    tokens = tokenize(code)
    
    assert tokens[0].type == TokenType.START
    assert tokens[1].type == TokenType.END
    assert tokens[2].type == TokenType.EOF


def test_tokenize_list_syntax():
    """Test list literal syntax."""
    code = "shuru mylist = [1, 2, 3] khatam"
    tokens = tokenize(code)
    
    assert tokens[3].type == TokenType.LBRACKET
    assert tokens[5].type == TokenType.COMMA
    assert tokens[9].type == TokenType.RBRACKET

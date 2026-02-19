"""
Comprehensive tests for enhanced lexer with regex tokenization.

Tests cover all token types, edge cases, error handling, and Unicode support.

Author: MeriLang Team
Version: 2.0
"""

import pytest
from merilang.lexer_enhanced import (
    Lexer, Token, TokenType, tokenize,
    LexerError
)


class TestBasicTokenization:
    """Test basic token recognition."""
    
    def test_numbers_integers(self):
        """Test integer tokenization."""
        tokens = tokenize("42 100 0 999")
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42
        assert tokens[1].value == 100
        assert tokens[2].value == 0
        assert tokens[3].value == 999
    
    def test_numbers_floats(self):
        """Test float tokenization."""
        tokens = tokenize("3.14 0.5 99.99")
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 3.14
        assert tokens[1].value == 0.5
        assert tokens[2].value == 99.99
    
    def test_strings_double_quotes(self):
        """Test double-quoted strings."""
        tokens = tokenize('"hello" "world"')
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"
        assert tokens[1].value == "world"
    
    def test_strings_single_quotes(self):
        """Test single-quoted strings."""
        tokens = tokenize("'hello' 'world'")
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"
        assert tokens[1].value == "world"
    
    def test_strings_with_escapes(self):
        """Test string escape sequences."""
        tokens = tokenize(r'"line1\nline2" "tab\there" "quote\"test"')
        assert tokens[0].value == "line1\nline2"
        assert tokens[1].value == "tab\there"
        assert tokens[2].value == 'quote"test'
    
    def test_identifiers(self):
        """Test identifier recognition."""
        tokens = tokenize("count x_value name123")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "count"
        assert tokens[1].value == "x_value"
        assert tokens[2].value == "name123"
    
    def test_unicode_identifiers(self):
        """Test Unicode (Hindi) identifiers."""
        tokens = tokenize("गणना नाम संख्या")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert len(tokens) == 4  # 3 identifiers + EOF


class TestKeywords:
    """Test keyword recognition."""
    
    def test_control_flow_keywords(self):
        """Test control flow keywords."""
        tokens = tokenize("agar warna agarlena jab_tak bar_bar")
        assert tokens[0].type == TokenType.IF
        assert tokens[1].type == TokenType.ELSE
        assert tokens[2].type == TokenType.ELSEIF
        assert tokens[3].type == TokenType.WHILE
        assert tokens[4].type == TokenType.FOR
    
    def test_function_keywords(self):
        """Test function-related keywords."""
        tokens = tokenize("kaam wapas")
        assert tokens[0].type == TokenType.FUNCTION
        assert tokens[1].type == TokenType.RETURN
    
    def test_boolean_keywords(self):
        """Test boolean literals."""
        tokens = tokenize("sach jhoot")
        assert tokens[0].type == TokenType.BOOLEAN
        assert tokens[0].value == True
        assert tokens[1].type == TokenType.BOOLEAN
        assert tokens[1].value == False
    
    def test_oop_keywords(self):
        """Test OOP keywords."""
        tokens = tokenize("class naya yeh badhaao upar")
        assert tokens[0].type == TokenType.CLASS
        assert tokens[1].type == TokenType.NEW
        assert tokens[2].type == TokenType.THIS
        assert tokens[3].type == TokenType.EXTENDS
        assert tokens[4].type == TokenType.SUPER
    
    def test_error_handling_keywords(self):
        """Test error handling keywords."""
        tokens = tokenize("koshish pakdo fenko akhir")
        assert tokens[0].type == TokenType.TRY
        assert tokens[1].type == TokenType.CATCH
        assert tokens[2].type == TokenType.THROW
        assert tokens[3].type == TokenType.FINALLY


class TestOperators:
    """Test operator recognition."""
    
    def test_arithmetic_operators(self):
        """Test arithmetic operators."""
        tokens = tokenize("+ - * / %")
        assert tokens[0].type == TokenType.PLUS
        assert tokens[1].type == TokenType.MINUS
        assert tokens[2].type == TokenType.MULTIPLY
        assert tokens[3].type == TokenType.DIVIDE
        assert tokens[4].type == TokenType.MODULO
    
    def test_comparison_operators(self):
        """Test comparison operators."""
        tokens = tokenize("== != > < >= <=")
        assert tokens[0].type == TokenType.EQUAL
        assert tokens[1].type == TokenType.NOT_EQUAL
        assert tokens[2].type == TokenType.GREATER
        assert tokens[3].type == TokenType.LESS
        assert tokens[4].type == TokenType.GREATER_EQUAL
        assert tokens[5].type == TokenType.LESS_EQUAL
    
    def test_assignment_operator(self):
        """Test assignment operator."""
        tokens = tokenize("=")
        assert tokens[0].type == TokenType.ASSIGN


class TestDelimiters:
    """Test delimiter recognition."""
    
    def test_parentheses(self):
        """Test parentheses."""
        tokens = tokenize("( )")
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[1].type == TokenType.RPAREN
    
    def test_braces(self):
        """Test braces."""
        tokens = tokenize("{ }")
        assert tokens[0].type == TokenType.LBRACE
        assert tokens[1].type == TokenType.RBRACE
    
    def test_brackets(self):
        """Test brackets."""
        tokens = tokenize("[ ]")
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].type == TokenType.RBRACKET
    
    def test_other_delimiters(self):
        """Test other delimiters."""
        tokens = tokenize(", . :")
        assert tokens[0].type == TokenType.COMMA
        assert tokens[1].type == TokenType.DOT
        assert tokens[2].type == TokenType.COLON


class TestComplexExpressions:
    """Test tokenization of complex expressions."""
    
    def test_variable_assignment(self):
        """Test variable assignment."""
        tokens = tokenize("maan x = 42")
        assert [t.type for t in tokens[:-1]] == [
            TokenType.LET,
            TokenType.IDENTIFIER,
            TokenType.ASSIGN,
            TokenType.NUMBER
        ]
    
    def test_function_call(self):
        """Test function call."""
        tokens = tokenize('likho("hello")')
        assert [t.type for t in tokens[:-1]] == [
            TokenType.PRINT,
            TokenType.LPAREN,
            TokenType.STRING,
            TokenType.RPAREN
        ]
    
    def test_if_statement(self):
        """Test if statement."""
        tokens = tokenize("agar x > 10 { likho(x) }")
        types = [t.type for t in tokens[:-1]]
        assert TokenType.IF in types
        assert TokenType.GREATER in types
        assert TokenType.LBRACE in types
        assert TokenType.RBRACE in types
    
    def test_array_literal(self):
        """Test array literal."""
        tokens = tokenize("[1, 2, 3]")
        assert [t.type for t in tokens[:-1]] == [
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.RBRACKET
        ]
    
    def test_method_call(self):
        """Test method call with dot notation."""
        tokens = tokenize("person.greet()")
        assert [t.type for t in tokens[:-1]] == [
            TokenType.IDENTIFIER,
            TokenType.DOT,
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.RPAREN
        ]


class TestComments:
    """Test comment handling."""
    
    def test_single_line_comment(self):
        """Test single-line comment skipping."""
        tokens = tokenize("maan x = 42 // this is a comment")
        # Comment should be skipped
        assert len(tokens) == 5  # maan, x, =, 42, EOF
        assert tokens[-1].type == TokenType.EOF
    
    def test_comment_at_start(self):
        """Test comment at start of line."""
        tokens = tokenize("// comment\nmaan x = 10")
        assert tokens[0].type == TokenType.LET
    
    def test_multiple_comments(self):
        """Test multiple comments."""
        code = """
        // First comment
        maan x = 10  // inline comment
        // Another comment
        likho(x)
        """
        tokens = tokenize(code)
        # Should have: maan, x, =, 10, likho, (, x, ), EOF
        identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        assert len(identifiers) == 2  # x appears twice


class TestWhitespace:
    """Test whitespace handling."""
    
    def test_spaces(self):
        """Test space separation."""
        tokens = tokenize("maan   x   =   42")
        assert len(tokens) == 5  # maan, x, =, 42, EOF
    
    def test_tabs(self):
        """Test tab separation."""
        tokens = tokenize("maan\tx\t=\t42")
        assert len(tokens) == 5
    
    def test_newlines(self):
        """Test newline handling."""
        tokens = tokenize("maan x = 42\nlikho(x)")
        # Newlines are skipped in current implementation
        assert TokenType.NEWLINE not in [t.type for t in tokens]
    
    def test_mixed_whitespace(self):
        """Test mixed whitespace."""
        tokens = tokenize("maan  \t  x\n=\t\t42")
        assert len(tokens) == 5


class TestLineColumnTracking:
    """Test line and column number tracking."""
    
    def test_single_line_positions(self):
        """Test column positions on single line."""
        tokens = tokenize("maan x = 42")
        assert tokens[0].line == 1
        assert tokens[0].column == 1  # 'maan' starts at column 1
        assert tokens[1].line == 1
        assert tokens[1].column == 6  # 'x' starts at column 6
    
    def test_multiline_positions(self):
        """Test line numbers on multiple lines."""
        code = """maan x = 10
likho(x)
maan y = 20"""
        tokens = tokenize(code)
        
        # Find tokens by type
        let_tokens = [t for t in tokens if t.type == TokenType.LET]
        assert len(let_tokens) == 2
        assert let_tokens[0].line == 1
        assert let_tokens[1].line == 3


class TestErrorHandling:
    """Test error cases."""
    
    def test_unterminated_string_double(self):
        """Test error on unterminated double-quoted string."""
        with pytest.raises(LexerError) as exc_info:
            tokenize('"hello')
        assert "Unterminated" in str(exc_info.value)
    
    def test_unterminated_string_single(self):
        """Test error on unterminated single-quoted string."""
        with pytest.raises(LexerError) as exc_info:
            tokenize("'hello")
        assert "Unterminated" in str(exc_info.value)
    
    def test_unexpected_character(self):
        """Test error on unexpected character."""
        with pytest.raises(LexerError) as exc_info:
            tokenize("maan x = @")
        assert "Unexpected" in str(exc_info.value)
    
    def test_error_includes_line_info(self):
        """Test that errors include line information."""
        try:
            tokenize('maan x = 10\nlikho("hello)')
        except LexerError as e:
            assert e.line is not None


class TestEdgeCases:
    """Test edge cases and corner scenarios."""
    
    def test_empty_string(self):
        """Test tokenizing empty string."""
        tokens = tokenize("")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_only_whitespace(self):
        """Test tokenizing only whitespace."""
        tokens = tokenize("   \t  \n  ")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_only_comments(self):
        """Test tokenizing only comments."""
        tokens = tokenize("// comment 1\n// comment 2")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_adjacent_operators(self):
        """Test adjacent operators."""
        tokens = tokenize("x==10")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[1].type == TokenType.EQUAL
        assert tokens[2].type == TokenType.NUMBER
    
    def test_string_with_numbers(self):
        """Test string containing numbers."""
        tokens = tokenize('"123"')
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "123"
    
    def test_very_long_identifier(self):
        """Test very long identifier."""
        long_name = "a" * 1000
        tokens = tokenize(f"maan {long_name} = 42")
        assert tokens[1].type == TokenType.IDENTIFIER
        assert len(tokens[1].value) == 1000


class TestTokenEquality:
    """Test token equality and representation."""
    
    def test_token_equality(self):
        """Test token equality comparison."""
        t1 = Token(TokenType.NUMBER, 42, 1, 1)
        t2 = Token(TokenType.NUMBER, 42, 1, 1)
        t3 = Token(TokenType.NUMBER, 43, 1, 1)
        
        assert t1 == t2
        assert t1 != t3
    
    def test_token_repr(self):
        """Test token string representation."""
        t = Token(TokenType.IDENTIFIER, "count", 1, 5)
        repr_str = repr(t)
        assert "IDENTIFIER" in repr_str
        assert "count" in repr_str
        assert "line=1" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

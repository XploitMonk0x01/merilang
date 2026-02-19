"""
Enhanced Parser for MeriLang Phase 2.

Production-ready recursive descent parser with:
- Comprehensive type hints (mypy strict compliance)
- Google-style docstrings
- Integration with lexer_enhanced and errors_enhanced
- Float literal support
- Parenthesized expressions
- Unary operators (-, nahi)
- Improved error recovery with helpful suggestions
- Lambda functions
- Dictionary literals

Author: MeriLang Team
Version: 2.0 - Phase 2
"""

from typing import List, Optional, Union, Set
from dataclasses import dataclass

from merilang.lexer_enhanced import Token, TokenType, Lexer
from merilang.errors_enhanced import ParserError, ParserErrorCollection, ErrorLanguage
from merilang.ast_nodes_enhanced import (
    ASTNode, ProgramNode, NumberNode, StringNode, BooleanNode,
    ListNode, DictNode, VariableNode, AssignmentNode,
    BinaryOpNode, UnaryOpNode, ParenthesizedNode,
    IfNode, WhileNode, ForNode, BreakNode, ContinueNode,
    FunctionDefNode, FunctionCallNode, ReturnNode, LambdaNode,
    ClassDefNode, NewObjectNode, MethodCallNode, PropertyAccessNode,
    PropertyAssignmentNode, ThisNode, SuperNode,
    TryNode, ThrowNode, PrintNode, InputNode, ImportNode,
    IndexNode, IndexAssignmentNode
)


class Parser:
    """
    Recursive descent parser for MeriLang.
    
    Parses tokens from the lexer and constructs an Abstract Syntax Tree (AST).
    Implements operator precedence and proper error recovery.
    
    Grammar (simplified):
        program        → statement* EOF
        statement      → declaration | assignment | expression | control_flow
        declaration    → "maan" IDENTIFIER "=" expression
        assignment     → IDENTIFIER ("=" | "[" expression "]" "=") expression
        expression     → logical_or
        logical_or     → logical_and ("ya" logical_and)*
        logical_and    → equality ("aur" equality)*
        equality       → comparison (("==" | "!=") comparison)*
        comparison     → addition (("<" | ">" | "<=" | ">=") addition)*
        addition       → multiplication (("+" | "-") multiplication)*
        multiplication → unary (("*" | "/" | "%") unary)*
        unary          → ("-" | "nahi") unary | postfix
        postfix        → primary ("(" arguments ")" | "[" expression "]" | "." IDENTIFIER)*
        primary        → NUMBER | STRING | BOOLEAN | IDENTIFIER | "(" expression ")"
                       | "[" elements "]" | "{" pairs "}" | "lambada" parameters ":" expression
        
    Attributes:
        tokens: List of tokens from lexer
        current_index: Current position in token stream
        current_token: Token being examined
        error_language: Language for error messages (English/Hindi/Both)
        
    Examples:
        >>> lexer = Lexer("maan x = 42")
        >>> parser = Parser(lexer.tokenize())
        >>> ast = parser.parse()
        >>> print(ast)
        ProgramNode([AssignmentNode('x', NumberNode(42))])
    """
    
    def __init__(
        self,
        tokens: List[Token],
        error_language: ErrorLanguage = ErrorLanguage.ENGLISH
    ) -> None:
        """
        Initialize the parser with tokens.
        
        Args:
            tokens: List of tokens from the lexer
            error_language: Language for error messages
            
        Examples:
            >>> tokens = lexer.tokenize("maan x = 42")
            >>> parser = Parser(tokens)
        """
        self.tokens: List[Token] = tokens
        self.current_index: int = 0
        self.current_token: Token = tokens[0] if tokens else Token(TokenType.EOF, "", 1, 1)
        self.error_language: ErrorLanguage = error_language
        # Panic-mode: all syntax errors are collected here.
        self.errors: List[ParserError] = []
        self.had_error: bool = False
        
    def parse(self) -> ProgramNode:
        """
        Parse the token stream and return the AST root.

        Uses panic-mode error recovery: when a ``ParserError`` is raised inside
        ``parse_statement`` the parser records the error, calls
        ``synchronize()`` to find the next safe boundary token, and resumes
        parsing.  After the entire stream is consumed a
        ``ParserErrorCollection`` is raised if any errors were collected, so
        the caller sees *all* syntax problems at once.
        
        Returns:
            ProgramNode containing all top-level statements
            
        Raises:
            ParserErrorCollection: Aggregated collection of all parse errors.
            
        Examples:
            >>> parser = Parser(tokens)
            >>> program = parser.parse()
            >>> print(len(program.statements))
            5
        """
        statements: List[ASTNode] = []

        while not self.is_at_end():
            try:
                stmt = self.parse_statement()
                if stmt is not None:
                    statements.append(stmt)
            except ParserError as err:
                # Panic-mode: record the error, synchronise to a safe boundary.
                self.errors.append(err)
                self.had_error = True
                self.synchronize()

        if self.had_error:
            raise ParserErrorCollection(self.errors)

        return ProgramNode(statements=statements, line=1)
    
    # ========================================================================
    # Token Navigation
    # ========================================================================
    
    def advance(self) -> Token:
        """
        Consume current token and move to next.
        
        Returns:
            The consumed token
            
        Examples:
            >>> parser.current_token.type
            TokenType.IDENTIFIER
            >>> parser.advance()
            Token(IDENTIFIER, 'x', 1, 1)
            >>> parser.current_token.type
            TokenType.ASSIGN
        """
        if not self.is_at_end():
            self.current_index += 1
            if self.current_index < len(self.tokens):
                self.current_token = self.tokens[self.current_index]
        return self.tokens[self.current_index - 1]
    
    def peek(self, offset: int = 0) -> Token:
        """
        Look ahead at token without consuming it.
        
        Args:
            offset: How many tokens ahead to look (0 = current)
            
        Returns:
            The token at current_index + offset
            
        Examples:
            >>> parser.peek()  # Current token
            Token(IDENTIFIER, 'x', 1, 1)
            >>> parser.peek(1)  # Next token
            Token(ASSIGN, '=', 1, 3)
        """
        index = self.current_index + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return Token(TokenType.EOF, "", self.current_token.line, self.current_token.column)
    
    def match(self, *token_types: TokenType) -> bool:
        """
        Check if current token matches any of the given types.
        
        Args:
            *token_types: Variable number of TokenTypes to check
            
        Returns:
            True if current token matches any type
            
        Examples:
            >>> parser.match(TokenType.PLUS, TokenType.MINUS)
            True
            >>> parser.match(TokenType.MULTIPLY)
            False
        """
        return self.current_token.type in token_types
    
    def expect(self, token_type: TokenType) -> Token:
        """
        Consume current token if it matches expected type, otherwise error.
        
        Args:
            token_type: Expected token type
            
        Returns:
            The consumed token
            
        Raises:
            ParserError: If current token doesn't match expected type
            
        Examples:
            >>> parser.expect(TokenType.ASSIGN)
            Token(ASSIGN, '=', 1, 3)
        """
        if self.current_token.type != token_type:
            raise ParserError.expected_token(
                expected=token_type.name,
                got=self.current_token.type.name,
                line=self.current_token.line,
                column=self.current_token.column,
                language=self.error_language
            )
        return self.advance()
    
    def is_at_end(self) -> bool:
        """
        Check if we've reached end of token stream.
        
        Returns:
            True if at EOF
            
        Examples:
            >>> parser.is_at_end()
            False
            >>> # ... parse everything ...
            >>> parser.is_at_end()
            True
        """
        return self.current_token.type == TokenType.EOF

    def synchronize(self) -> None:
        """Panic-mode synchronisation: skip tokens until a safe boundary.

        After recording a syntax error the parser needs to advance to a point
        in the token stream where it can resume parsing cleanly.  Block-ending
        tokens (``}`` , ``khatam``, ``EOF``) and block-starting keywords
        (``kaam``, ``class``, ``agar``, ``jab_tak``, ``bar_bar``, ``koshish``)
        are treated as synchronisation points.

        This implements the standard panic-mode recovery strategy described in
        the Dragon Book (Aho et al.).
        """
        SYNC_TOKENS = {
            TokenType.RBRACE,
            TokenType.END,
            TokenType.FUNCTION,
            TokenType.CLASS,
            TokenType.IF,
            TokenType.WHILE,
            TokenType.FOR,
            TokenType.TRY,
            TokenType.EOF,
        }
        # Consume tokens until we hit a boundary or EOF.
        while not self.is_at_end():
            if self.current_token.type in SYNC_TOKENS:
                # Consume the boundary token itself (e.g. the closing '}') so
                # the next call to parse_statement starts on fresh ground.
                if self.current_token.type not in (TokenType.EOF, TokenType.END):
                    self.advance()
                return
            self.advance()
    
    def parse_statement(self) -> Optional[ASTNode]:
        """
        Parse a single statement.
        
        Returns:
            AST node for the statement, or None if no valid statement
            
        Raises:
            ParserError: If syntax error is encountered
            
        Examples:
            >>> stmt = parser.parse_statement()
            >>> isinstance(stmt, AssignmentNode)
            True
        """
        line = self.current_token.line
        
        # Variable declaration: maan x = value
        if self.match(TokenType.LET):
            return self.parse_declaration()
        
        # Print statement: likho(...)
        if self.match(TokenType.PRINT):
            return self.parse_print()
        
        # Input statement: padho variable
        if self.match(TokenType.INPUT):
            return self.parse_input()
        
        # If statement: agar ... { } warna { }
        if self.match(TokenType.IF):
            return self.parse_if()
        
        # While loop: jab_tak ... { }
        if self.match(TokenType.WHILE):
            return self.parse_while()
        
        # For loop: bar_bar x in [...] { }
        if self.match(TokenType.FOR):
            return self.parse_for()
        
        # Break statement: ruk
        if self.match(TokenType.BREAK):
            self.advance()
            return BreakNode(line=line)
        
        # Continue statement: age_badho
        if self.match(TokenType.CONTINUE):
            self.advance()
            return ContinueNode(line=line)
        
        # Function definition: kaam name(params) { ... }
        if self.match(TokenType.FUNCTION):
            return self.parse_function_def()
        
        # Return statement: wapas value
        if self.match(TokenType.RETURN):
            return self.parse_return()
        
        # Class definition: class Name { ... }
        if self.match(TokenType.CLASS):
            return self.parse_class_def()
        
        # Try-catch: koshish { ... } pakdo e { ... }
        if self.match(TokenType.TRY):
            return self.parse_try()
        
        # Throw statement: fenko error
        if self.match(TokenType.THROW):
            return self.parse_throw()
        
        # TODO: Import statement (requires IMPORT token in lexer)
        # if self.match(TokenType.IMPORT):
        #     return self.parse_import()
        
        # Assignment, method call, or expression
        if self.match(TokenType.IDENTIFIER, TokenType.THIS):
            return self.parse_assignment_or_expression()
        
        raise ParserError.unexpected_token(
            token=self.current_token.value,
            line=self.current_token.line,
            column=self.current_token.column,
            language=self.error_language
        )
    
    def parse_declaration(self) -> AssignmentNode:
        """
        Parse variable declaration: maan name = value.
        
        Returns:
            AssignmentNode with variable name and initial value
            
        Raises:
            ParserError: If syntax is invalid
            
        Examples:
            >>> # maan x = 42
            >>> decl = parser.parse_declaration()
            >>> decl.name
            'x'
            >>> decl.value.value
            42
        """
        line = self.current_token.line
        self.expect(TokenType.LET)
        
        if not self.match(TokenType.IDENTIFIER):
            raise ParserError.expected_identifier(
                line=self.current_token.line,
                column=self.current_token.column,
                language=self.error_language
            )
        
        name = self.current_token.value
        self.advance()
        
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        
        return AssignmentNode(name=name, value=value, line=line)
    
    def parse_print(self) -> PrintNode:
        """
        Parse print statement: likho(expr1, expr2, ...).
        
        Returns:
            PrintNode with list of expressions to print
            
        Examples:
            >>> # likho("Hello", name, 42)
            >>> print_stmt = parser.parse_print()
            >>> len(print_stmt.arguments)
            3
        """
        line = self.current_token.line
        self.expect(TokenType.PRINT)
        
        self.expect(TokenType.LPAREN)
        
        arguments: List[ASTNode] = []
        if not self.match(TokenType.RPAREN):
            arguments.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                arguments.append(self.parse_expression())
        
        self.expect(TokenType.RPAREN)
        
        return PrintNode(arguments=arguments, line=line)
    
    def parse_input(self) -> InputNode:
        """
        Parse input statement: padho variable.
        
        Returns:
            InputNode with variable name to store input
            
        Examples:
            >>> # padho name
            >>> input_stmt = parser.parse_input()
            >>> input_stmt.variable
            'name'
        """
        line = self.current_token.line
        self.expect(TokenType.INPUT)
        
        if not self.match(TokenType.IDENTIFIER):
            raise ParserError.expected_identifier(
                line=self.current_token.line,
                column=self.current_token.column,
                language=self.error_language
            )
        
        var_name = self.current_token.value
        self.advance()
        
        # Optional prompt: padho name "Enter name: "
        prompt: Optional[ASTNode] = None
        if self.match(TokenType.STRING):
            prompt = StringNode(value=self.current_token.value, line=self.current_token.line)
            self.advance()
        
        return InputNode(variable=var_name, prompt=prompt, line=line)
    
    def parse_if(self) -> IfNode:
        """
        Parse if-else statement.
        
        Grammar:
            agar condition { statements } [warna { statements }]
            
        Returns:
            IfNode with condition, then-branch, and optional else-branch
            
        Examples:
            >>> # agar x > 10 { likho("big") } warna { likho("small") }
            >>> if_stmt = parser.parse_if()
            >>> len(if_stmt.then_branch)
            1
            >>> len(if_stmt.else_branch)
            1
        """
        line = self.current_token.line
        self.expect(TokenType.IF)
        
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        
        then_branch: List[ASTNode] = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt is not None:
                then_branch.append(stmt)
        
        self.expect(TokenType.RBRACE)
        
        # Handle elif branches
        elif_branches: List[tuple[ASTNode, List[ASTNode]]] = []
        while self.match(TokenType.ELSEIF):
            self.advance()
            elif_condition = self.parse_expression()
            self.expect(TokenType.LBRACE)
            
            elif_body: List[ASTNode] = []
            while not self.match(TokenType.RBRACE):
                stmt = self.parse_statement()
                if stmt is not None:
                    elif_body.append(stmt)
            
            self.expect(TokenType.RBRACE)
            elif_branches.append((elif_condition, elif_body))
        
        # Optional else branch
        else_branch: Optional[List[ASTNode]] = None
        if self.match(TokenType.ELSE):
            self.advance()
            self.expect(TokenType.LBRACE)
            
            else_branch = []
            while not self.match(TokenType.RBRACE):
                stmt = self.parse_statement()
                if stmt is not None:
                    else_branch.append(stmt)
            
            self.expect(TokenType.RBRACE)
        
        return IfNode(
            condition=condition,
            then_branch=then_branch,
            elif_branches=elif_branches,
            else_branch=else_branch,
            line=line
        )
    
    def parse_while(self) -> WhileNode:
        """
        Parse while loop: jab_tak condition { statements }.
        
        Returns:
            WhileNode with condition and body
            
        Examples:
            >>> # jab_tak x < 10 { x = x + 1 }
            >>> while_loop = parser.parse_while()
            >>> isinstance(while_loop.condition, BinaryOpNode)
            True
        """
        line = self.current_token.line
        self.expect(TokenType.WHILE)
        
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        
        body: List[ASTNode] = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
        
        self.expect(TokenType.RBRACE)
        
        return WhileNode(condition=condition, body=body, line=line)
    
    def parse_for(self) -> ForNode:
        """
        Parse for loop: bar_bar variable in iterable { statements }.
        
        Returns:
            ForNode with loop variable, iterable, and body
            
        Examples:
            >>> # bar_bar x in [1, 2, 3] { likho(x) }
            >>> for_loop = parser.parse_for()
            >>> for_loop.variable
            'x'
        """
        line = self.current_token.line
        self.expect(TokenType.FOR)
        
        if not self.match(TokenType.IDENTIFIER):
            raise ParserError.expected_identifier(
                line=self.current_token.line,
                column=self.current_token.column,
                language=self.error_language
            )
        
        var_name = self.current_token.value
        self.advance()
        
        self.expect(TokenType.IN)
        
        iterable = self.parse_expression()
        self.expect(TokenType.LBRACE)
        
        body: List[ASTNode] = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
        
        self.expect(TokenType.RBRACE)
        
        return ForNode(variable=var_name, iterable=iterable, body=body, line=line)
    
    def parse_function_def(self) -> FunctionDefNode:
        """
        Parse function definition: kaam name(params) { statements }.
        
        Returns:
            FunctionDefNode with name, parameters, and body
            
        Examples:
            >>> # kaam add(a, b) { wapas a + b }
            >>> func = parser.parse_function_def()
            >>> func.name
            'add'
            >>> func.parameters
            ['a', 'b']
        """
        line = self.current_token.line
        self.expect(TokenType.FUNCTION)
        
        if not self.match(TokenType.IDENTIFIER):
            raise ParserError.expected_identifier(
                line=self.current_token.line,
                column=self.current_token.column,
                language=self.error_language
            )
        
        func_name = self.current_token.value
        self.advance()
        
        self.expect(TokenType.LPAREN)
        
        params: List[str] = []
        if not self.match(TokenType.RPAREN):
            if not self.match(TokenType.IDENTIFIER):
                raise ParserError.expected_identifier(
                    line=self.current_token.line,
                    column=self.current_token.column,
                    language=self.error_language
                )
            
            params.append(self.current_token.value)
            self.advance()
            
            while self.match(TokenType.COMMA):
                self.advance()
                if not self.match(TokenType.IDENTIFIER):
                    raise ParserError.expected_identifier(
                        line=self.current_token.line,
                        column=self.current_token.column,
                        language=self.error_language
                    )
                params.append(self.current_token.value)
                self.advance()
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        
        body: List[ASTNode] = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
        
        self.expect(TokenType.RBRACE)
        
        return FunctionDefNode(name=func_name, parameters=params, body=body, line=line)
    
    def parse_return(self) -> ReturnNode:
        """
        Parse return statement: wapas [value].
        
        Returns:
            ReturnNode with optional return value
            
        Examples:
            >>> # wapas 42
            >>> ret = parser.parse_return()
            >>> ret.value.value
            42
            
            >>> # wapas (no value)
            >>> ret = parser.parse_return()
            >>> ret.value is None
            True
        """
        line = self.current_token.line
        self.expect(TokenType.RETURN)
        
        # Check if return has a value
        value: Optional[ASTNode] = None
        if not self.match(TokenType.RBRACE, TokenType.EOF):
            value = self.parse_expression()
        
        return ReturnNode(value=value, line=line)
    
    def parse_class_def(self) -> ClassDefNode:
        """
        Parse class definition: class Name [badhaao Parent] { methods }.
        
        Returns:
            ClassDefNode with name, optional parent, and methods
            
        Examples:
            >>> # class Person { kaam greet() { likho("Hi") } }
            >>> cls = parser.parse_class_def()
            >>> cls.name
            'Person'
            >>> len(cls.methods)
            1
        """
        line = self.current_token.line
        self.expect(TokenType.CLASS)
        
        if not self.match(TokenType.IDENTIFIER):
            raise ParserError.expected_identifier(
                line=self.current_token.line,
                column=self.current_token.column,
                language=self.error_language
            )
        
        class_name = self.current_token.value
        self.advance()
        
        # Optional inheritance: badhaao ParentClass
        parent: Optional[str] = None
        if self.match(TokenType.EXTENDS):
            self.advance()
            if not self.match(TokenType.IDENTIFIER):
                raise ParserError.expected_identifier(
                    line=self.current_token.line,
                    column=self.current_token.column,
                    language=self.error_language
                )
            parent = self.current_token.value
            self.advance()
        
        self.expect(TokenType.LBRACE)
        
        methods: List[FunctionDefNode] = []
        while not self.match(TokenType.RBRACE):
            if self.match(TokenType.FUNCTION):
                methods.append(self.parse_function_def())
            else:
                raise ParserError.unexpected_token(
                    token=self.current_token.value,
                    line=self.current_token.line,
                    column=self.current_token.column,
                    language=self.error_language
                )
        
        self.expect(TokenType.RBRACE)
        
        return ClassDefNode(name=class_name, parent=parent, methods=methods, line=line)
    
    def parse_try(self) -> TryNode:
        """
        Parse try-catch-finally: koshish { } pakdo var { } [akhir { }].
        
        Returns:
            TryNode with try block, optional catch, and optional finally
            
        Examples:
            >>> # koshish { risky() } pakdo e { likho(e) } akhir { cleanup() }
            >>> try_stmt = parser.parse_try()
            >>> len(try_stmt.try_block) > 0
            True
        """
        line = self.current_token.line
        self.expect(TokenType.TRY)
        
        # Parse try block
        self.expect(TokenType.LBRACE)
        try_block: List[ASTNode] = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt is not None:
                try_block.append(stmt)
        self.expect(TokenType.RBRACE)
        
        # Optional catch block
        exception_var: Optional[str] = None
        catch_block: Optional[List[ASTNode]] = None
        
        if self.match(TokenType.CATCH):
            self.advance()
            
            # Optional exception variable
            if self.match(TokenType.IDENTIFIER):
                exception_var = self.current_token.value
                self.advance()
            
            self.expect(TokenType.LBRACE)
            catch_block = []
            while not self.match(TokenType.RBRACE):
                stmt = self.parse_statement()
                if stmt is not None:
                    catch_block.append(stmt)
            self.expect(TokenType.RBRACE)
        
        # Optional finally block
        finally_block: Optional[List[ASTNode]] = None
        if self.match(TokenType.FINALLY):
            self.advance()
            self.expect(TokenType.LBRACE)
            finally_block = []
            while not self.match(TokenType.RBRACE):
                stmt = self.parse_statement()
                if stmt is not None:
                    finally_block.append(stmt)
            self.expect(TokenType.RBRACE)
        
        return TryNode(
            try_block=try_block,
            exception_var=exception_var,
            catch_block=catch_block,
            finally_block=finally_block,
            line=line
        )
    
    def parse_throw(self) -> ThrowNode:
        """
        Parse throw statement: fenko expression.
        
        Returns:
            ThrowNode with exception expression
            
        Examples:
            >>> # fenko "Error occurred"
            >>> throw_stmt = parser.parse_throw()
            >>> isinstance(throw_stmt.exception, StringNode)
            True
        """
        line = self.current_token.line
        self.expect(TokenType.THROW)
        
        exception = self.parse_expression()
        
        return ThrowNode(exception=exception, line=line)
    
    def parse_import(self) -> ImportNode:
        """
        Parse import statement: lao "filename".
        
        Returns:
            ImportNode with module name
            
        Examples:
            >>> # lao "math_lib"
            >>> import_stmt = parser.parse_import()
            >>> import_stmt.module_name
            'math_lib'
        """
        line = self.current_token.line
        self.expect(TokenType.IMPORT)
        
        if not self.match(TokenType.STRING):
            raise ParserError(
                message="Expected filename string after 'lao'",
                line=self.current_token.line,
                column=self.current_token.column,
                language=self.error_language
            )
        
        module_name = self.current_token.value
        self.advance()
        
        return ImportNode(module_name=module_name, line=line)
    
    def parse_assignment_or_expression(self) -> ASTNode:
        """
        Parse assignment, property assignment, index assignment, or expression.
        
        Handles:
        - Simple assignment: x = value
        - Property assignment: obj.prop = value
        - Index assignment: arr[0] = value
        - Method calls: obj.method()
        - Function calls: func()
        
        Returns:
            Appropriate AST node based on syntax
            
        Examples:
            >>> # x = 42
            >>> node = parser.parse_assignment_or_expression()
            >>> isinstance(node, AssignmentNode)
            True
            
            >>> # person.name = "Ahmed"
            >>> node = parser.parse_assignment_or_expression()
            >>> isinstance(node, PropertyAssignmentNode)
            True
        """
        line = self.current_token.line
        
        # Handle 'this' keyword
        if self.match(TokenType.THIS):
            self.advance()
            
            # yeh.property = value
            if self.match(TokenType.DOT):
                self.advance()
                if not self.match(TokenType.IDENTIFIER):
                    raise ParserError(
                        message="Expected property name after 'yeh.'",
                        line=self.current_token.line,
                        column=self.current_token.column,
                        language=self.error_language
                    )
                
                property_name = self.current_token.value
                self.advance()
                
                self.expect(TokenType.ASSIGN)
                value = self.parse_expression()
                
                return PropertyAssignmentNode(
                    object=ThisNode(line=line),
                    property_name=property_name,
                    value=value,
                    line=line
                )
            
            # Just 'yeh' by itself (shouldn't happen at statement level)
            raise ParserError(
                message="Unexpected 'yeh' keyword",
                line=line,
                column=self.current_token.column,
                language=self.error_language
            )
        
        # Must be identifier
        if not self.match(TokenType.IDENTIFIER):
            # This is an expression, not a statement
            return self.parse_expression()
        
        name = self.current_token.value
        self.advance()
        
        # Property assignment: obj.property = value
        if self.match(TokenType.DOT):
            self.advance()
            if not self.match(TokenType.IDENTIFIER):
                raise ParserError(
                    message="Expected property name after '.'",
                    line=self.current_token.line,
                    column=self.current_token.column,
                    language=self.error_language
                )
            
            property_name = self.current_token.value
            self.advance()
            
            # Method call: obj.method()
            if self.match(TokenType.LPAREN):
                self.advance()
                args: List[ASTNode] = []
                if not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        args.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                return MethodCallNode(
                    object=VariableNode(name=name, line=line),
                    method_name=property_name,
                    arguments=args,
                    line=line
                )
            
            # Property assignment: obj.property = value
            self.expect(TokenType.ASSIGN)
            value = self.parse_expression()
            return PropertyAssignmentNode(
                object=VariableNode(name=name, line=line),
                property_name=property_name,
                value=value,
                line=line
            )
        
        # Index assignment: arr[0] = value
        if self.match(TokenType.LBRACKET):
            self.advance()
            index = self.parse_expression()
            self.expect(TokenType.RBRACKET)
            self.expect(TokenType.ASSIGN)
            value = self.parse_expression()
            return IndexAssignmentNode(
                object=VariableNode(name=name, line=line),
                index=index,
                value=value,
                line=line
            )
        
        # Simple assignment: var = value
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
            return AssignmentNode(name=name, value=value, line=line)
        
        # Function call: func(args)
        if self.match(TokenType.LPAREN):
            self.advance()
            args = []
            if not self.match(TokenType.RPAREN):
                args.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    args.append(self.parse_expression())
            self.expect(TokenType.RPAREN)
            return FunctionCallNode(name=name, arguments=args, line=line)
        
        raise ParserError(
            message=f"Expected '=', '[', '(', or '.' after identifier '{name}'",
            line=self.current_token.line,
            column=self.current_token.column,
            language=self.error_language
        )
    
    # ========================================================================
    # Expression Parsing (with proper precedence)
    # ========================================================================
    
    def parse_expression(self) -> ASTNode:
        """
        Parse expression (entry point for expression parsing).
        
        Returns:
            AST node for the expression
            
        Examples:
            >>> expr = parser.parse_expression()
            >>> # Handles: 1 + 2 * 3, x ya y, nahi flag, etc.
        """
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> ASTNode:
        """
        Parse logical OR: expr ya expr.
        
        Precedence: Lowest (except assignment)
        
        Returns:
            BinaryOpNode with 'ya' operator or lower precedence node
        """
        left = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            op_line = self.current_token.line
            self.advance()
            right = self.parse_logical_and()
            left = BinaryOpNode(operator="ya", left=left, right=right, line=op_line)
        
        return left
    
    def parse_logical_and(self) -> ASTNode:
        """
        Parse logical AND: expr aur expr.
        
        Precedence: Higher than OR, lower than equality
        
        Returns:
            BinaryOpNode with 'aur' operator or lower precedence node
        """
        left = self.parse_equality()
        
        while self.match(TokenType.AND):
            op_line = self.current_token.line
            self.advance()
            right = self.parse_equality()
            left = BinaryOpNode(operator="aur", left=left, right=right, line=op_line)
        
        return left
    
    def parse_equality(self) -> ASTNode:
        """
        Parse equality: expr == expr, expr != expr.
        
        Precedence: Higher than logical operators, lower than comparison
        
        Returns:
            BinaryOpNode with '==' or '!=' operator or lower precedence node
        """
        left = self.parse_comparison()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.current_token.value
            op_line = self.current_token.line
            self.advance()
            right = self.parse_comparison()
            left = BinaryOpNode(operator=operator, left=left, right=right, line=op_line)
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        """
        Parse comparison: <, >, <=, >=.
        
        Precedence: Higher than equality, lower than addition
        
        Returns:
            BinaryOpNode with comparison operator or lower precedence node
        """
        left = self.parse_addition()
        
        while self.match(TokenType.LESS, TokenType.GREATER, 
                         TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            operator = self.current_token.value
            op_line = self.current_token.line
            self.advance()
            right = self.parse_addition()
            left = BinaryOpNode(operator=operator, left=left, right=right, line=op_line)
        
        return left
    
    def parse_addition(self) -> ASTNode:
        """
        Parse addition and subtraction: +, -.
        
        Precedence: Higher than comparison, lower than multiplication
        
        Returns:
            BinaryOpNode with '+' or '-' operator or lower precedence node
        """
        left = self.parse_multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.current_token.value
            op_line = self.current_token.line
            self.advance()
            right = self.parse_multiplication()
            left = BinaryOpNode(operator=operator, left=left, right=right, line=op_line)
        
        return left
    
    def parse_multiplication(self) -> ASTNode:
        """
        Parse multiplication, division, modulo: *, /, %.
        
        Precedence: Higher than addition, lower than unary
        
        Returns:
            BinaryOpNode with '*', '/', or '%' operator or lower precedence node
        """
        left = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.current_token.value
            op_line = self.current_token.line
            self.advance()
            right = self.parse_unary()
            left = BinaryOpNode(operator=operator, left=left, right=right, line=op_line)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """
        Parse unary operators: -expr (negation), nahi expr (NOT).
        
        Precedence: Higher than binary operators, lower than postfix
        
        Returns:
            UnaryOpNode or lower precedence node
            
        Examples:
            >>> # -42
            >>> expr = parser.parse_unary()
            >>> expr.operator
            '-'
            
            >>> # nahi flag
            >>> expr = parser.parse_unary()
            >>> expr.operator
            'nahi'
        """
        # Negation: -expr
        if self.match(TokenType.MINUS):
            op_line = self.current_token.line
            self.advance()
            operand = self.parse_unary()  # Right-associative
            return UnaryOpNode(operator="-", operand=operand, line=op_line)
        
        # Logical NOT: nahi expr
        if self.match(TokenType.NOT):
            op_line = self.current_token.line
            self.advance()
            operand = self.parse_unary()  # Right-associative
            return UnaryOpNode(operator="nahi", operand=operand, line=op_line)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ASTNode:
        """
        Parse postfix expressions: function calls, property access, indexing.
        
        Handles:
        - func(args)
        - obj.property
        - obj.method(args)
        - arr[index]
        
        Returns:
            FunctionCallNode, PropertyAccessNode, MethodCallNode, or IndexNode
            
        Examples:
            >>> # person.name
            >>> expr = parser.parse_postfix()
            >>> isinstance(expr, PropertyAccessNode)
            True
            
            >>> # arr[0]
            >>> expr = parser.parse_postfix()
            >>> isinstance(expr, IndexNode)
            True
        """
        expr = self.parse_primary()
        
        while True:
            # Function call: expr(args)
            if self.match(TokenType.LPAREN):
                if not isinstance(expr, VariableNode):
                    raise ParserError(
                        message="Only identifiers can be called as functions",
                        line=self.current_token.line,
                        column=self.current_token.column,
                        language=self.error_language
                    )
                
                line = self.current_token.line
                self.advance()
                
                args: List[ASTNode] = []
                if not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        args.append(self.parse_expression())
                
                self.expect(TokenType.RPAREN)
                expr = FunctionCallNode(name=expr.name, arguments=args, line=line)
            
            # Index access: expr[index]
            elif self.match(TokenType.LBRACKET):
                line = self.current_token.line
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = IndexNode(object=expr, index=index, line=line)
            
            # Property/Method access: expr.property or expr.method(args)
            elif self.match(TokenType.DOT):
                line = self.current_token.line
                self.advance()
                
                if not self.match(TokenType.IDENTIFIER):
                    raise ParserError(
                        message="Expected property or method name after '.'",
                        line=self.current_token.line,
                        column=self.current_token.column,
                        language=self.error_language
                    )
                
                member_name = self.current_token.value
                self.advance()
                
                # Method call: expr.method(args)
                if self.match(TokenType.LPAREN):
                    self.advance()
                    args = []
                    if not self.match(TokenType.RPAREN):
                        args.append(self.parse_expression())
                        while self.match(TokenType.COMMA):
                            self.advance()
                            args.append(self.parse_expression())
                    self.expect(TokenType.RPAREN)
                    expr = MethodCallNode(
                        object=expr,
                        method_name=member_name,
                        arguments=args,
                        line=line
                    )
                else:
                    # Property access: expr.property
                    expr = PropertyAccessNode(
                        object=expr,
                        property_name=member_name,
                        line=line
                    )
            
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ASTNode:
        """
        Parse primary expressions (atoms).
        
        Handles:
        - Number literals: 42, 3.14
        - String literals: "hello"
        - Boolean literals: sach, jhoot
        - Identifiers: variable names
        - List literals: [1, 2, 3]
        - Dict literals: {key: value}
        - Parenthesized expressions: (expr)
        - Object instantiation: naya Class(args)
        - Lambda functions: lambada x: x * 2
        - this keyword: yeh
        - super keyword: upar
        
        Returns:
            Appropriate AST node for the primary expression
            
        Raises:
            ParserError: If no valid primary expression
            
        Examples:
            >>> # 42
            >>> expr = parser.parse_primary()
            >>> isinstance(expr, NumberNode)
            True
            
            >>> # "hello"
            >>> expr = parser.parse_primary()
            >>> isinstance(expr, StringNode)
            True
            
            >>> # (1 + 2)
            >>> expr = parser.parse_primary()
            >>> isinstance(expr, ParenthesizedNode)
            True
        """
        line = self.current_token.line
        
        # Number literal (int or float)
        if self.match(TokenType.NUMBER):
            value = self.current_token.value
            self.advance()
            return NumberNode(value=value, line=line)
        
        # String literal
        if self.match(TokenType.STRING):
            value = self.current_token.value
            self.advance()
            return StringNode(value=value, line=line)
        
        # Boolean literal
        if self.match(TokenType.BOOLEAN):
            value = self.current_token.value
            self.advance()
            return BooleanNode(value=value, line=line)
        
        # List literal: [...]
        if self.match(TokenType.LBRACKET):
            return self.parse_list()
        
        # Dict literal: {...}
        if self.match(TokenType.LBRACE):
            return self.parse_dict()
        
        # Object instantiation: naya Class(args)
        if self.match(TokenType.NEW):
            return self.parse_new_object()
        
        # Lambda function: lambada params: expr
        if self.match(TokenType.LAMBDA):
            return self.parse_lambda()
        
        # This keyword: yeh
        if self.match(TokenType.THIS):
            self.advance()
            return ThisNode(line=line)
        
        # Super keyword: upar
        if self.match(TokenType.SUPER):
            return self.parse_super()
        
        # Identifier (variable reference)
        if self.match(TokenType.IDENTIFIER):
            name = self.current_token.value
            self.advance()
            return VariableNode(name=name, line=line)
        
        # Parenthesized expression: (expr)
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return ParenthesizedNode(expression=expr, line=line)
        
        raise ParserError.unexpected_token(
            expected="expression",
            got=str(self.current_token.value),
            line=self.current_token.line,
            column=self.current_token.column,
        )
    
    def parse_list(self) -> ListNode:
        """
        Parse list literal: [element1, element2, ...].
        
        Returns:
            ListNode with list of element expressions
            
        Examples:
            >>> # [1, 2, 3]
            >>> list_node = parser.parse_list()
            >>> len(list_node.elements)
            3
        """
        line = self.current_token.line
        self.expect(TokenType.LBRACKET)
        
        elements: List[ASTNode] = []
        if not self.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                # Allow trailing comma
                if self.match(TokenType.RBRACKET):
                    break
                elements.append(self.parse_expression())
        
        self.expect(TokenType.RBRACKET)
        return ListNode(elements=elements, line=line)
    
    def parse_dict(self) -> DictNode:
        """
        Parse dictionary literal: {key1: value1, key2: value2, ...}.
        
        Returns:
            DictNode with list of (key, value) pairs
            
        Examples:
            >>> # {name: "Ahmed", age: 25}
            >>> dict_node = parser.parse_dict()
            >>> len(dict_node.pairs)
            2
        """
        line = self.current_token.line
        self.expect(TokenType.LBRACE)
        
        pairs: List[tuple[ASTNode, ASTNode]] = []
        if not self.match(TokenType.RBRACE):
            # Parse first pair
            key = self.parse_expression()
            self.expect(TokenType.COLON)
            value = self.parse_expression()
            pairs.append((key, value))
            
            while self.match(TokenType.COMMA):
                self.advance()
                # Allow trailing comma
                if self.match(TokenType.RBRACE):
                    break
                key = self.parse_expression()
                self.expect(TokenType.COLON)
                value = self.parse_expression()
                pairs.append((key, value))
        
        self.expect(TokenType.RBRACE)
        return DictNode(pairs=pairs, line=line)
    
    def parse_new_object(self) -> NewObjectNode:
        """
        Parse object instantiation: naya ClassName(args).
        
        Returns:
            NewObjectNode with class name and constructor arguments
            
        Examples:
            >>> # naya Person("Ahmed", 25)
            >>> obj = parser.parse_new_object()
            >>> obj.class_name
            'Person'
            >>> len(obj.arguments)
            2
        """
        line = self.current_token.line
        self.expect(TokenType.NEW)
        
        if not self.match(TokenType.IDENTIFIER):
            raise ParserError.expected_identifier(
                line=self.current_token.line,
                column=self.current_token.column,
                language=self.error_language
            )
        
        class_name = self.current_token.value
        self.advance()
        
        # Constructor arguments
        arguments: List[ASTNode] = []
        if self.match(TokenType.LPAREN):
            self.advance()
            if not self.match(TokenType.RPAREN):
                arguments.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    arguments.append(self.parse_expression())
            self.expect(TokenType.RPAREN)
        
        return NewObjectNode(class_name=class_name, arguments=arguments, line=line)
    
    def parse_lambda(self) -> LambdaNode:
        """
        Parse lambda function: lambada x: x * 2 or lambada x, y: x + y.
        
        Returns:
            LambdaNode with parameters and body expression
            
        Examples:
            >>> # lambada x: x * 2
            >>> lambda_node = parser.parse_lambda()
            >>> lambda_node.parameters
            ['x']
            >>> isinstance(lambda_node.body, BinaryOpNode)
            True
        """
        line = self.current_token.line
        self.expect(TokenType.LAMBDA)
        
        # Parse parameters
        params: List[str] = []
        if self.match(TokenType.IDENTIFIER):
            params.append(self.current_token.value)
            self.advance()
            
            while self.match(TokenType.COMMA):
                self.advance()
                if not self.match(TokenType.IDENTIFIER):
                    raise ParserError.expected_identifier(
                        line=self.current_token.line,
                        column=self.current_token.column,
                        language=self.error_language
                    )
                params.append(self.current_token.value)
                self.advance()
        
        self.expect(TokenType.COLON)
        
        # Parse body (single expression)
        body = self.parse_expression()
        
        return LambdaNode(parameters=params, body=body, line=line)
    
    def parse_super(self) -> SuperNode:
        """
        Parse super method call: upar.method(args).
        
        Returns:
            SuperNode with method name and arguments
            
        Examples:
            >>> # upar.greet("Hi")
            >>> super_node = parser.parse_super()
            >>> super_node.method_name
            'greet'
        """
        line = self.current_token.line
        self.expect(TokenType.SUPER)
        
        self.expect(TokenType.DOT)
        
        if not self.match(TokenType.IDENTIFIER):
            raise ParserError(
                message="Expected method name after 'upar.'",
                line=self.current_token.line,
                column=self.current_token.column,
                language=self.error_language
            )
        
        method_name = self.current_token.value
        self.advance()
        
        # Parse arguments
        arguments: List[ASTNode] = []
        if self.match(TokenType.LPAREN):
            self.advance()
            if not self.match(TokenType.RPAREN):
                arguments.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    arguments.append(self.parse_expression())
            self.expect(TokenType.RPAREN)
        
        return SuperNode(method_name=method_name, arguments=arguments, line=line)


def parse_MeriLang(code: str, error_language: ErrorLanguage = ErrorLanguage.ENGLISH) -> ProgramNode:
    """
    Convenience function to tokenize and parse MeriLang code.
    
    Args:
        code: MeriLang source code
        error_language: Language for error messages
        
    Returns:
        ProgramNode (AST root)
        
    Raises:
        LexerError: If tokenization fails
        ParserError: If parsing fails
        
    Examples:
        >>> ast = parse_MeriLang("maan x = 42\\nlikho(x)")
        >>> len(ast.statements)
        2
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, error_language)
    return parser.parse()

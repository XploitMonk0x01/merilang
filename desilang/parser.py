"""
Parser for DesiLang - Production version.
Implements a recursive descent parser with precedence climbing for expressions.
"""

from typing import List, Optional
from .lexer import Token, TokenType
from .ast_nodes import *
from .errors import ParserError


class Parser:
    """Recursive descent parser for DesiLang."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else Token(TokenType.EOF, None, 1, 1)
    
    def error(self, message: str) -> None:
        """Raise a parser error at current token position."""
        raise ParserError(message, self.current_token.line, self.current_token.column)
    
    def advance(self) -> Token:
        """Move to next token and return previous."""
        prev_token = self.current_token
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current_token = self.tokens[self.pos]
        return prev_token
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """Look ahead at next token(s) without advancing."""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, token_type: TokenType) -> Token:
        """Consume a token of expected type or raise error."""
        if self.current_token.type != token_type:
            self.error(f"Expected {token_type.name}, got {self.current_token.type.name}")
        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current_token.type in token_types
    
    def parse(self) -> ProgramNode:
        """Parse the entire program."""
        return self.parse_program()
    
    def parse_program(self) -> ProgramNode:
        """
        Program: START statement* END
        """
        start_line = self.current_token.line
        self.expect(TokenType.START)  # shuru
        
        statements = []
        while not self.match(TokenType.END, TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.expect(TokenType.END)  # khatam
        
        return ProgramNode(statements=statements, line=start_line)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement."""
        # Print statement
        if self.match(TokenType.PRINT):
            return self.parse_print()
        
        # Input statement
        if self.match(TokenType.INPUT):
            return self.parse_input()
        
        # If statement
        if self.match(TokenType.IF):
            return self.parse_if()
        
        # While loop
        if self.match(TokenType.WHILE):
            return self.parse_while()
        
        # For loop
        if self.match(TokenType.FOR):
            return self.parse_for()
        
        # Function definition
        if self.match(TokenType.FUNCTION):
            return self.parse_function_def()
        
        # Function call with bulayo
        if self.match(TokenType.CALL):
            return self.parse_function_call_stmt()
        
        # Return statement
        if self.match(TokenType.RETURN):
            return self.parse_return()
        
        # Import statement
        if self.match(TokenType.IMPORT):
            return self.parse_import()
        
        # File write
        if self.match(TokenType.WRITE_FILE):
            return self.parse_write_file()
        
        # Class definition
        if self.match(TokenType.CLASS):
            return self.parse_class_def()
        
        # Try-catch-finally
        if self.match(TokenType.TRY):
            return self.parse_try()
        
        # Throw statement
        if self.match(TokenType.THROW):
            return self.parse_throw()
        
        # This property assignment: yeh.property = value
        if self.match(TokenType.THIS):
            return self.parse_this_property_assignment()
        
        # Super method call as statement: upar.method()
        if self.match(TokenType.SUPER):
            return self.parse_super()
        
        # Assignment or index assignment
        if self.match(TokenType.IDENTIFIER):
            return self.parse_assignment_or_call()
        
        self.error(f"Unexpected token: {self.current_token.type.name}")
    
    def parse_print(self) -> PrintNode:
        """Parse print statement: dikhao <expression>"""
        line = self.current_token.line
        self.expect(TokenType.PRINT)
        expr = self.parse_expression()
        return PrintNode(expression=expr, line=line)
    
    def parse_input(self) -> InputNode:
        """Parse input statement: padho <variable>"""
        line = self.current_token.line
        self.expect(TokenType.INPUT)
        
        if not self.match(TokenType.IDENTIFIER):
            self.error("Expected variable name after 'padho'")
        
        var_name = self.current_token.value
        self.advance()
        
        return InputNode(variable=var_name, line=line)
    
    def parse_if(self) -> IfNode:
        """Parse if-else statement: agar <condition> { statements } [warna { statements }] bas"""
        line = self.current_token.line
        self.expect(TokenType.IF)
        
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        
        then_branch = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                then_branch.append(stmt)
        
        self.expect(TokenType.RBRACE)
        
        else_branch = None
        if self.match(TokenType.ELSE):
            self.advance()
            self.expect(TokenType.LBRACE)
            
            else_branch = []
            while not self.match(TokenType.RBRACE):
                stmt = self.parse_statement()
                if stmt:
                    else_branch.append(stmt)
            
            self.expect(TokenType.RBRACE)
        
        self.expect(TokenType.ENDIF)  # bas
        
        return IfNode(condition=condition, then_branch=then_branch, else_branch=else_branch, line=line)
    
    def parse_while(self) -> WhileNode:
        """Parse while loop: jabtak <condition> { statements } band"""
        line = self.current_token.line
        self.expect(TokenType.WHILE)
        
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        
        body = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.expect(TokenType.RBRACE)
        self.expect(TokenType.ENDWHILE)  # band
        
        return WhileNode(condition=condition, body=body, line=line)
    
    def parse_for(self) -> ForNode:
        """Parse for loop: chalao <var> se <start> tak <end> { statements }"""
        line = self.current_token.line
        self.expect(TokenType.FOR)
        
        if not self.match(TokenType.IDENTIFIER):
            self.error("Expected variable name after 'chalao'")
        
        var_name = self.current_token.value
        self.advance()
        
        self.expect(TokenType.FROM)  # se
        start_expr = self.parse_expression()
        
        self.expect(TokenType.TO)  # tak
        end_expr = self.parse_expression()
        
        self.expect(TokenType.LBRACE)
        
        body = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.expect(TokenType.RBRACE)
        
        return ForNode(variable=var_name, start=start_expr, end=end_expr, body=body, line=line)
    
    def parse_function_def(self) -> FunctionDefNode:
        """Parse function definition: vidhi <name> ( <params> ) { statements } samapt"""
        line = self.current_token.line
        self.expect(TokenType.FUNCTION)
        
        if not self.match(TokenType.IDENTIFIER):
            self.error("Expected function name after 'vidhi'")
        
        func_name = self.current_token.value
        self.advance()
        
        self.expect(TokenType.LPAREN)
        
        params = []
        if not self.match(TokenType.RPAREN):
            params.append(self.expect(TokenType.IDENTIFIER).value)
            
            while self.match(TokenType.COMMA):
                self.advance()
                params.append(self.expect(TokenType.IDENTIFIER).value)
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        
        body = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.expect(TokenType.RBRACE)
        self.expect(TokenType.ENDFUNC)  # samapt
        
        return FunctionDefNode(name=func_name, parameters=params, body=body, line=line)
    
    def parse_function_call_stmt(self) -> FunctionCallNode:
        """Parse function call as statement: bulayo <name> ( <args> )"""
        line = self.current_token.line
        self.expect(TokenType.CALL)
        
        if not self.match(TokenType.IDENTIFIER):
            self.error("Expected function name after 'bulayo'")
        
        func_name = self.current_token.value
        self.advance()
        
        self.expect(TokenType.LPAREN)
        
        args = []
        if not self.match(TokenType.RPAREN):
            args.append(self.parse_expression())
            
            while self.match(TokenType.COMMA):
                self.advance()
                args.append(self.parse_expression())
        
        self.expect(TokenType.RPAREN)
        
        return FunctionCallNode(name=func_name, arguments=args, line=line)
    
    def parse_return(self) -> ReturnNode:
        """Parse return statement: vapas [<expression>]"""
        line = self.current_token.line
        self.expect(TokenType.RETURN)
        
        # Return can be empty or have a value
        value = None
        if not self.match(TokenType.RBRACE, TokenType.EOF):
            # Check if next token could start an expression
            if not self.match(TokenType.ENDFUNC, TokenType.ENDIF, TokenType.ENDWHILE):
                value = self.parse_expression()
        
        return ReturnNode(value=value, line=line)
    
    def parse_import(self) -> ImportNode:
        """Parse import statement: lao "<filename>" """
        line = self.current_token.line
        self.expect(TokenType.IMPORT)
        
        if not self.match(TokenType.STRING):
            self.error("Expected filename string after 'lao'")
        
        filename = self.current_token.value
        self.advance()
        
        return ImportNode(filename=filename, line=line)
    
    def parse_write_file(self) -> FunctionCallNode:
        """Parse file write: likho "<filename>" <content>"""
        line = self.current_token.line
        self.expect(TokenType.WRITE_FILE)
        
        if not self.match(TokenType.STRING):
            self.error("Expected filename string after 'likho'")
        
        filename = StringNode(value=self.current_token.value, line=self.current_token.line)
        self.advance()
        
        content = self.parse_expression()
        
        # Convert to function call node for consistency
        return FunctionCallNode(name='likho', arguments=[filename, content], line=line)
    
    def parse_assignment_or_call(self) -> ASTNode:
        """Parse assignment or expression (could be function call)."""
        line = self.current_token.line
        name = self.current_token.value
        self.advance()
        
        # Property assignment or method call: obj.property = value OR obj.method()
        if self.match(TokenType.DOT):
            self.advance()
            if not self.match(TokenType.IDENTIFIER):
                self.error("Expected property name or method name after '.'")
            member_name = self.current_token.value
            self.advance()
            
            # Method call: obj.method()
            if self.match(TokenType.LPAREN):
                self.advance()
                args = []
                if not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        args.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                return MethodCallNode(
                    object_expr=VariableNode(name=name, line=line),
                    method_name=member_name,
                    arguments=args,
                    line=line
                )
            
            # Property assignment: obj.property = value
            self.expect(TokenType.ASSIGN)
            value = self.parse_expression()
            return PropertyAssignmentNode(
                object_expr=VariableNode(name=name, line=line),
                property_name=member_name,
                value=value,
                line=line
            )
        
        # Index assignment: var[index] = value
        if self.match(TokenType.LBRACKET):
            self.advance()
            index = self.parse_expression()
            self.expect(TokenType.RBRACKET)
            self.expect(TokenType.ASSIGN)
            value = self.parse_expression()
            return IndexAssignmentNode(list_name=name, index=index, value=value, line=line)
        
        # Regular assignment: var = value
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
            return AssignmentNode(name=name, value=value, line=line)
        
        # Function call without bulayo: func(args)
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
        
        self.error(f"Expected '=', '[', or '(' after identifier '{name}'")
    
    def parse_expression(self) -> ASTNode:
        """Parse expression with proper precedence."""
        return self.parse_comparison()
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparison operators: ==, !=, <, >, <=, >="""
        left = self.parse_additive()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS, 
                         TokenType.GREATER, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            op_token = self.current_token
            operator = op_token.value
            self.advance()
            right = self.parse_additive()
            left = BinaryOpNode(operator=operator, left=left, right=right, line=op_token.line)
        
        return left
    
    def parse_additive(self) -> ASTNode:
        """Parse addition and subtraction: +, -"""
        left = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_token = self.current_token
            operator = op_token.value
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOpNode(operator=operator, left=left, right=right, line=op_token.line)
        
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        """Parse multiplication, division, and modulo: *, /, %"""
        left = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op_token = self.current_token
            operator = op_token.value
            self.advance()
            right = self.parse_unary()
            left = BinaryOpNode(operator=operator, left=left, right=right, line=op_token.line)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """Parse unary operators: - (negation)"""
        if self.match(TokenType.MINUS):
            op_token = self.current_token
            self.advance()
            operand = self.parse_unary()
            return UnaryOpNode(operator='-', operand=operand, line=op_token.line)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ASTNode:
        """Parse postfix expressions: function calls, index access."""
        expr = self.parse_primary()
        
        while True:
            # Function call: expr(args)
            if self.match(TokenType.LPAREN):
                if not isinstance(expr, VariableNode):
                    self.error("Only identifiers can be called as functions")
                
                line = self.current_token.line
                self.advance()
                
                args = []
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
                expr = IndexAccessNode(list_expr=expr, index=index, line=line)
            
            # Property/Method access: expr.property or expr.method(args)
            elif self.match(TokenType.DOT):
                line = self.current_token.line
                self.advance()
                if not self.match(TokenType.IDENTIFIER):
                    self.error("Expected property or method name after '.'")
                
                member_name = self.current_token.value
                self.advance()
                
                # Check if it's a method call
                if self.match(TokenType.LPAREN):
                    self.advance()
                    args = []
                    if not self.match(TokenType.RPAREN):
                        args.append(self.parse_expression())
                        while self.match(TokenType.COMMA):
                            self.advance()
                            args.append(self.parse_expression())
                    self.expect(TokenType.RPAREN)
                    expr = MethodCallNode(object_expr=expr, method_name=member_name, arguments=args, line=line)
                else:
                    # Property access
                    expr = PropertyAccessNode(object_expr=expr, property_name=member_name, line=line)
            
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ASTNode:
        """Parse primary expressions: literals, variables, parenthesized expressions."""
        line = self.current_token.line
        
        # Number literal
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
        
        # List literal
        if self.match(TokenType.LBRACKET):
            return self.parse_list()
        
        # Object instantiation: naya ClassName(args)
        if self.match(TokenType.NEW):
            return self.parse_new_object()
        
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
        
        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        self.error(f"Unexpected token in expression: {self.current_token.type.name}")
    
    def parse_list(self) -> ListNode:
        """Parse list literal: [expr, expr, ...]"""
        line = self.current_token.line
        self.expect(TokenType.LBRACKET)
        
        elements = []
        if not self.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                elements.append(self.parse_expression())
        
        self.expect(TokenType.RBRACKET)
        return ListNode(elements=elements, line=line)
    
    # OOP Parsing Methods
    def parse_class_def(self) -> ClassDefNode:
        """Parse class definition: class ClassName [badhaao ParentClass] { methods }"""
        line = self.current_token.line
        self.expect(TokenType.CLASS)
        
        if not self.match(TokenType.IDENTIFIER):
            self.error("Expected class name")
        
        class_name = self.current_token.value
        self.advance()
        
        # Check for inheritance
        parent = None
        if self.match(TokenType.EXTENDS):
            self.advance()
            if not self.match(TokenType.IDENTIFIER):
                self.error("Expected parent class name after 'badhaao'")
            parent = self.current_token.value
            self.advance()
        
        self.expect(TokenType.LBRACE)
        
        methods = []
        properties = []
        
        # Parse methods (functions inside class)
        while not self.match(TokenType.RBRACE):
            if self.match(TokenType.FUNCTION):
                methods.append(self.parse_function_def())
            else:
                self.error("Expected method definition inside class")
        
        self.expect(TokenType.RBRACE)
        
        return ClassDefNode(
            name=class_name,
            parent=parent,
            methods=methods,
            properties=properties,
            line=line
        )
    
    # Error Handling Parsing Methods
    def parse_try(self) -> TryNode:
        """Parse try-catch-finally: koshish { } pakdo var { } [akhir { }]"""
        line = self.current_token.line
        self.expect(TokenType.TRY)
        
        # Parse try block
        self.expect(TokenType.LBRACE)
        try_block = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                try_block.append(stmt)
        self.expect(TokenType.RBRACE)
        
        # Parse catch block
        catch_var = None
        catch_block = []
        
        if self.match(TokenType.CATCH):
            self.advance()
            
            # Optional: catch variable name
            if self.match(TokenType.IDENTIFIER):
                catch_var = self.current_token.value
                self.advance()
            
            self.expect(TokenType.LBRACE)
            while not self.match(TokenType.RBRACE):
                stmt = self.parse_statement()
                if stmt:
                    catch_block.append(stmt)
            self.expect(TokenType.RBRACE)
        
        # Parse optional finally block
        finally_block = None
        if self.match(TokenType.FINALLY):
            self.advance()
            self.expect(TokenType.LBRACE)
            finally_block = []
            while not self.match(TokenType.RBRACE):
                stmt = self.parse_statement()
                if stmt:
                    finally_block.append(stmt)
            self.expect(TokenType.RBRACE)
        
        return TryNode(
            try_block=try_block,
            catch_var=catch_var,
            catch_block=catch_block,
            finally_block=finally_block,
            line=line
        )
    
    def parse_throw(self) -> ThrowNode:
        """Parse throw statement: fenko <expression>"""
        line = self.current_token.line
        self.expect(TokenType.THROW)
        expr = self.parse_expression()
        return ThrowNode(expression=expr, line=line)
    
    def parse_new_object(self) -> NewObjectNode:
        """Parse object instantiation: naya ClassName(args)"""
        line = self.current_token.line
        self.expect(TokenType.NEW)
        
        if not self.match(TokenType.IDENTIFIER):
            self.error("Expected class name after 'naya'")
        
        class_name = self.current_token.value
        self.advance()
        
        # Parse constructor arguments
        args = []
        if self.match(TokenType.LPAREN):
            self.advance()
            if not self.match(TokenType.RPAREN):
                args.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    args.append(self.parse_expression())
            self.expect(TokenType.RPAREN)
        
        return NewObjectNode(class_name=class_name, arguments=args, line=line)
    
    def parse_super(self) -> SuperNode:
        """Parse super method call: upar.method(args)"""
        line = self.current_token.line
        self.expect(TokenType.SUPER)
        
        self.expect(TokenType.DOT)
        
        if not self.match(TokenType.IDENTIFIER):
            self.error("Expected method name after 'upar.'")
        
        method_name = self.current_token.value
        self.advance()
        
        # Parse arguments
        args = []
        if self.match(TokenType.LPAREN):
            self.advance()
            if not self.match(TokenType.RPAREN):
                args.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    args.append(self.parse_expression())
            self.expect(TokenType.RPAREN)
        
        return SuperNode(method_name=method_name, arguments=args, line=line)
    
    def parse_this_property_assignment(self) -> PropertyAssignmentNode:
        """Parse yeh.property = value"""
        line = self.current_token.line
        self.expect(TokenType.THIS)
        
        self.expect(TokenType.DOT)
        
        if not self.match(TokenType.IDENTIFIER):
            self.error("Expected property name after 'yeh.'")
        
        property_name = self.current_token.value
        self.advance()
        
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        
        return PropertyAssignmentNode(
            object_expr=ThisNode(line=line),
            property_name=property_name,
            value=value,
            line=line
        )

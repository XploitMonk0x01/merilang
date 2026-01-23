"""
Interpreter for DesiLang - Production version.
Executes the AST using the visitor pattern with proper scoping and error handling.
"""

from typing import Any, Dict, List, Optional
import os
import sys
from .ast_nodes import *
from .errors import RuntimeError as DesiRuntimeError, NameError as DesiNameError, \
    TypeError as DesiTypeError, DivisionByZeroError, IndexError as DesiIndexError, FileIOError
from .builtins import BUILTINS, BuiltinFunction


class ReturnValue(Exception):
    """Exception used to implement return statements."""
    def __init__(self, value: Any):
        self.value = value


class DesiException(Exception):
    """Exception used for user-thrown exceptions (fenko)."""
    def __init__(self, message: Any, line: int = 0):
        self.message = message
        self.line = line
        super().__init__(str(message))


class Environment:
    """Represents a scope for variable and function storage."""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
    
    def define(self, name: str, value: Any) -> None:
        """Define a variable in the current scope."""
        self.variables[name] = value
    
    def get(self, name: str) -> Any:
        """Get a variable value, searching parent scopes if necessary."""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise DesiNameError(f"Undefined variable: '{name}'")
    
    def set(self, name: str, value: Any) -> None:
        """Set a variable value, searching parent scopes if necessary."""
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent:
            self.parent.set(name, value)
            return
        # If variable doesn't exist, define it in current scope
        self.define(name, value)
    
    def exists(self, name: str) -> bool:
        """Check if a variable exists in current or parent scopes."""
        if name in self.variables:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False


class UserFunction:
    """Represents a user-defined function."""
    
    def __init__(self, name: str, parameters: List[str], body: List[ASTNode], closure: Environment):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.closure = closure  # Lexical scope for closures


class DesiClass:
    """Represents a class definition."""
    
    def __init__(self, name: str, parent: Optional['DesiClass'], methods: Dict[str, UserFunction]):
        self.name = name
        self.parent = parent
        self.methods = methods
    
    def get_method(self, name: str) -> Optional[UserFunction]:
        """Get method by name, checking parent class if necessary."""
        if name in self.methods:
            return self.methods[name]
        if self.parent:
            return self.parent.get_method(name)
        return None


class DesiInstance:
    """Represents an instance of a class."""
    
    def __init__(self, desi_class: DesiClass):
        self.desi_class = desi_class
        self.properties: Dict[str, Any] = {}
    
    def get(self, name: str) -> Any:
        """Get property value."""
        if name in self.properties:
            return self.properties[name]
        raise DesiNameError(f"Undefined property: '{name}'")
    
    def set(self, name: str, value: Any) -> None:
        """Set property value."""
        self.properties[name] = value
    
    def __repr__(self) -> str:
        return f"<instance of {self.desi_class.name}>"


class Interpreter:
    """Interprets and executes DesiLang AST."""
    
    def __init__(self, debug: bool = False):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.debug = debug
        
        # Register built-in functions
        for name, func in BUILTINS.items():
            self.global_env.define(name, func)
    
    def error(self, message: str, line: int = 0) -> None:
        """Raise a runtime error."""
        raise DesiRuntimeError(message, line)
    
    def execute(self, program: ProgramNode) -> None:
        """Execute the entire program."""
        try:
            self.visit(program)
        except ReturnValue:
            # Top-level return is allowed, just exit
            pass
    
    def visit(self, node: ASTNode) -> Any:
        """Dispatch to appropriate visit method based on node type."""
        method_name = f'visit_{node.__class__.__name__}'
        method = getattr(self, method_name, None)
        
        if method is None:
            self.error(f"No visit method for {node.__class__.__name__}", node.line)
        
        return method(node)
    
    def visit_ProgramNode(self, node: ProgramNode) -> None:
        """Execute all statements in the program."""
        for statement in node.statements:
            self.visit(statement)
    
    def visit_NumberNode(self, node: NumberNode) -> int | float:
        """Return the number value."""
        return node.value
    
    def visit_StringNode(self, node: StringNode) -> str:
        """Return the string value."""
        return node.value
    
    def visit_BooleanNode(self, node: BooleanNode) -> bool:
        """Return the boolean value."""
        return node.value
    
    def visit_ListNode(self, node: ListNode) -> List[Any]:
        """Evaluate and return a list."""
        return [self.visit(elem) for elem in node.elements]
    
    def visit_VariableNode(self, node: VariableNode) -> Any:
        """Get variable value from environment."""
        try:
            return self.current_env.get(node.name)
        except DesiNameError as e:
            self.error(str(e.message), node.line)
    
    def visit_AssignmentNode(self, node: AssignmentNode) -> None:
        """Assign value to a variable."""
        value = self.visit(node.value)
        self.current_env.set(node.name, value)
    
    def visit_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        """Evaluate binary operation."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.operator
        
        try:
            # Arithmetic operators
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                if right == 0:
                    raise DivisionByZeroError("Division by zero", node.line)
                # Integer division if both operands are integers
                if isinstance(left, int) and isinstance(right, int):
                    return left // right
                return left / right
            elif op == '%':
                if right == 0:
                    raise DivisionByZeroError("Modulo by zero", node.line)
                return left % right
            
            # Comparison operators
            elif op == '>':
                return left > right
            elif op == '<':
                return left < right
            elif op == '>=':
                return left >= right
            elif op == '<=':
                return left <= right
            elif op == '==':
                return left == right
            elif op == '!=':
                return left != right
            
            else:
                self.error(f"Unknown operator: {op}", node.line)
        
        except TypeError as e:
            raise DesiTypeError(f"Type error in operation '{op}': {str(e)}", node.line)
        except Exception as e:
            self.error(f"Error in operation '{op}': {str(e)}", node.line)
    
    def visit_UnaryOpNode(self, node: UnaryOpNode) -> Any:
        """Evaluate unary operation."""
        operand = self.visit(node.operand)
        
        if node.operator == '-':
            try:
                return -operand
            except TypeError:
                raise DesiTypeError(f"Cannot negate {type(operand).__name__}", node.line)
        
        self.error(f"Unknown unary operator: {node.operator}", node.line)
    
    def visit_PrintNode(self, node: PrintNode) -> None:
        """Print expression value to stdout."""
        value = self.visit(node.expression)
        
        # Format output
        if isinstance(value, bool):
            print("sahi" if value else "galat")
        elif isinstance(value, list):
            print(value)
        elif value is None:
            print("")
        else:
            print(value)
    
    def visit_InputNode(self, node: InputNode) -> None:
        """Read input from stdin and store in variable."""
        value = input()
        self.current_env.set(node.variable, value)
    
    def visit_IfNode(self, node: IfNode) -> None:
        """Execute if-else statement."""
        condition = self.visit(node.condition)
        
        # Convert to boolean
        if self.is_truthy(condition):
            for stmt in node.then_branch:
                self.visit(stmt)
        elif node.else_branch:
            for stmt in node.else_branch:
                self.visit(stmt)
    
    def visit_WhileNode(self, node: WhileNode) -> None:
        """Execute while loop."""
        iteration_count = 0
        max_iterations = 1000000  # Prevent infinite loops in safe mode
        
        while self.is_truthy(self.visit(node.condition)):
            iteration_count += 1
            if iteration_count > max_iterations:
                self.error("Maximum iteration count exceeded (possible infinite loop)", node.line)
            
            for stmt in node.body:
                self.visit(stmt)
    
    def visit_ForNode(self, node: ForNode) -> None:
        """Execute for loop."""
        start = self.visit(node.start)
        end = self.visit(node.end)
        
        if not isinstance(start, int) or not isinstance(end, int):
            raise DesiTypeError(f"For loop range must be integers", node.line)
        
        # Create new scope for loop variable
        loop_env = Environment(self.current_env)
        prev_env = self.current_env
        self.current_env = loop_env
        
        try:
            for i in range(start, end):
                self.current_env.define(node.variable, i)
                for stmt in node.body:
                    self.visit(stmt)
        finally:
            self.current_env = prev_env
    
    def visit_FunctionDefNode(self, node: FunctionDefNode) -> None:
        """Define a function."""
        func = UserFunction(node.name, node.parameters, node.body, self.current_env)
        self.current_env.define(node.name, func)
    
    def visit_FunctionCallNode(self, node: FunctionCallNode) -> Any:
        """Call a function."""
        func_name = node.name
        
        # Handle special built-in file operations
        if func_name == 'likho':
            return self.builtin_write_file(node)
        elif func_name == 'padho_file':
            return self.builtin_read_file(node)
        
        # Get function
        try:
            func = self.current_env.get(func_name)
        except DesiNameError:
            self.error(f"Undefined function: '{func_name}'", node.line)
        
        # Evaluate arguments
        args = [self.visit(arg) for arg in node.arguments]
        
        # Call built-in function
        if isinstance(func, BuiltinFunction):
            try:
                return func(*args)
            except Exception as e:
                self.error(f"Error in function '{func_name}': {str(e)}", node.line)
        
        # Call user-defined function
        elif isinstance(func, UserFunction):
            if len(args) != len(func.parameters):
                self.error(f"Function '{func_name}' expects {len(func.parameters)} arguments, got {len(args)}", node.line)
            
            # Create new environment for function execution
            func_env = Environment(func.closure)
            
            # Bind parameters
            for param, arg in zip(func.parameters, args):
                func_env.define(param, arg)
            
            # Execute function body
            prev_env = self.current_env
            self.current_env = func_env
            
            try:
                for stmt in func.body:
                    self.visit(stmt)
                return None  # No explicit return
            except ReturnValue as ret:
                return ret.value
            finally:
                self.current_env = prev_env
        
        else:
            self.error(f"'{func_name}' is not a function", node.line)
    
    def visit_ReturnNode(self, node: ReturnNode) -> None:
        """Execute return statement."""
        value = None
        if node.value:
            value = self.visit(node.value)
        raise ReturnValue(value)
    
    def visit_IndexAccessNode(self, node: IndexAccessNode) -> Any:
        """Access list element by index."""
        list_val = self.visit(node.list_expr)
        index = self.visit(node.index)
        
        if not isinstance(list_val, (list, str)):
            raise DesiTypeError(f"Cannot index {type(list_val).__name__}", node.line)
        
        if not isinstance(index, int):
            raise DesiTypeError(f"List index must be integer, got {type(index).__name__}", node.line)
        
        try:
            return list_val[index]
        except IndexError:
            raise DesiIndexError(f"List index out of range: {index}", node.line)
    
    def visit_IndexAssignmentNode(self, node: IndexAssignmentNode) -> None:
        """Assign value to list element at index."""
        list_val = self.current_env.get(node.list_name)
        index = self.visit(node.index)
        value = self.visit(node.value)
        
        if not isinstance(list_val, list):
            raise DesiTypeError(f"Cannot index assign to {type(list_val).__name__}", node.line)
        
        if not isinstance(index, int):
            raise DesiTypeError(f"List index must be integer, got {type(index).__name__}", node.line)
        
        try:
            list_val[index] = value
        except IndexError:
            raise DesiIndexError(f"List index out of range: {index}", node.line)
    
    def visit_ImportNode(self, node: ImportNode) -> None:
        """Import and execute another DesiLang file."""
        filename = node.filename
        
        # Add .desilang extension if not present
        if not filename.endswith('.desilang'):
            filename += '.desilang'
        
        # Try to find and read the file
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            raise FileIOError(f"Cannot import '{filename}': File not found", node.line)
        except Exception as e:
            raise FileIOError(f"Cannot import '{filename}': {str(e)}", node.line)
        
        # Parse and execute the imported file
        from .lexer import tokenize
        from .parser import Parser
        
        try:
            tokens = tokenize(code)
            parser = Parser(tokens)
            imported_ast = parser.parse()
            
            # Execute in current environment
            for stmt in imported_ast.statements:
                self.visit(stmt)
        except Exception as e:
            raise FileIOError(f"Error executing '{filename}': {str(e)}", node.line)
    
    def builtin_write_file(self, node: FunctionCallNode) -> None:
        """Write content to a file."""
        if len(node.arguments) != 2:
            self.error("likho expects 2 arguments: filename and content", node.line)
        
        filename = self.visit(node.arguments[0])
        content = self.visit(node.arguments[1])
        
        if not isinstance(filename, str):
            raise DesiTypeError("Filename must be a string", node.line)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(content))
        except Exception as e:
            raise FileIOError(f"Cannot write to file '{filename}': {str(e)}", node.line)
    
    def builtin_read_file(self, node: FunctionCallNode) -> str:
        """Read content from a file."""
        if len(node.arguments) != 1:
            self.error("padho_file expects 1 argument: filename", node.line)
        
        filename = self.visit(node.arguments[0])
        
        if not isinstance(filename, str):
            raise DesiTypeError("Filename must be a string", node.line)
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileIOError(f"File not found: '{filename}'", node.line)
        except Exception as e:
            raise FileIOError(f"Cannot read file '{filename}': {str(e)}", node.line)
    
    def is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy."""
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, list):
            return len(value) > 0
        return True
    
    # OOP Visitor Methods
    def visit_ClassDefNode(self, node: ClassDefNode) -> None:
        """Define a class."""
        # Get parent class if specified
        parent = None
        if node.parent:
            parent_value = self.current_env.get(node.parent)
            if not isinstance(parent_value, DesiClass):
                self.error(f"'{node.parent}' is not a class", node.line)
            parent = parent_value
        
        # Create method dictionary
        methods = {}
        for method_node in node.methods:
            # Methods are stored as UserFunction objects
            func = UserFunction(
                method_node.name,
                method_node.parameters,
                method_node.body,
                self.current_env  # Capture current environment
            )
            methods[method_node.name] = func
        
        # Create and store class
        desi_class = DesiClass(node.name, parent, methods)
        self.current_env.define(node.name, desi_class)
    
    def visit_NewObjectNode(self, node: NewObjectNode) -> DesiInstance:
        """Instantiate a new object."""
        class_value = self.current_env.get(node.class_name)
        
        if not isinstance(class_value, DesiClass):
            self.error(f"'{node.class_name}' is not a class", node.line)
        
        # Create instance
        instance = DesiInstance(class_value)
        
        # Call constructor if it exists
        constructor = class_value.get_method('__init__')
        if constructor:
            # Create method environment with 'yeh' bound to instance
            method_env = Environment(constructor.closure)
            method_env.define('yeh', instance)
            
            # Bind parameters
            if len(node.arguments) != len(constructor.parameters):
                self.error(
                    f"Constructor expects {len(constructor.parameters)} arguments, got {len(node.arguments)}",
                    node.line
                )
            
            for param, arg in zip(constructor.parameters, node.arguments):
                arg_value = self.visit(arg)
                method_env.define(param, arg_value)
            
            # Execute constructor body
            prev_env = self.current_env
            self.current_env = method_env
            try:
                for stmt in constructor.body:
                    self.visit(stmt)
            except ReturnValue:
                pass  # Constructor can return early
            finally:
                self.current_env = prev_env
        
        return instance
    
    def visit_MethodCallNode(self, node: MethodCallNode) -> Any:
        """Call a method on an object."""
        obj = self.visit(node.object_expr)
        
        if not isinstance(obj, DesiInstance):
            self.error(f"Cannot call method on non-object", node.line)
        
        method = obj.desi_class.get_method(node.method_name)
        if not method:
            self.error(f"Method '{node.method_name}' not found", node.line)
        
        # Create method environment with 'yeh' bound to instance
        method_env = Environment(method.closure)
        method_env.define('yeh', obj)
        
        # Bind parameters
        if len(node.arguments) != len(method.parameters):
            self.error(
                f"Method '{node.method_name}' expects {len(method.parameters)} arguments, got {len(node.arguments)}",
                node.line
            )
        
        for param, arg in zip(method.parameters, node.arguments):
            arg_value = self.visit(arg)
            method_env.define(param, arg_value)
        
        # Execute method body
        prev_env = self.current_env
        self.current_env = method_env
        try:
            for stmt in method.body:
                self.visit(stmt)
            return None
        except ReturnValue as ret:
            return ret.value
        finally:
            self.current_env = prev_env
    
    def visit_PropertyAccessNode(self, node: PropertyAccessNode) -> Any:
        """Access a property on an object."""
        obj = self.visit(node.object_expr)
        
        if not isinstance(obj, DesiInstance):
            self.error(f"Cannot access property on non-object", node.line)
        
        return obj.get(node.property_name)
    
    def visit_PropertyAssignmentNode(self, node: PropertyAssignmentNode) -> None:
        """Assign a value to a property."""
        obj = self.visit(node.object_expr)
        
        if not isinstance(obj, DesiInstance):
            self.error(f"Cannot assign property on non-object", node.line)
        
        value = self.visit(node.value)
        obj.set(node.property_name, value)
    
    def visit_ThisNode(self, node: ThisNode) -> DesiInstance:
        """Return the current instance (yeh)."""
        try:
            return self.current_env.get('yeh')
        except DesiNameError:
            self.error("'yeh' can only be used inside methods", node.line)
    
    def visit_SuperNode(self, node: SuperNode) -> Any:
        """Call a parent class method."""
        # Get current instance
        try:
            instance = self.current_env.get('yeh')
        except DesiNameError:
            self.error("'upar' can only be used inside methods", node.line)
        
        if not isinstance(instance, DesiInstance):
            self.error("'upar' requires an instance", node.line)
        
        # Get parent class
        if not instance.desi_class.parent:
            self.error(f"Class '{instance.desi_class.name}' has no parent", node.line)
        
        # Get method from parent
        method = instance.desi_class.parent.get_method(node.method_name)
        if not method:
            self.error(f"Parent method '{node.method_name}' not found", node.line)
        
        # Create method environment
        method_env = Environment(method.closure)
        method_env.define('yeh', instance)
        
        # Bind parameters
        if len(node.arguments) != len(method.parameters):
            self.error(
                f"Method '{node.method_name}' expects {len(method.parameters)} arguments, got {len(node.arguments)}",
                node.line
            )
        
        for param, arg in zip(method.parameters, node.arguments):
            arg_value = self.visit(arg)
            method_env.define(param, arg_value)
        
        # Execute method
        prev_env = self.current_env
        self.current_env = method_env
        try:
            for stmt in method.body:
                self.visit(stmt)
            return None
        except ReturnValue as ret:
            return ret.value
        finally:
            self.current_env = prev_env
    
    # Error Handling Visitor Methods
    def visit_TryNode(self, node: TryNode) -> None:
        """Execute try-catch-finally block."""
        exception_caught = None
        
        # Execute try block
        try:
            for stmt in node.try_block:
                self.visit(stmt)
        except DesiException as e:
            exception_caught = e
        except (DesiRuntimeError, DesiNameError, DesiTypeError, DivisionByZeroError, DesiIndexError) as e:
            exception_caught = e
        
        # Execute catch block if exception was caught
        if exception_caught and node.catch_block:
            # Create new scope for catch block
            catch_env = Environment(self.current_env)
            
            # Bind exception to variable if specified
            if node.catch_var:
                catch_env.define(node.catch_var, str(exception_caught))
            
            prev_env = self.current_env
            self.current_env = catch_env
            try:
                for stmt in node.catch_block:
                    self.visit(stmt)
            finally:
                self.current_env = prev_env
        
        # Always execute finally block
        if node.finally_block:
            for stmt in node.finally_block:
                self.visit(stmt)
        
        # Re-raise exception if not caught
        if exception_caught and not node.catch_block:
            raise exception_caught
    
    def visit_ThrowNode(self, node: ThrowNode) -> None:
        """Throw an exception."""
        message = self.visit(node.expression)
        raise DesiException(message, node.line)

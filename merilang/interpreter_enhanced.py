"""
Enhanced Interpreter for MeriLang Phase 2.

Production-ready AST visitor interpreter with:
- Comprehensive type hints (mypy strict compliance)
- Google-style docstrings
- Integration with Environment class for proper lexical scoping
- Integration with errors_enhanced for bilingual error messages
- Float operations support
- Lambda function execution
- Dictionary operations
- Improved error reporting with stack traces

Author: MeriLang Team
Version: 2.0 - Phase 2
"""

from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass

from merilang.environment import Environment
from merilang.errors_enhanced import (
    RuntimeError as DesiRuntimeError,
    NameError as DesiNameError,
    TypeError as DesiTypeError,
    DivisionByZeroError,
    IndexError as DesiIndexError,
    AttributeError as DesiAttributeError,
    RecursionError as DesiRecursionError,
    UserException,
    ErrorLanguage
)
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


# ============================================================================
# Control Flow Exceptions
# ============================================================================

class ReturnValue(Exception):
    """Exception used to implement return statement."""
    
    def __init__(self, value: Any) -> None:
        self.value = value
        super().__init__()


class BreakException(Exception):
    """Exception used to implement break statement."""
    pass


class ContinueException(Exception):
    """Exception used to implement continue statement."""
    pass


# ============================================================================
# Function Objects
# ============================================================================

@dataclass
class UserFunction:
    """
    Represents a user-defined function.
    
    Attributes:
        name: Function name
        parameters: List of parameter names
        body: List of AST nodes for function body
        closure: Environment where function was defined (for closures)
    """
    name: str
    parameters: List[str]
    body: List[ASTNode]
    closure: Environment
    
    def __repr__(self) -> str:
        return f"<function {self.name}>"


@dataclass
class Lambda:
    """
    Represents a lambda (anonymous) function.
    
    Attributes:
        parameters: List of parameter names
        body: Single expression AST node
        closure: Environment where lambda was defined
    """
    parameters: List[str]
    body: ASTNode
    closure: Environment
    
    def __repr__(self) -> str:
        return f"<lambda with {len(self.parameters)} params>"


# ============================================================================
# Class Objects
# ============================================================================

@dataclass
class DesiClass:
    """
    Represents a class definition.
    
    Attributes:
        name: Class name
        parent: Parent class (for inheritance)
        methods: Dictionary of method name -> UserFunction
    """
    name: str
    parent: Optional['DesiClass']
    methods: Dict[str, UserFunction]
    
    def get_method(self, name: str) -> Optional[UserFunction]:
        """
        Get method by name, checking parent classes if needed.
        
        Args:
            name: Method name to find
            
        Returns:
            UserFunction if found, None otherwise
        """
        if name in self.methods:
            return self.methods[name]
        if self.parent:
            return self.parent.get_method(name)
        return None
    
    def __repr__(self) -> str:
        return f"<class {self.name}>"


class DesiInstance:
    """
    Represents an instance of a DesiClass.
    
    Attributes:
        desi_class: The class this is an instance of
        properties: Dictionary of property name -> value
    """
    
    def __init__(self, desi_class: DesiClass) -> None:
        self.desi_class = desi_class
        self.properties: Dict[str, Any] = {}
    
    def get(self, name: str) -> Any:
        """
        Get property value.
        
        Args:
            name: Property name
            
        Returns:
            Property value
            
        Raises:
            DesiAttributeError: If property doesn't exist
        """
        if name in self.properties:
            return self.properties[name]
        raise DesiAttributeError(
            message_en=f"'{self.desi_class.name}' object has no attribute '{name}'", line=0,
            message_hi=None
        )
    
    def set(self, name: str, value: Any) -> None:
        """
        Set property value.
        
        Args:
            name: Property name
            value: Value to set
        """
        self.properties[name] = value
    
    def __repr__(self) -> str:
        return f"<instance of {self.desi_class.name}>"


# ============================================================================
# Built-in Functions
# ============================================================================

def builtin_len(obj: Any) -> int:
    """Get length of list, string, or dict."""
    if isinstance(obj, (list, str, dict)):
        return len(obj)
    raise DesiTypeError(
        message_en=f"len() not supported for {type(obj).__name__}",
        line=0,
        message_hi=None
    )


def builtin_type(obj: Any) -> str:
    """Get type name of object."""
    if isinstance(obj, bool):
        return "bool"
    elif isinstance(obj, int):
        return "int"
    elif isinstance(obj, float):
        return "float"
    elif isinstance(obj, str):
        return "str"
    elif isinstance(obj, list):
        return "list"
    elif isinstance(obj, dict):
        return "dict"
    elif isinstance(obj, (UserFunction, Lambda)):
        return "function"
    elif isinstance(obj, DesiClass):
        return "class"
    elif isinstance(obj, DesiInstance):
        return "object"
    else:
        return type(obj).__name__


def builtin_str(obj: Any) -> str:
    """Convert object to string."""
    if isinstance(obj, bool):
        return "sach" if obj else "jhoot"
    return str(obj)


def builtin_int(obj: Any) -> int:
    """Convert object to integer."""
    try:
        return int(obj)
    except (ValueError, TypeError) as e:
        raise DesiTypeError(
            message_en=f"Cannot convert {type(obj).__name__} to int",
            line=0,
            message_hi=None
        )


def builtin_float(obj: Any) -> float:
    """Convert object to float."""
    try:
        return float(obj)
    except (ValueError, TypeError) as e:
        raise DesiTypeError(
            message_en=f"Cannot convert {type(obj).__name__} to float",
            line=0,
            message_hi=None
        )


def builtin_range(start: int, stop: Optional[int] = None, step: int = 1) -> List[int]:
    """Generate a range of integers."""
    if stop is None:
        return list(range(start))
    return list(range(start, stop, step))


def builtin_abs(num: Union[int, float]) -> Union[int, float]:
    """Get absolute value."""
    if not isinstance(num, (int, float)):
        raise DesiTypeError(
            message_en=f"abs() requires number, got {type(num).__name__}",
            line=0,
            message_hi=None
        )
    return abs(num)


def builtin_min(*args: Any) -> Any:
    """Get minimum value."""
    if len(args) == 1 and isinstance(args[0], list):
        return min(args[0])
    return min(args)


def builtin_max(*args: Any) -> Any:
    """Get maximum value."""
    if len(args) == 1 and isinstance(args[0], list):
        return max(args[0])
    return max(args)


def builtin_sum(items: List[Union[int, float]]) -> Union[int, float]:
    """Sum all numbers in list."""
    if not isinstance(items, list):
        raise DesiTypeError(
            message_en=f"sum() requires list, got {type(items).__name__}",
            line=0,
            message_hi=None
        )
    return sum(items)


def builtin_append(lst: List[Any], item: Any) -> None:
    """Append item to list."""
    if not isinstance(lst, list):
        raise DesiTypeError(
            message_en=f"append() requires list, got {type(lst).__name__}",
            line=0,
            message_hi=None
        )
    lst.append(item)


def builtin_pop(lst: List[Any], index: int = -1) -> Any:
    """Remove and return item at index."""
    if not isinstance(lst, list):
        raise DesiTypeError(
            message_en=f"pop() requires list, got {type(lst).__name__}",
            line=0,
            message_hi=None
        )
    try:
        return lst.pop(index)
    except IndexError:
        raise DesiIndexError(
            message_en=f"pop index out of range: {index}", line=0,
            message_hi=None
        )


def builtin_keys(d: Dict[Any, Any]) -> List[Any]:
    """Get list of dictionary keys."""
    if not isinstance(d, dict):
        raise DesiTypeError(
            message_en=f"keys() requires dict, got {type(d).__name__}",
            line=0,
            message_hi=None
        )
    return list(d.keys())


def builtin_values(d: Dict[Any, Any]) -> List[Any]:
    """Get list of dictionary values."""
    if not isinstance(d, dict):
        raise DesiTypeError(
            message_en=f"values() requires dict, got {type(d).__name__}",
            line=0,
            message_hi=None
        )
    return list(d.values())


# Built-in function registry
BUILTINS: Dict[str, Callable[..., Any]] = {
    'lambai': builtin_len,      # length
    'prakar': builtin_type,     # type
    'shabd': builtin_str,       # string
    'ank': builtin_int,         # integer
    'dashamlav': builtin_float, # float
    'disha': builtin_range,     # range
    'nirpeksha': builtin_abs,   # absolute
    'nyuntam': builtin_min,     # minimum
    'adhiktam': builtin_max,    # maximum
    'yog': builtin_sum,         # sum
    'jodo': builtin_append,     # append
    'nikalo': builtin_pop,      # pop
    'kunji': builtin_keys,      # keys
    'mul': builtin_values,      # values
}


# ============================================================================
# Interpreter
# ============================================================================

class Interpreter:
    """
    AST visitor interpreter for MeriLang.
    
    Executes MeriLang programs by traversing the AST and performing operations.
    Uses visitor pattern with proper lexical scoping via Environment class.
    
    Attributes:
        global_env: Global environment for top-level bindings
        current_env: Currently active environment
        error_language: Language for error messages
        call_stack: Function call stack for debugging
        max_call_depth: Maximum recursion depth
        
    Examples:
        >>> from merilang.parser_enhanced import parse_MeriLang
        >>> ast = parse_MeriLang("maan x = 42\\nlikho(x)")
        >>> interpreter = Interpreter()
        >>> interpreter.execute(ast)
        42
    """
    
    MAX_CALL_DEPTH: int = 1000
    MAX_ITERATIONS: int = 1000000
    
    def __init__(
        self,
        error_language: ErrorLanguage = ErrorLanguage.ENGLISH,
        debug: bool = False
    ) -> None:
        """
        Initialize the interpreter.
        
        Args:
            error_language: Language for error messages
            debug: Enable debug mode for verbose output
        """
        self.global_env = Environment()
        self.current_env = self.global_env
        self.error_language = error_language
        self.debug = debug
        self.call_stack: List[str] = []
        
        # Register built-in functions
        for name, func in BUILTINS.items():
            self.global_env.define(name, func)
    
    def execute(self, program: ProgramNode) -> None:
        """
        Execute the entire program.
        
        Args:
            program: Root AST node containing all statements
            
        Raises:
            Various MeriLang exceptions for runtime errors
            
        Examples:
            >>> interpreter.execute(ast)
        """
        try:
            self.visit(program)
        except ReturnValue:
            # Top-level return is allowed
            pass
    
    def visit(self, node: ASTNode) -> Any:
        """
        Dispatch to appropriate visit method based on node type.
        
        Uses visitor pattern: calls visit_<NodeClassName>(node).
        
        Args:
            node: AST node to visit
            
        Returns:
            Result of visiting the node (type depends on node)
            
        Raises:
            DesiRuntimeError: If no visitor method found
        """
        method_name = f'visit_{node.__class__.__name__}'
        method = getattr(self, method_name, None)
        
        if method is None:
            raise DesiRuntimeError(
                message_en=f"No visitor method for {node.__class__.__name__}", line=node.line
            )
        
        return method(node)
    
    # ========================================================================
    # Literal Visitors
    # ========================================================================
    
    def visit_ProgramNode(self, node: ProgramNode) -> None:
        """Execute all statements in program."""
        for statement in node.statements:
            self.visit(statement)
    
    def visit_NumberNode(self, node: NumberNode) -> Union[int, float]:
        """Return number value (int or float)."""
        return node.value
    
    def visit_StringNode(self, node: StringNode) -> str:
        """Return string value."""
        return node.value
    
    def visit_BooleanNode(self, node: BooleanNode) -> bool:
        """Return boolean value."""
        return node.value
    
    def visit_ListNode(self, node: ListNode) -> List[Any]:
        """Evaluate and return list."""
        return [self.visit(elem) for elem in node.elements]
    
    def visit_DictNode(self, node: DictNode) -> Dict[Any, Any]:
        """
        Evaluate and return dictionary.
        
        Examples:
            >>> # {name: "Ahmed", age: 25}
            >>> result = interpreter.visit_DictNode(dict_node)
            >>> result
            {'name': 'Ahmed', 'age': 25}
        """
        result: Dict[Any, Any] = {}
        for key_node, value_node in node.pairs:
            key = self.visit(key_node)
            value = self.visit(value_node)
            
            # Ensure key is hashable
            if not isinstance(key, (str, int, float, bool)):
                raise DesiTypeError(
                    message_en=f"Dictionary key must be immutable, got {type(key).__name__}",
                    line=node.line
                )
            
            result[key] = value
        
        return result
    
    def visit_ParenthesizedNode(self, node: ParenthesizedNode) -> Any:
        """Evaluate expression inside parentheses."""
        return self.visit(node.expression)
    
    # ========================================================================
    # Variable Visitors
    # ========================================================================
    
    def visit_VariableNode(self, node: VariableNode) -> Any:
        """Get variable value from environment."""
        try:
            return self.current_env.get(node.name)
        except DesiNameError as e:
            # Re-raise with proper line info (error already has correct format)
            raise
    
    def visit_AssignmentNode(self, node: AssignmentNode) -> None:
        """Assign value to variable."""
        value = self.visit(node.value)
        
        # Use set() which handles both new and existing variables
        try:
            self.current_env.set(node.name, value)
        except DesiNameError:
            # Variable doesn't exist, define it
            self.current_env.define(node.name, value)
    
    # ========================================================================
    # Operation Visitors
    # ========================================================================
    
    def visit_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        """
        Evaluate binary operation.
        
        Supports:
        - Arithmetic: +, -, *, /, %
        - Comparison: ==, !=, <, >, <=, >=
        - Logical: aur (and), ya (or)
        
        Returns:
            Result of operation (type depends on operator)
            
        Raises:
            DesiTypeError: If operation invalid for operand types
            DivisionByZeroError: If dividing by zero
        """
        # Short-circuit evaluation for logical operators
        if node.operator == "ya":  # OR
            left = self.visit(node.left)
            if self.is_truthy(left):
                return True
            right = self.visit(node.right)
            return self.is_truthy(right)
        
        if node.operator == "aur":  # AND
            left = self.visit(node.left)
            if not self.is_truthy(left):
                return False
            right = self.visit(node.right)
            return self.is_truthy(right)
        
        # Evaluate both operands for other operators
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.operator
        
        try:
            # Arithmetic operators
            if op == '+':
                # String concatenation or numeric addition
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            
            elif op == '-':
                return left - right
            
            elif op == '*':
                return left * right
            
            elif op == '/':
                if right == 0 or (isinstance(right, float) and abs(right) < 1e-10):
                    raise DivisionByZeroError(
                        message_en="Division by zero", line=node.line
                    )
                # Python 3 true division (always returns float)
                return left / right
            
            elif op == '%':
                if right == 0:
                    raise DivisionByZeroError(
                        message_en="Modulo by zero", line=node.line
                    )
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
                raise DesiRuntimeError(
                    message_en=f"Unknown operator: {op}", line=node.line
                )
        
        except TypeError as e:
            raise DesiTypeError(
                message_en=f"Invalid operation '{op}' between {type(left).__name__} and {type(right).__name__}",
                line=node.line
            )
        except Exception as e:
            raise DesiRuntimeError(
                message_en=f"Error in operation '{op}': {str(e)}",
                line=node.line
            )
    
    def visit_UnaryOpNode(self, node: UnaryOpNode) -> Any:
        """
        Evaluate unary operation.
        
        Supports:
        - Negation: -expr
        - Logical NOT: nahi expr
        
        Returns:
            Result of operation
            
        Raises:
            DesiTypeError: If operation invalid for operand type
        """
        operand = self.visit(node.operand)
        
        if node.operator == '-':
            # Arithmetic negation
            if not isinstance(operand, (int, float)):
                raise DesiTypeError(
                    message_en=f"Cannot negate {type(operand).__name__}",
                    line=node.line
                )
            return -operand
        
        elif node.operator == 'nahi':
            # Logical NOT
            return not self.is_truthy(operand)
        
        else:
            raise DesiRuntimeError(
                message_en=f"Unknown unary operator: {node.operator}", line=node.line
            )
    
    # ========================================================================
    # I/O Visitors
    # ========================================================================
    
    def visit_PrintNode(self, node: PrintNode) -> None:
        """
        Print values to stdout.
        
        Handles multiple arguments with space separation.
        Formats booleans as "sach"/"jhoot".
        """
        values = [self.visit(arg) for arg in node.arguments]
        
        # Format output
        formatted = []
        for value in values:
            if isinstance(value, bool):
                formatted.append("sach" if value else "jhoot")
            elif value is None:
                formatted.append("")
            else:
                formatted.append(str(value))
        
        print(" ".join(formatted))
    
    def visit_InputNode(self, node: InputNode) -> None:
        """Read input from stdin and store in variable."""
        # Display prompt if provided
        if node.prompt:
            prompt_text = self.visit(node.prompt)
            value = input(str(prompt_text))
        else:
            value = input()
        
        # Store in variable
        self.current_env.set(node.variable, value)
    
    # ========================================================================
    # Control Flow Visitors
    # ========================================================================
    
    def visit_IfNode(self, node: IfNode) -> None:
        """Execute if-elif-else statement."""
        condition = self.visit(node.condition)
        
        if self.is_truthy(condition):
            for stmt in node.then_branch:
                self.visit(stmt)
        else:
            # Check elif branches
            for elif_condition, elif_body in node.elif_branches:
                if self.is_truthy(self.visit(elif_condition)):
                    for stmt in elif_body:
                        self.visit(stmt)
                    return
            
            # Execute else branch if present
            if node.else_branch:
                for stmt in node.else_branch:
                    self.visit(stmt)
    
    def visit_WhileNode(self, node: WhileNode) -> None:
        """Execute while loop with iteration limit."""
        iteration_count = 0
        
        while self.is_truthy(self.visit(node.condition)):
            iteration_count += 1
            if iteration_count > self.MAX_ITERATIONS:
                raise DesiRuntimeError(
                    message_en=f"Maximum iteration count exceeded ({self.MAX_ITERATIONS})",
                    line=node.line
                )
            
            try:
                for stmt in node.body:
                    self.visit(stmt)
            except BreakException:
                break
            except ContinueException:
                continue
    
    def visit_ForNode(self, node: ForNode) -> None:
        """
        Execute for loop over iterable.
        
        Supports iterating over lists, strings, and range objects.
        Creates new scope for loop variable.
        """
        iterable = self.visit(node.iterable)
        
        # Ensure iterable
        if not isinstance(iterable, (list, str)):
            raise DesiTypeError(
                message_en=f"Cannot iterate over {type(iterable).__name__}",
                line=node.line
            )
        
        # Create loop scope
        loop_env = Environment(self.current_env)
        prev_env = self.current_env
        self.current_env = loop_env
        
        try:
            for item in iterable:
                self.current_env.define(node.variable, item)
                
                try:
                    for stmt in node.body:
                        self.visit(stmt)
                except BreakException:
                    break
                except ContinueException:
                    continue
        finally:
            self.current_env = prev_env
    
    def visit_BreakNode(self, node: BreakNode) -> None:
        """Execute break statement."""
        raise BreakException()
    
    def visit_ContinueNode(self, node: ContinueNode) -> None:
        """Execute continue statement."""
        raise ContinueException()
    
    # ========================================================================
    # Function Visitors
    # ========================================================================
    
    def visit_FunctionDefNode(self, node: FunctionDefNode) -> None:
        """Define a function in current environment."""
        func = UserFunction(
            name=node.name,
            parameters=node.parameters,
            body=node.body,
            closure=self.current_env
        )
        self.current_env.define(node.name, func)
    
    def visit_FunctionCallNode(self, node: FunctionCallNode) -> Any:
        """
        Call a function (built-in, user-defined, or lambda).
        
        Returns:
            Function return value
            
        Raises:
            DesiNameError: If function not found
            DesiTypeError: If called object is not callable
            DesiRuntimeError: If argument count mismatch
            DesiRecursionError: If call stack exceeds limit
        """
        # Get function
        try:
            func = self.current_env.get(node.name)
        except DesiNameError:
            raise DesiNameError(
                message_en=f"Undefined function: '{node.name}'", line=node.line
            )
        
        # Evaluate arguments
        args = [self.visit(arg) for arg in node.arguments]
        
        # Call built-in function
        if callable(func) and not isinstance(func, (UserFunction, Lambda)):
            try:
                return func(*args)
            except (DesiTypeError, DesiIndexError, DesiRuntimeError):
                raise  # Re-raise MeriLang exceptions
            except Exception as e:
                raise DesiRuntimeError(
                    message_en=f"Error in function '{node.name}': {str(e)}",
                    line=node.line
                )
        
        # Call user-defined function
        elif isinstance(func, UserFunction):
            return self._call_user_function(func, args, node.line)
        
        # Call lambda
        elif isinstance(func, Lambda):
            return self._call_lambda(func, args, node.line)
        
        else:
            raise DesiTypeError(
                message_en=f"'{node.name}' is not callable", line=node.line
            )
    
    def _call_user_function(
        self,
        func: UserFunction,
        args: List[Any],
        line: int
    ) -> Any:
        """
        Call a user-defined function.
        
        Args:
            func: UserFunction object
            args: Evaluated argument values
            line: Line number for error reporting
            
        Returns:
            Function return value
        """
        # Check argument count
        if len(args) != len(func.parameters):
            raise DesiRuntimeError(
                message_en=f"Function '{func.name}' expects {len(func.parameters)} arguments, got {len(args)}",
                line=line
            )
        
        # Check recursion depth
        if len(self.call_stack) >= self.MAX_CALL_DEPTH:
            raise DesiRecursionError(
                message_en=f"Maximum recursion depth exceeded ({self.MAX_CALL_DEPTH})",
                line=line
            )
        
        # Create function environment
        func_env = Environment(func.closure)
        
        # Bind parameters
        for param, arg in zip(func.parameters, args):
            func_env.define(param, arg)
        
        # Execute function body
        prev_env = self.current_env
        self.current_env = func_env
        self.call_stack.append(func.name)
        
        try:
            for stmt in func.body:
                self.visit(stmt)
            return None  # No explicit return
        except ReturnValue as ret:
            return ret.value
        finally:
            self.current_env = prev_env
            self.call_stack.pop()
    
    def _call_lambda(
        self,
        func: Lambda,
        args: List[Any],
        line: int
    ) -> Any:
        """
        Call a lambda function.
        
        Args:
            func: Lambda object
            args: Evaluated argument values
            line: Line number for error reporting
            
        Returns:
            Lambda return value
        """
        # Check argument count
        if len(args) != len(func.parameters):
            raise DesiRuntimeError(
                message_en=f"Lambda expects {len(func.parameters)} arguments, got {len(args)}",
                line=line
            )
        
        # Create lambda environment
        lambda_env = Environment(func.closure)
        
        # Bind parameters
        for param, arg in zip(func.parameters, args):
            lambda_env.define(param, arg)
        
        # Evaluate body (single expression)
        prev_env = self.current_env
        self.current_env = lambda_env
        
        try:
            return self.visit(func.body)
        finally:
            self.current_env = prev_env
    
    def visit_ReturnNode(self, node: ReturnNode) -> None:
        """Execute return statement."""
        value = None
        if node.value:
            value = self.visit(node.value)
        raise ReturnValue(value)
    
    def visit_LambdaNode(self, node: LambdaNode) -> Lambda:
        """Create and return lambda function."""
        return Lambda(
            parameters=node.parameters,
            body=node.body,
            closure=self.current_env
        )
    
    # ========================================================================
    # Object-Oriented Programming Visitors
    # ========================================================================
    
    def visit_ClassDefNode(self, node: ClassDefNode) -> None:
        """Define a class in current environment."""
        # Get parent class if specified
        parent: Optional[DesiClass] = None
        if node.parent:
            parent_value = self.current_env.get(node.parent)
            if not isinstance(parent_value, DesiClass):
                raise DesiTypeError(
                    message_en=f"'{node.parent}' is not a class", line=node.line
                )
            parent = parent_value
        
        # Create method dictionary
        methods: Dict[str, UserFunction] = {}
        for method_node in node.methods:
            func = UserFunction(
                name=method_node.name,
                parameters=method_node.parameters,
                body=method_node.body,
                closure=self.current_env
            )
            methods[method_node.name] = func
        
        # Create and store class
        desi_class = DesiClass(node.name, parent, methods)
        self.current_env.define(node.name, desi_class)
    
    def visit_NewObjectNode(self, node: NewObjectNode) -> DesiInstance:
        """Instantiate a new object."""
        class_value = self.current_env.get(node.class_name)
        
        if not isinstance(class_value, DesiClass):
            raise DesiTypeError(
                message_en=f"'{node.class_name}' is not a class", line=node.line
            )
        
        # Create instance
        instance = DesiInstance(class_value)
        
        # Call constructor if it exists
        constructor = class_value.get_method('__init__')
        if constructor:
            # Evaluate arguments
            args = [self.visit(arg) for arg in node.arguments]
            
            # Check argument count
            if len(args) != len(constructor.parameters):
                raise DesiRuntimeError(
                    message_en=f"Constructor expects {len(constructor.parameters)} arguments, got {len(args)}",
                    line=node.line
                )
            
            # Create method environment with 'yeh' bound to instance
            method_env = Environment(constructor.closure)
            method_env.define('yeh', instance)
            
            # Bind parameters
            for param, arg in zip(constructor.parameters, args):
                method_env.define(param, arg)
            
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
        obj = self.visit(node.object)
        
        if not isinstance(obj, DesiInstance):
            raise DesiTypeError(
                message_en=f"Cannot call method on {type(obj).__name__}",
                line=node.line
            )
        
        method = obj.desi_class.get_method(node.method_name)
        if not method:
            raise DesiAttributeError(
                message_en=f"'{obj.desi_class.name}' object has no method '{node.method_name}'", line=node.line
            )
        
        # Evaluate arguments
        args = [self.visit(arg) for arg in node.arguments]
        
        # Check argument count
        if len(args) != len(method.parameters):
            raise DesiRuntimeError(
                message_en=f"Method '{node.method_name}' expects {len(method.parameters)} arguments, got {len(args)}",
                line=node.line
            )
        
        # Create method environment with 'yeh' bound to instance
        method_env = Environment(method.closure)
        method_env.define('yeh', obj)
        
        # Bind parameters
        for param, arg in zip(method.parameters, args):
            method_env.define(param, arg)
        
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
        obj = self.visit(node.object)
        
        if not isinstance(obj, DesiInstance):
            raise DesiTypeError(
                message_en=f"Cannot access property on {type(obj).__name__}",
                line=node.line
            )
        
        try:
            return obj.get(node.property_name)
        except DesiAttributeError as e:
            # Re-raise with proper line info
            raise DesiAttributeError(
                message_en=str(e),
                line=node.line
            )
    
    def visit_PropertyAssignmentNode(self, node: PropertyAssignmentNode) -> None:
        """Assign a value to a property."""
        obj = self.visit(node.object)
        
        if not isinstance(obj, DesiInstance):
            raise DesiTypeError(
                message_en=f"Cannot assign property on {type(obj).__name__}",
                line=node.line
            )
        
        value = self.visit(node.value)
        obj.set(node.property_name, value)
    
    def visit_ThisNode(self, node: ThisNode) -> DesiInstance:
        """Return current instance ('yeh' keyword)."""
        try:
            instance = self.current_env.get('yeh')
            if not isinstance(instance, DesiInstance):
                raise DesiRuntimeError(
                    message_en="'yeh' is not bound to an instance", line=node.line
                )
            return instance
        except DesiNameError:
            raise DesiRuntimeError(
                message_en="'yeh' can only be used inside methods", line=node.line
            )
    
    def visit_SuperNode(self, node: SuperNode) -> Any:
        """Call parent class method."""
        # Get current instance
        try:
            instance = self.current_env.get('yeh')
        except DesiNameError:
            raise DesiRuntimeError(
                message_en="'upar' can only be used inside methods", line=node.line
            )
        
        if not isinstance(instance, DesiInstance):
            raise DesiRuntimeError(
                message_en="'upar' requires an instance", line=node.line
            )
        
        # Get parent class
        if not instance.desi_class.parent:
            raise DesiRuntimeError(
                message_en=f"Class '{instance.desi_class.name}' has no parent", line=node.line
            )
        
        # Get method from parent
        method = instance.desi_class.parent.get_method(node.method_name)
        if not method:
            raise DesiAttributeError(
                message_en=f"Parent class has no method '{node.method_name}'", line=node.line
            )
        
        # Evaluate arguments
        args = [self.visit(arg) for arg in node.arguments]
        
        # Check argument count
        if len(args) != len(method.parameters):
            raise DesiRuntimeError(
                message_en=f"Method '{node.method_name}' expects {len(method.parameters)} arguments, got {len(args)}",
                line=node.line
            )
        
        # Create method environment
        method_env = Environment(method.closure)
        method_env.define('yeh', instance)
        
        # Bind parameters
        for param, arg in zip(method.parameters, args):
            method_env.define(param, arg)
        
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
    
    # ========================================================================
    # Error Handling Visitors
    # ========================================================================
    
    def visit_TryNode(self, node: TryNode) -> None:
        """Execute try-catch-finally block."""
        exception_caught: Optional[Exception] = None
        
        # Execute try block
        try:
            for stmt in node.try_block:
                self.visit(stmt)
        except (UserException, DesiRuntimeError, DesiNameError, DesiTypeError,
                DivisionByZeroError, DesiIndexError, DesiAttributeError,
                DesiRecursionError) as e:
            exception_caught = e
        
        # Execute catch block if exception was caught
        if exception_caught and node.catch_block:
            # Create catch scope
            catch_env = Environment(self.current_env)
            
            # Bind exception to variable if specified
            if node.exception_var:
                catch_env.define(node.exception_var, str(exception_caught))
            
            prev_env = self.current_env
            self.current_env = catch_env
            try:
                for stmt in node.catch_block:
                    self.visit(stmt)
            finally:
                self.current_env = prev_env
                exception_caught = None  # Mark as handled
        
        # Always execute finally block
        if node.finally_block:
            for stmt in node.finally_block:
                self.visit(stmt)
        
        # Re-raise exception if not handled
        if exception_caught:
            raise exception_caught
    
    def visit_ThrowNode(self, node: ThrowNode) -> None:
        """Throw an exception."""
        message = self.visit(node.exception)
        raise UserException(
            message_en=str(message),
            line=node.line
        )
    
    # ========================================================================
    # Indexing Visitors
    # ========================================================================
    
    def visit_IndexNode(self, node: IndexNode) -> Any:
        """Access element by index (list/string) or key (dict)."""
        obj = self.visit(node.object)
        index = self.visit(node.index)
        
        # Dictionary access
        if isinstance(obj, dict):
            if index not in obj:
                raise DesiIndexError(
                    message_en=f"Key not found: {index}", line=node.line
                )
            return obj[index]
        
        # List/string access
        if not isinstance(obj, (list, str)):
            raise DesiTypeError(
                message_en=f"Cannot index {type(obj).__name__}",
                line=node.line
            )
        
        if not isinstance(index, int):
            raise DesiTypeError(
                message_en=f"Index must be integer, got {type(index).__name__}",
                line=node.line
            )
        
        try:
            return obj[index]
        except IndexError:
            raise DesiIndexError(
                message_en=f"Index out of range: {index}", line=node.line
            )
    
    def visit_IndexAssignmentNode(self, node: IndexAssignmentNode) -> None:
        """Assign value to element at index or key."""
        obj = self.visit(node.object)
        index = self.visit(node.index)
        value = self.visit(node.value)
        
        # Dictionary assignment
        if isinstance(obj, dict):
            # Ensure key is hashable
            if not isinstance(index, (str, int, float, bool)):
                raise DesiTypeError(
                    message_en=f"Dictionary key must be immutable, got {type(index).__name__}",
                    line=node.line
                )
            obj[index] = value
            return
        
        # List assignment
        if not isinstance(obj, list):
            raise DesiTypeError(
                message_en=f"Cannot index assign to {type(obj).__name__}",
                line=node.line
            )
        
        if not isinstance(index, int):
            raise DesiTypeError(
                message_en=f"List index must be integer, got {type(index).__name__}",
                line=node.line
            )
        
        try:
            obj[index] = value
        except IndexError:
            raise DesiIndexError(
                message_en=f"Index out of range: {index}", line=node.line
            )
    
    # ========================================================================
    # Import Visitor
    # ========================================================================
    
    def visit_ImportNode(self, node: ImportNode) -> None:
        """Import and execute another MeriLang file."""
        from merilang.parser_enhanced import parse_MeriLang
        from merilang.errors_enhanced import LexerError, ParserError, FileIOError
        
        filename = node.module_name
        
        # Add .dl extension if not present
        if not filename.endswith('.dl'):
            filename += '.dl'
        
        # Try to find and read file
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            raise FileIOError(
                message_en=f"Cannot import '{filename}': File not found", line=node.line
            )
        except Exception as e:
            raise FileIOError(
                message_en=f"Cannot import '{filename}': {str(e)}",
                line=node.line
            )
        
        # Parse and execute imported file
        try:
            imported_ast = parse_MeriLang(code, self.error_language)
            
            # Execute in current environment
            for stmt in imported_ast.statements:
                self.visit(stmt)
        except (LexerError, ParserError) as e:
            raise FileIOError(
                message_en=f"Error parsing '{filename}': {str(e)}",
                line=node.line
            )
        except Exception as e:
            raise FileIOError(
                message_en=f"Error executing '{filename}': {str(e)}",
                line=node.line
            )
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def is_truthy(self, value: Any) -> bool:
        """
        Determine if a value is truthy.
        
        Rules:
        - bool: identity
        - None: False
        - numbers: != 0
        - strings: len > 0
        - lists: len > 0
        - dicts: len > 0
        - other: True
        
        Args:
            value: Value to check
            
        Returns:
            True if value is truthy
        """
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True




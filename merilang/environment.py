"""
Environment class for DesiLang - Production scoping system.

This module provides lexical scoping functionality with parent chain
for proper variable resolution across nested scopes (functions, blocks, classes).

Author: DesiLang Team
Version: 2.0
"""

from typing import Any, Dict, Optional, Set
from .errors_enhanced import NameError as DesiNameError


class Environment:
    """Represents a lexical scope with parent chain for variable resolution.
    
    This class implements lexical scoping similar to Python, where each scope
    can access variables from parent scopes but cannot modify them without
    explicit declaration. Supports nested scopes for functions, blocks, and classes.
    
    Attributes:
        bindings: Dictionary mapping variable names to their values
        parent: Parent environment (outer scope), None for global scope
        recursion_depth: Track recursion depth to prevent stack overflow
        
    Example:
        >>> global_env = Environment()
        >>> global_env.define('x', 10)
        >>> local_env = Environment(parent=global_env)
        >>> local_env.define('y', 20)
        >>> local_env.get('x')  # Access parent scope
        10
        >>> local_env.get('y')  # Access local scope
        20
    """
    
    MAX_RECURSION_DEPTH = 1000  # Prevent stack overflow
    
    def __init__(self, parent: Optional['Environment'] = None):
        """Initialize a new environment.
        
        Args:
            parent: Parent environment for nested scopes (None for global)
        """
        self.bindings: Dict[str, Any] = {}
        self.parent = parent
        
        # Calculate recursion depth
        if parent is None:
            self.recursion_depth = 0
        else:
            self.recursion_depth = parent.recursion_depth + 1
            
            if self.recursion_depth > self.MAX_RECURSION_DEPTH:
                from .errors_enhanced import RuntimeError as DesiRuntimeError
                raise DesiRuntimeError(
                    f"Maximum recursion depth exceeded ({self.MAX_RECURSION_DEPTH}). "
                    "Possible infinite recursion."
                )
    
    def define(self, name: str, value: Any) -> None:
        """Define a new variable in the current scope.
        
        This creates or updates a variable in the current environment only.
        It does not affect parent scopes.
        
        Args:
            name: Variable name
            value: Variable value
            
        Example:
            >>> env = Environment()
            >>> env.define('count', 42)
            >>> env.get('count')
            42
        """
        self.bindings[name] = value
    
    def get(self, name: str, line: Optional[int] = None) -> Any:
        """Get a variable's value, searching parent scopes if needed.
        
        Searches for the variable in current scope, then recursively in
        parent scopes. Raises NameError if variable is not found anywhere.
        
        Args:
            name: Variable name to look up
            line: Line number for error reporting (optional)
            
        Returns:
            Value of the variable
            
        Raises:
            DesiNameError: If variable is not defined in any accessible scope
            
        Example:
            >>> env = Environment()
            >>> env.define('x', 10)
            >>> env.get('x')
            10
            >>> env.get('y')  # Raises DesiNameError
        """
        if name in self.bindings:
            return self.bindings[name]
        
        if self.parent is not None:
            return self.parent.get(name, line)
        
        # Variable not found in any scope
        raise DesiNameError(
            f"Undefined variable: '{name}'",
            line=line
        )
    
    def set(self, name: str, value: Any, line: Optional[int] = None) -> None:
        """Update an existing variable's value.
        
        Searches for the variable in current scope and parent scopes.
        Updates the first occurrence found. Raises NameError if not found.
        
        Args:
            name: Variable name to update
            value: New value
            line: Line number for error reporting (optional)
            
        Raises:
            DesiNameError: If variable is not defined in any accessible scope
            
        Example:
            >>> env = Environment()
            >>> env.define('x', 10)
            >>> env.set('x', 20)
            >>> env.get('x')
            20
        """
        if name in self.bindings:
            self.bindings[name] = value
            return
        
        if self.parent is not None:
            self.parent.set(name, value, line)
            return
        
        # Variable not found - raise error
        raise DesiNameError(
            f"Cannot assign to undefined variable: '{name}'. "
            f"Use 'maan {name} = ...' to declare it first.",
            line=line
        )
    
    def exists(self, name: str) -> bool:
        """Check if a variable exists in current or parent scopes.
        
        Args:
            name: Variable name to check
            
        Returns:
            True if variable exists, False otherwise
            
        Example:
            >>> env = Environment()
            >>> env.define('x', 10)
            >>> env.exists('x')
            True
            >>> env.exists('y')
            False
        """
        if name in self.bindings:
            return True
        
        if self.parent is not None:
            return self.parent.exists(name)
        
        return False
    
    def exists_local(self, name: str) -> bool:
        """Check if a variable exists in current scope only.
        
        Args:
            name: Variable name to check
            
        Returns:
            True if variable exists in current scope, False otherwise
            
        Example:
            >>> global_env = Environment()
            >>> global_env.define('x', 10)
            >>> local_env = Environment(parent=global_env)
            >>> local_env.exists('x')  # True (found in parent)
            >>> local_env.exists_local('x')  # False (not in current scope)
        """
        return name in self.bindings
    
    def get_all_names(self) -> Set[str]:
        """Get all variable names in current and parent scopes.
        
        Returns:
            Set of all accessible variable names
            
        Example:
            >>> env1 = Environment()
            >>> env1.define('x', 1)
            >>> env2 = Environment(parent=env1)
            >>> env2.define('y', 2)
            >>> sorted(env2.get_all_names())
            ['x', 'y']
        """
        names = set(self.bindings.keys())
        
        if self.parent is not None:
            names.update(self.parent.get_all_names())
        
        return names
    
    def __repr__(self) -> str:
        """Return string representation for debugging."""
        local_vars = ', '.join(f"{k}={v}" for k, v in self.bindings.items())
        parent_info = "with parent" if self.parent else "global"
        return f"Environment({local_vars}) [{parent_info}]"
    
    def __contains__(self, name: str) -> bool:
        """Support 'in' operator for checking variable existence.
        
        Example:
            >>> env = Environment()
            >>> env.define('x', 10)
            >>> 'x' in env
            True
        """
        return self.exists(name)

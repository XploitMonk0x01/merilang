"""
Tests for Environment class - lexical scoping system.

Author: MeriLang Team
Version: 2.0
"""

import pytest
from merilang.environment import Environment
from merilang.errors_enhanced import NameError as DesiNameError, RecursionError as DesiRecursionError


class TestBasicOperations:
    """Test basic environment operations."""
    
    def test_define_and_get(self):
        """Test defining and getting variables."""
        env = Environment()
        env.define('x', 42)
        assert env.get('x') == 42
    
    def test_define_multiple(self):
        """Test defining multiple variables."""
        env = Environment()
        env.define('x', 10)
        env.define('y', 20)
        env.define('name', "Ahmed")
        
        assert env.get('x') == 10
        assert env.get('y') == 20
        assert env.get('name') == "Ahmed"
    
    def test_redefine_variable(self):
        """Test redefining (updating) a variable."""
        env = Environment()
        env.define('x', 10)
        env.define('x', 20)  # Redefine
        assert env.get('x') == 20
    
    def test_get_undefined_raises_error(self):
        """Test that getting undefined variable raises NameError."""
        env = Environment()
        with pytest.raises(DesiNameError) as exc_info:
            env.get('undefined')
        assert "Undefined variable" in str(exc_info.value)


class TestScoping:
    """Test lexical scoping with parent environments."""
    
    def test_parent_scope_access(self):
        """Test accessing variables from parent scope."""
        global_env = Environment()
        global_env.define('x', 10)
        
        local_env = Environment(parent=global_env)
        assert local_env.get('x') == 10
    
    def test_local_shadows_parent(self):
        """Test that local variables shadow parent variables."""
        global_env = Environment()
        global_env.define('x', 10)
        
        local_env = Environment(parent=global_env)
        local_env.define('x', 20)
        
        assert local_env.get('x') == 20  # Local value
        assert global_env.get('x') == 10  # Parent unchanged
    
    def test_nested_scopes(self):
        """Test multiple levels of nested scopes."""
        global_env = Environment()
        global_env.define('global_var', 'global')
        
        func_env = Environment(parent=global_env)
        func_env.define('func_var', 'function')
        
        block_env = Environment(parent=func_env)
        block_env.define('block_var', 'block')
        
        # Block can access all levels
        assert block_env.get('block_var') == 'block'
        assert block_env.get('func_var') == 'function'
        assert block_env.get('global_var') == 'global'
        
        # Function cannot access block
        with pytest.raises(DesiNameError):
            func_env.get('block_var')
    
    def test_set_updates_correct_scope(self):
        """Test that set() updates variable in correct scope."""
        global_env = Environment()
        global_env.define('x', 10)
        
        local_env = Environment(parent=global_env)
        local_env.set('x', 20)  # Update parent's x
        
        assert global_env.get('x') == 20
        assert local_env.get('x') == 20
    
    def test_set_undefined_raises_error(self):
        """Test that setting undefined variable raises error."""
        env = Environment()
        with pytest.raises(DesiNameError) as exc_info:
            env.set('undefined', 42)
        assert "Cannot assign" in str(exc_info.value)


class TestExistenceChecks:
    """Test variable existence checking."""
    
    def test_exists_local(self):
        """Test exists() method."""
        env = Environment()
        env.define('x', 10)
        
        assert env.exists('x') is True
        assert env.exists('y') is False
    
    def test_exists_in_parent(self):
        """Test exists() checks parent scopes."""
        global_env = Environment()
        global_env.define('x', 10)
        
        local_env = Environment(parent=global_env)
        assert local_env.exists('x') is True
    
    def test_exists_local_only(self):
        """Test exists_local() doesn't check parent."""
        global_env = Environment()
        global_env.define('x', 10)
        
        local_env = Environment(parent=global_env)
        assert local_env.exists('x') is True  # Found in parent
        assert local_env.exists_local('x') is False  # Not in local
        
        local_env.define('y', 20)
        assert local_env.exists_local('y') is True
    
    def test_in_operator(self):
        """Test 'in' operator support."""
        env = Environment()
        env.define('x', 10)
        
        assert 'x' in env
        assert 'y' not in env


class TestGetAllNames:
    """Test getting all accessible variable names."""
    
    def test_get_all_names_single_scope(self):
        """Test get_all_names() in single scope."""
        env = Environment()
        env.define('x', 10)
        env.define('y', 20)
        env.define('z', 30)
        
        names = env.get_all_names()
        assert names == {'x', 'y', 'z'}
    
    def test_get_all_names_with_parent(self):
        """Test get_all_names() includes parent scope."""
        global_env = Environment()
        global_env.define('a', 1)
        global_env.define('b', 2)
        
        local_env = Environment(parent=global_env)
        local_env.define('c', 3)
        local_env.define('d', 4)
        
        names = local_env.get_all_names()
        assert names == {'a', 'b', 'c', 'd'}
    
    def test_get_all_names_shadowed_variables(self):
        """Test get_all_names() with shadowed variables."""
        global_env = Environment()
        global_env.define('x', 10)
        
        local_env = Environment(parent=global_env)
        local_env.define('x', 20)  # Shadow
        local_env.define('y', 30)
        
        names = local_env.get_all_names()
        assert names == {'x', 'y'}  # x appears once (shadowed)


class TestRecursionDepth:
    """Test recursion depth tracking and limits."""
    
    def test_recursion_depth_tracking(self):
        """Test that recursion depth is tracked correctly."""
        env1 = Environment()
        assert env1.recursion_depth == 0
        
        env2 = Environment(parent=env1)
        assert env2.recursion_depth == 1
        
        env3 = Environment(parent=env2)
        assert env3.recursion_depth == 2
    
    def test_max_recursion_depth_exceeded(self):
        """Test that exceeding max depth raises error."""
        # Temporarily reduce max depth for testing
        original_max = Environment.MAX_RECURSION_DEPTH
        Environment.MAX_RECURSION_DEPTH = 10
        
        try:
            env = Environment()
            for _ in range(10):
                env = Environment(parent=env)
            
            # This should raise error
            from merilang.errors_enhanced import RuntimeError as DesiRuntimeError
            with pytest.raises(DesiRuntimeError) as exc_info:
                Environment(parent=env)
            assert "recursion depth" in str(exc_info.value).lower()
        
        finally:
            Environment.MAX_RECURSION_DEPTH = original_max


class TestStringRepresentation:
    """Test string representation of environments."""
    
    def test_repr_empty(self):
        """Test repr of empty environment."""
        env = Environment()
        repr_str = repr(env)
        assert "Environment" in repr_str
        assert "global" in repr_str
    
    def test_repr_with_variables(self):
        """Test repr with variables."""
        env = Environment()
        env.define('x', 10)
        env.define('name', "test")
        repr_str = repr(env)
        assert "Environment" in repr_str
        assert "x=10" in repr_str
    
    def test_repr_with_parent(self):
        """Test repr shows parent existence."""
        global_env = Environment()
        local_env = Environment(parent=global_env)
        repr_str = repr(local_env)
        assert "with parent" in repr_str


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_define_none_value(self):
        """Test defining variable with None value."""
        env = Environment()
        env.define('x', None)
        assert env.get('x') is None
    
    def test_define_empty_string(self):
        """Test defining variable with empty string."""
        env = Environment()
        env.define('text', '')
        assert env.get('text') == ''
    
    def test_define_zero(self):
        """Test defining variable with zero."""
        env = Environment()
        env.define('count', 0)
        assert env.get('count') == 0
    
    def test_define_false(self):
        """Test defining variable with False."""
        env = Environment()
        env.define('flag', False)
        assert env.get('flag') is False
    
    def test_variable_name_unicode(self):
        """Test variable names with Unicode characters."""
        env = Environment()
        env.define('नाम', "Hindi")
        env.define('संख्या', 42)
        assert env.get('नाम') == "Hindi"
        assert env.get('संख्या') == 42


class TestComplexScenarios:
    """Test complex real-world scenarios."""
    
    def test_function_closure_simulation(self):
        """Simulate function closure with nested environments."""
        # Global scope
        global_env = Environment()
        global_env.define('multiplier', 2)
        
        # Function scope
        func_env = Environment(parent=global_env)
        func_env.define('x', 10)
        
        # Function can access both
        assert func_env.get('x') == 10
        assert func_env.get('multiplier') == 2
        
        # Result calculation
        result = func_env.get('x') * func_env.get('multiplier')
        assert result == 20
    
    def test_class_instance_simulation(self):
        """Simulate class instance with properties."""
        # Class scope (like class definition)
        class_env = Environment()
        class_env.define('classVar', 'class')
        
        # Instance scope
        instance_env = Environment(parent=class_env)
        instance_env.define('instanceVar', 'instance')
        
        # Instance can access class variables
        assert instance_env.get('classVar') == 'class'
        assert instance_env.get('instanceVar') == 'instance'
    
    def test_block_scope_simulation(self):
        """Simulate block scoping (if/while blocks)."""
        func_env = Environment()
        func_env.define('x', 10)
        
        # If block
        if_env = Environment(parent=func_env)
        if_env.define('temp', 20)
        
        # Can access parent
        assert if_env.get('x') == 10
        
        # Parent cannot access block-local
        with pytest.raises(DesiNameError):
            func_env.get('temp')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

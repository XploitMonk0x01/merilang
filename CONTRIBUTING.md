# Contributing to DesiLang

Thank you for your interest in contributing to DesiLang! This document provides guidelines for contributing to the project.

## 🌟 Ways to Contribute

### 1. Report Bugs 🐛

Found a bug? Please [open an issue](https://github.com/XploitMonk0x01/merilang/issues) with:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Minimal code to reproduce the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: Python version, OS, DesiLang version

**Example**:

````markdown
**Bug**: Division by zero not caught properly

**Code**:

```desilang
maan x = 10 / 0
```
````

**Expected**: DivisionByZeroError
**Actual**: Generic RuntimeError
**Environment**: Python 3.11, Windows 11, DesiLang 2.0.0

````

### 2. Suggest Features 💡

Have an idea? [Open a feature request](https://github.com/XploitMonk0x01/merilang/issues) with:
- **Feature Description**: What you want to add
- **Use Case**: Why it's useful
- **Examples**: Code examples showing the feature
- **Alternatives**: Other ways to achieve the same goal

### 3. Improve Documentation 📖

Documentation improvements are always welcome:
- Fix typos and grammar
- Add missing explanations
- Create new examples
- Translate content
- Improve clarity

### 4. Submit Code 🔧

Want to fix a bug or add a feature? Follow these steps:

#### Setup Development Environment

```bash
# Fork and clone
git clone https://github.com/XploitMonk0x01/merilang.git
cd merilang

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
````

#### Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/bug-description
```

#### Make Changes

1. **Write Code**: Implement your feature/fix
2. **Add Tests**: Write tests for new functionality
3. **Update Docs**: Update documentation if needed
4. **Run Tests**: Ensure all tests pass
5. **Format Code**: Use black and ruff

```bash
# Run tests
pytest

# Check coverage
pytest --cov=desilang --cov-report=html

# Type checking
mypy desilang

# Format code
black desilang tests

# Lint code
ruff check desilang tests
```

#### Commit Changes

Follow commit message conventions:

```bash
# Feature
git commit -m "feat: add dictionary comprehension support"

# Bug fix
git commit -m "fix: handle division by zero in parser"

# Documentation
git commit -m "docs: add examples for lambda functions"

# Tests
git commit -m "test: add test cases for error handling"

# Refactor
git commit -m "refactor: simplify environment lookup logic"
```

#### Submit Pull Request

1. Push to your fork
2. Open a pull request
3. Describe your changes
4. Link related issues
5. Wait for review

## 📋 Code Guidelines

### Python Style

Follow [PEP 8](https://pep8.org/) and use type hints:

```python
def process_node(node: ASTNode, env: Environment) -> Any:
    """
    Process an AST node.

    Args:
        node: The AST node to process
        env: The current environment

    Returns:
        The result of processing the node

    Raises:
        RuntimeError: If processing fails
    """
    # Implementation
    pass
```

### Testing

Write tests for all new functionality:

```python
def test_lambda_function():
    """Test lambda function creation and execution."""
    code = "maan f = lambada x: x * 2\nwapas f(5)"
    result = run_code(code)
    assert result == 10
```

### Documentation

Document all public APIs:

```python
class Parser:
    """
    Parse tokens into an Abstract Syntax Tree.

    The parser consumes a list of tokens and produces an AST
    representing the program structure.

    Example:
        >>> lexer = Lexer("maan x = 10")
        >>> tokens = lexer.tokenize()
        >>> parser = Parser(tokens)
        >>> ast = parser.parse()
    """
```

## 🔍 Code Review Process

1. **Automated Checks**: GitHub Actions will run tests
2. **Manual Review**: Maintainers will review code
3. **Feedback**: Address review comments
4. **Approval**: Get approval from maintainer
5. **Merge**: PR will be merged

## 🎯 Priority Areas

### High Priority

- 🐛 Bug fixes
- 🔒 Security improvements
- 📖 Documentation improvements
- ✅ Test coverage

### Medium Priority

- ✨ New language features
- 🚀 Performance improvements
- 🌍 Translations
- 📝 Example programs

### Low Priority

- 🎨 Code style improvements
- ♻️ Refactoring
- 🧹 Code cleanup

## 📚 Resources

### Documentation

- [Tutorial](docs/TUTORIAL.md) - Language tutorial
- [API Reference](docs/API.md) - API documentation
- [Examples](examples/) - Example programs

### Code Structure

```
desilang/
├── lexer_enhanced.py      # Tokenization
├── parser_enhanced.py     # Parsing
├── interpreter_enhanced.py # Execution
├── environment.py         # Variable scopes
├── errors_enhanced.py     # Error handling
└── ast_nodes_enhanced.py  # AST definitions
```

### Testing

- Unit tests in `tests/`
- Integration tests for features
- Performance benchmarks in `benchmarks/`

## 🤝 Community

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

### Communication

- **Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions
- **Discussions**: General questions and ideas

## 🎓 First-Time Contributors

New to open source? Start here:

### Good First Issues

Look for issues labeled `good first issue`:

- Documentation fixes
- Simple bug fixes
- Adding tests
- Adding examples

### Getting Help

- Read the documentation
- Check existing issues
- Ask in discussions
- Tag maintainers if stuck

## 📝 Checklist

Before submitting a pull request:

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Tests pass locally
- [ ] Type hints added
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main
- [ ] No merge conflicts

## 🏆 Recognition

Contributors will be:

- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Acknowledged in documentation

## 📧 Contact

Questions? Reach out:

- **Issues**: [GitHub Issues](https://github.com/XploitMonk0x01/merilang/issues)
- **Email**: maintainer@desilang.org (if applicable)

---

**Thank you for contributing to DesiLang!** 🙏

Your contributions help make programming more accessible to millions of Hindustani speakers worldwide.

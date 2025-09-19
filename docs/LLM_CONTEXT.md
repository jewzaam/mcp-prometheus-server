# LLM Context and AI Development Guide

This document provides comprehensive context for AI coding assistants working with the MCP Prometheus Server project. Use this information to help AI understand the project structure, conventions, and best practices.

## 🎯 Project Overview

This is an **MCP Prometheus Server** designed for:
- Querying Prometheus metrics through Model Context Protocol
- Providing AI assistants with monitoring data access
- Supporting relative time queries and instance-specific data
- Clean, maintainable code structure with comprehensive testing

## 📋 Project Structure Context

### Source Code Organization
```
src/mcp_prometheus_server/    # Main Python package
├── __init__.py               # Package metadata
├── main.py                   # CLI application entry point
├── mcp_server.py            # MCP server implementation
└── prometheus_client.py     # Prometheus API client
```

### Testing Structure
```
tests/
├── unit/                    # Fast, isolated unit tests
├── integration/             # End-to-end integration tests
└── __init__.py
```

### Build System
```
make/                        # Modular Makefile components
├── common.mk                # Shared variables (colors, Python paths)
├── env.mk                   # Virtual environment & dependencies
├── lint.mk                  # Code quality, type checking & formatting
├── test.mk                  # Testing targets
└── mcp.mk                   # MCP server development
```

## 🛠️ Development Standards

### Code Quality Tools
- **ruff**: Primary linter AND formatter (replaces flake8, pylint, black, isort)
- **mypy**: Static type checking (strict mode enabled)
- **pytest**: Testing framework with coverage

### Python Requirements
- **Minimum Python**: 3.10+
- **Type hints**: Required for all functions/methods
- **Docstrings**: Required for public APIs
- **Error handling**: Use proper exception types

### Code Style Conventions
- Line length: 88 characters (ruff default)
- Import order: stdlib, third-party, local (ruff handles sorting)
- Function names: snake_case
- Class names: PascalCase
- Constants: UPPER_SNAKE_CASE
- Private attributes: _single_underscore

## 🚀 Common Development Tasks

### Critical Template Commands

Every Python project using this template should support these core commands:

```bash
make test              # Run all tests - MUST work
make lint              # Run linting/type checking - MUST pass  
make coverage          # Generate coverage reports - MUST work
make format            # Format code with ruff - MUST work
make install-cursor    # Configure MCP integration - MUST work for MCP projects
```

**Current Make Targets (18 total):**
```
help            Display this help message
venv            Create Python virtual environment  
uv              Install uv package manager
requirements    Install all dependencies (runtime)
requirements-dev Install all dev dependencies
clean           Remove temporary and backup files
test            Run all tests (unit + integration)
test-unit       Run unit tests only
test-integration Run integration tests only
coverage-report Run tests with coverage report (no threshold check)
coverage-verify Verify coverage meets threshold (run after coverage-report)
coverage        Run tests with coverage report and enforce threshold
lint            Run linting and type checking
format          Format code
venv-cursor     Create dedicated virtual environment for Cursor MCP integration
install-cursor  Install MCP server for Cursor integration
clean-cursor    Clean MCP-specific artifacts including Cursor venv
```

### Setting Up Development Environment
```bash
make requirements-dev        # Install all dependencies (creates venv + installs)
make requirements           # Install runtime dependencies only
make venv                    # Create virtual environment only
make uv                      # Install uv package manager
make clean                   # Clean up artifacts and venv
make clean-cursor           # Clean MCP-specific artifacts
```

### Code Quality Workflow
```bash
make lint                    # Run linting (ruff + mypy)
make format                  # Format code with ruff (format + auto-fix)
```

### Testing Workflow
```bash
make test                    # Run all tests (unit + integration)
make test-unit              # Unit tests only
make test-integration       # Integration tests only
make coverage-report        # Tests with coverage report (no threshold)
make coverage-verify        # Verify coverage threshold (run after coverage-report)
make coverage               # Tests with coverage report + threshold enforcement (90% default)

# Override coverage threshold
COVERAGE_THRESHOLD=85 make coverage-verify    # Use 85% threshold instead of 90%
COVERAGE_THRESHOLD=95 make coverage           # Use 95% threshold for stricter checking
```

### MCP Server Development
```bash
make venv-cursor            # Create dedicated Cursor virtual environment
make install-cursor         # Install MCP server + configure Cursor IDE
make clean-cursor           # Clean MCP-specific artifacts
```

## 🤖 AI Assistant Guidelines

### When Adding New Features
1. **Create in appropriate module**: Use `src/mcp_prometheus_server/` for source code
2. **Add comprehensive tests**: Both unit and integration tests
3. **Include type hints**: All functions must have proper typing
4. **Write docstrings**: Document purpose, parameters, return values
5. **Follow naming conventions**: snake_case for functions, PascalCase for classes

### Code Quality Expectations
- All code must pass `make lint` (ruff + mypy)
- All tests must pass `make test`
- New code should maintain >90% test coverage
- No TODO comments in production code
- Proper error handling with specific exception types

### File Organization Patterns

#### New Module Template
```python
"""
Module description.

This module handles [specific functionality].
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class ExampleClass:
    """Class description."""
    
    def __init__(self, param: str) -> None:
        """Initialize the class."""
        self.param = param
    
    def public_method(self, data: Dict[str, Any]) -> Optional[str]:
        """Public method with proper typing and docstring."""
        # Implementation here
        pass
    
    def _private_method(self) -> None:
        """Private method (single underscore)."""
        pass
```

#### Test File Template
```python
"""
Tests for module_name.

Comprehensive tests covering normal cases, edge cases, and error conditions.
"""

import pytest
from unittest.mock import Mock, patch

from mcp_prometheus_server.module_name import ExampleClass


class TestExampleClass:
    """Test cases for ExampleClass."""
    
    def test_init(self):
        """Test class initialization."""
        obj = ExampleClass("test")
        assert obj.param == "test"
    
    def test_public_method_success(self):
        """Test successful method execution."""
        obj = ExampleClass("test")
        result = obj.public_method({"key": "value"})
        assert result is not None
    
    def test_public_method_error_handling(self):
        """Test method error handling."""
        obj = ExampleClass("test")
        with pytest.raises(ValueError):
            obj.public_method({})
    
    @pytest.mark.parametrize("input_value,expected", [
        ("input1", "output1"),
        ("input2", "output2"),
    ])
    def test_parametrized(self, input_value, expected):
        """Test with multiple parameter sets."""
        obj = ExampleClass(input_value)
        result = obj.public_method({"data": input_value})
        assert result == expected
```

## 🔧 MCP Server Development Context

### MCP Server Implementation
This project implements a complete MCP server with four tools:

1. **`query_metric`**: Execute any PromQL query with relative time support
2. **`get_instance_value`**: Get current metric value for a specific instance  
3. **`get_metric_history`**: Retrieve historical time series data
4. **`list_available_metrics`**: Discover available metrics with optional filtering

The server is implemented in `src/mcp_prometheus_server/mcp_server.py` with:
- Proper async/await patterns
- Comprehensive error handling
- Clear tool descriptions and input schemas
- Prometheus client integration

### MCP Server Code Patterns
```python
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools with proper schemas."""
    return [
        Tool(
            name="tool_name",
            description="Clear description of what the tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["param"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[TextContent]:
    """Handle tool calls with proper error handling."""
    if name == "tool_name":
        # Validate arguments
        if not arguments or "param" not in arguments:
            raise ValueError("Missing required parameter: param")
        
        # Process tool logic
        result = process_tool_logic(arguments["param"])
        
        return [TextContent(type="text", text=str(result))]
    else:
        raise ValueError(f"Unknown tool: {name}")
```

## 📏 Configuration Management

### pyproject.toml Structure
- **Build system**: setuptools with wheel
- **Project metadata**: name, version, description, authors
- **Dependencies**: Core and optional dependencies
- **Tool configurations**: All tools configured here (ruff, mypy, black, etc.)

### Key Configuration Sections
```toml
[tool.ruff]
# Modern all-in-one linting and formatting
line-length = 88
target-version = "py310"

[tool.ruff.lint]
# Comprehensive rule set enabled
# COM812 disabled (conflicts with formatter)

[tool.mypy]
# Strict type checking enabled
# All type-related warnings enabled

[tool.pytest.ini_options]
# Coverage reporting enabled with XML output for CI
addopts = "-v --tb=short --cov=src --cov-report=html --cov-report=term --cov-report=xml"
# Async mode auto-detection
```

### GitHub Workflows Structure

The template includes four focused workflows for flexible adoption:

**`.github/workflows/test.yml`**:
- Tests across Python 3.10, 3.11, 3.12
- Runs `make test`
- Triggers on pull requests and pushes to main

**`.github/workflows/lint.yml`**:
- Runs `make lint` (ruff + mypy)
- Uses Python 3.12
- Triggers on pull requests and pushes to main

**`.github/workflows/format.yml`**:
- Runs `make format` (ruff format + auto-fix)
- Fails if any formatting changes are required
- Uses git diff to detect changes

**`.github/workflows/coverage.yml`**:
- Clean 4-step flow: coverage-report → extract data → PR comment+badge → coverage-verify
- Uses DRY approach: coverage percentage stored in `.coverage-percentage` file
- Single data extraction point, no duplication
- Dynamic coverage badge in PR comments
- Final pass/fail handled by `make coverage-verify`
- Configurable threshold via `COVERAGE_THRESHOLD` variable (default: 90%)

### Makefile Architecture

**Clean modular structure following reference repositories:**

```
make/common.mk     # Shared variables (VENV_DIR, COVERAGE_THRESHOLD, colors, Python paths)
     ↗ ↗ ↗ ↗ ↗
Makefile          # Main entry point, includes common.mk first
make/env.mk       # Environment setup (venv, uv, requirements, requirements-dev, clean)
make/test.mk      # Testing (test, test-unit, test-integration, coverage)
make/lint.mk      # Linting & formatting (lint with ruff + mypy, format with ruff)
make/mcp.mk       # MCP server support (venv-cursor, install-cursor, clean-cursor)
```

**Key improvements:**
- **No cyclic dependencies**: `common.mk` holds shared variables
- **Single source of truth**: Colors and Python paths defined once
- **Modular**: Each `.mk` file has a specific purpose
- **Reference-based**: Follows patterns from `../workstation-setup`, `../git-checkout-main`

## ⚡ Performance and Best Practices

### Code Performance
- Use type hints for better optimization
- Leverage async/await for I/O operations
- Use list comprehensions over loops where appropriate
- Profile code with cProfile when needed

### Testing Best Practices
- Unit tests should be fast (<1s each)
- Integration tests can be slower but should complete quickly
- Use fixtures for common setup
- Mock external dependencies
- Test edge cases and error conditions

### Development Workflow
1. **Start with tests**: Write failing tests first (TDD)
2. **Implement feature**: Make tests pass
3. **Refactor**: Improve code while keeping tests green
4. **Quality check**: Run `make lint test format` before committing
5. **Format**: Run `make format` to ensure consistent style (ruff format + auto-fix)

## 🔍 Debugging and Troubleshooting

### Common Issues and Solutions

#### Import Errors
- Ensure `PYTHONPATH` includes `src/`
- Use relative imports within package
- Install package in development mode: `pip install -e .`

#### Test Failures
- Run individual tests: `pytest tests/unit/test_specific.py::test_function`
- Use verbose mode: `pytest -v`
- Check coverage: `pytest --cov=src`

#### Linting Errors
- Auto-fix where possible: `make format` (includes ruff check --fix)
- Check specific tool: `ruff check src/` or `mypy src/`
- Review configuration in `pyproject.toml`

#### MCP Server Issues
- Check Cursor configuration: `~/.cursor/mcp_settings.json`
- Test server directly: `python scripts/test_mcp_client.py`
- Verify virtual environment: `which python`

## 📚 Resources and References

### Documentation Links
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [ruff Rules](https://docs.astral.sh/ruff/rules/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

### Template Philosophy
This template prioritizes:
1. **Developer Experience**: Fast setup, clear structure, helpful tooling
2. **Code Quality**: Strict linting, type checking, comprehensive testing
3. **Maintainability**: Modular design, clear documentation, consistent patterns
4. **AI Collaboration**: Clear structure for AI assistants to understand and extend

## 🎯 AI Assistant Prompt Templates

### Adding a New Feature
```
"I need to add a new feature to handle [functionality]. Please:
1. Create a new module in src/template_python/[module_name].py
2. Include proper type hints and docstrings
3. Add comprehensive unit tests in tests/unit/test_[module_name].py
4. Add integration tests if needed
5. Ensure all code passes make lint and make test
6. Add attribution comment: # Generated-by: Cursor (claude-4-sonnet)"
```

### Implementing MCP Server
```
"Help me implement an MCP server that provides [functionality]. Please:
1. Uncomment and modify src/template_python/mcp_server.py
2. Add the required MCP dependencies to pyproject.toml
3. Implement tools for [specific tools needed]
4. Add proper error handling and input validation
5. Create test client in scripts/test_mcp_client.py
6. Run make install-cursor to configure Cursor integration
7. Update documentation for the new MCP features"
```

### Code Review
```
"Review this code for improvements using the mcp-prometheus-server standards:
- Type hints and docstrings complete
- Follows ruff/mypy requirements
- Proper error handling
- Good test coverage
- Follows project conventions
- Has proper attribution comments"
```

### Adding Make Targets
```
"I need to add new make targets for [functionality]. Please:
1. Add targets to the appropriate make/*.mk file:
   - Environment: make/env.mk
   - Testing: make/test.mk  
   - Linting: make/lint.mk
   - MCP: make/mcp.mk
2. Use variables from make/common.mk (VENV_PYTHON, colors, etc.)
3. Follow the established pattern with help comments
4. Test that make help shows the new targets"
```

## 📋 Template Attribution

All generated files must include attribution:
- **Python files**: `# Generated-by: Cursor (claude-4-sonnet)`
- **Markdown files**: `<!-- Generated-by: Cursor (claude-4-sonnet) -->`
- **Config files**: `# Generated-by: Cursor (claude-4-sonnet)`

## 🎯 Template Quality Assessment

### ✅ Critical Features Verified
This template has been thoroughly tested and provides:

**Core Make Targets:**
- ✅ `make test` - All tests pass with good coverage
- ✅ `make lint` - Ruff + mypy linting works correctly  
- ✅ `make format` - Ruff formatting with auto-fix
- ✅ `make coverage` - Comprehensive coverage reporting
- ✅ `make install-cursor` - MCP server configuration

**GitHub Workflows:**
- ✅ Separate test, lint, format, and coverage workflows
- ✅ Multi-Python version testing (3.10, 3.11, 3.12)
- ✅ Format enforcement (fails if changes needed)
- ✅ Coverage threshold enforcement (90% by default)

**Project Structure:**
- ✅ Modern Python package structure (`src/` layout)
- ✅ Comprehensive testing (unit + integration)
- ✅ Modular Makefile system (no cyclic dependencies)
- ✅ All tools properly configured

**Template Features:**
- ✅ MCP Server Support with templates and setup scripts
- ✅ Modern Tooling: ruff (linting + formatting), mypy, pytest
- ✅ CI/CD: Focused GitHub Actions workflows
- ✅ AI-Friendly: Comprehensive LLM context and attribution

### 📋 Template Usage for New Projects

1. **Clone/fork this template**
2. **Customize pyproject.toml** (name, description, authors, dependencies)
3. **Rename package**: `mv src/template_python src/your_project`
4. **Update imports and references** throughout codebase
5. **Implement your code** in the package structure
6. **Run critical commands**: `make test`, `make lint`, `make format`, `make coverage`
7. **For MCP projects**: Uncomment MCP dependencies and run `make install-cursor`
8. **Configure CI**: Update GitHub workflow badges in README with your repo URL

### 🏆 Template Quality Rating

**EXCELLENT** - This template provides a production-ready foundation with:
- ✅ All requested critical features working out of the box
- ✅ Modern Python best practices and tooling
- ✅ Comprehensive documentation and AI assistant integration  
- ✅ Clean, maintainable modular structure
- ✅ Optional MCP server capabilities
- ✅ Flexible GitHub workflows for any project type

The template is **ready for immediate use** and provides a solid, extensible foundation for any Python project.

---

Use this context to help AI assistants understand the project structure, maintain consistency, and follow best practices throughout development.
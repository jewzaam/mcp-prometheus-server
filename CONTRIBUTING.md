<!-- Generated-by: Cursor (claude-4-sonnet) -->
# Contributing to Python Template Project

Thank you for your interest in contributing to this Python template project! This document provides guidelines for contributing to the template itself.

## 🎯 Types of Contributions

We welcome several types of contributions:

1. **Template improvements**: Better structure, tooling, or practices
2. **Documentation**: Clearer guides, examples, or LLM context
3. **Bug fixes**: Issues with the template setup or scripts
4. **New features**: Additional tools, integrations, or capabilities
5. **Examples**: Sample implementations or use cases

## 🚀 Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/your-username/template-python.git
cd template-python
```

### 2. Set Up Development Environment

```bash
make requirements-dev
```

### 3. Verify Everything Works

```bash
make test lint format
```

This should pass all linting and tests.

## 📝 Development Guidelines

### Code Quality Standards

All contributions must:
- Pass `make lint` (ruff + mypy)
- Pass `make test` with coverage meeting threshold (90% default, configurable via COVERAGE_THRESHOLD)
- Follow the established project structure
- Include appropriate documentation
- Use proper type hints and docstrings

### Template Design Principles

When contributing to the template, keep these principles in mind:

1. **Simplicity**: Template should be easy to understand and use
2. **Modularity**: Keep concerns separated (e.g., modular Makefiles)
3. **Best Practices**: Follow modern Python development standards
4. **AI-Friendly**: Structure should be clear for AI assistants
5. **Documentation**: Every feature should be well-documented

### Making Changes

#### For Template Structure Changes
1. Create a feature branch: `git checkout -b feature/improve-makefile`
2. Make your changes
3. Test thoroughly: `make clean && make requirements-dev && make test lint format`
4. Update documentation if needed
5. Commit with clear messages

#### For Documentation Changes
1. Update relevant `.md` files
2. Ensure accuracy with current code
3. Test any code examples
4. Consider impact on LLM context

#### For MCP-Related Changes
1. Test MCP functionality: `make install-cursor`
2. Verify Cursor integration works
3. Update MCP documentation
4. Consider backward compatibility

## 🧪 Testing Your Changes

### Manual Testing Checklist

Before submitting, verify:

- [ ] `make clean && make requirements-dev` works from scratch
- [ ] `make lint` passes without errors
- [ ] `make test` passes all tests
- [ ] `make format` doesn't change anything (code already formatted)
- [ ] `make coverage` meets the threshold
- [ ] MCP functionality works if modified: `make install-cursor`
- [ ] Documentation is accurate and complete

### Testing the Template

To test the template as a new user would:

```bash
# In a temporary directory
cp -r template-python new-test-project
cd new-test-project
rm -rf .git

# Test fresh setup
make requirements-dev
make test lint format

# Test MCP if applicable
make install-cursor
```

## 📋 Pull Request Process

### Before Submitting

1. **Clean commit history**: Squash related commits if needed
2. **Clear description**: Explain what changed and why
3. **Test thoroughly**: Follow the testing checklist above
4. **Update docs**: Include relevant documentation updates

### Pull Request Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Template improvement
- [ ] Other (please describe)

## Testing
- [ ] Ran `make clean && make requirements-dev && make test lint format`
- [ ] All tests pass with coverage threshold
- [ ] Manual testing completed
- [ ] MCP functionality tested (if applicable): `make install-cursor`

## Documentation
- [ ] Documentation updated
- [ ] LLM context updated if needed
- [ ] Examples provided if needed

## Additional Context
Any additional information that reviewers should know.
```

### Review Process

1. **Automated checks**: GitHub Actions will run linting and tests
2. **Manual review**: Maintainers will review for:
   - Code quality and consistency
   - Template design principles
   - Documentation accuracy
   - Backward compatibility
3. **Testing**: Changes will be tested in real-world scenarios
4. **Merge**: Once approved, changes will be merged

## 🔧 Specific Contribution Areas

### Improving the Makefile System

The modular Makefile system is a key feature. When contributing:

- Keep targets in appropriate `.mk` files (`common.mk`, `env.mk`, `test.mk`, `lint.mk`, `mcp.mk`)
- Maintain clear target documentation with `## comments`
- Ensure targets work across different environments
- Add color output for better UX
- Test targets in isolation and combination

### Enhancing MCP Integration

For MCP-related improvements:

- Maintain compatibility with Cursor IDE
- Keep MCP dependencies optional
- Provide clear examples and documentation
- Test with actual MCP servers
- Consider different MCP use cases

### Documentation Improvements

When improving documentation:

- Keep the AI/LLM context comprehensive
- Provide concrete examples
- Test all code snippets
- Consider different skill levels
- Update both README and docs/

### Adding New Tools

When adding new development tools:

- Integrate with the existing Makefile system
- Configure in `pyproject.toml` when possible
- Document usage clearly
- Ensure cross-platform compatibility
- Add appropriate CI/CD integration

## 🐛 Reporting Issues

### Bug Reports

Include:
- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
- Output from `make --version` and relevant make targets
- Any error messages

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative approaches considered
- Impact on existing functionality

## 💬 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check docs/ directory first

## 🎉 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributor graphs

Thank you for helping make this Python template better for everyone! 🚀
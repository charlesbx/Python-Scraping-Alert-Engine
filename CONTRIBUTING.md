# Contributing to AutoScrape

Thank you for your interest in contributing to AutoScrape! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/charlesbx/Python-Scraping-Alert-Engine.git
   cd Python-Scraping-Alert-Engine
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## Code Quality Standards

This project follows professional Python development practices:

### Code Formatting
- **Black**: Code formatting (line length: 100)
- **isort**: Import sorting

Run formatters:
```bash
black src/ tests/
isort src/ tests/
```

### Linting
- **flake8**: Code linting
- **pylint**: Additional linting (optional)

Run linters:
```bash
flake8 src/ tests/
```

### Type Hints
- All functions should have type hints
- Use `typing` module for complex types

### Testing
- **pytest**: Testing framework
- All new features must include tests
- Maintain or improve code coverage

Run tests:
```bash
pytest tests/ -v
pytest tests/ --cov=src/autoscrape --cov-report=term
```

## Contributing Workflow

1. **Fork the repository**
   - Click the "Fork" button on GitHub

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

4. **Run quality checks**
   ```bash
   # Format code
   black src/ tests/
   isort src/ tests/
   
   # Run tests
   pytest tests/ -v
   
   # Check linting
   flake8 src/ tests/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Test additions/changes
   - `refactor:` - Code refactoring
   - `style:` - Code style changes
   - `chore:` - Maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Provide a clear description of your changes

## Code Review Process

1. All PRs require at least one review
2. CI checks must pass (tests, linting, security)
3. Code coverage should not decrease
4. Documentation must be updated if needed

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces

## Questions?

Feel free to open an issue for any questions or discussions about contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

Thank you for contributing! 🎉

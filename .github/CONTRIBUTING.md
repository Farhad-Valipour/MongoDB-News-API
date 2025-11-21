# Contributing to MongoDB News API

First off, thank you for considering contributing to MongoDB News API! It's people like you that make this project better for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Testing Guidelines](#testing-guidelines)

---

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, curl commands, etc.)
- **Describe the behavior you observed** and what you expected
- **Include error messages and stack traces**
- **Specify your environment** (OS, Python version, MongoDB version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **Provide examples** of how it would work
- **List any alternative solutions** you've considered

### Pull Requests

We actively welcome your pull requests! Here's how:

1. Fork the repo and create your branch from `main`
2. If you've added code, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

---

## Development Setup

### Prerequisites

- Python 3.11+
- MongoDB 7.0+
- Git
- Docker (optional)

### Setup Steps

1. **Fork and clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/mongodb-news-api.git
cd mongodb-news-api
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

4. **Setup MongoDB**
```bash
# Option 1: Local MongoDB
sudo systemctl start mongodb

# Option 2: Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

6. **Run tests to verify setup**
```bash
pytest
```

---

## Pull Request Process

### Before Submitting

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Update CHANGELOG.md** with your changes
4. **Run the full test suite**:
```bash
pytest --cov=app --cov-report=html
```
5. **Check code quality**:
```bash
black app/ tests/
flake8 app/ tests/
mypy app/
```

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Coverage maintained (80%+)
- [ ] Commit messages follow conventions

### PR Title Format

Use conventional commits format:

```
<type>(<scope>): <subject>

Examples:
feat(api): add websocket support
fix(auth): resolve token expiration issue
docs(readme): update installation steps
test(news): add pagination edge cases
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Imports**: Use absolute imports
- **Type hints**: Required for all functions
- **Docstrings**: Google style

### Code Formatting

We use these tools:

- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting
- **MyPy**: Type checking

Run before committing:
```bash
# Format code
black app/ tests/
isort app/ tests/

# Check style
flake8 app/ tests/

# Check types
mypy app/
```

### Docstring Example

```python
def get_news_by_slug(slug: str, db: Database) -> NewsDetail:
    """
    Retrieve a single news article by its unique slug.
    
    This function queries the database for a news article matching
    the provided slug and returns detailed information.
    
    Args:
        slug: Unique identifier for the news article
        db: Database connection instance
    
    Returns:
        NewsDetail: Complete news article with metadata
    
    Raises:
        NewsNotFoundException: If article with slug not found
        
    Example:
        >>> news = get_news_by_slug("bitcoin-hits-50k", db)
        >>> print(news.title)
        "Bitcoin Hits $50,000 Milestone"
    """
    # Implementation
```

---

## Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Guidelines

- **Subject**: Imperative mood, lowercase, no period, max 50 chars
- **Body**: Explain what and why (not how), wrap at 72 chars
- **Footer**: Reference issues, breaking changes

### Examples

```
feat(api): add websocket endpoint for real-time news

Implement WebSocket connection for streaming news updates.
Clients can subscribe to specific sources or assets.

Closes #123
```

```
fix(auth): resolve token expiration handling

Token expiration was causing 500 errors instead of 401.
Now properly returns authentication error.

Fixes #456
```

---

## Testing Guidelines

### Writing Tests

1. **Test file location**: `tests/test_<module>.py`
2. **Test class name**: `Test<Feature>`
3. **Test method name**: `test_<behavior>`
4. **Use fixtures**: Defined in `conftest.py`
5. **Follow AAA**: Arrange, Act, Assert

### Test Example

```python
import pytest

@pytest.mark.unit
class TestNewsEndpoint:
    """Test suite for news endpoints."""
    
    async def test_get_news_returns_list(
        self,
        async_client,
        auth_headers,
        mock_database_manager
    ):
        """Test that GET /news returns list of news items."""
        # Arrange
        mock_db = mock_database_manager
        # ... setup mocks
        
        # Act
        response = await async_client.get(
            "/api/v1/news",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        assert "data" in response.json()
```

### Test Categories

Use markers for categorization:

```python
@pytest.mark.unit          # Unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.security      # Security tests
@pytest.mark.slow          # Slow tests
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific category
pytest -m unit
pytest -m integration

# Specific file
pytest tests/test_news.py

# Specific test
pytest tests/test_news.py::TestNewsEndpoint::test_get_news_returns_list
```

---

## Code Review Process

### What We Look For

1. **Correctness**: Does it work as intended?
2. **Tests**: Are there adequate tests?
3. **Documentation**: Is it well documented?
4. **Style**: Does it follow our guidelines?
5. **Performance**: Are there any bottlenecks?
6. **Security**: Are there any vulnerabilities?

### Review Timeline

- **Initial review**: Within 2-3 days
- **Follow-up**: Within 1-2 days after changes

---

## Getting Help

- 💬 **GitHub Discussions**: Ask questions
- 📫 **Email**: support@example.com
- 📚 **Documentation**: Check [docs/](docs/)

---

## Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md** file
- GitHub contributors page
- Release notes

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing! 🎉**

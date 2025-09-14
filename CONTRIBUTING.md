# Contributing to Shopify Partners SDK

Thank you for your interest in contributing to the Shopify Partners SDK! We welcome contributions from the community and are grateful for your help in making this project better.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Community](#community)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the [maintainer](mailto:mail@amitray.dev).

### Our Standards

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome newcomers and help them get started
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Remember that everyone has different experience levels

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- Git for version control
- A Shopify Partners account for testing (optional but recommended)

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/your-username/shopify-partners-sdk.git
   cd shopify-partners-sdk
   ```

2. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install Dependencies**
   ```bash
   poetry install
   ```

4. **Activate the Virtual Environment**
   ```bash
   poetry shell
   ```

5. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

6. **Verify Installation**
   ```bash
   poetry run pytest --version
   poetry run ruff --version
   poetry run mypy --version
   ```

## 📝 Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Suggest new features or improvements
- **📖 Documentation**: Improve or add documentation
- **🔧 Code Contributions**: Fix bugs or implement new features
- **🧪 Tests**: Add or improve test coverage
- **🎨 Examples**: Create usage examples or tutorials

### Before You Start

1. **Check Existing Issues**: Look through existing issues to avoid duplicates
2. **Discuss Major Changes**: For significant changes, open an issue first to discuss
3. **Follow Conventions**: Adhere to our coding standards and conventions
4. **Write Tests**: Include tests for new features or bug fixes

## 🔄 Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Write clean, readable code
- Follow our coding standards
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
poetry run pytest

# Run linting
poetry run ruff check .
poetry run ruff format --check .

# Run type checking
poetry run mypy .

# Run security checks
poetry run bandit -r src/

# Check test coverage
poetry run pytest --cov=shopify_partners_sdk --cov-report=term-missing
```

### 4. Commit Your Changes

Use conventional commit messages:

```bash
git add .
git commit -m "feat: add new field selector for app events"
# or
git commit -m "fix: handle rate limiting in pagination"
# or
git commit -m "docs: update installation instructions"
```

#### Commit Message Format

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:

- **Clear Title**: Describe what the PR does
- **Detailed Description**: Explain the changes and why they're needed
- **Issue References**: Link to related issues
- **Testing Notes**: Describe how you tested the changes
- **Breaking Changes**: Note any breaking changes

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 🎨 Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line Length**: 88 characters (Black default)
- **Imports**: Use `isort` for import sorting
- **Type Hints**: Required for all public APIs
- **Docstrings**: Google-style docstrings for all public functions/classes

### Code Quality Tools

We use several tools to maintain code quality:

- **[Black](https://black.readthedocs.io/)**: Code formatting
- **[Ruff](https://docs.astral.sh/ruff/)**: Fast Python linter
- **[MyPy](https://mypy.readthedocs.io/)**: Static type checking
- **[isort](https://pycqa.github.io/isort/)**: Import sorting
- **[Bandit](https://bandit.readthedocs.io/)**: Security linting

### Example Code Style

```python
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from shopify_partners_sdk.exceptions import GraphQLError


class AppQuery(BaseModel):
    """Represents an app query with field selection.
    
    Args:
        app_id: The unique identifier for the app.
        fields: List of fields to include in the query.
        include_events: Whether to include app events in the response.
        
    Raises:
        GraphQLError: If the query is invalid.
        
    Example:
        >>> query = AppQuery(
        ...     app_id="gid://shopify/App/123",
        ...     fields=["id", "title", "handle"],
        ...     include_events=True
        ... )
        >>> result = client.execute_query(query)
    """
    
    app_id: str = Field(..., description="The app identifier")
    fields: List[str] = Field(default_factory=list, description="Fields to query")
    include_events: bool = Field(default=False, description="Include app events")
    
    def to_graphql(self) -> str:
        """Convert the query to GraphQL format.
        
        Returns:
            The GraphQL query string.
            
        Raises:
            GraphQLError: If the query cannot be converted.
        """
        if not self.fields:
            raise GraphQLError("At least one field must be specified")
            
        # Implementation here...
        return query_string
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── test_client.py
│   ├── test_models.py
│   └── test_queries.py
├── integration/          # Integration tests
│   ├── test_api_calls.py
│   └── test_pagination.py
└── fixtures/             # Test data and fixtures
    ├── responses.json
    └── test_data.py
```

### Writing Tests

- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test interactions between components
- **Use Fixtures**: Create reusable test data
- **Mock External Calls**: Use `responses` library for HTTP mocking

### Test Example

```python
import pytest
from responses import mock

from shopify_partners_sdk import ShopifyPartnersClient
from shopify_partners_sdk.exceptions import AuthenticationError


class TestShopifyPartnersClient:
    """Test cases for ShopifyPartnersClient."""
    
    def test_client_initialization(self):
        """Test client can be initialized with valid credentials."""
        client = ShopifyPartnersClient(
            organization_id="test-org",
            access_token="test-token"
        )
        assert client.organization_id == "test-org"
        assert client.access_token == "test-token"
    
    @mock.activate
    def test_authentication_error(self):
        """Test client raises AuthenticationError for invalid credentials."""
        mock.add(
            mock.POST,
            "https://partners.shopify.com/api/graphql",
            json={"errors": [{"message": "Invalid credentials"}]},
            status=401
        )
        
        client = ShopifyPartnersClient(
            organization_id="invalid",
            access_token="invalid"
        )
        
        with pytest.raises(AuthenticationError):
            client.execute_raw("query { apps { id } }")
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/unit/test_client.py

# Run with coverage
poetry run pytest --cov=shopify_partners_sdk

# Run only unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration
```

## 📖 Documentation

### Documentation Types

- **API Documentation**: Docstrings in code
- **User Guide**: Usage examples and tutorials
- **Contributing Guide**: This document
- **Changelog**: Version history and changes

### Writing Documentation

- **Clear and Concise**: Use simple language
- **Include Examples**: Show practical usage
- **Keep Updated**: Update docs with code changes
- **Use Proper Formatting**: Follow Markdown conventions

### Building Documentation Locally

```bash
# Install documentation dependencies
poetry install --with docs

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

## 🐛 Issue Reporting

### Before Reporting

1. **Search Existing Issues**: Check if the issue already exists
2. **Check Documentation**: Ensure it's not a usage question
3. **Test with Latest Version**: Verify the issue exists in the latest release

### Bug Report Template

```markdown
**Describe the Bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Initialize client with '...'
2. Call method '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS 12.0]
- Python version: [e.g., 3.9.0]
- SDK version: [e.g., 0.1.1]

**Additional Context**
Any other context about the problem.
```

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Describe the problem this feature would solve.

**Proposed Solution**
How you think this feature should work.

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Any other context or screenshots.
```

## 💬 Community

### Getting Help

- **GitHub Discussions**: Ask questions and share ideas
- **Issues**: Report bugs and request features
- **Email**: Contact maintainers directly for sensitive issues

### Communication Guidelines

- **Be Respectful**: Treat everyone with kindness
- **Be Clear**: Provide context and details
- **Be Patient**: Maintainers are volunteers
- **Search First**: Check existing discussions and issues

## 🏆 Recognition

Contributors will be recognized in:

- **README.md**: Contributors section
- **CHANGELOG.md**: Release notes
- **GitHub**: Contributor graphs and statistics

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You

Thank you for contributing to the Shopify Partners SDK! Your efforts help make this project better for everyone in the Shopify developer community.

---

**Questions?** Feel free to reach out via [GitHub Discussions](https://github.com/amitray007/shopify-partners-sdk/discussions) or email the [maintainer](mailto:mail@amitray.dev).

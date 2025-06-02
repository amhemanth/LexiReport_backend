# Contributing to LexiReport

Thank you for your interest in contributing to LexiReport! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in the Issues section
2. If not, create a new issue with:
   - Clear and descriptive title
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots if applicable
   - Environment details

### Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue with:
   - Clear and descriptive title
   - Detailed description
   - Use cases
   - Potential implementation approach

### Pull Requests

1. Fork the repository
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Run tests:
   ```bash
   # Backend
   cd backend
   pytest

   # Frontend
   cd frontend
   npm test
   ```
5. Commit your changes:
   ```bash
   git commit -m "feat: add your feature"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a Pull Request

### Development Workflow

1. Set up development environment:
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

2. Start development servers:
   ```bash
   # Backend
   cd backend
   uvicorn app.main:app --reload

   # Frontend
   cd frontend
   npx expo start
   ```

### Code Style

#### Backend (Python)
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings
- Maximum line length: 88 characters

#### Frontend (TypeScript/React)
- Use functional components
- Follow TypeScript best practices
- Use proper type definitions
- Follow React Native guidelines

### Testing

#### Backend
- Write unit tests for new features
- Maintain test coverage
- Run tests before submitting PR:
  ```bash
  pytest
  ```

#### Frontend
- Write component tests
- Test on multiple platforms
- Run tests before submitting PR:
  ```bash
  npm test
  ```

### Documentation

- Update README.md if needed
- Add comments for complex logic
- Update API documentation
- Document new features

### Commit Messages

Follow the Conventional Commits specification:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `style:` for formatting
- `refactor:` for code changes
- `test:` for tests
- `chore:` for maintenance

Example:
```
feat: add user authentication
fix: resolve login error
docs: update API documentation
```

## Review Process

1. All PRs require at least one review
2. CI checks must pass
3. Code coverage must be maintained
4. Documentation must be updated

## Getting Help

- Join our Discord community
- Open an issue for questions
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 
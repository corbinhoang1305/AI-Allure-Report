# Contributing to QUALIFY.AI

Thank you for your interest in contributing to QUALIFY.AI! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check if the bug has already been reported in Issues
2. Collect information about the bug:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots (if applicable)
   - Environment details (OS, browser, versions)

Create a bug report with:
- Clear, descriptive title
- Detailed description
- Steps to reproduce
- Expected vs actual behavior
- Any relevant logs or screenshots

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
1. Check if the enhancement has been suggested
2. Provide a clear use case
3. Explain why this enhancement would be useful
4. Consider implementation details

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, documented code
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation

4. **Commit your changes**
   ```bash
   git commit -m "feat: add amazing feature"
   ```
   Follow [Conventional Commits](https://www.conventionalcommits.org/)

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description
   - Reference any related issues
   - Include screenshots for UI changes

## Development Setup

See [DEVELOPMENT.md](./docs/DEVELOPMENT.md) for detailed setup instructions.

## Coding Standards

### Python

- Follow PEP 8
- Use type hints
- Write docstrings
- Maximum line length: 100 characters

### TypeScript/React

- Use functional components
- Use TypeScript for all files
- Follow React best practices
- Use proper prop typing

### Commit Messages

Format: `<type>(<scope>): <subject>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(ai): add predictive analysis
fix(auth): resolve token refresh issue
docs(api): update endpoint documentation
```

## Testing

All contributions should include appropriate tests:

### Backend Tests
```bash
cd backend
pytest services/your-service/tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Documentation

- Update README.md if needed
- Add/update API documentation
- Update relevant docs in `/docs`
- Include inline code comments

## Review Process

1. Automated checks must pass
2. Code review by maintainers
3. Address feedback
4. Approval and merge

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

## Questions?

Feel free to:
- Open a discussion in GitHub Discussions
- Ask in pull request comments
- Contact maintainers

Thank you for contributing to QUALIFY.AI! 🚀


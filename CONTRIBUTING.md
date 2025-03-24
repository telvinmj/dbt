# Contributing to DBT Metadata Explorer

Thank you for your interest in contributing to DBT Metadata Explorer! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Workflow](#workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to maintain a welcoming and inclusive community.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/dbt-metadata-explorer.git
   cd dbt-metadata-explorer
   ```
3. **Set up the upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/dbt-metadata-explorer.git
   ```
4. **Create a new branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Environment

### Backend Setup

1. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the development server:
   ```bash
   python run.py
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Workflow

1. **Keep your branch updated** with the upstream main branch:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git commit -m "Feature: Add new model filtering capability"
   ```

3. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Submit a pull request** from your fork to the main repository

## Coding Standards

### Backend (Python)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints when possible
- Document functions, classes, and modules using docstrings
- Run formatting tools before committing:
  ```bash
  black .
  isort .
  flake8
  ```

### Frontend (TypeScript/React)

- Follow the project's ESLint and Prettier configuration
- Use TypeScript interfaces to define prop types
- Follow React best practices and hooks guidelines
- Run linting before committing:
  ```bash
  npm run lint
  npm run format
  ```

## Testing

### Backend

- Write unit tests for new functionality
- Ensure all tests pass before submitting changes:
  ```bash
  pytest
  ```

### Frontend

- Write component tests for new UI elements
- Ensure all tests pass before submitting changes:
  ```bash
  npm test
  ```

## Documentation

- Update the README.md if you change functionality
- Document new features in the appropriate docs files
- Add JSDoc comments to functions and components
- Update API documentation when endpoints change

## Submitting Changes

1. Ensure your code follows the project's coding standards
2. Ensure all tests pass
3. Update documentation as needed
4. Submit a pull request with a clear description of the changes and any relevant issue numbers
5. Respond to code review feedback

---

Thank you for contributing to DBT Metadata Explorer! Your efforts help make this project better for everyone. 
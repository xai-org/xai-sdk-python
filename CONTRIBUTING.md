# Contributing to xAI Python SDK

**Contributor License Agreement (CLA)**: By contributing to this repository, you agree to the terms outlined in the [CLA.md](CLA.md). Please read and ensure you understand and agree to the terms before submitting any contributions.

Thank you for your interest in contributing to the `xai-sdk-python` project! This guide outlines the process for external developers to add new features, fix bugs, or improve documentation through pull requests (PRs).

## Scope of Contributions

As an external contributor, you can propose changes to the codebase, tests, or documentation via PRs. However, version bumps and release processes are managed internally by the project maintainers. Your contributions will be reviewed and, if approved, merged into the `main` branch.

**Note on Contribution Size**: If you are considering a larger change or reporting a significant bug, we encourage you to first create a feature request or bug report issue in the repository. This allows for discussion and alignment with the project maintainers before investing time in a pull request. For small fixes, such as correcting typos or making minor documentation improvements, feel free to submit a pull request directly.

## Step 1: Fork and Clone the Repository, and Set Up the Development Environment

1. **Fork the Repository**: If you are an external contributor, start by forking the `xai-sdk-python` repository to your own GitHub account. This creates a copy of the repository under your control.
2. **Clone the Repository**: Clone the forked repository to your local machine and navigate to the project directory.
3. **Set Up Python Environment**: Ensure you have a version of Python ≥3.10 installed, as this project only supports Python 3.10 and above. The project uses `uv` for dependency management, so you'll also need to install it if not already installed.
4. **Install Dependencies**: Run `uv sync` to install the project dependencies into a virtual environment. `uv sync` will create the virtual environment and install all project dependencies for you.
5. **Install pre-commit hooks**: Run `uv run pre-commit install` to install the pre-commit hooks. This repo is configured to run pre-commit hooks such as ruff linting, formatting and secret detection preventing you from accidentally committing erroneous changes.

## Step 2: Create a Feature Branch

1. **Branch Off `main`**: Create a new branch from the `main` branch for your feature or fix. Name it descriptively, e.g., `feature/add-support-for-file-uploads` or `bugfix/resolve-api-error`.
2. **Implement Your Changes**: Write your code, add tests, and ensure your changes adhere to the project's coding standards.

## Step 3: Run CI Checks Locally

1. **Run Formatting Check**: Execute `uv run ruff format --check` to ensure your code adheres to the project's formatting standards. If issues are found, run `uv run ruff format` to automatically fix them.
2. **Run Linting Check**: Execute `uv run ruff check` to check for code quality and style issues. Address any warnings or errors reported.
3. **Run Type Safety Check**: Execute `uv run pyright` to verify type annotations and ensure type safety.
4. **Run Tests**: Execute `uv run pytest -n auto -v` to run the test suite locally. This ensures your changes don't break existing functionality.
5. **Fix Issues**: Address any issues identified by these checks before proceeding to the next step.

**Checks Involved**:
- These are the same checks as in the `ci.yaml` GitHub Actions workflow, allowing you to catch formatting, linting, type safety, and test issues locally before pushing to the remote repository.

## Step 4: Commit Changes and Push to Remote

1. **Commit Changes**: Commit your changes with meaningful commit messages that clearly describe the purpose of your changes.
2. **Push to Remote**: Push your branch to the remote repository (your fork or the main repository if you have write access).

**Checks Involved**: None at this stage. Checks will be triggered once a pull request is created.

## Step 5: Create a Pull Request (PR)

1. **Open a PR**: Create a pull request from your feature branch in your forked repository to the `main` branch of the `xai-sdk-python` repository.
2. **Add a Detailed Description**: Provide a high-quality description of the changes in your PR. Explain the purpose, the problem it solves, and any relevant context. This helps maintainers review your contribution effectively.
3. **Trigger CI Checks**: The `ci.yaml` workflow will automatically run on your PR. This includes:
   - **Formatting Check**: Ensures code adheres to formatting standards using `ruff format --check`.
   - **Linting Check**: Checks for code quality and style issues using `ruff check`.
   - **Type Safety Check**: Verifies type annotations using `pyright`.
   - **Tests**: Runs the test suite with `pytest` across multiple Python versions (3.10 to 3.13) to ensure compatibility and correctness.
   

**Checks Involved**:
- `ci.yaml` ensures your code meets quality and compatibility standards.

## Step 6: Address Feedback and Merge PR

1. **Review Feedback**: Address any comments or issues raised by reviewers or failing CI checks.
2. **Re-run Checks**: Push updates to your branch, and the CI checks will re-run automatically.
3. **Merge PR**: Once approved by maintainers and all checks pass, your PR will be merged into `main`. Note that merging does not trigger a release; release processes are handled internally.

**Checks Involved**: Same as Step 5, re-triggered on each push to the PR branch.

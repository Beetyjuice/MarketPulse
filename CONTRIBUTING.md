# Contributing to MarketPulse

First off, thank you for considering contributing to MarketPulse! It's people like you that make MarketPulse such a great tool for the Morocco investment community.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [your.email@example.com].

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title** for the issue
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples** to demonstrate the steps
* **Describe the behavior you observed** and explain what behavior you expected
* **Include screenshots** if possible
* **Include your environment details**: OS, Python version, Docker version, etc.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description** of the suggested enhancement
* **Explain why this enhancement would be useful**
* **List some examples** of how it would be used

### Pull Requests

* Fill in the required template
* Follow the Python style guide (PEP 8)
* Include docstrings for all functions and classes
* Add tests for new features
* Update documentation as needed
* Ensure the test suite passes
* Make sure your code lints (use `flake8`)

## Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/yourusername/MarketPulse.git
cd MarketPulse
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Run tests**
```bash
pytest tests/
```

5. **Run linting**
```bash
flake8 .
black .
mypy .
```

## Development Workflow

1. Create a new branch from `main`:
```bash
git checkout -b feature/amazing-feature
```

2. Make your changes

3. Add tests for your changes

4. Run the test suite:
```bash
pytest tests/
```

5. Commit your changes:
```bash
git add .
git commit -m "Add amazing feature"
```

6. Push to your fork:
```bash
git push origin feature/amazing-feature
```

7. Open a Pull Request

## Style Guide

### Python Code Style

* Follow [PEP 8](https://pep8.org/)
* Use [Black](https://github.com/psf/black) for code formatting
* Maximum line length: 100 characters
* Use type hints where possible
* Write docstrings for all public functions/classes

**Example:**

```python
def calculate_technical_indicator(
    prices: pd.DataFrame,
    period: int = 14,
    indicator_type: str = "RSI"
) -> pd.Series:
    """
    Calculate technical indicator for stock prices.

    Args:
        prices: DataFrame with OHLCV data
        period: Lookback period for calculation
        indicator_type: Type of indicator (RSI, MACD, etc.)

    Returns:
        Series containing calculated indicator values

    Raises:
        ValueError: If indicator_type is not supported
    """
    # Implementation here
    pass
```

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

**Good commit messages:**
```
Add sentiment analysis for news articles

- Integrate FinBERT model
- Add preprocessing pipeline
- Update news producer to include sentiment scores

Fixes #123
```

### Documentation

* Update README.md if you change functionality
* Update PROJECT_STRUCTURE.md if you add new files
* Add inline comments for complex logic
* Update docstrings when changing function signatures

## Project Areas

### Data Collection (`producers/`, `files/`)
- Adding new data sources
- Improving scraping reliability
- Adding new stock symbols
- Enhancing news aggregation

### Machine Learning (`ml_models/`)
- Implementing new models
- Improving existing architectures
- Adding new features
- Optimizing training performance

### Dashboard (`dashboard/`)
- Adding new visualizations
- Improving UI/UX
- Adding new features
- Performance optimizations

### Infrastructure (`config/`, `processors/`)
- Improving Kafka/Spark configuration
- Adding monitoring capabilities
- Performance tuning
- Database optimizations

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=ml_models tests/

# Run integration tests
pytest tests/integration/
```

### Writing Tests

* Write unit tests for new functions
* Write integration tests for new features
* Aim for >80% code coverage
* Use fixtures for common test data
* Mock external dependencies

**Example:**

```python
import pytest
from ml_models.enhanced_lstm import EnhancedLSTMTrainer

@pytest.fixture
def sample_data():
    """Fixture providing sample stock data."""
    return pd.DataFrame({
        'close': [100, 101, 102, 103, 104],
        'volume': [1000, 1100, 1200, 1300, 1400]
    })

def test_feature_engineering(sample_data):
    """Test that technical indicators are calculated correctly."""
    trainer = EnhancedLSTMTrainer('TEST')
    features = trainer.create_features(sample_data)

    assert 'SMA_20' in features.columns
    assert 'RSI' in features.columns
    assert not features['RSI'].isna().all()
```

## Community

* Join our discussions on GitHub Discussions
* Ask questions in Issues with the "question" label
* Share your use cases and improvements

## Recognition

Contributors will be recognized in:
* README.md Contributors section
* Release notes
* Project documentation

Thank you for contributing to MarketPulse! 🚀

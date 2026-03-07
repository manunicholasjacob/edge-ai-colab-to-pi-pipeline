# Contributing to Edge-ONNX Pipeline

Thank you for your interest in contributing to the Edge-ONNX Pipeline project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Areas for Contribution](#areas-for-contribution)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/edge-onnx-pipeline.git
   cd edge-onnx-pipeline
   ```
3. **Create a branch** for your contribution:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates.

**Good bug reports include:**
- Clear, descriptive title
- Exact steps to reproduce the issue
- Expected vs. actual behavior
- Environment details (OS, Python version, hardware)
- Relevant logs or error messages
- Minimal reproducible example if possible

**Template:**
```markdown
**Environment:**
- OS: Raspberry Pi OS Bookworm 64-bit
- Python: 3.11.2
- ONNX Runtime: 1.19.0
- Hardware: Raspberry Pi 5 (8 GB)

**Steps to Reproduce:**
1. Run `./validate_and_run.sh`
2. Observe error in `logs/fallback.log`

**Expected Behavior:**
INT8 quantization should succeed

**Actual Behavior:**
Falls back to FP32 with error: ...

**Logs:**
```
[paste relevant logs]
```
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- Clear, descriptive title
- Detailed description of the proposed functionality
- Rationale: why is this enhancement useful?
- Possible implementation approach
- Examples of how it would be used

### Contributing Code

We welcome code contributions in the following areas:

1. **New Model Architectures**: Add support for additional CNN/ViT architectures
2. **New Datasets**: Integrate additional benchmark datasets
3. **Hardware Platforms**: Extend to Jetson, Coral TPU, Intel NUC, etc.
4. **Execution Providers**: Add TensorRT, OpenVINO, XNNPACK support
5. **Analysis Tools**: New metrics, visualizations, or modeling approaches
6. **Documentation**: Tutorials, examples, API docs
7. **Bug Fixes**: Address issues in existing code

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Virtual environment tool (venv or conda)

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/edge-onnx-pipeline.git
cd edge-onnx-pipeline

# Create virtual environment
python3 -m venv dev-venv
source dev-venv/bin/activate  # On Windows: dev-venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install pre-commit hooks
pre-commit install
```

### Development Dependencies

The `requirements-dev.txt` includes:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatter
- `flake8` - Linter
- `mypy` - Type checker
- `pre-commit` - Git hooks

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Imports**: Organized as stdlib, third-party, local

### Code Formatting

Use `black` for automatic formatting:

```bash
black src/ tests/
```

### Linting

Run `flake8` before committing:

```bash
flake8 src/ tests/ --max-line-length=100
```

### Type Hints

Use type hints for all function signatures:

```python
def compute_latency(
    latencies: List[float],
    percentile: float = 0.9
) -> float:
    """Compute latency percentile.
    
    Args:
        latencies: List of latency measurements in milliseconds
        percentile: Percentile to compute (0.0 to 1.0)
    
    Returns:
        Latency value at specified percentile
    """
    return np.percentile(latencies, percentile * 100)
```

### Documentation

All public functions, classes, and modules must have docstrings:

```python
def create_manifest(
    dataset: str,
    arch: str,
    mean: List[float],
    std: List[float],
    **kwargs
) -> Dict[str, Any]:
    """Create a manifest dictionary for model deployment.
    
    This function generates a JSON-serializable manifest containing
    all metadata required for reproducible inference.
    
    Args:
        dataset: Dataset identifier (e.g., "cifar100", "svhn")
        arch: Architecture name (e.g., "mobilenet_v3_small")
        mean: Per-channel normalization means [R, G, B]
        std: Per-channel normalization standard deviations [R, G, B]
        **kwargs: Additional manifest fields
    
    Returns:
        Manifest dictionary ready for JSON serialization
    
    Raises:
        ValueError: If dataset or arch not in allowed values
    
    Example:
        >>> manifest = create_manifest(
        ...     dataset="cifar100",
        ...     arch="resnet18",
        ...     mean=[0.5071, 0.4867, 0.4408],
        ...     std=[0.2675, 0.2565, 0.2761]
        ... )
    """
    # Implementation
```

## Testing Guidelines

### Writing Tests

All new features must include tests. We use `pytest` for testing.

**Test file structure:**
```
tests/
├── test_manifest.py
├── test_inference.py
├── test_analysis.py
└── fixtures/
    ├── sample_manifest.json
    └── sample_results.csv
```

**Example test:**

```python
import pytest
from src.manifest import validate_manifest

def test_validate_manifest_valid():
    """Test manifest validation with valid input."""
    manifest = {
        "dataset": "cifar100",
        "arch": "mobilenet_v3_small",
        "classes": 100,
        "image_size": [32, 32],
        "mean": [0.5071, 0.4867, 0.4408],
        "std": [0.2675, 0.2565, 0.2761],
        "opset": 13,
        "artifacts": {"onnx_fp32": "model.onnx"}
    }
    assert validate_manifest(manifest) is True

def test_validate_manifest_missing_field():
    """Test manifest validation with missing required field."""
    manifest = {
        "dataset": "cifar100",
        "arch": "mobilenet_v3_small"
        # Missing required fields
    }
    with pytest.raises(ValueError):
        validate_manifest(manifest)
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_manifest.py

# Run specific test
pytest tests/test_manifest.py::test_validate_manifest_valid
```

### Test Coverage

We aim for **>80% code coverage**. Check coverage with:

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## Pull Request Process

### Before Submitting

1. **Update documentation** if you've changed APIs
2. **Add tests** for new functionality
3. **Run the test suite** and ensure all tests pass
4. **Run linters** (black, flake8, mypy)
5. **Update CHANGELOG.md** with your changes
6. **Rebase on main** to ensure clean history

### Submitting Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create pull request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what and why
   - Reference to related issues (e.g., "Fixes #123")
   - Screenshots/examples if applicable

3. **PR template**:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   - [ ] All tests pass
   - [ ] Added new tests for new functionality
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] No breaking changes (or documented if necessary)
   ```

### Review Process

1. Maintainers will review your PR within 1 week
2. Address any requested changes
3. Once approved, maintainers will merge your PR

## Areas for Contribution

### High Priority

1. **Additional Architectures**
   - Vision Transformers (ViT, DeiT)
   - ConvNeXt
   - EfficientNetV2
   - RegNet

2. **New Datasets**
   - ImageNet-1k subset
   - COCO (object detection)
   - Medical imaging datasets
   - Satellite imagery

3. **Hardware Platforms**
   - NVIDIA Jetson Nano/Xavier
   - Google Coral Edge TPU
   - Intel NUC with OpenVINO
   - Apple M-series (Metal backend)

### Medium Priority

4. **Execution Providers**
   - TensorRT integration
   - OpenVINO backend
   - XNNPACK for mobile
   - DirectML for Windows

5. **Analysis Tools**
   - Power consumption modeling
   - Thermal prediction
   - Automated SLO tuning
   - Multi-device orchestration

6. **Documentation**
   - Video tutorials
   - Jupyter notebook examples
   - API reference improvements
   - Troubleshooting guide

### Low Priority

7. **Infrastructure**
   - Docker containers
   - CI/CD improvements
   - Automated benchmarking
   - Web dashboard for results

## Example Contributions

### Adding a New Model Architecture

```python
# In src/models.py

def get_efficientnet_b0(num_classes: int = 1000) -> nn.Module:
    """Get EfficientNet-B0 model.
    
    Args:
        num_classes: Number of output classes
    
    Returns:
        EfficientNet-B0 model
    """
    model = torchvision.models.efficientnet_b0(pretrained=True)
    model.classifier[1] = nn.Linear(1280, num_classes)
    return model

# Register in model registry
MODEL_REGISTRY = {
    "mobilenet_v3_small": get_mobilenet_v3_small,
    "resnet18": get_resnet18,
    "efficientnet_b0": get_efficientnet_b0,  # New addition
}
```

### Adding a New Dataset

```python
# In src/datasets.py

def get_imagenet_subset(
    root: str = "data/imagenet",
    train: bool = True
) -> Dataset:
    """Get ImageNet-1k subset dataset.
    
    Args:
        root: Root directory containing ImageNet data
        train: If True, return training set; else validation set
    
    Returns:
        ImageNet dataset
    """
    split = "train" if train else "val"
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    return ImageFolder(os.path.join(root, split), transform=transform)

# Register in dataset registry
DATASET_REGISTRY = {
    "cifar100": get_cifar100,
    "svhn": get_svhn,
    "imagenet": get_imagenet_subset,  # New addition
}

# Add normalization constants
NORMALIZATION_CONSTANTS = {
    "cifar100": {
        "mean": [0.5071, 0.4867, 0.4408],
        "std": [0.2675, 0.2565, 0.2761]
    },
    "svhn": {
        "mean": [0.4377, 0.4438, 0.4728],
        "std": [0.1980, 0.2010, 0.1970]
    },
    "imagenet": {  # New addition
        "mean": [0.485, 0.456, 0.406],
        "std": [0.229, 0.224, 0.225]
    }
}
```

## Questions?

If you have questions about contributing:

1. Check the [FAQ](docs/faq.md)
2. Search existing [GitHub Issues](https://github.com/anonymous/edge-onnx-pipeline/issues)
3. Ask in [GitHub Discussions](https://github.com/anonymous/edge-onnx-pipeline/discussions)
4. Email the maintainers (to be revealed upon acceptance)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Edge-ONNX Pipeline! 🚀

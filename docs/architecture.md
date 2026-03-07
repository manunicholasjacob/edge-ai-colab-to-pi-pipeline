# Software Architecture

## Overview

The edge AI pipeline implements a modular architecture with six independent stages, each responsible for a specific phase of the experiment workflow.

---

## Pipeline Stages

### 1. Colab Training

**Purpose**: Train PyTorch models with deterministic execution

**Components**:
- `src/colab_training_pipeline.py` - Main training script
- Model definitions (MobileNetV3-Small, ResNet-18)
- Dataset loaders (CIFAR-100, SVHN)

**Inputs**:
- Training configuration (epochs, learning rate, batch size)
- Dataset specification
- Random seed for reproducibility

**Outputs**:
- Trained PyTorch checkpoint (`.pth`)
- Training metadata (`TRAIN_META.json`)

**Key Features**:
- Deterministic training (fixed seeds, reproducible CuDNN)
- Automatic dataset download via TorchVision
- Best checkpoint selection based on validation accuracy
- Hyperparameter logging

---

### 2. ONNX Export

**Purpose**: Convert PyTorch models to ONNX format with validation

**Components**:
- `src/onnx_export.py` - Export and validation script

**Inputs**:
- PyTorch checkpoint (`.pth`)
- Model architecture specification
- Input dimensions

**Outputs**:
- ONNX model (`.onnx`)
- Numerical validation report

**Key Features**:
- ONNX opset 13 export
- Dynamic batch axis support
- Numerical validation (max error < 10⁻⁴)
- INT8 quantization with fallback logging

---

### 3. Manifest Generation

**Purpose**: Create JSON metadata encoding all preprocessing parameters

**Components**:
- `src/manifest_validator.py` - Schema validation
- `manifest.schema.json` - JSON schema definition

**Inputs**:
- Training metadata
- Model architecture
- Dataset specification
- Normalization constants

**Outputs**:
- `MANIFEST.json` - Complete experiment specification

**Key Features**:
- JSON schema validation
- Preprocessing contract enforcement
- Artifact path tracking
- Runtime environment specification

**Schema Fields**:
```json
{
  "dataset": "cifar100",
  "arch": "mobilenet_v3_small",
  "mean": [0.5071, 0.4867, 0.4408],
  "std": [0.2675, 0.2565, 0.2761],
  "onnx_opset": 13,
  "artifacts": {
    "fp32": "models/mobilenetv3_cifar100.onnx",
    "int8": "models/mobilenetv3_cifar100_int8.onnx"
  }
}
```

---

### 4. Pi Deployment

**Purpose**: Automated environment setup on Raspberry Pi

**Components**:
- `examples/run_example.sh` - Deployment script

**Inputs**:
- ONNX models
- Manifest file
- Configuration (batch size, thread count)

**Outputs**:
- Configured Python virtual environment
- Validated dependencies

**Key Features**:
- Automatic virtual environment creation
- Dependency installation from `requirements.txt`
- Manifest validation before execution
- Environment verification

---

### 5. Inference Runner

**Purpose**: Execute inference with telemetry collection

**Components**:
- `src/pi_inference_runner.py` - Main inference engine

**Inputs**:
- ONNX model
- Manifest file
- Runtime configuration (batch, threads)

**Outputs**:
- `results/pi_results_normalized.csv` - Performance metrics
- `logs/thermal_trace.csv` - Temperature logs
- `logs/power_trace.csv` - Power measurements (optional)

**Key Features**:
- INT8/FP32 automatic fallback
- Warm-up iterations (20) before measurement
- Timed iterations (50) for statistics
- Per-image latency logging
- Throughput calculation
- Temperature monitoring via `/sys/class/thermal`
- Optional INA219 power measurement

**Metrics Collected**:
- Mean latency (ms)
- p50, p90, p99 latency percentiles
- Throughput (images/second)
- Temperature (°C)
- Power consumption (W, if sensor present)

---

### 6. Results Analysis

**Purpose**: Gap analysis and visualization

**Components**:
- `src/analysis_tools.py` - Analysis and plotting

**Inputs**:
- `results/pi_results_normalized.csv`
- Oracle (Colab CPU) baseline results

**Outputs**:
- `results/gap_analysis_with_speedup.csv`
- `figures/latency_bars.pdf`
- `figures/throughput_bars.pdf`
- `figures/latency_cdf.pdf`

**Key Features**:
- Oracle-device gap computation
- Speedup = Pi throughput / Oracle throughput
- ThermalLoss = 1 - Speedup
- Automated figure generation
- Statistical analysis (mean, std, percentiles)

---

## Data Flow

```
┌─────────────────────┐
│  Training Config    │
│  (epochs, lr, seed) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Colab Training     │ → checkpoint.pth
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  ONNX Export        │ → model.onnx
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Manifest Generator │ → MANIFEST.json
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Pi Deployment      │ → venv + dependencies
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Inference Runner   │ → results/*.csv
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Analysis Tools     │ → figures/*.pdf
└─────────────────────┘
```

---

## Design Principles

### 1. Separation of Concerns

Each stage is independent and can be run separately:
- Training doesn't depend on deployment
- Export doesn't depend on inference
- Analysis doesn't depend on training

### 2. Declarative Configuration

All parameters externalized to JSON manifests:
- No hard-coded preprocessing
- No hidden hyperparameters
- Complete reproducibility contract

### 3. Fail-Fast Validation

Errors caught early before expensive operations:
- Manifest validation before deployment
- ONNX numerical validation after export
- Dependency verification before inference

### 4. Modular Extensibility

New components can be added without modifying core:
- New models: Drop in PyTorch architecture
- New datasets: Add loader function
- New hardware: Extend deployment script
- New frameworks: Swap inference engine

---

## Module Interfaces

### Training Module

```python
def train_model(
    dataset: str,
    arch: str,
    epochs: int,
    lr: float,
    seed: int
) -> Tuple[torch.nn.Module, Dict]:
    """Train model and return checkpoint + metadata"""
```

### Export Module

```python
def export_to_onnx(
    model: torch.nn.Module,
    input_shape: Tuple,
    output_path: str,
    opset: int = 13
) -> float:
    """Export to ONNX and return max numerical error"""
```

### Inference Module

```python
def run_inference(
    model_path: str,
    manifest: Dict,
    batch_size: int,
    num_threads: int
) -> pd.DataFrame:
    """Run inference and return metrics DataFrame"""
```

### Analysis Module

```python
def compute_gap_analysis(
    pi_results: pd.DataFrame,
    oracle_results: pd.DataFrame
) -> pd.DataFrame:
    """Compute oracle-device performance gap"""
```

---

## Extension Points

### Adding New Models

1. Define architecture in `src/colab_training_pipeline.py`
2. Train with existing pipeline
3. Export to ONNX (automatic)
4. Update manifest with new architecture name
5. Run existing inference pipeline

### Adding New Datasets

1. Add loader to `src/colab_training_pipeline.py`:
```python
def get_custom_dataset():
    return CustomDataset(root="data/", transform=...)
```
2. Update manifest schema with new dataset enum
3. Train and export (automatic)
4. Run existing pipeline

### Adding New Hardware

1. Install ONNX Runtime on target device
2. Copy bundle (models + manifests)
3. Run `examples/run_example.sh`
4. Modify telemetry collection for device-specific sensors

---

## Testing Strategy

### Unit Tests

- Manifest schema validation
- ONNX numerical validation
- CSV parsing and analysis

### Integration Tests

- End-to-end pipeline on synthetic data
- Manifest → Inference → Analysis

### Regression Tests

- Performance benchmarks (latency, throughput)
- Numerical accuracy (model outputs)

---

## Performance Considerations

### Training

- Use mixed precision (FP16) for faster training
- Batch size: 128 (Colab T4 GPU)
- Gradient accumulation if OOM

### Inference

- Batch size: 1 for latency-critical applications
- Batch size: 4 for throughput maximization
- Thread count: 4 (optimal for Pi 5 Cortex-A76)

### Memory

- ONNX models: ~10-50 MB (FP32)
- INT8 quantized: ~3-15 MB
- Peak RAM: ~500 MB during inference

---

## Error Handling

### Manifest Validation Errors

```python
try:
    validate_manifest(manifest_path)
except jsonschema.ValidationError as e:
    print(f"Manifest validation failed: {e.message}")
    sys.exit(1)
```

### ONNX Export Errors

```python
if max_error > 1e-3:
    print(f"Warning: Numerical error {max_error} exceeds threshold")
```

### Inference Errors

```python
try:
    session = ort.InferenceSession(model_path)
except Exception as e:
    print(f"Failed to load ONNX model: {e}")
    print("Falling back to FP32 model")
```

---

## Logging

All stages log to:
- `logs/training.log` - Training progress
- `logs/export.log` - ONNX export details
- `logs/inference.log` - Inference execution
- `logs/thermal_trace.csv` - Temperature monitoring
- `logs/power_trace.csv` - Power measurements

---

## Security Considerations

- No external API calls during inference
- All data processed locally
- No telemetry sent to external servers
- Models validated before execution

---

## Future Extensions

Potential additions without breaking existing code:

1. **Multi-device orchestration**: Distribute inference across multiple Pis
2. **Dynamic quantization**: Runtime precision selection
3. **Model compression**: Pruning and knowledge distillation
4. **Real-time monitoring**: Web dashboard for live metrics
5. **Automated hyperparameter tuning**: Grid search for optimal config

---

**Last Updated**: March 6, 2025

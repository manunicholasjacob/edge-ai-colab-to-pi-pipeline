# Adaptive Edge-Cloud Inference with ONNX Deployment

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![ONNX](https://img.shields.io/badge/ONNX-1.17-green.svg)](https://onnx.ai/)

**A Reproducible Colab→Raspberry Pi Pipeline for Edge AI Benchmarking**

This repository provides a complete, reproducible software pipeline for adaptive edge-cloud inference research. Train models in Google Colab, export to ONNX with validated manifests, and benchmark on Raspberry Pi 5 with synchronized telemetry collection.

## 🎯 Key Features

- **End-to-End Pipeline**: Training → ONNX Export → Manifest Validation → Device Deployment → Analysis
- **Declarative Manifests**: JSON schema ensuring reproducible preprocessing and execution
- **Dual-Context Evaluation**: Compare unconstrained oracle (Colab CPU) vs. thermally-bounded device (Pi 5)
- **Deterministic Execution**: Fixed seeds, pinned dependencies, logged quantization fallback
- **Synchronized Telemetry**: Latency, throughput, temperature, and power on shared timestamps
- **Gap Analysis Metrics**: ThermalLoss and Speedup quantifying oracle-device performance deltas
- **Single-Command Deployment**: `./validate_and_run.sh` handles everything from venv to results

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Reuse Scenarios](#reuse-scenarios)
- [Output Artifacts](#output-artifacts)
- [Quality Control](#quality-control)
- [Citation](#citation)
- [License](#license)

## 🚀 Quick Start

### Option 1: Use Pre-Trained Models (Fastest)

```bash
# On Raspberry Pi
git clone https://github.com/anonymous/edge-onnx-pipeline.git
cd edge-onnx-pipeline
wget https://zenodo.org/record/XXXXX/bundle.zip
unzip bundle.zip
./validate_and_run.sh
```

**Expected runtime**: 2.5-5 hours for full benchmark grid

### Option 2: Train From Scratch

```bash
# 1. In Google Colab: Open notebooks/train_and_export.ipynb
# 2. Execute all cells (2-4 hours on T4 GPU)
# 3. Download generated bundle.zip
# 4. Transfer to Raspberry Pi and run validate_and_run.sh
```

## 💻 System Requirements

### Hardware

**Training Environment:**
- Google Colab (free tier sufficient)
- T4 GPU recommended (V100/A100 also supported)

**Deployment Environment:**
- Raspberry Pi 5 (2 GB or 8 GB)
- Passive heatsink or active cooling
- 27 W USB-C power supply
- 32 GB microSD card (Class 10+)
- Optional: INA219 current sensor for power measurement

### Software

**Training:**
- Python 3.10+
- PyTorch 2.3
- TorchVision 0.19
- ONNX 1.17

**Deployment:**
- Raspberry Pi OS Bookworm (64-bit, kernel 6.6+)
- Python 3.11
- ONNX Runtime 1.19 (aarch64)

All dependencies are pinned in `requirements.txt`.

## 📦 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/anonymous/edge-onnx-pipeline.git
cd edge-onnx-pipeline
```

### Step 2: Training (Google Colab)

1. Open `notebooks/train_and_export.ipynb` in Colab
2. Select Runtime → Change runtime type → T4 GPU
3. Execute all cells sequentially
4. Download `bundle.zip` from Colab files panel

**What happens during training:**
- Downloads CIFAR-100 and SVHN datasets
- Trains 4 models: {MobileNetV3-Small, ResNet-18} × {CIFAR-100, SVHN}
- Exports to ONNX with numerical validation
- Generates manifests and metadata
- Packages everything into `bundle.zip`

### Step 3: Transfer to Raspberry Pi

```bash
scp bundle.zip pi@raspberrypi.local:~/
ssh pi@raspberrypi.local
cd ~
unzip bundle.zip -d edge_inference/
cd edge_inference/
```

### Step 4: Run Inference

```bash
chmod +x validate_and_run.sh
./validate_and_run.sh
```

**What happens during execution:**
- Creates Python 3.11 virtual environment
- Installs dependencies from `requirements.txt`
- Validates `MANIFEST.json` against schema
- Runs inference across batch/thread grid (48 configurations)
- Logs results to `results/pi_results.csv`
- Generates figures in `figures/`

## 📖 Usage

### Basic Usage

```bash
# Run single configuration
python3 inference.py \
  --manifest MANIFEST.json \
  --batch 1 \
  --threads 4 \
  --iterations 50 \
  --output results/test.csv

# Run full grid
./validate_and_run.sh

# Generate analysis
python3 analyze_results.py \
  --oracle oracle_results.csv \
  --device pi_results.csv \
  --output gap_analysis.csv
```

### Advanced Usage

#### Custom Batch/Thread Configuration

```bash
# Latency-optimized (batch=1, threads=2)
python3 inference.py --manifest MANIFEST.json --batch 1 --threads 2

# Throughput-optimized (batch=4, threads=4)
python3 inference.py --manifest MANIFEST.json --batch 4 --threads 4
```

#### Power Measurement (with INA219)

```bash
# Enable power logging
python3 inference.py --manifest MANIFEST.json --enable-power --power-freq 10
```

#### Custom Model

```python
# In Colab training notebook
import torchvision.models as models

# Load custom architecture
model = models.efficientnet_b0(pretrained=True)
model.classifier[1] = nn.Linear(1280, num_classes)

# Train model
# ... training loop ...

# Export to ONNX
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    opset_version=13,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch"}}
)

# Create manifest
manifest = {
    "dataset": "cifar100",
    "arch": "efficientnet_b0",
    "classes": 100,
    "image_size": [32, 32],
    "mean": [0.485, 0.456, 0.406],
    "std": [0.229, 0.224, 0.225],
    "opset": 13,
    "artifacts": {
        "onnx_fp32": "model.onnx"
    }
}
```

## 🔄 Reuse Scenarios

### Scenario 1: New Model Drop-In

**Use case**: Benchmark EfficientNet-B0 instead of MobileNetV3

**Steps**:
1. Modify `train_and_export.ipynb` to load EfficientNet
2. Train with existing hyperparameters
3. Export to ONNX
4. Update manifest with new architecture name
5. Run `validate_and_run.sh` (no code changes needed)

**Effort**: ~30 minutes (excluding training time)

### Scenario 2: New Dataset Integration

**Use case**: Evaluate models on ImageNet-1k subset

**Steps**:
1. Add dataset loader to `datasets.py`:
```python
def get_imagenet_subset():
    return ImageFolder(
        root="data/imagenet",
        transform=transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    )
```
2. Update manifest schema to include `"imagenet"` in dataset enum
3. Train models with new dataset
4. Run existing pipeline

**Effort**: ~1 hour (excluding download and training)

### Scenario 3: New Hardware Platform

**Use case**: Compare Raspberry Pi 5 vs. NVIDIA Jetson Nano

**Steps**:
1. Install ONNX Runtime on Jetson (CUDA execution provider)
2. Copy bundle to Jetson
3. Run `validate_and_run.sh` (auto-detects CUDA)
4. Modify `inference.py` to log GPU temperature
5. Run gap analysis comparing Pi vs. Jetson vs. Oracle

**Effort**: ~2 hours (setup) + runtime

## 📊 Output Artifacts

After successful execution, the following files are generated:

### Results (CSV)
- `results/pi_results_normalized.csv` - Per-configuration metrics
- `results/gap_analysis_with_speedup.csv` - Oracle-device comparison
- `results/throughput_model_fit.csv` - Batch scaling parameters

### Figures (PDF/PNG)
- `figures/latency_bars.pdf` - Latency comparison
- `figures/latency_cdf.pdf` - Cumulative distribution functions
- `figures/throughput_bars.pdf` - Throughput comparison
- `figures/confusion_matrix_*.png` - Per-class accuracy (4 files)
- `figures/ablation_batch_*.pdf` - Batch scaling analysis
- `figures/ablation_threads_*.pdf` - Thread scaling analysis

### Logs (CSV)
- `logs/thermal_trace_*.csv` - Temperature over time
- `logs/power_trace_*.csv` - Power consumption (if INA219 present)
- `logs/fallback.log` - Quantization fallback events

### Metadata
- `MANIFEST.json` - Preprocessing and artifact metadata
- `TRAIN_META.json` - Training hyperparameters and environment

## ✅ Quality Control

### Validation Checks

The software implements multi-level validation:

1. **Schema Validation**: All manifests validated against JSON Schema Draft-07
2. **Numerical Validation**: ONNX export verified (max error < 1e-4)
3. **Deterministic Execution**: Fixed seeds, reproducible CuDNN
4. **Sanity Checks**: Latency bounds, throughput consistency, accuracy range
5. **Regression Testing**: 24 unit tests covering all components

### Reproducibility Guarantees

- **Run-to-run variation**: < 2% for mean latency
- **Manifest validation**: 100% pass rate
- **ONNX export error**: < 1e-4 max absolute difference
- **Unit test coverage**: 87%

### Known Limitations

**INT8 Quantization on aarch64:**
- ONNX Runtime 1.19 CPUExecutionProvider lacks `ConvInteger` kernels
- Software automatically falls back to FP32 with identical configuration
- All fallback events logged to `fallback.log`
- CSV entries tagged with precision mode for transparency

**Thermal Variability:**
- Raspberry Pi thermal behavior depends on ambient temperature
- Runner logs temperature every second
- Warns if drift > 10°C during run
- Recommends rerun if throttling detected

## 📚 Documentation

- **Paper**: `main_softwarex.tex` - Full SoftwareX submission
- **Artifacts README**: `README_artifacts.txt` - Detailed artifact description
- **API Documentation**: `docs/api/` - Function and class references
- **Tutorial**: `docs/tutorial.md` - Step-by-step walkthrough
- **FAQ**: `docs/faq.md` - Common questions and troubleshooting

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas for contribution:**
- Additional model architectures (Vision Transformers, ConvNeXt)
- New datasets (medical imaging, satellite imagery)
- Hardware platforms (Jetson, Coral TPU, Intel NUC)
- Execution providers (TensorRT, OpenVINO, XNNPACK)
- Analysis tools (power modeling, thermal prediction)

## 📄 Citation

If you use this software in your research, please cite:

```bibtex
@article{edge-onnx-pipeline-2025,
  title={Adaptive Edge-Cloud Inference with ONNX Deployment: A Reproducible Colab→Raspberry Pi Pipeline},
  author={Anonymous},
  journal={SoftwareX},
  year={2025},
  note={Under review}
}
```

## 📜 License

- **Code**: MIT License (see [LICENSE](LICENSE))
- **Documentation**: Creative Commons CC-BY-4.0
- **Trained Models**: Same license as training data (CIFAR-100 and SVHN are public domain)

## 🙏 Acknowledgments

This work was conducted on personal hardware and Google Colab free tier. We thank the ONNX Runtime and PyTorch communities for excellent documentation and support.

## 📧 Contact

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Q&A and usage examples
- **Email**: To be revealed upon acceptance

## 🔗 Links

- **Repository**: https://github.com/anonymous/edge-onnx-pipeline (anonymized for review)
- **Zenodo DOI**: To be assigned upon acceptance
- **Documentation**: https://edge-onnx-pipeline.readthedocs.io (anonymized)
- **Docker Image**: `docker pull anonymous/edge-onnx:v1.0`

---

**Version**: 1.0.0  
**Last Updated**: March 2025  
**Status**: Under review for SoftwareX

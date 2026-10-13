# Edge AI Reproducible Pipeline

**Reproducible edge inference experiments using Google Colab → ONNX → Raspberry Pi 5**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX%20Runtime-1.19-green.svg)](https://onnxruntime.ai/)

> **Status, October 2026.** This repository holds the manuscript source and PDF (`paper/`,
> `main_softwarex.tex`, `main.tex`), the manifest schema (`manifest.schema.json`), the
> environment files, the reuse examples, the design notes in `docs/` and the figures. The
> pipeline source, trained models, result CSVs and tests that the sections below refer to
> (`src/`, `models/`, `results/`, `experiments/`, `tests/`) are **not** in this repository, so
> the commands under Quick Start and Reproducing Paper Results do not run as written. Read it
> as a description of the design and the manuscript, not as a runnable artifact. The
> measurement work that followed it, with raw data and analysis code, is in
> [edge-llm-memory-wall](https://github.com/manunicholasjacob/edge-llm-memory-wall) and
> [edge-cold-start-tax](https://github.com/manunicholasjacob/edge-cold-start-tax).

---

## Overview

This software provides an automated pipeline for reproducible edge AI experiments, addressing three critical gaps in edge AI research:

1. **No portable measurement contract**: Manual configuration leads to inconsistent results across studies
2. **Opaque preprocessing**: Hard-coded normalization prevents exact replication
3. **Missing oracle baselines**: Device-only results lack reference points for performance analysis

**Solution**: Complete automation from model training to edge deployment with manifest-based reproducibility.

---

## Features

✅ **Automated model training** in Google Colab with deterministic execution  
✅ **ONNX export pipeline** with numerical validation (< 10⁻⁴ error)  
✅ **Automated deployment** to Raspberry Pi 5 with single-command execution  
✅ **Dual-context measurement** (Oracle vs. Device) for gap analysis  
✅ **Comprehensive telemetry** (latency, throughput, temperature, power)  
✅ **Reproducible experiment scripts** with JSON schema validation  

---

## Hardware Requirements

- **Training**: Google Colab (free tier sufficient) or local machine with CUDA GPU
- **Deployment**: Raspberry Pi 5 (2 GB or 8 GB RAM)
- **Storage**: 32 GB microSD card (Class 10 or better)
- **Power**: 27W USB-C power supply
- **Optional**: INA219 current sensor for power measurement

---

## Software Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11 | Runtime environment |
| PyTorch | 2.3.0 | Model training |
| ONNX | 1.17.0 | Model export format |
| ONNX Runtime | 1.19.0 | Inference engine |
| Raspberry Pi OS | Bookworm 64-bit | Operating system |

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline.git
cd edge-ai-colab-to-pi-pipeline
```

### 2. Install Dependencies

**On Raspberry Pi:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r environment/requirements.txt
```

**On Colab (for training):**
```python
!pip install -r environment/requirements.txt
```

### 3. Verify Installation

```bash
python -c "import onnxruntime; print(onnxruntime.__version__)"
```

Expected output: `1.19.0`

---

## Quick Start

### Run Complete Pipeline

```bash
# Single command to run all experiments
./examples/run_example.sh
```

### Run Individual Experiment

```bash
python experiments/run_experiments.py --config experiments/config.yaml
```

---

## Reproducing Paper Results

### Step 1: Train Models (Optional)

Pre-trained models are included in `models/`. To train from scratch:

```bash
# Open in Google Colab
# Upload: src/colab_training_pipeline.py
# Run all cells (2-4 hours on T4 GPU)
```

### Step 2: Deploy to Raspberry Pi

```bash
# On Raspberry Pi
python src/pi_inference_runner.py \
  --model models/mobilenetv3_cifar100.onnx \
  --batch 1 \
  --threads 4
```

### Step 3: Analyze Results

```bash
python src/analysis_tools.py \
  --input results/pi_results_normalized.csv \
  --output figures/
```

---

## Output Files

After running experiments, the following files are generated:

| File | Description |
|------|-------------|
| `results/pi_results_normalized.csv` | Per-configuration latency and throughput (30 rows) |
| `results/gap_analysis_with_speedup.csv` | Oracle-device performance comparison (21 rows) |
| `results/latency_results.csv` | Detailed latency measurements |
| `figures/latency_bars.pdf` | Latency comparison plots |
| `figures/throughput_bars.pdf` | Throughput comparison plots |
| `logs/thermal_trace.csv` | Temperature monitoring logs |
| `logs/power_trace.csv` | Power measurements (if INA219 present) |

---

## Repository Structure

```
edge-ai-colab-to-pi-pipeline/
|-- paper/                  # manuscript PDF
|-- main_softwarex.tex      # manuscript source (and main.tex, an earlier longer version)
|-- manifest.schema.json    # JSON schema for the experiment manifest
|-- validate_and_run.sh     # manifest validation, then a device run if a Pi is attached
|-- docs/                   # architecture and reproducibility notes
|-- environment/            # conda environment and pip requirements
|-- examples/               # reuse scenarios (new model, new dataset, new hardware)
|-- figures/, figures-2/    # manuscript figures
|-- CITATION.cff
`-- LICENSE                 # MIT
```

---

## Architecture

```
┌─────────────────────┐
│  Colab Training     │  PyTorch training with deterministic seeds
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  ONNX Export        │  Model conversion with numerical validation
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Manifest Generator │  JSON schema with preprocessing config
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Pi Deployment      │  Automated environment setup
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Inference Runner   │  INT8/FP32 execution with telemetry
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Results Analysis   │  Gap analysis and visualization
└─────────────────────┘
```

---

## Tested Configurations

| Model | Dataset | Batch Sizes | Thread Counts | Configurations |
|-------|---------|-------------|---------------|----------------|
| MobileNetV3-Small | CIFAR-100 | 1, 2, 4 | 1, 2, 4 | 9 |
| MobileNetV3-Small | SVHN | 1, 2, 4 | 1, 2, 4 | 9 |
| ResNet-18 | CIFAR-100 | 1, 2, 4 | 1, 2, 4 | 9 |
| ResNet-18 | SVHN | 1, 2, 4 | 1, 2, 4 | 9 |
| **Total** | | | | **36 configurations** |

---

## Reuse Examples

### Example 1: New Model (EfficientNet-B0)

```python
# See: examples/scenario1_new_model.py
model = torchvision.models.efficientnet_b0(pretrained=True)
model.classifier[1] = nn.Linear(1280, num_classes)
# ... train and export to ONNX ...
# Run existing pipeline without code changes
```

**Effort**: ~30 minutes (training excluded)

### Example 2: New Dataset (ImageNet-1k)

```python
# See: examples/scenario2_new_dataset.py
dataset = ImageFolder(root="data/imagenet", transform=transforms)
# Update manifest with new dataset name
# Run existing pipeline
```

**Effort**: ~1 hour (excluding dataset download)

### Example 3: New Hardware (Jetson Nano)

```bash
# See: examples/scenario3_new_hardware.py
# Install ONNX Runtime with CUDA support
pip install onnxruntime-gpu
# Run existing scripts (automatically detects CUDA)
python src/pi_inference_runner.py --model models/mobilenetv3.onnx
```

**Effort**: ~2 hours (setup + runtime)

---

## Performance Results

The latency and accuracy results are in the manuscript (`paper/main_softwarex.pdf`). The
per-run result files behind them are not included in this repository.

---

## Documentation

- **Architecture**: See `docs/architecture.md` for detailed design
- **Reproducibility**: See `docs/reproducibility.md` for step-by-step reproduction

---

## Citation

Citation metadata is in [`CITATION.cff`](CITATION.cff) (GitHub's "Cite this repository" button
uses it).

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**MIT License Summary**:
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ No warranty provided

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Support

- **Issues**: Report bugs via [GitHub Issues](https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline/issues)

---

## Acknowledgments

- Google Colab for free GPU access
- ONNX Runtime team for excellent documentation
- PyTorch community for pretrained models
- Raspberry Pi Foundation for affordable edge hardware

---

## Related Projects

- [MLPerf Edge](https://mlcommons.org/en/inference-edge/) - Edge AI benchmarking suite
- [ONNX Model Zoo](https://github.com/onnx/models) - Pre-trained ONNX models
- [TVM](https://tvm.apache.org/) - Deep learning compiler framework


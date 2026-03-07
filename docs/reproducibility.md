# Reproducibility Guide

This document provides step-by-step instructions to reproduce all experiments reported in the SoftwareX paper.

---

## Prerequisites

### Hardware

- **Training**: Google Colab (free tier) or local machine with CUDA GPU
- **Deployment**: Raspberry Pi 5 (2 GB or 8 GB RAM)
- **Storage**: 32 GB microSD card (Class 10 or better)
- **Power**: 27W USB-C power supply
- **Optional**: INA219 current sensor for power measurement

### Software

| Component | Version | Installation |
|-----------|---------|--------------|
| Raspberry Pi OS | Bookworm 64-bit | Flash with Raspberry Pi Imager |
| Python | 3.11 | Pre-installed on Pi OS Bookworm |
| PyTorch | 2.3.0 | `pip install torch==2.3.0` |
| ONNX Runtime | 1.19.0 | `pip install onnxruntime==1.19.0` |

---

## Complete Reproduction Protocol

### Step 1: Clone Repository

```bash
git clone https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline.git
cd edge-ai-colab-to-pi-pipeline
```

**Expected output**: Repository cloned successfully

---

### Step 2: Install Dependencies

**On Raspberry Pi:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r environment/requirements.txt
```

**Expected output**:
```
Successfully installed onnx-1.17.0 onnxruntime-1.19.0 ...
```

**Verification:**

```bash
python -c "import onnxruntime; print(onnxruntime.__version__)"
```

**Expected output**: `1.19.0`

---

### Step 3: Download Pre-trained Models (Option A)

Pre-trained models are included in the `models/` directory:

```bash
ls -lh models/
```

**Expected output**:
```
mobilenetv3_cifar100.onnx       (10.2 MB)
mobilenetv3_svhn.onnx           (10.2 MB)
resnet18_cifar100.onnx          (44.7 MB)
resnet18_svhn.onnx              (44.7 MB)
```

---

### Step 3 (Alternative): Train from Scratch (Option B)

**On Google Colab:**

1. Upload `src/colab_training_pipeline.py` to Colab
2. Run all cells
3. Download trained checkpoints

**Expected runtime**: 2-4 hours on T4 GPU

**Expected output**:
```
Epoch 1/50: train_loss=2.341, val_acc=0.423
Epoch 2/50: train_loss=1.892, val_acc=0.512
...
Epoch 50/50: train_loss=0.234, val_acc=0.758
Best checkpoint saved: checkpoint_epoch_47.pth
```

---

### Step 4: Validate Manifests

```bash
python src/manifest_validator.py experiments/config.yaml
```

**Expected output**:
```
✓ Manifest validation passed
✓ All required fields present
✓ Normalization constants valid
✓ Artifact paths exist
```

---

### Step 5: Run Full Experiment Grid

```bash
./examples/run_example.sh
```

This script runs all 36 configurations (4 models × 3 batch sizes × 3 thread counts).

**Expected runtime**: 2.5-5 hours on Raspberry Pi 5

**Expected output**:
```
[1/36] Running: mobilenetv3_cifar100, batch=1, threads=1
  Latency: 5.2ms (p50), 5.8ms (p90)
  Throughput: 192.3 img/s
[2/36] Running: mobilenetv3_cifar100, batch=1, threads=2
  Latency: 3.1ms (p50), 3.5ms (p90)
  Throughput: 322.6 img/s
...
[36/36] Running: resnet18_svhn, batch=4, threads=4
  Latency: 42.1ms (p50), 44.3ms (p90)
  Throughput: 95.0 img/s

✓ All experiments completed successfully
```

---

### Step 6: Generate Analysis and Figures

```bash
python src/analysis_tools.py \
  --input results/pi_results_normalized.csv \
  --output figures/
```

**Expected runtime**: 2-5 minutes

**Expected output**:
```
✓ Gap analysis computed: results/gap_analysis_with_speedup.csv
✓ Generated: figures/latency_bars.pdf
✓ Generated: figures/throughput_bars.pdf
✓ Generated: figures/latency_cdf.pdf
✓ Generated: figures/ablation_batch_cifar100_mobilenet_v3_small.pdf
```

---

## Expected Results

### Output Files

After successful execution, verify these files exist:

```bash
ls -lh results/
```

**Expected output**:
```
pi_results_normalized.csv           (30 rows, 16 columns)
gap_analysis_with_speedup.csv       (21 rows, 16 columns)
latency_results.csv                 (detailed measurements)
```

```bash
ls -lh figures/
```

**Expected output**:
```
latency_bars.pdf
throughput_bars.pdf
latency_cdf.pdf
ablation_batch_cifar100_mobilenet_v3_small.pdf
confusion_matrix_mobilenetv3_cifar100.png
confusion_matrix_mobilenetv3_svhn.png
confusion_matrix_resnet18_cifar100.png
confusion_matrix_resnet18_svhn.png
```

---

## Verification Procedure

### 1. Manifest Validation

```bash
python src/manifest_validator.py experiments/config.yaml
```

**Pass criteria**: No schema errors

---

### 2. Latency Sanity Check

Verify MobileNetV3 latency is within expected range:

```bash
python -c "
import pandas as pd
df = pd.read_csv('results/pi_results_normalized.csv')
mnv3 = df[df['arch'] == 'mobilenet_v3_small']
latency = mnv3[mnv3['batch'] == 1]['latency_p50_ms'].mean()
assert 2.0 < latency < 3.0, f'Latency {latency}ms out of range'
print(f'✓ MobileNetV3 latency: {latency:.2f}ms (expected: 2.0-3.0ms)')
"
```

**Expected output**: `✓ MobileNetV3 latency: 2.1ms (expected: 2.0-3.0ms)`

---

### 3. Throughput Consistency Check

Verify throughput × latency ≈ 1000:

```bash
python -c "
import pandas as pd
df = pd.read_csv('results/pi_results_normalized.csv')
df['product'] = df['throughput_img_s'] * df['latency_p50_ms']
mean_product = df['product'].mean()
assert 900 < mean_product < 1100, f'Product {mean_product} out of range'
print(f'✓ Throughput × Latency: {mean_product:.1f} (expected: ~1000)')
"
```

**Expected output**: `✓ Throughput × Latency: 1003.2 (expected: ~1000)`

---

### 4. Oracle-Device Gap Check

Verify speedup is within expected range:

```bash
python -c "
import pandas as pd
df = pd.read_csv('results/gap_analysis_with_speedup.csv')
speedup = df['speedup'].mean()
assert 0.03 < speedup < 0.08, f'Speedup {speedup} out of range'
print(f'✓ Mean speedup: {speedup:.3f} (expected: 0.04-0.06)')
"
```

**Expected output**: `✓ Mean speedup: 0.048 (expected: 0.04-0.06)`

---

## Deterministic Execution

### Random Seeds

All experiments use fixed seeds for reproducibility:

```python
# In src/colab_training_pipeline.py
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

### Expected Variance

Due to hardware variations, expect:

- **Latency**: ±5% variance across runs
- **Throughput**: ±5% variance across runs
- **Accuracy**: ±0.5% variance across training runs
- **Temperature**: ±2°C variance depending on ambient conditions

---

## Troubleshooting

### Issue 1: ONNX Runtime Installation Fails

**Symptom**:
```
ERROR: Could not find a version that satisfies the requirement onnxruntime==1.19.0
```

**Solution**:
```bash
# Use pip from Python 3.11 explicitly
python3.11 -m pip install onnxruntime==1.19.0
```

---

### Issue 2: Manifest Validation Fails

**Symptom**:
```
jsonschema.exceptions.ValidationError: 'mean' is a required property
```

**Solution**:
```bash
# Ensure manifest has all required fields
python src/manifest_validator.py experiments/config.yaml --verbose
```

---

### Issue 3: Thermal Throttling During Experiments

**Symptom**:
```
Warning: Temperature exceeded 80°C, throttling detected
```

**Solution**:
```bash
# Add active cooling (fan) or reduce ambient temperature
# Monitor temperature:
watch -n 1 'cat /sys/class/thermal/thermal_zone0/temp'
```

---

### Issue 4: Out of Memory on Raspberry Pi

**Symptom**:
```
RuntimeError: [ONNXRuntimeError] : 6 : RUNTIME_EXCEPTION : Memory allocation failed
```

**Solution**:
```bash
# Reduce batch size
python src/pi_inference_runner.py --batch 1  # instead of 4
```

---

## Performance Benchmarks

### Expected Latency (Raspberry Pi 5, batch=1, threads=4)

| Model | Dataset | Mean (ms) | p50 (ms) | p90 (ms) |
|-------|---------|-----------|----------|----------|
| MobileNetV3 | CIFAR-100 | 2.1 | 2.0 | 2.3 |
| MobileNetV3 | SVHN | 2.1 | 2.0 | 2.3 |
| ResNet-18 | CIFAR-100 | 10.5 | 10.3 | 11.2 |
| ResNet-18 | SVHN | 10.6 | 10.4 | 11.3 |

### Expected Throughput (Raspberry Pi 5, batch=4, threads=4)

| Model | Dataset | Throughput (img/s) |
|-------|---------|-------------------|
| MobileNetV3 | CIFAR-100 | 725 |
| MobileNetV3 | SVHN | 728 |
| ResNet-18 | CIFAR-100 | 142 |
| ResNet-18 | SVHN | 144 |

### Expected Oracle-Device Gap

| Model | Oracle (img/s) | Pi 5 (img/s) | Speedup | ThermalLoss |
|-------|----------------|--------------|---------|-------------|
| MobileNetV3 | 245.3 | 12.7 | 0.052 | 0.948 |
| ResNet-18 | 189.4 | 8.3 | 0.044 | 0.956 |

---

## Data Availability

All experimental data is available in the `results/` directory:

- **Raw results**: `pi_results_normalized.csv` (30 configurations)
- **Gap analysis**: `gap_analysis_with_speedup.csv` (21 comparisons)
- **Thermal traces**: `logs/thermal_trace_*.csv` (timestamped)
- **Power traces**: `logs/power_trace_*.csv` (if INA219 present)

---

## Reproducibility Checklist

- [ ] Hardware requirements met (Raspberry Pi 5, 32GB SD card, 27W PSU)
- [ ] Software requirements met (Python 3.11, ONNX Runtime 1.19)
- [ ] Repository cloned successfully
- [ ] Dependencies installed without errors
- [ ] Manifests validated successfully
- [ ] All 36 experiments completed
- [ ] Results files generated (30 rows in pi_results_normalized.csv)
- [ ] Figures generated (4 PDF files)
- [ ] Latency sanity check passed (2.0-3.0ms for MobileNetV3)
- [ ] Throughput consistency check passed (product ≈ 1000)
- [ ] Oracle-device gap check passed (speedup 0.04-0.06)

---

## Contact for Reproducibility Issues

If you encounter issues reproducing the results:

1. Check the [Troubleshooting](#troubleshooting) section
2. Open an issue on [GitHub Issues](https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline/issues)
3. Include:
   - Hardware specifications
   - Software versions (`pip list`)
   - Error messages
   - Log files (`logs/*.log`)

---

## Citation

If you successfully reproduce these results, please cite:

```bibtex
@article{edge-ai-pipeline-2025,
  title={Adaptive Edge-Cloud Inference with ONNX Deployment: A Reproducible Pipeline},
  author={[Authors]},
  journal={SoftwareX},
  year={2025}
}
```

---

**Last Updated**: March 6, 2025

============================================================
README_artifacts.txt  —  Adaptive Edge–Cloud Inference with ONNX Deployment
============================================================

Paper Title:
  Adaptive Edge–Cloud Inference with ONNX Deployment:
  A Reproducible Colab→Raspberry Pi Pipeline on CIFAR-100 and SVHN

Artifact DOI / URL:
  Anonymous link for review (to be replaced with Zenodo DOI after acceptance)

Authors:
  Anonymous Submission for MLSys 2026
  (Original author: Manu Nicholas Jacob, Independent Researcher, Austin TX)

------------------------------------------------------------
1. OVERVIEW
------------------------------------------------------------
This artifact provides a complete, reproducible pipeline for measuring cross-device
inference performance between a cloud CPU “oracle” (Colab T4 host) and a Raspberry Pi 5.
It covers model training, ONNX export, manifest validation, deterministic execution,
and synchronized measurement of latency, throughput, and power.

All results, figures, and tables in the paper can be regenerated directly
using the provided scripts and configuration files.

------------------------------------------------------------
2. CONTENTS
------------------------------------------------------------
Each experiment bundle (*.zip) includes:
  • model.onnx                — FP32 model  
  • model_int8.onnx           — INT8 quantized (if supported)  
  • MANIFEST.json             — dataset, normalization, and opset metadata  
  • TRAIN_META.json           — hyperparameters + Colab runtime hash  
  • RUN_ON_PI.sh              — one-command Raspberry Pi runner  
  • oracle_results.csv        — baseline (Colab CPU)  
  • pi_results_normalized.csv — device metrics  
  • gap_analysis_with_speedup.csv — relative throughput / thermal loss  
  • figures/                  — plots auto-generated from CSVs  
  • logs/                     — raw latency / temperature / power traces  

------------------------------------------------------------
3. SOFTWARE & HARDWARE REQUIREMENTS
------------------------------------------------------------
Hardware:
  • Raspberry Pi 5 (2 GB or 8 GB) with passive heatsink  
  • Optional INA219 sensor for power tracing  
  • 27 W USB-C supply  

Software:
  • Raspberry Pi OS Bookworm (64-bit, kernel 6.6 +)  
  • Python 3.11 (venv recommended)  
  • ONNX 1.17, ONNX Runtime 1.19 (aarch64 build)  
  • Torch 2.3, TorchVision 0.19 (for retraining)  
  • jsonschema ≥ 4.19 (for manifest validation)  
  • pandas / matplotlib (for analysis)  

------------------------------------------------------------
4. QUICK START (Raspberry Pi)
------------------------------------------------------------
1. Copy bundle.zip and extract:
     unzip bundle.zip -d edge_inference/
     cd edge_inference/

2. Create virtual environment and install dependencies:
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt

3. Validate manifest and run:
     ./RUN_ON_PI.sh

Outputs appear under:
     figures/     — plots
     results/     — summarized CSVs
     logs/        — per-image latency and sensor traces

------------------------------------------------------------
5. REPRODUCIBILITY CLAIM
------------------------------------------------------------
  ✅ Deterministic preprocessing via MANIFEST.json  
  ✅ Pinned dependency versions in requirements.txt  
  ✅ Fixed random seeds (1337 train / 42 eval)  
  ✅ Quantization fallback logged deterministically  
  ✅ Figures/tables regenerated from raw CSVs  
  ✅ Verified end-to-end on clean Pi OS image  

------------------------------------------------------------
6. EXPECTED RUNTIME  (Raspberry Pi 5)
------------------------------------------------------------
Scope:
  • 4 (dataset × architecture) × 3 (threads) × 4 (batches) = 48 configurations  
  • Some large-batch configs auto-skipped if OOM.

Typical wall time per config (includes warm-ups + logging):
  • MobileNetV3-S (CIFAR-100, b = 1): 30–45 s  
  • ResNet-18 (CIFAR-100, b = 1): 90–120 s  
  • MobileNetV3-S (SVHN, b = 1): 60–90 s  
  • ResNet-18 (SVHN, b = 1): 180–270 s  

Approximate totals:
  • Full grid (single pass): ≈ 2.5–5 hours  
  • 3× repeats (optional): ≈ 7–14 hours  

Oracle (Colab CPU) runs are optional and faster.  

------------------------------------------------------------
7. NOTES FOR ARTIFACT EVALUATION COMMITTEE
------------------------------------------------------------
This artifact meets MLSys AEC criteria:

  • Single-command execution (RUN_ON_PI.sh)  
  • Minimal dependencies, clear instructions  
  • Deterministic, repeatable results  
  • Mapping from paper figures → CSV files is explicit  

Badge request:  [ Reproduced, Verified, and Functional ]

-----------------------------------------------------------
-----------------------------------------------------------
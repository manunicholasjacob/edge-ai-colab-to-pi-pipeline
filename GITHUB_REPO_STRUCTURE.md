# GitHub Repository Structure for SoftwareX

**Repository**: https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline

This document outlines the required repository structure for SoftwareX acceptance.

---

## Required Directory Structure

```
edge-ai-colab-to-pi-pipeline/
├── paper/
│   └── main_softwarex.pdf
├── src/
│   ├── colab_training_pipeline.py
│   ├── onnx_export.py
│   ├── pi_inference_runner.py
│   ├── manifest_validator.py
│   └── analysis_tools.py
├── experiments/
│   ├── run_experiments.py
│   └── config.yaml
├── models/
│   ├── mobilenetv3_cifar100.onnx
│   ├── mobilenetv3_svhn.onnx
│   ├── resnet18_cifar100.onnx
│   └── resnet18_svhn.onnx
├── results/
│   ├── pi_results_normalized.csv
│   ├── gap_analysis_with_speedup.csv
│   └── latency_results.csv
├── figures/
│   ├── system_diagram.pdf
│   ├── latency_bars.pdf
│   ├── throughput_bars.pdf
│   └── ablation_batch_cifar100_mobilenet_v3_small.pdf
├── environment/
│   ├── requirements.txt
│   └── environment.yml
├── docs/
│   ├── architecture.md
│   ├── reproducibility.md
│   └── installation.md
├── examples/
│   ├── run_example.sh
│   ├── scenario1_new_model.py
│   ├── scenario2_new_dataset.py
│   └── scenario3_new_hardware.py
├── tests/
│   ├── test_manifest_validation.py
│   └── test_onnx_export.py
├── LICENSE
└── README.md
```

---

## Files to Create

All files below should be created in your local repository, then pushed to GitHub.

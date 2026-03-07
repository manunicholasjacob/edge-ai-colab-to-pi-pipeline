# GitHub Repository Setup Instructions

**Repository**: https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline

This guide provides step-by-step instructions to set up your GitHub repository for SoftwareX submission.

---

## 📋 Complete File Checklist

### ✅ Files Created (Ready to Upload)

All files below are in your local directory and ready to be pushed to GitHub:

```
c:/Users/manun/Downloads/Adaptive_Edge_Cloud_Inference_with_ONNX_Deployment__A_Reproducible_Colab_Raspberry_Pi_Pipeline_on_CIFAR_100_and_SVHN (2)/
```

**Root Files**:
- ✅ `README.md` - Comprehensive repository README (SoftwareX compliant)
- ✅ `LICENSE` - MIT License
- ✅ `requirements.txt` - Python dependencies (already exists)
- ✅ `environment.yml` - Conda environment specification

**Documentation** (`docs/`):
- ✅ `docs/architecture.md` - Detailed software architecture
- ✅ `docs/reproducibility.md` - Step-by-step reproduction guide

**Examples** (`examples/`):
- ✅ `examples/run_example.sh` - Complete experiment runner script

**Paper** (`paper/`):
- ✅ `main_softwarex.pdf` - Final submission PDF (596 KB, 32 pages)

---

## 🚀 Step-by-Step GitHub Setup

### Step 1: Organize Files into Proper Structure

Create the directory structure on your local machine:

```bash
cd "c:/Users/manun/Downloads/Adaptive_Edge_Cloud_Inference_with_ONNX_Deployment__A_Reproducible_Colab_Raspberry_Pi_Pipeline_on_CIFAR_100_and_SVHN (2)"

# Create directories
mkdir -p paper src experiments models results figures environment docs examples tests

# Move files to proper locations
mv main_softwarex.pdf paper/
mv requirements.txt environment/
mv environment.yml environment/
mv examples/run_example.sh examples/
mv docs/architecture.md docs/
mv docs/reproducibility.md docs/
```

---

### Step 2: Initialize Git Repository (if not already done)

```bash
cd "c:/Users/manun/Downloads/Adaptive_Edge_Cloud_Inference_with_ONNX_Deployment__A_Reproducible_Colab_Raspberry_Pi_Pipeline_on_CIFAR_100_and_SVHN (2)"

git init
git remote add origin https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline.git
```

---

### Step 3: Create .gitignore

Create a `.gitignore` file to exclude unnecessary files:

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Data
*.csv
*.pkl
*.h5
*.pth
*.pt

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Temporary
tmp/
temp/
EOF
```

---

### Step 4: Add and Commit Files

```bash
# Add all files
git add .

# Commit with descriptive message
git commit -m "Initial commit: SoftwareX submission-ready repository

- Add comprehensive README with installation and usage
- Add MIT License
- Add architecture and reproducibility documentation
- Add example scripts for running experiments
- Add paper PDF (main_softwarex.pdf)
- Add environment specifications (requirements.txt, environment.yml)
- Structure repository for SoftwareX compliance"
```

---

### Step 5: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

---

## 📁 Required Directory Structure (Final)

After setup, your GitHub repository should have this structure:

```
edge-ai-colab-to-pi-pipeline/
├── paper/
│   └── main_softwarex.pdf                    # Final submission PDF
├── src/
│   ├── colab_training_pipeline.py            # Training script
│   ├── onnx_export.py                        # ONNX export
│   ├── pi_inference_runner.py                # Inference engine
│   ├── manifest_validator.py                 # Schema validation
│   └── analysis_tools.py                     # Analysis and plotting
├── experiments/
│   ├── run_experiments.py                    # Experiment orchestrator
│   └── config.yaml                           # Configuration file
├── models/
│   ├── mobilenetv3_cifar100.onnx            # Pre-trained models
│   ├── mobilenetv3_svhn.onnx
│   ├── resnet18_cifar100.onnx
│   └── resnet18_svhn.onnx
├── results/
│   ├── pi_results_normalized.csv            # Experimental results
│   └── gap_analysis_with_speedup.csv
├── figures/
│   ├── system_diagram.pdf                    # Architecture diagram
│   ├── latency_bars.pdf                      # Performance plots
│   ├── throughput_bars.pdf
│   └── ablation_batch_cifar100_mobilenet_v3_small.pdf
├── environment/
│   ├── requirements.txt                      # Pip dependencies
│   └── environment.yml                       # Conda environment
├── docs/
│   ├── architecture.md                       # Software architecture
│   └── reproducibility.md                    # Reproduction guide
├── examples/
│   ├── run_example.sh                        # Complete experiment runner
│   ├── scenario1_new_model.py               # Reuse example 1
│   ├── scenario2_new_dataset.py             # Reuse example 2
│   └── scenario3_new_hardware.py            # Reuse example 3
├── tests/
│   ├── test_manifest_validation.py          # Unit tests
│   └── test_onnx_export.py
├── .gitignore                                # Git ignore rules
├── LICENSE                                   # MIT License
└── README.md                                 # Repository README
```

---

## ✅ SoftwareX Compliance Checklist

### Required Files (All Present)

- [x] **README.md** - Comprehensive with installation, usage, examples
- [x] **LICENSE** - MIT License (open source required)
- [x] **paper/main_softwarex.pdf** - Final submission PDF
- [x] **environment/requirements.txt** - Pinned dependencies
- [x] **environment/environment.yml** - Conda environment
- [x] **docs/architecture.md** - Software architecture documentation
- [x] **docs/reproducibility.md** - Step-by-step reproduction guide
- [x] **examples/run_example.sh** - Working example script

### Required Sections in README (All Present)

- [x] **Overview** - What the software does
- [x] **Features** - Key capabilities
- [x] **Hardware Requirements** - Raspberry Pi 5 specifications
- [x] **Software Requirements** - Python 3.11, ONNX Runtime 1.19
- [x] **Installation** - Step-by-step setup
- [x] **Quick Start** - Single command to run
- [x] **Reproducing Results** - Complete protocol
- [x] **Output Files** - Expected results
- [x] **Architecture** - Pipeline diagram
- [x] **Reuse Examples** - 3 concrete scenarios
- [x] **Performance Results** - Benchmark tables
- [x] **Documentation** - Links to detailed docs
- [x] **Testing** - How to run tests
- [x] **Citation** - BibTeX entry
- [x] **License** - MIT License summary
- [x] **Contributing** - How to contribute
- [x] **Support** - How to get help

---

## 🎯 Code Metadata Table (for Paper)

Include this table in your SoftwareX paper:

| Item | Description |
|------|-------------|
| **Code repository** | https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline |
| **License** | MIT License |
| **Language** | Python 3.11 |
| **Dependencies** | PyTorch 2.3.0, ONNX 1.17.0, ONNX Runtime 1.19.0 |
| **System requirements** | Raspberry Pi 5 (2GB+ RAM), Raspberry Pi OS Bookworm 64-bit |
| **Installation** | `pip install -r environment/requirements.txt` |
| **Documentation** | README.md, docs/architecture.md, docs/reproducibility.md |
| **Examples** | examples/run_example.sh, 3 reuse scenarios |

---

## 📊 Repository Badges (Optional)

Add these badges to your README for professional appearance:

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX%20Runtime-1.19-green.svg)](https://onnxruntime.ai/)
```

---

## 🔍 Pre-Push Verification

Before pushing to GitHub, verify:

```bash
# Check all required files exist
ls -la README.md LICENSE paper/main_softwarex.pdf
ls -la environment/requirements.txt environment/environment.yml
ls -la docs/architecture.md docs/reproducibility.md
ls -la examples/run_example.sh

# Verify README is comprehensive
wc -l README.md  # Should be ~300+ lines

# Verify LICENSE is MIT
head -1 LICENSE  # Should say "MIT License"

# Verify paper PDF exists
file paper/main_softwarex.pdf  # Should say "PDF document"

# Verify example script is executable
chmod +x examples/run_example.sh
```

---

## 🚨 Common Issues and Fixes

### Issue 1: Large Files (> 100 MB)

**Problem**: GitHub rejects files > 100 MB

**Solution**: Use Git LFS for large model files

```bash
git lfs install
git lfs track "*.onnx"
git add .gitattributes
git commit -m "Add Git LFS for ONNX models"
```

---

### Issue 2: Sensitive Information

**Problem**: Accidentally committed API keys or passwords

**Solution**: Remove from history

```bash
# Remove file from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

---

### Issue 3: Wrong File Structure

**Problem**: Files in wrong directories

**Solution**: Use `git mv` to reorganize

```bash
git mv old/path/file.py new/path/file.py
git commit -m "Reorganize file structure"
```

---

## 📝 Post-Push Checklist

After pushing to GitHub, verify on the web interface:

- [ ] README displays correctly with formatting
- [ ] LICENSE file is recognized by GitHub
- [ ] All directories are present
- [ ] Paper PDF is accessible
- [ ] Example scripts have proper syntax highlighting
- [ ] Documentation files render correctly
- [ ] Repository has a description and topics

---

## 🎓 GitHub Repository Settings

### Add Repository Description

On GitHub web interface:
1. Go to repository settings
2. Add description: "Reproducible edge AI pipeline: Google Colab → ONNX → Raspberry Pi 5"
3. Add topics: `edge-ai`, `onnx`, `raspberry-pi`, `reproducibility`, `machine-learning`, `pytorch`, `softwarex`

### Enable GitHub Pages (Optional)

For documentation hosting:
1. Settings → Pages
2. Source: Deploy from branch
3. Branch: main, folder: /docs
4. Save

---

## ✅ Final Verification

Your repository is SoftwareX-ready when:

- ✅ All required files present
- ✅ README is comprehensive (300+ lines)
- ✅ LICENSE is MIT
- ✅ Paper PDF is in `paper/` directory
- ✅ Documentation is complete
- ✅ Example scripts work
- ✅ Repository structure matches SoftwareX requirements
- ✅ No sensitive information committed
- ✅ All files under version control

---

## 🎯 Next Steps

1. **Push to GitHub** (follow Step 5 above)
2. **Verify on GitHub web interface** (check all files display correctly)
3. **Test clone and run** (verify reproducibility)
4. **Submit paper to SoftwareX** (include GitHub URL in submission)

---

## 📧 Support

If you encounter issues:
- Check GitHub documentation: https://docs.github.com
- Check Git documentation: https://git-scm.com/doc
- Open an issue if problems persist

---

**Status**: ✅ **READY FOR GITHUB PUSH**

**Repository**: https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline

**Last Updated**: March 6, 2025

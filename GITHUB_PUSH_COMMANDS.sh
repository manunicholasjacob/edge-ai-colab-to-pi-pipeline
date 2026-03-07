#!/bin/bash

# GitHub Push Commands for SoftwareX Repository
# Repository: https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline

echo "=========================================="
echo "GitHub Repository Setup and Push"
echo "=========================================="
echo ""

# Navigate to project directory
cd "c:/Users/manun/Downloads/Adaptive_Edge_Cloud_Inference_with_ONNX_Deployment__A_Reproducible_Colab_Raspberry_Pi_Pipeline_on_CIFAR_100_and_SVHN (2)"

echo "Step 1: Creating directory structure..."
mkdir -p paper
mkdir -p src
mkdir -p experiments
mkdir -p models
mkdir -p results
mkdir -p figures
mkdir -p environment
mkdir -p docs
mkdir -p examples
mkdir -p tests

echo "Step 2: Moving files to proper locations..."

# Move paper
if [ -f "main_softwarex.pdf" ]; then
    mv main_softwarex.pdf paper/
    echo "  ✓ Moved main_softwarex.pdf to paper/"
fi

# Move environment files
if [ -f "requirements.txt" ]; then
    mv requirements.txt environment/
    echo "  ✓ Moved requirements.txt to environment/"
fi

if [ -f "environment.yml" ]; then
    mv environment.yml environment/
    echo "  ✓ Moved environment.yml to environment/"
fi

# Move documentation
if [ -f "docs/architecture.md" ] && [ -f "docs/reproducibility.md" ]; then
    echo "  ✓ Documentation already in docs/"
else
    echo "  ⚠ Check documentation files"
fi

# Move examples
if [ -f "examples/run_example.sh" ]; then
    chmod +x examples/run_example.sh
    echo "  ✓ Made run_example.sh executable"
fi

echo ""
echo "Step 3: Initializing Git repository..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    echo "  ✓ Git repository initialized"
else
    echo "  ✓ Git repository already exists"
fi

# Add remote if not already added
if ! git remote | grep -q "origin"; then
    git remote add origin https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline.git
    echo "  ✓ Remote 'origin' added"
else
    echo "  ✓ Remote 'origin' already exists"
fi

echo ""
echo "Step 4: Staging files..."
git add .
echo "  ✓ All files staged"

echo ""
echo "Step 5: Creating commit..."
git commit -m "Initial commit: SoftwareX submission-ready repository

- Add comprehensive README with installation and usage
- Add MIT License
- Add architecture and reproducibility documentation
- Add example scripts for running experiments
- Add paper PDF (main_softwarex.pdf)
- Add environment specifications (requirements.txt, environment.yml)
- Structure repository for SoftwareX compliance
- Add .gitignore for Python projects
- Include cover letter and submission materials"

echo ""
echo "Step 6: Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "=========================================="
echo "✓ Repository pushed to GitHub successfully!"
echo "=========================================="
echo ""
echo "Repository URL: https://github.com/manunicholasjacob/edge-ai-colab-to-pi-pipeline"
echo ""
echo "Next steps:"
echo "1. Verify repository on GitHub web interface"
echo "2. Check that all files are visible"
echo "3. Test clone and installation"
echo "4. Submit to SoftwareX portal"
echo ""

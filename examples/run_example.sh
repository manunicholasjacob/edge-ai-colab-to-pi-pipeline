#!/bin/bash

# Edge AI Pipeline - Complete Experiment Runner
# This script runs all 36 configurations (4 models × 3 batch sizes × 3 thread counts)

set -e  # Exit on error

echo "=========================================="
echo "Edge AI Pipeline - Experiment Runner"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /sys/class/thermal/thermal_zone0/temp ]; then
    echo "Warning: Not running on Raspberry Pi. Temperature monitoring disabled."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r environment/requirements.txt

# Validate manifests
echo "Validating manifests..."
python src/manifest_validator.py experiments/config.yaml

# Create output directories
mkdir -p results
mkdir -p logs
mkdir -p figures

# Configuration arrays
MODELS=("mobilenetv3_cifar100" "mobilenetv3_svhn" "resnet18_cifar100" "resnet18_svhn")
BATCH_SIZES=(1 2 4)
THREAD_COUNTS=(1 2 4)

# Total configurations
TOTAL=$((${#MODELS[@]} * ${#BATCH_SIZES[@]} * ${#THREAD_COUNTS[@]}))
CURRENT=0

echo ""
echo "Running $TOTAL configurations..."
echo ""

# Run all experiments
for model in "${MODELS[@]}"; do
    for batch in "${BATCH_SIZES[@]}"; do
        for threads in "${THREAD_COUNTS[@]}"; do
            CURRENT=$((CURRENT + 1))
            echo "[$CURRENT/$TOTAL] Running: $model, batch=$batch, threads=$threads"
            
            # Run inference
            python src/pi_inference_runner.py \
                --model "models/${model}.onnx" \
                --batch "$batch" \
                --threads "$threads" \
                --output "results/pi_results_normalized.csv"
            
            echo "  ✓ Completed"
            echo ""
        done
    done
done

echo "=========================================="
echo "All experiments completed successfully!"
echo "=========================================="
echo ""
echo "Output files:"
echo "  - results/pi_results_normalized.csv"
echo "  - logs/thermal_trace.csv"
echo ""

# Generate analysis
echo "Generating analysis and figures..."
python src/analysis_tools.py \
    --input results/pi_results_normalized.csv \
    --output figures/

echo ""
echo "✓ Analysis complete"
echo "✓ Figures saved to figures/"
echo ""
echo "=========================================="
echo "Experiment Summary"
echo "=========================================="

# Display summary statistics
python -c "
import pandas as pd
df = pd.read_csv('results/pi_results_normalized.csv')
print(f'Total configurations: {len(df)}')
print(f'Mean latency: {df[\"latency_p50_ms\"].mean():.2f} ms')
print(f'Mean throughput: {df[\"throughput_img_s\"].mean():.1f} img/s')
print('')
print('Latency by model (batch=1, threads=4):')
for model in df['arch'].unique():
    subset = df[(df['arch'] == model) & (df['batch'] == 1) & (df['threads'] == 4)]
    if len(subset) > 0:
        print(f'  {model}: {subset[\"latency_p50_ms\"].mean():.2f} ms')
"

echo ""
echo "=========================================="
echo "Done! Check results/ and figures/ directories."
echo "=========================================="

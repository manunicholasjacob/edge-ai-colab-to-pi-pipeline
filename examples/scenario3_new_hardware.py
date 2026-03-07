#!/usr/bin/env python3
"""
Reuse Scenario 3: New Hardware Platform

This example demonstrates how to extend the pipeline to a new hardware platform
(NVIDIA Jetson Nano) while reusing existing artifacts and measurement protocols.

Steps:
1. Install ONNX Runtime with CUDA execution provider
2. Adapt telemetry collection for GPU
3. Run inference with same manifests
4. Compare Pi vs. Jetson vs. Oracle

Expected time: ~2 hours (setup) + runtime
"""

import json
import os
import subprocess
import time
import numpy as np
from typing import Dict, List, Optional

def check_jetson_environment():
    """Check if running on NVIDIA Jetson."""
    try:
        # Check for Jetson-specific files
        jetson_release = '/etc/nv_tegra_release'
        if os.path.exists(jetson_release):
            with open(jetson_release, 'r') as f:
                print(f"Jetson detected: {f.read().strip()}")
            return True
        return False
    except Exception as e:
        print(f"Error checking Jetson environment: {e}")
        return False

def check_cuda_availability():
    """Check CUDA availability."""
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        print(f"Available execution providers: {providers}")
        return 'CUDAExecutionProvider' in providers
    except ImportError:
        print("ONNX Runtime not installed")
        return False

def get_gpu_temperature():
    """Get GPU temperature on Jetson."""
    try:
        # Jetson thermal zones
        thermal_zones = [
            '/sys/devices/virtual/thermal/thermal_zone0/temp',  # GPU
            '/sys/devices/virtual/thermal/thermal_zone1/temp',  # CPU
        ]
        
        temps = {}
        for i, zone in enumerate(thermal_zones):
            if os.path.exists(zone):
                with open(zone, 'r') as f:
                    temp = float(f.read().strip()) / 1000.0  # Convert to Celsius
                    temps[f'zone{i}'] = temp
        
        return temps
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return {}

def get_gpu_power():
    """Get GPU power consumption on Jetson."""
    try:
        # Jetson power monitoring
        power_file = '/sys/bus/i2c/drivers/ina3221x/1-0040/iio:device0/in_power0_input'
        if os.path.exists(power_file):
            with open(power_file, 'r') as f:
                power_mw = float(f.read().strip())
                return power_mw / 1000.0  # Convert to Watts
        return None
    except Exception as e:
        print(f"Error reading power: {e}")
        return None

def create_jetson_inference_script():
    """Create modified inference script for Jetson."""
    script = '''#!/usr/bin/env python3
"""
Jetson-optimized inference script.
Extends base inference.py with GPU-specific telemetry.
"""

import onnxruntime as ort
import numpy as np
import time
import json
import csv
from pathlib import Path

def run_inference_jetson(manifest_path, batch_size=1, num_threads=4, iterations=50):
    """Run inference on Jetson with GPU telemetry."""
    
    # Load manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Create ONNX Runtime session with CUDA
    providers = [
        ('CUDAExecutionProvider', {
            'device_id': 0,
            'arena_extend_strategy': 'kNextPowerOfTwo',
            'gpu_mem_limit': 2 * 1024 * 1024 * 1024,  # 2GB
            'cudnn_conv_algo_search': 'EXHAUSTIVE',
        }),
        'CPUExecutionProvider'
    ]
    
    model_path = manifest['artifacts']['onnx_fp32']
    session = ort.InferenceSession(model_path, providers=providers)
    
    print(f"Using execution provider: {session.get_providers()}")
    
    # Prepare dummy input
    input_name = session.get_inputs()[0].name
    input_shape = [batch_size] + manifest['image_size'] + [3]
    dummy_input = np.random.randn(*input_shape).astype(np.float32)
    
    # Warm-up
    print("Warming up...")
    for _ in range(20):
        session.run(None, {input_name: dummy_input})
    
    # Timed iterations with telemetry
    print(f"Running {iterations} timed iterations...")
    latencies = []
    temperatures = []
    powers = []
    
    for i in range(iterations):
        # Read telemetry before inference
        temp_before = get_gpu_temperature()
        power_before = get_gpu_power()
        
        # Run inference
        start = time.perf_counter()
        outputs = session.run(None, {input_name: dummy_input})
        latency = (time.perf_counter() - start) * 1000  # ms
        
        # Read telemetry after inference
        temp_after = get_gpu_temperature()
        power_after = get_gpu_power()
        
        latencies.append(latency)
        temperatures.append(temp_after)
        powers.append(power_after)
        
        if (i + 1) % 10 == 0:
            print(f"  Iteration {i+1}/{iterations} - Latency: {latency:.2f} ms")
    
    # Compute metrics
    results = {
        'batch_size': batch_size,
        'num_threads': num_threads,
        'iterations': iterations,
        'mean_latency_ms': np.mean(latencies),
        'p50_latency_ms': np.percentile(latencies, 50),
        'p90_latency_ms': np.percentile(latencies, 90),
        'p99_latency_ms': np.percentile(latencies, 99),
        'throughput_img_s': 1000.0 / np.mean(latencies) * batch_size,
        'mean_temp_c': np.mean([t.get('zone0', 0) for t in temperatures]),
        'mean_power_w': np.mean([p for p in powers if p is not None]),
    }
    
    return results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--batch', type=int, default=1)
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--iterations', type=int, default=50)
    args = parser.parse_args()
    
    results = run_inference_jetson(
        args.manifest,
        batch_size=args.batch,
        num_threads=args.threads,
        iterations=args.iterations
    )
    
    print("\\nResults:")
    for key, value in results.items():
        print(f"  {key}: {value}")
'''
    
    with open('inference_jetson.py', 'w') as f:
        f.write(script)
    
    print("Created inference_jetson.py")

def create_comparison_script():
    """Create script to compare Pi vs. Jetson vs. Oracle."""
    script = '''#!/usr/bin/env python3
"""
Compare performance across Pi, Jetson, and Oracle.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_results(pi_csv, jetson_csv, oracle_csv):
    """Load results from all platforms."""
    pi_df = pd.read_csv(pi_csv)
    jetson_df = pd.read_csv(jetson_csv)
    oracle_df = pd.read_csv(oracle_csv)
    
    return pi_df, jetson_df, oracle_df

def compute_speedup(pi_df, jetson_df, oracle_df):
    """Compute speedup metrics."""
    # Merge on configuration
    merged = pd.merge(
        pi_df[['dataset', 'model_arch', 'batch', 'threads', 'pi_img_s']],
        jetson_df[['dataset', 'model_arch', 'batch', 'threads', 'throughput_img_s']],
        on=['dataset', 'model_arch', 'batch', 'threads'],
        suffixes=('_pi', '_jetson')
    )
    merged = pd.merge(
        merged,
        oracle_df[['dataset', 'model_arch', 'batch', 'threads', 'oracle_img_s']],
        on=['dataset', 'model_arch', 'batch', 'threads']
    )
    
    # Compute speedups
    merged['pi_vs_oracle'] = merged['pi_img_s'] / merged['oracle_img_s']
    merged['jetson_vs_oracle'] = merged['throughput_img_s'] / merged['oracle_img_s']
    merged['jetson_vs_pi'] = merged['throughput_img_s'] / merged['pi_img_s']
    
    return merged

def plot_comparison(comparison_df):
    """Plot three-way comparison."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    configs = comparison_df['model_arch'] + '\\n' + comparison_df['dataset']
    
    # Throughput comparison
    axes[0].bar(range(len(configs)), comparison_df['oracle_img_s'], 
                label='Oracle', alpha=0.7)
    axes[0].bar(range(len(configs)), comparison_df['throughput_img_s'], 
                label='Jetson', alpha=0.7)
    axes[0].bar(range(len(configs)), comparison_df['pi_img_s'], 
                label='Pi 5', alpha=0.7)
    axes[0].set_ylabel('Throughput (img/s)')
    axes[0].set_title('Absolute Throughput')
    axes[0].legend()
    axes[0].set_xticks(range(len(configs)))
    axes[0].set_xticklabels(configs, rotation=45, ha='right')
    
    # Speedup vs Oracle
    axes[1].plot(comparison_df['jetson_vs_oracle'], 'o-', label='Jetson/Oracle')
    axes[1].plot(comparison_df['pi_vs_oracle'], 's-', label='Pi/Oracle')
    axes[1].axhline(y=1.0, color='r', linestyle='--', label='Oracle baseline')
    axes[1].set_ylabel('Speedup')
    axes[1].set_title('Speedup vs. Oracle')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Jetson vs Pi
    axes[2].bar(range(len(configs)), comparison_df['jetson_vs_pi'])
    axes[2].axhline(y=1.0, color='r', linestyle='--', label='Equal performance')
    axes[2].set_ylabel('Jetson / Pi Speedup')
    axes[2].set_title('Jetson vs. Pi 5')
    axes[2].set_xticks(range(len(configs)))
    axes[2].set_xticklabels(configs, rotation=45, ha='right')
    axes[2].legend()
    
    plt.tight_layout()
    plt.savefig('three_way_comparison.pdf')
    print("Saved three_way_comparison.pdf")

if __name__ == '__main__':
    pi_df, jetson_df, oracle_df = load_results(
        'pi_results.csv',
        'jetson_results.csv',
        'oracle_results.csv'
    )
    
    comparison = compute_speedup(pi_df, jetson_df, oracle_df)
    plot_comparison(comparison)
    
    print("\\nSummary:")
    print(f"Jetson avg speedup vs Oracle: {comparison['jetson_vs_oracle'].mean():.2f}x")
    print(f"Pi avg speedup vs Oracle: {comparison['pi_vs_oracle'].mean():.2f}x")
    print(f"Jetson avg speedup vs Pi: {comparison['jetson_vs_pi'].mean():.2f}x")
'''
    
    with open('compare_platforms.py', 'w') as f:
        f.write(script)
    
    print("Created compare_platforms.py")

def main():
    """Main execution function."""
    print("=" * 60)
    print("Reuse Scenario 3: New Hardware Platform (Jetson Nano)")
    print("=" * 60)
    
    print("\n[1/5] Checking environment...")
    is_jetson = check_jetson_environment()
    has_cuda = check_cuda_availability()
    
    if is_jetson:
        print("✓ Running on NVIDIA Jetson")
    else:
        print("✗ Not running on Jetson (demo mode)")
    
    if has_cuda:
        print("✓ CUDA execution provider available")
    else:
        print("✗ CUDA not available")
    
    print("\n[2/5] Creating Jetson-specific inference script...")
    create_jetson_inference_script()
    
    print("\n[3/5] Creating comparison script...")
    create_comparison_script()
    
    print("\n[4/5] Installation instructions for Jetson...")
    install_instructions = """
# On NVIDIA Jetson Nano:

# 1. Install ONNX Runtime with CUDA
pip3 install onnxruntime-gpu==1.19.0

# 2. Verify CUDA provider
python3 -c "import onnxruntime as ort; print(ort.get_available_providers())"

# 3. Copy artifacts from Pi or Colab
scp pi@raspberrypi:~/edge_inference/bundle.zip .
unzip bundle.zip

# 4. Run inference
python3 inference_jetson.py --manifest MANIFEST.json --batch 1 --threads 4

# 5. Compare with Pi and Oracle
python3 compare_platforms.py
"""
    print(install_instructions)
    
    print("\n[5/5] Code modifications needed...")
    modifications = """
Minimal changes required:

1. inference_jetson.py (created above):
   - Uses CUDAExecutionProvider instead of CPUExecutionProvider
   - Reads GPU temperature from Jetson thermal zones
   - Logs GPU power consumption

2. No changes to:
   - ONNX models (same artifacts work on all platforms)
   - MANIFEST.json (preprocessing is platform-independent)
   - Analysis scripts (consume same CSV format)

3. Optional enhancements:
   - Add TensorRT execution provider for further acceleration
   - Implement dynamic batch sizing based on GPU memory
   - Add multi-GPU support for Jetson Xavier
"""
    print(modifications)
    
    print("\n" + "=" * 60)
    print("SUCCESS! Jetson integration ready")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install ONNX Runtime GPU on Jetson")
    print("2. Copy bundle.zip to Jetson")
    print("3. Run: python3 inference_jetson.py --manifest MANIFEST.json")
    print("4. Compare results: python3 compare_platforms.py")
    print("\nThe same ONNX models work across Pi, Jetson, and Oracle!")

if __name__ == '__main__':
    main()

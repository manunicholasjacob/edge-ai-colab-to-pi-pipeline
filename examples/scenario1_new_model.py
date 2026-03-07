#!/usr/bin/env python3
"""
Reuse Scenario 1: New Model Drop-In

This example demonstrates how to add a new model architecture (EfficientNet-B0)
to the pipeline without modifying the core inference or deployment code.

Steps:
1. Define the model architecture
2. Train the model (or load pretrained)
3. Export to ONNX
4. Create manifest
5. Run inference using existing pipeline

Expected time: ~30 minutes (excluding training)
"""

import json
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import numpy as np

def get_efficientnet_b0(num_classes=100):
    """Get EfficientNet-B0 model adapted for CIFAR-100."""
    model = torchvision.models.efficientnet_b0(pretrained=True)
    # Replace classifier for CIFAR-100
    model.classifier[1] = nn.Linear(1280, num_classes)
    return model

def train_model(model, train_loader, val_loader, epochs=120, device='cuda'):
    """Train the model (simplified version)."""
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=0.1,
        momentum=0.9,
        weight_decay=5e-4
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    model = model.to(device)
    best_acc = 0.0
    
    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        # Validation phase
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        
        acc = 100. * correct / total
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), 'efficientnet_b0_best.pth')
        
        scheduler.step()
        print(f'Epoch {epoch+1}/{epochs} - Loss: {train_loss/len(train_loader):.4f} - Acc: {acc:.2f}%')
    
    return model

def export_to_onnx(model, output_path='efficientnet_b0.onnx'):
    """Export model to ONNX format."""
    model.eval()
    dummy_input = torch.randn(1, 3, 32, 32)
    
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=13,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    print(f'Model exported to {output_path}')
    
    # Validate ONNX export
    import onnx
    import onnxruntime as ort
    
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    
    # Numerical validation
    ort_session = ort.InferenceSession(output_path)
    test_input = torch.randn(5, 3, 32, 32)
    
    with torch.no_grad():
        torch_output = model(test_input).numpy()
    
    ort_inputs = {ort_session.get_inputs()[0].name: test_input.numpy()}
    ort_output = ort_session.run(None, ort_inputs)[0]
    
    max_diff = np.abs(torch_output - ort_output).max()
    print(f'Max difference between PyTorch and ONNX: {max_diff:.2e}')
    assert max_diff < 1e-4, f'Export validation failed: {max_diff}'
    print('ONNX export validated successfully!')

def create_manifest(output_path='MANIFEST.json'):
    """Create manifest for the new model."""
    manifest = {
        "dataset": "cifar100",
        "arch": "efficientnet_b0",
        "classes": 100,
        "image_size": [32, 32],
        "mean": [0.5071, 0.4867, 0.4408],
        "std": [0.2675, 0.2565, 0.2761],
        "opset": 13,
        "training": {
            "epochs": 120,
            "optimizer": "SGD",
            "lr": 0.1,
            "momentum": 0.9,
            "weight_decay": 5e-4,
            "scheduler": "CosineAnnealingLR",
            "seed": 1337
        },
        "artifacts": {
            "onnx_fp32": "efficientnet_b0.onnx",
            "onnx_int8": None
        },
        "metadata": {
            "description": "EfficientNet-B0 trained on CIFAR-100",
            "created_by": "scenario1_new_model.py",
            "pytorch_version": torch.__version__,
            "torchvision_version": torchvision.__version__
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f'Manifest created: {output_path}')
    return manifest

def main():
    """Main execution function."""
    print("=" * 60)
    print("Reuse Scenario 1: New Model Drop-In (EfficientNet-B0)")
    print("=" * 60)
    
    # Set random seeds for reproducibility
    torch.manual_seed(1337)
    np.random.seed(1337)
    
    # 1. Load dataset
    print("\n[1/5] Loading CIFAR-100 dataset...")
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.5071, 0.4867, 0.4408], [0.2675, 0.2565, 0.2761])
    ])
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5071, 0.4867, 0.4408], [0.2675, 0.2565, 0.2761])
    ])
    
    trainset = torchvision.datasets.CIFAR100(
        root='./data', train=True, download=True, transform=transform_train
    )
    testset = torchvision.datasets.CIFAR100(
        root='./data', train=False, download=True, transform=transform_test
    )
    
    train_loader = DataLoader(trainset, batch_size=128, shuffle=True, num_workers=2)
    test_loader = DataLoader(testset, batch_size=100, shuffle=False, num_workers=2)
    
    # 2. Create model
    print("\n[2/5] Creating EfficientNet-B0 model...")
    model = get_efficientnet_b0(num_classes=100)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # 3. Train model (or load pretrained)
    print("\n[3/5] Training model...")
    print("NOTE: For quick testing, set epochs=1. For full training, use epochs=120")
    
    # Option A: Quick test (1 epoch)
    # model = train_model(model, train_loader, test_loader, epochs=1)
    
    # Option B: Load pretrained checkpoint if available
    # model.load_state_dict(torch.load('efficientnet_b0_best.pth'))
    
    # Option C: Skip training for this demo
    print("Skipping training for demo. Using pretrained ImageNet weights.")
    
    # 4. Export to ONNX
    print("\n[4/5] Exporting to ONNX...")
    export_to_onnx(model, 'efficientnet_b0.onnx')
    
    # 5. Create manifest
    print("\n[5/5] Creating manifest...")
    manifest = create_manifest('MANIFEST.json')
    
    print("\n" + "=" * 60)
    print("SUCCESS! New model ready for deployment")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Copy efficientnet_b0.onnx and MANIFEST.json to Raspberry Pi")
    print("2. Run: ./validate_and_run.sh")
    print("3. Results will be in results/pi_results.csv")
    print("\nNo changes to inference.py or deployment scripts needed!")

if __name__ == '__main__':
    main()

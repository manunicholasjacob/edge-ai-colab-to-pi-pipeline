#!/usr/bin/env python3
"""
Reuse Scenario 2: New Dataset Integration

This example demonstrates how to integrate a new dataset (ImageNet-1k subset)
into the pipeline while reusing existing training and deployment infrastructure.

Steps:
1. Create dataset loader
2. Update normalization constants
3. Train model on new dataset
4. Export and create manifest
5. Run inference using existing pipeline

Expected time: ~1 hour (excluding dataset download and training)
"""

import json
import os
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision.datasets import ImageFolder
import numpy as np

# ImageNet normalization constants (standard)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

class ImageNetSubset(Dataset):
    """ImageNet-1k subset dataset wrapper."""
    
    def __init__(self, root, split='train', num_classes=100, samples_per_class=500):
        """
        Args:
            root: Root directory containing ImageNet data
            split: 'train' or 'val'
            num_classes: Number of classes to include (subset of 1000)
            samples_per_class: Number of samples per class
        """
        self.root = root
        self.split = split
        
        # Define transforms
        if split == 'train':
            self.transform = transforms.Compose([
                transforms.RandomResizedCrop(224),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD)
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD)
            ])
        
        # Load full ImageNet
        full_dataset = ImageFolder(
            os.path.join(root, split),
            transform=self.transform
        )
        
        # Create subset
        indices = []
        class_counts = {}
        for idx, (_, label) in enumerate(full_dataset.samples):
            if label >= num_classes:
                continue
            if label not in class_counts:
                class_counts[label] = 0
            if class_counts[label] < samples_per_class:
                indices.append(idx)
                class_counts[label] += 1
        
        self.dataset = Subset(full_dataset, indices)
        self.num_classes = num_classes
        
        print(f"Created {split} subset: {len(self.dataset)} samples, {num_classes} classes")
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

def get_imagenet_loaders(root='./data/imagenet', num_classes=100, batch_size=128):
    """Create ImageNet data loaders."""
    print(f"Loading ImageNet subset ({num_classes} classes)...")
    
    # Check if ImageNet data exists
    if not os.path.exists(root):
        print(f"ERROR: ImageNet data not found at {root}")
        print("Please download ImageNet and extract to the specified directory")
        print("Expected structure:")
        print("  imagenet/")
        print("    train/")
        print("      n01440764/")
        print("      n01443537/")
        print("      ...")
        print("    val/")
        print("      n01440764/")
        print("      ...")
        return None, None
    
    train_dataset = ImageNetSubset(root, split='train', num_classes=num_classes)
    val_dataset = ImageNetSubset(root, split='val', num_classes=num_classes)
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    return train_loader, val_loader

def train_on_imagenet(model, train_loader, val_loader, epochs=90, device='cuda'):
    """Train model on ImageNet subset."""
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=0.1,
        momentum=0.9,
        weight_decay=1e-4
    )
    scheduler = torch.optim.lr_scheduler.MultiStepLR(
        optimizer,
        milestones=[30, 60, 80],
        gamma=0.1
    )
    
    model = model.to(device)
    best_acc = 0.0
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            
            if batch_idx % 100 == 0:
                print(f'  Batch {batch_idx}/{len(train_loader)} - Loss: {loss.item():.4f}')
        
        # Validation
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
            torch.save(model.state_dict(), 'mobilenet_v3_imagenet_best.pth')
        
        scheduler.step()
        print(f'Epoch {epoch+1}/{epochs} - Loss: {train_loss/len(train_loader):.4f} - Acc: {acc:.2f}% (Best: {best_acc:.2f}%)')
    
    return model

def export_and_create_manifest(model, dataset_name='imagenet100'):
    """Export model and create manifest for new dataset."""
    # Export to ONNX
    model.eval()
    dummy_input = torch.randn(1, 3, 224, 224)  # ImageNet uses 224x224
    
    onnx_path = f'mobilenet_v3_{dataset_name}.onnx'
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
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
    print(f'Model exported to {onnx_path}')
    
    # Validate ONNX
    import onnx
    import onnxruntime as ort
    
    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)
    
    ort_session = ort.InferenceSession(onnx_path)
    test_input = torch.randn(5, 3, 224, 224)
    
    with torch.no_grad():
        torch_output = model(test_input).numpy()
    
    ort_inputs = {ort_session.get_inputs()[0].name: test_input.numpy()}
    ort_output = ort_session.run(None, ort_inputs)[0]
    
    max_diff = np.abs(torch_output - ort_output).max()
    print(f'Max difference: {max_diff:.2e}')
    assert max_diff < 1e-4
    
    # Create manifest
    manifest = {
        "dataset": dataset_name,
        "arch": "mobilenet_v3_small",
        "classes": 100,
        "image_size": [224, 224],  # ImageNet uses 224x224
        "mean": IMAGENET_MEAN,
        "std": IMAGENET_STD,
        "opset": 13,
        "training": {
            "epochs": 90,
            "optimizer": "SGD",
            "lr": 0.1,
            "momentum": 0.9,
            "weight_decay": 1e-4,
            "scheduler": "MultiStepLR",
            "seed": 1337
        },
        "artifacts": {
            "onnx_fp32": onnx_path,
            "onnx_int8": None
        },
        "metadata": {
            "description": "MobileNetV3-Small trained on ImageNet-100 subset",
            "created_by": "scenario2_new_dataset.py"
        }
    }
    
    manifest_path = f'MANIFEST_{dataset_name}.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f'Manifest created: {manifest_path}')
    return manifest

def update_dataset_registry():
    """Example code showing how to update the dataset registry."""
    code = '''
# Add to src/datasets.py

DATASET_REGISTRY = {
    "cifar100": get_cifar100,
    "svhn": get_svhn,
    "imagenet100": get_imagenet_subset,  # NEW
}

NORMALIZATION_CONSTANTS = {
    "cifar100": {
        "mean": [0.5071, 0.4867, 0.4408],
        "std": [0.2675, 0.2565, 0.2761]
    },
    "svhn": {
        "mean": [0.4377, 0.4438, 0.4728],
        "std": [0.1980, 0.2010, 0.1970]
    },
    "imagenet100": {  # NEW
        "mean": [0.485, 0.456, 0.406],
        "std": [0.229, 0.224, 0.225]
    }
}

def get_imagenet_subset(root="data/imagenet", train=True):
    """Get ImageNet-100 subset."""
    split = "train" if train else "val"
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    return ImageFolder(os.path.join(root, split), transform=transform)
'''
    print("\n" + "=" * 60)
    print("Dataset Registry Update")
    print("=" * 60)
    print(code)

def main():
    """Main execution function."""
    print("=" * 60)
    print("Reuse Scenario 2: New Dataset Integration (ImageNet-100)")
    print("=" * 60)
    
    # Set random seeds
    torch.manual_seed(1337)
    np.random.seed(1337)
    
    print("\n[1/4] Setting up ImageNet-100 dataset...")
    print("NOTE: This example assumes ImageNet data is available.")
    print("For demo purposes, we'll show the integration pattern.")
    
    # Show how to create loaders (commented out if data not available)
    # train_loader, val_loader = get_imagenet_loaders(
    #     root='./data/imagenet',
    #     num_classes=100,
    #     batch_size=128
    # )
    
    print("\n[2/4] Creating model...")
    model = torchvision.models.mobilenet_v3_small(pretrained=True)
    model.classifier[3] = nn.Linear(1024, 100)  # Adapt for 100 classes
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    print("\n[3/4] Training on ImageNet-100...")
    print("NOTE: Skipping actual training for demo.")
    print("In practice, run: train_on_imagenet(model, train_loader, val_loader, epochs=90)")
    
    print("\n[4/4] Exporting and creating manifest...")
    manifest = export_and_create_manifest(model, 'imagenet100')
    
    # Show dataset registry update
    update_dataset_registry()
    
    print("\n" + "=" * 60)
    print("SUCCESS! New dataset integrated")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update manifest.schema.json to include 'imagenet100' in dataset enum")
    print("2. Add dataset loader to src/datasets.py (see code above)")
    print("3. Copy ONNX and manifest to Raspberry Pi")
    print("4. Run: ./validate_and_run.sh")
    print("\nThe inference pipeline will automatically use the new dataset!")

if __name__ == '__main__':
    main()

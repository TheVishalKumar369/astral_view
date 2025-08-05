#!/usr/bin/env python3
"""
GPU Test Script for Cosmic Explorer
Tests GPU availability and performance in Podman containers.
"""

import sys
import subprocess
import platform

def test_nvidia_smi():
    """Test nvidia-smi command availability and output."""
    print("🔍 Testing nvidia-smi...")
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ nvidia-smi is working")
            print("📊 GPU Information:")
            print(result.stdout)
            return True
        else:
            print("❌ nvidia-smi failed")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi not found")
        return False
    except subprocess.TimeoutExpired:
        print("❌ nvidia-smi timed out")
        return False
    except Exception as e:
        print(f"❌ nvidia-smi error: {e}")
        return False

def test_cuda_toolkit():
    """Test CUDA toolkit availability."""
    print("\n🔍 Testing CUDA toolkit...")
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CUDA toolkit is available")
            print("🔥 CUDA Version:")
            print(result.stdout)
            return True
        else:
            print("❌ CUDA toolkit not working")
            return False
    except FileNotFoundError:
        print("❌ nvcc not found - CUDA toolkit may not be installed")
        return False
    except Exception as e:
        print(f"❌ CUDA toolkit error: {e}")
        return False

def test_pytorch_cuda():
    """Test PyTorch CUDA support."""
    print("\n🔍 Testing PyTorch CUDA support...")
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        
        if torch.cuda.is_available():
            print("✅ CUDA is available in PyTorch")
            device_count = torch.cuda.device_count()
            print(f"📱 GPU devices found: {device_count}")
            
            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                device_props = torch.cuda.get_device_properties(i)
                memory_gb = device_props.total_memory / (1024**3)
                print(f"  Device {i}: {device_name} ({memory_gb:.1f} GB)")
            
            # Test basic tensor operations
            print("\n🧮 Testing CUDA tensor operations...")
            try:
                x = torch.randn(1000, 1000).cuda()
                y = torch.randn(1000, 1000).cuda()
                z = torch.mm(x, y)
                print("✅ CUDA tensor operations working")
                return True
            except Exception as e:
                print(f"❌ CUDA tensor operations failed: {e}")
                return False
        else:
            print("❌ CUDA not available in PyTorch")
            return False
            
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    except Exception as e:
        print(f"❌ PyTorch CUDA test failed: {e}")
        return False

def test_tensorflow_gpu():
    """Test TensorFlow GPU support."""
    print("\n🔍 Testing TensorFlow GPU support...")
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow version: {tf.__version__}")
        
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"✅ TensorFlow GPU devices found: {len(gpus)}")
            for i, gpu in enumerate(gpus):
                print(f"  Device {i}: {gpu}")
            
            # Test basic operations
            try:
                with tf.device('/GPU:0'):
                    a = tf.random.normal([1000, 1000])
                    b = tf.random.normal([1000, 1000])
                    c = tf.matmul(a, b)
                print("✅ TensorFlow GPU operations working")
                return True
            except Exception as e:
                print(f"❌ TensorFlow GPU operations failed: {e}")
                return False
        else:
            print("❌ No TensorFlow GPU devices found")
            return False
            
    except ImportError:
        print("❌ TensorFlow not installed")
        return False
    except Exception as e:
        print(f"❌ TensorFlow GPU test failed: {e}")
        return False

def test_gpu_memory():
    """Test GPU memory usage."""
    print("\n🔍 Testing GPU memory...")
    try:
        result = subprocess.run([
            'nvidia-smi', '--query-gpu=memory.total,memory.used,memory.free',
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("📊 GPU Memory Status:")
            lines = result.stdout.strip().split('\n')
            for i, line in enumerate(lines):
                total, used, free = map(int, line.split(', '))
                total_gb = total / 1024
                used_gb = used / 1024
                free_gb = free / 1024
                usage_pct = (used / total) * 100
                print(f"  GPU {i}: {total_gb:.1f}GB total, {used_gb:.1f}GB used ({usage_pct:.1f}%), {free_gb:.1f}GB free")
            return True
        else:
            print("❌ Failed to get GPU memory info")
            return False
    except Exception as e:
        print(f"❌ GPU memory test failed: {e}")
        return False

def main():
    """Run all GPU tests."""
    print("🚀 GPU Test Suite for Cosmic Explorer")
    print("=" * 50)
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print("=" * 50)
    
    tests = [
        ("NVIDIA SMI", test_nvidia_smi),
        ("CUDA Toolkit", test_cuda_toolkit),
        ("PyTorch CUDA", test_pytorch_cuda),
        ("TensorFlow GPU", test_tensorflow_gpu),
        ("GPU Memory", test_gpu_memory),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All GPU tests passed! Your setup is ready for GPU tasks.")
        return 0
    elif passed > 0:
        print("⚠️  Some GPU tests passed. Partial GPU functionality available.")
        return 1
    else:
        print("❌ No GPU tests passed. GPU access may not be configured correctly.")
        return 2

if __name__ == "__main__":
    sys.exit(main())

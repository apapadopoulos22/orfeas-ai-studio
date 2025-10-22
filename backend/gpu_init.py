
"""
ORFEAS GPU Initialization
Auto-configure GPU acceleration and optimization
"""

import os
import json
import logging
from pathlib import Path

def initialize_gpu_acceleration() -> None:
    """Initialize GPU acceleration with optimal settings"""
    
    # Load GPU configuration
    config_path = Path(__file__).parent / "gpu_config.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = {"gpu_acceleration": {"enabled": False}}
    
    # Set environment variables
    env_vars = config.get("environment_variables", {})
    for key, value in env_vars.items():
        os.environ[key] = str(value)
    
    # Configure PyTorch
    try:
        import torch
        
        # GPU settings
        if config["gpu_acceleration"]["enabled"] and torch.cuda.is_available():
            # Set memory fraction
            memory_fraction = config["gpu_acceleration"].get("memory_fraction", 0.9)
            torch.cuda.set_per_process_memory_fraction(memory_fraction)
            
            # Enable optimizations
            if config["pytorch_settings"]["backends_cudnn_benchmark"]:
                torch.backends.cudnn.benchmark = True
            
            torch.backends.cudnn.deterministic = config["pytorch_settings"]["backends_cudnn_deterministic"]
            
            # Mixed precision
            if config["gpu_acceleration"]["mixed_precision"]:
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
            
            print(f"[OK] GPU acceleration initialized: {torch.cuda.get_device_name(0)}")
            print(f"[TARGET] GPU Memory: {torch.cuda.get_device_properties(0).total_memory // (1024**3)} GB")
            print(f"[FAST] Memory fraction: {memory_fraction * 100:.1f}%")
        else:
            print("[WARN] GPU acceleration disabled - using CPU mode")
            
    except ImportError:
        print("[WARN] PyTorch not available - GPU acceleration disabled")
    
    return config

# Auto-initialize when imported
if __name__ != "__main__":
    initialize_gpu_acceleration()

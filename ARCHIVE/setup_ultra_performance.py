#!/usr/bin/env python3
"""
Ultra Performance Setup Script for ORFEAS AI System
Installs and configures all dependencies for maximum AI performance
Optimized for RTX 3090 + i9-9900K + 64GB RAM
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(cmd, description=""):
    """Run command with error handling"""
    print(f"\nÔ£ø√º√Æ√ü {description}")
    print(f"   Command: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"   '√∫√ñ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   '√π√• Failed: {e.stderr}")
        return False

def check_system_requirements():
    """Check system meets ultra performance requirements"""
    print("Ô£ø√º√Æ√ß Checking System Requirements...")

    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 9:
        print(f"   '√∫√ñ Python {python_version.major}.{python_version.minor}")
    else:
        print(f"   '√π√• Python {python_version.major}.{python_version.minor} (need 3.9+)")
        return False

    # Check CUDA availability
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"   '√∫√ñ GPU: {gpu_name} ({gpu_memory:.1f}GB)")

            if "3090" in gpu_name and gpu_memory >= 20:
                print(f"   Ô£ø√º√∂√Ñ Ultra Performance GPU Detected!")
                return True
            elif gpu_memory >= 8:
                print(f"   '√∂¬∞ High Performance GPU Detected")
                return True
            else:
                print(f"   ‚ö†Ô∏è  Limited GPU Memory ({gpu_memory:.1f}GB)")
                return True
        else:
            print(f"   '√π√• No CUDA GPU detected")
            return False
    except ImportError:
        print(f"   ‚ö†Ô∏è  PyTorch not installed yet")

    return True

def install_pytorch_ultra():
    """Install PyTorch with CUDA for ultra performance"""
    print("\nÔ£ø√º√∂√Ñ Installing PyTorch Ultra Performance...")

    # Uninstall existing PyTorch first
    uninstall_cmds = [
        "pip uninstall torch torchvision torchaudio -y",
        "pip uninstall xformers -y"
    ]

    for cmd in uninstall_cmds:
        run_command(cmd, "Cleaning previous PyTorch installations")

    # Install latest PyTorch with CUDA 12.1
    pytorch_cmd = (
        "pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 "
        "--index-url https://download.pytorch.org/whl/cu121"
    )

    if not run_command(pytorch_cmd, "Installing PyTorch 2.1.0 with CUDA 12.1"):
        return False

    # Install xformers for memory efficiency
    xformers_cmd = "pip install xformers --index-url https://download.pytorch.org/whl/cu121"
    if not run_command(xformers_cmd, "Installing xformers for ultra memory efficiency"):
        print("   ‚ö†Ô∏è  xformers failed, continuing without it")

    return True

def install_ai_dependencies():
    """Install AI and ML dependencies for ultra performance"""
    print("\nÔ£ø√º¬ß√± Installing AI/ML Dependencies...")

    dependencies = [
        # Core AI libraries
        "transformers>=4.30.0",
        "diffusers>=0.20.0",
        "accelerate>=0.20.0",
        "huggingface-hub>=0.15.0",

        # Computer Vision
        "opencv-python>=4.8.0",
        "Pillow>=10.0.0",
        "scikit-image>=0.21.0",
        "albumentations>=1.3.0",

        # 3D Processing
        "trimesh>=3.21.0",
        "open3d>=0.17.0",
        "meshio>=5.3.0",
        "pyvista>=0.41.0",

        # High Performance Computing
        "numba>=0.57.0",
        "cupy-cuda12x>=12.0.0",  # GPU accelerated NumPy
        "tensorrt>=8.6.0",  # NVIDIA TensorRT

        # Memory and Performance
        "psutil>=5.9.0",
        "GPUtil>=1.4.0",
        "py3nvml>=0.2.7",

        # Advanced AI features
        "flash-attn>=2.0.0",  # Ultra fast attention
        "triton>=2.0.0",  # GPU kernel optimization
        "bitsandbytes>=0.41.0",  # 8-bit quantization
    ]

    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep.split('>=')[0]}"):
            print(f"   ‚ö†Ô∏è  Failed to install {dep}, continuing...")

    return True

def install_web_dependencies():
    """Install web server and communication dependencies"""
    print("\nÔ£ø√º√•√™ Installing Web Dependencies...")

    web_deps = [
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "flask-socketio>=5.3.0",
        "python-socketio>=5.8.0",
        "gunicorn>=21.0.0",  # High performance WSGI server
        "gevent>=23.0.0",  # Async I/O
        "requests>=2.31.0",
        "aiohttp>=3.8.0",  # Async HTTP
        "websockets>=11.0.0",
    ]

    for dep in web_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep.split('>=')[0]}"):
            return False

    return True

def install_development_tools():
    """Install development and debugging tools"""
    print("\nüõ†Ô∏è Installing Development Tools...")

    dev_tools = [
        "jupyter>=1.0.0",
        "ipython>=8.14.0",
        "matplotlib>=3.7.0",
        "plotly>=5.15.0",
        "tqdm>=4.65.0",  # Progress bars
        "rich>=13.4.0",  # Beautiful terminal output
        "wandb>=0.15.0",  # Experiment tracking
        "tensorboard>=2.13.0",  # Visualization
    ]

    for tool in dev_tools:
        if not run_command(f"pip install {tool}", f"Installing {tool.split('>=')[0]}"):
            print(f"   ‚ö†Ô∏è  Failed to install {tool}, continuing...")

    return True

def setup_hunyuan3d_ultra():
    """Setup Hunyuan3D with ultra performance optimizations"""
    print("\nüéØ Setting up Hunyuan3D Ultra Performance...")

    base_dir = Path.cwd()
    hunyuan_source_dir = base_dir / "Hunyuan3D-2.1-SOURCE"

    if hunyuan_source_dir.exists():
        print(f"   '√∫√ñ Hunyuan3D source found: {hunyuan_source_dir}")

        # Install Hunyuan3D requirements
        requirements_file = hunyuan_source_dir / "requirements.txt"
        if requirements_file.exists():
            if not run_command(
                f"pip install -r {requirements_file}",
                "Installing Hunyuan3D requirements"
            ):
                return False

        # Setup custom rasterizer for ultra performance
        rasterizer_dir = hunyuan_source_dir / "hy3dpaint" / "custom_rasterizer"
        if rasterizer_dir.exists():
            original_dir = Path.cwd()
            try:
                os.chdir(rasterizer_dir)
                if not run_command("pip install -e .", "Installing custom rasterizer"):
                    print("   ‚ö†Ô∏è  Custom rasterizer install failed")
            finally:
                os.chdir(original_dir)

        # Setup differential renderer
        renderer_dir = hunyuan_source_dir / "hy3dpaint" / "DifferentiableRenderer"
        if renderer_dir.exists():
            original_dir = Path.cwd()
            try:
                os.chdir(renderer_dir)
                compile_script = renderer_dir / "compile_mesh_painter.sh"
                if compile_script.exists() and platform.system() != "Windows":
                    if not run_command("bash compile_mesh_painter.sh", "Compiling mesh painter"):
                        print("   ‚ö†Ô∏è  Mesh painter compilation failed")
                else:
                    print("   ‚ö†Ô∏è  Mesh painter compilation skipped (Windows or script missing)")
            finally:
                os.chdir(original_dir)

        return True
    else:
        print(f"   '√π√• Hunyuan3D source not found at {hunyuan_source_dir}")
        return False

def download_essential_models():
    """Download essential AI models for ultra performance"""
    print("\nÔ£ø√º√¨‚Ä¢ Downloading Essential AI Models...")

    # Create models directory
    models_dir = Path("backend/models")
    models_dir.mkdir(exist_ok=True)

    # Download Real-ESRGAN for upscaling
    esrgan_url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
    esrgan_path = Path("Hunyuan3D-2.1-SOURCE/hy3dpaint/ckpt/RealESRGAN_x4plus.pth")

    if not esrgan_path.exists():
        esrgan_path.parent.mkdir(parents=True, exist_ok=True)
        download_cmd = f"curl -L {esrgan_url} -o {esrgan_path}"
        if platform.system() == "Windows":
            download_cmd = f"powershell -Command \"Invoke-WebRequest -Uri {esrgan_url} -OutFile {esrgan_path}\""

        if not run_command(download_cmd, "Downloading Real-ESRGAN model"):
            print("   ‚ö†Ô∏è  Model download failed, will download automatically on first use")
    else:
        print("   '√∫√ñ Real-ESRGAN model already exists")

    return True

def configure_environment():
    """Configure environment variables for ultra performance"""
    print("\n‚öôÔ∏è Configuring Ultra Performance Environment...")

    env_vars = {
        # PyTorch optimizations
        "TORCH_CUDNN_V8_API_ENABLED": "1",
        "CUDA_LAUNCH_BLOCKING": "0",
        "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512,roundup_power2_divisions:16",
        "NVIDIA_TF32_OVERRIDE": "1",

        # ORFEAS optimizations
        "MAX_CONCURRENT_JOBS": "8",
        "GPU_MEMORY_LIMIT": "0.95",
        "BATCH_SIZE": "4",
        "ENABLE_XFORMERS": "1",
        "USE_FLASH_ATTENTION": "1",
        "ULTRA_PERFORMANCE_MODE": "1",

        # Threading optimizations
        "OMP_NUM_THREADS": "16",
        "MKL_NUM_THREADS": "16",
    }

    # Create environment setup script for Windows
    env_script = Path("setup_ultra_env.bat")
    with open(env_script, 'w') as f:
        f.write("@echo off\n")
        f.write("echo Setting up ORFEAS Ultra Performance Environment...\n")
        for key, value in env_vars.items():
            f.write(f"set {key}={value}\n")
        f.write("echo Ultra Performance Environment Configured!\n")
        f.write("echo Starting ORFEAS Ultra Server...\n")
        f.write("C:\\Users\\johng\\anaconda3\\python.exe backend\\ultra_server.py\n")

    # Create PowerShell version
    ps_script = Path("setup_ultra_env.ps1")
    with open(ps_script, 'w') as f:
        f.write("# ORFEAS Ultra Performance Environment Setup\n")
        f.write("Write-Host 'Setting up ORFEAS Ultra Performance Environment...' -ForegroundColor Green\n")
        for key, value in env_vars.items():
            f.write(f"$env:{key}='{value}'\n")
        f.write("Write-Host 'Ultra Performance Environment Configured!' -ForegroundColor Green\n")
        f.write("Write-Host 'Starting ORFEAS Ultra Server...' -ForegroundColor Yellow\n")
        f.write("& 'C:\\Users\\johng\\anaconda3\\python.exe' 'backend\\ultra_server.py'\n")

    print(f"   '√∫√ñ Environment scripts created:")
    print(f"      - {env_script} (Windows Batch)")
    print(f"      - {ps_script} (PowerShell)")

    return True

def verify_installation():
    """Verify ultra performance installation"""
    print("\n'√∫√ñ Verifying Ultra Performance Installation...")

    # Test PyTorch CUDA
    try:
        import torch
        if torch.cuda.is_available():
            print(f"   '√∫√ñ PyTorch CUDA: {torch.version.cuda}")
            print(f"   '√∫√ñ GPU: {torch.cuda.get_device_name(0)}")
            print(f"   '√∫√ñ VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f}GB")
        else:
            print("   '√π√• PyTorch CUDA not available")
            return False
    except ImportError:
        print("   '√π√• PyTorch not installed")
        return False

    # Test xformers
    try:
        import xformers
        print(f"   '√∫√ñ xformers: {xformers.__version__}")
    except ImportError:
        print("   ‚ö†Ô∏è  xformers not available (memory optimizations disabled)")

    # Test Flask
    try:
        import flask
        print(f"   '√∫√ñ Flask: {flask.__version__}")
    except ImportError:
        print("   '√π√• Flask not installed")
        return False

    # Test 3D libraries
    try:
        import trimesh
        import open3d
        print(f"   '√∫√ñ 3D Processing: trimesh {trimesh.__version__}, open3d {open3d.__version__}")
    except ImportError:
        print("   '√π√• 3D processing libraries missing")
        return False

    print("\nÔ£ø√º√∂√Ñ Ultra Performance Installation Complete!")
    print("\nÔ£ø√º√¨√£ Next Steps:")
    print("   1. Run: setup_ultra_env.ps1 (PowerShell)")
    print("   2. Or: setup_ultra_env.bat (Command Prompt)")
    print("   3. Access: http://localhost:5000/studio")
    print("   4. Monitor: http://localhost:5000/api/health")

    return True

def main():
    """Main ultra performance setup"""
    print("Ô£ø√º√∂√Ñ ORFEAS Ultra Performance Setup")
    print("=" * 50)
    print("Optimized for RTX 3090 + i9-9900K + 64GB RAM")
    print("Installing Claude Sonnet 4-level AI capabilities")
    print()

    if not check_system_requirements():
        print("\n'√π√• System requirements not met")
        return False

    steps = [
        ("Installing PyTorch Ultra", install_pytorch_ultra),
        ("Installing AI Dependencies", install_ai_dependencies),
        ("Installing Web Dependencies", install_web_dependencies),
        ("Installing Development Tools", install_development_tools),
        ("Setting up Hunyuan3D Ultra", setup_hunyuan3d_ultra),
        ("Downloading Essential Models", download_essential_models),
        ("Configuring Environment", configure_environment),
        ("Verifying Installation", verify_installation),
    ]

    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if not step_func():
            print(f"\n'√π√• Failed: {step_name}")
            return False

    print("\n" + "="*70)
    print("Ô£ø√º√©√¢ ORFEAS Ultra Performance Setup Complete!")
    print("Ô£ø√º√∂√Ñ Your system is now configured for Claude Sonnet 4-level AI")
    print("Ô£ø√º√≠‚Ñ¢ Ready for ultra-fast 2D'√ú√≠3D conversion")
    print("="*70)

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n‚ö†Ô∏è Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n'√π√• Setup failed with error: {e}")
        sys.exit(1)

"""
ORFEAS Model Downloader
Downloads Hunyuan3D models and sets up proper paths
"""

import os
import sys
from pathlib import Path
import subprocess
import logging
from huggingface_hub import hf_hub_download, login, whoami
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelDownloader:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).parent.parent
        self.models_dir = self.base_dir / "models"
        self.models_dir.mkdir(exist_ok=True)

    def check_hf_auth(self) -> int:
        """Check if user is logged into Hugging Face"""
        try:
            user_info = whoami()
            logger.info(f"[CHECK] Logged into Hugging Face as: {user_info['name']}")
            return True
        except Exception:
            logger.warning("[WARN] Not logged into Hugging Face")
            logger.info("Please run: huggingface-cli login")
            logger.info("Get a free token at: https://huggingface.co/settings/tokens")
            return False

    def download_hunyuan3d_models(self) -> int:
        """Download Hunyuan3D-2 models"""
        logger.info("ðŸ“¥ Downloading Hunyuan3D-2 models...")

        model_repo = "tencent/Hunyuan3D-2"
        local_dir = self.models_dir / "Hunyuan3D-2"

        try:
            # Key model files to download
            files_to_download = [
                "config.json",
                "model.safetensors",
                "tokenizer.json",
                "tokenizer_config.json",
                "special_tokens_map.json",
                "vocab.txt"
            ]

            for filename in files_to_download:
                try:
                    logger.info(f"  Downloading {filename}...")
                    hf_hub_download(
                        repo_id=model_repo,
                        filename=filename,
                        local_dir=str(local_dir),
                        local_dir_use_symlinks=False
                    )
                    logger.info(f"  [CHECK] Downloaded {filename}")
                except Exception as e:
                    logger.warning(f"  [WARN] Failed to download {filename}: {e}")

            logger.info("[CHECK] Hunyuan3D-2 models downloaded")
            return True

        except Exception as e:
            logger.error(f"[FAIL] Failed to download Hunyuan3D models: {e}")
            return False

    def download_hunyuan_dit_models(self) -> int:
        """Download HunyuanDiT text-to-image models"""
        logger.info("ðŸ“¥ Downloading HunyuanDiT models...")

        model_repo = "Tencent-Hunyuan/HunyuanDiT-Diffusers"
        local_dir = self.models_dir / "HunyuanDiT-Diffusers"

        try:
            # Key model files
            files_to_download = [
                "model_index.json",
                "scheduler/scheduler_config.json",
                "text_encoder/config.json",
                "text_encoder/pytorch_model.bin",
                "tokenizer/tokenizer_config.json",
                "unet/config.json",
                "unet/diffusion_pytorch_model.safetensors",
                "vae/config.json",
                "vae/diffusion_pytorch_model.safetensors"
            ]

            for filename in files_to_download:
                try:
                    logger.info(f"  Downloading {filename}...")
                    hf_hub_download(
                        repo_id=model_repo,
                        filename=filename,
                        local_dir=str(local_dir),
                        local_dir_use_symlinks=False
                    )
                    logger.info(f"  [CHECK] Downloaded {filename}")
                except Exception as e:
                    logger.warning(f"  [WARN] Failed to download {filename}: {e}")

            logger.info("[CHECK] HunyuanDiT models downloaded")
            return True

        except Exception as e:
            logger.error(f"[FAIL] Failed to download HunyuanDiT models: {e}")
            return False

    def verify_downloads(self) -> None:
        """Verify that models were downloaded correctly"""
        logger.info("[SEARCH] Verifying model downloads...")

        hunyuan3d_dir = self.models_dir / "Hunyuan3D-2"
        hunyuan_dit_dir = self.models_dir / "HunyuanDiT-Diffusers"

        success = True

        if hunyuan3d_dir.exists():
            model_files = list(hunyuan3d_dir.rglob("*.safetensors")) + list(hunyuan3d_dir.rglob("*.bin"))
            if model_files:
                logger.info(f"  [CHECK] Hunyuan3D models found: {len(model_files)} files")
                total_size = sum(f.stat().st_size for f in model_files) / (1024**3)
                logger.info(f"    Total size: {total_size:.1f} GB")
            else:
                logger.warning("  [WARN] Hunyuan3D models not found")
                success = False
        else:
            logger.warning("  [WARN] Hunyuan3D directory not found")
            success = False

        if hunyuan_dit_dir.exists():
            model_files = list(hunyuan_dit_dir.rglob("*.safetensors")) + list(hunyuan_dit_dir.rglob("*.bin"))
            if model_files:
                logger.info(f"  [CHECK] HunyuanDiT models found: {len(model_files)} files")
                total_size = sum(f.stat().st_size for f in model_files) / (1024**3)
                logger.info(f"    Total size: {total_size:.1f} GB")
            else:
                logger.warning("  [WARN] HunyuanDiT models not found")
                success = False
        else:
            logger.warning("  [WARN] HunyuanDiT directory not found")
            success = False

        return success

    def setup_local_paths(self) -> None:
        """Update integration to use local model paths"""
        logger.info("[CONFIG] Setting up local model paths...")

        config_content = f'''
# ORFEAS Model Configuration
# Auto-generated by model downloader

MODEL_PATHS = {{
    "hunyuan3d": "{self.models_dir / 'Hunyuan3D-2'}",
    "hunyuan_dit": "{self.models_dir / 'HunyuanDiT-Diffusers'}",
}}

# Use local models if available, otherwise download from HuggingFace
USE_LOCAL_MODELS = True
'''

        config_file = Path(__file__).parent / "model_config.py"
        with open(config_file, 'w') as f:
            f.write(config_content)

        logger.info(f"  [CHECK] Model configuration saved to {config_file}")

def main() -> int:
    print("[LAUNCH] ORFEAS Model Downloader")
    print("=" * 50)

    downloader = ModelDownloader()

    # Check authentication
    if not downloader.check_hf_auth():
        print("\n[FAIL] Please login to Hugging Face first:")
        print("   huggingface-cli login")
        return False

    print(f"\n[FOLDER] Models will be saved to: {downloader.models_dir}")

    # Download models
    success = True

    if input("\nDownload Hunyuan3D-2 models? (~15GB) [y/N]: ").lower().startswith('y'):
        success &= downloader.download_hunyuan3d_models()

    if input("\nDownload HunyuanDiT models? (~5GB) [y/N]: ").lower().startswith('y'):
        success &= downloader.download_hunyuan_dit_models()

    # Verify and setup
    if success:
        downloader.verify_downloads()
        downloader.setup_local_paths()

        print("\nðŸŽ‰ Model download complete!")
        print("\nNext steps:")
        print("1. Restart the ORFEAS server: python integrated_server.py")
        print("2. Check API status: http://localhost:5000/api/models-info")
        print("3. Test AI generation in Studio: http://localhost:5000/studio")
    else:
        print("\n[WARN] Some downloads may have failed. Check the logs above.")

    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[PAUSE] Download cancelled by user")
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()

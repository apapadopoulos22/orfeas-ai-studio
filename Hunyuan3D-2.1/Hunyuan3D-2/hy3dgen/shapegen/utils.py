# Hunyuan 3D is licensed under the TENCENT HUNYUAN NON-COMMERCIAL LICENSE AGREEMENT
# except for the third-party components listed below.
# Hunyuan 3D does not impose any additional limitations beyond what is outlined
# in the repsective licenses of these third-party components.
# Users must comply with all terms and conditions of original licenses of these third-party
# components and must ensure that the usage of the third party components adheres to
# all relevant laws and regulations.

# For avoidance of doubts, Hunyuan 3D means the large language models and
# their software and algorithms, including trained model weights, parameters (including
# optimizer states), machine-learning model code, inference-enabling code, training-enabling code,
# fine-tuning enabling code and other elements of the foregoing made publicly available
# by Tencent in accordance with TENCENT HUNYUAN COMMUNITY LICENSE AGREEMENT.

import logging
import os
from functools import wraps

import torch


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


logger = get_logger('hy3dgen.shapgen')


class synchronize_timer:
    """ Synchronized timer to count the inference time of `nn.Module.forward`.

        Supports both context manager and decorator usage.

        Example as context manager:
        ```python
        with synchronize_timer('name') as t:
            run()
        ```

        Example as decorator:
        ```python
        @synchronize_timer('Export to trimesh')
        def export_to_trimesh(mesh_output):
            pass
        ```
    """

    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        """Context manager entry: start timing."""
        if os.environ.get('HY3DGEN_DEBUG', '0') == '1':
            self.start = torch.cuda.Event(enable_timing=True)
            self.end = torch.cuda.Event(enable_timing=True)
            self.start.record()
            return lambda: self.time

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Context manager exit: stop timing and log results."""
        if os.environ.get('HY3DGEN_DEBUG', '0') == '1':
            self.end.record()
            torch.cuda.synchronize()
            self.time = self.start.elapsed_time(self.end)
            if self.name is not None:
                logger.info(f'{self.name} takes {self.time} ms')

    def __call__(self, func):
        """Decorator: wrap the function to time its execution."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                result = func(*args, **kwargs)
            return result

        return wrapper


def smart_load_model(
    model_path,
    subfolder,
    use_safetensors,
    variant,
):
    original_model_path = model_path
    # try local path
    # [ORFEAS FIX] Use explicit path with backslashes instead of ~/. cache to prevent mixed separators on Windows
    home_dir = os.path.expanduser('~')
    hy3dgen_default = os.path.join(home_dir, '.cache', 'hy3dgen')  # Properly expand with backslashes
    base_dir = os.environ.get('HY3DGEN_MODELS', hy3dgen_default)

    # Convert repo_id format (tencent/Hunyuan3D-2) to HuggingFace cache format (models--tencent--Hunyuan3D-2)
    # This is the format HuggingFace hub uses when caching models
    model_repo_cache_name = f'models--{model_path.replace("/", "--")}'

    # First, try to find model in HuggingFace hub cache if base_dir points to hub
    if 'hub' in base_dir:
        # Looking in HuggingFace hub directory - need to find the snapshot
        repo_cache_dir = os.path.join(base_dir, model_repo_cache_name, 'snapshots')
        if os.path.exists(repo_cache_dir):
            # Find the first (and usually only) snapshot directory
            snapshots = os.listdir(repo_cache_dir)
            if snapshots:
                snapshot_dir = os.path.join(repo_cache_dir, snapshots[0])
                model_path_check = os.path.join(snapshot_dir, subfolder)
            else:
                model_path_check = None
        else:
            model_path_check = None
    else:
        # Looking in old-style hy3dgen cache directory
        # Convert forward slashes in model_path to backslashes for Windows compatibility
        model_path_normalized = model_path.replace('/', os.sep)
        subfolder_normalized = subfolder.replace('/', os.sep) if subfolder else ''
        model_path_check = os.path.join(base_dir, model_path_normalized, subfolder_normalized)

    logger.info(f'Try to load model from local path: {model_path_check if model_path_check else "not found"}')
    if not model_path_check or not os.path.exists(model_path_check):
        logger.info('Model path not exists, try to download from huggingface')
        try:
            from huggingface_hub import snapshot_download
            #
            path = snapshot_download(
                repo_id=original_model_path,
                allow_patterns=[f"{subfolder}/*"],  # :
            )
            model_path = os.path.join(path, subfolder)  #
        except ImportError:
            logger.warning(
                "You need to install HuggingFace Hub to load models from the hub."
            )
            raise RuntimeError(f"Model path {model_path_check} not found")
        except Exception as e:
            raise e
    else:
        model_path = model_path_check

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model path {original_model_path} not found")

    extension = 'ckpt' if not use_safetensors else 'safetensors'
    variant = '' if variant is None else f'.{variant}'
    ckpt_name = f'model{variant}.{extension}'
    config_path = os.path.join(model_path, 'config.yaml')
    ckpt_path = os.path.join(model_path, ckpt_name)
    return config_path, ckpt_path

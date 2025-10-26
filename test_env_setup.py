from dotenv import load_dotenv
import os

load_dotenv()
hy3dgen_models = os.environ.get('HY3DGEN_MODELS')
print('HY3DGEN_MODELS from os.environ:', hy3dgen_models)

# Now check what the code would see
home_dir = os.path.expanduser('~')
hy3dgen_default = os.path.join(home_dir, '.cache', 'hy3dgen')
base_dir = os.environ.get('HY3DGEN_MODELS', hy3dgen_default)
print('base_dir that would be used:', base_dir)

# Test the actual path that would be formed
model_path = 'tencent/Hunyuan3D-2'
subfolder = 'hunyuan3d-dit-v2-0'

# This is what hy3dgen does - it converts repo ID to HuggingFace cache format
# tencent/Hunyuan3D-2 → models--tencent--Hunyuan3D-2
model_path_for_cache = model_path.replace('/', '--')
print(f'\nModel path will be converted from "{model_path}" to "{model_path_for_cache}"')

# The actual check would look in HF_HOME/hub/models--tencent--Hunyuan3D-2/snapshots/{hash}/hunyuan3d-dit-v2-0/
# But since we don't know the snapshot hash, we'll just check if the repo directory exists
repo_dir = os.path.join(base_dir, f'models--{model_path_for_cache}')
print(f'Repository directory: {repo_dir}')
print(f'Does repo directory exist? {os.path.exists(repo_dir)}')

# List what's actually in there
if os.path.exists(repo_dir):
    print(f'\nContents of {repo_dir}:')
    for item in os.listdir(repo_dir):
        print(f'  - {item}')
        if item == 'snapshots':
            snapshots_dir = os.path.join(repo_dir, item)
            for snapshot in os.listdir(snapshots_dir):
                print(f'    - {snapshot}')
                snapshot_path = os.path.join(snapshots_dir, snapshot)
                for model_file in os.listdir(snapshot_path):
                    print(f'      - {model_file}')


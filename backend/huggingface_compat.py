"""
[ORFEAS] ORFEAS CRITICAL FIX: HuggingFace Compatibility Layer
==========================================================
Fixes the cached_download import issue for newer huggingface_hub versions

PROBLEM: Older diffusers package tries to import cached_download from huggingface_hub
         but newer huggingface_hub (>= 0.20.0) removed this function

SOLUTION: Monkey-patch cached_download back into huggingface_hub module
          before any imports of diffusers or transformers happen

This MUST be imported FIRST before any HuggingFace library imports!
"""

import sys

# ============================================================================
# CRITICAL: Apply patch BEFORE importing any HuggingFace libraries
# ============================================================================

def apply_huggingface_compatibility():
    """Apply compatibility patches to huggingface_hub"""
    try:
        from huggingface_hub import hf_hub_download
        import huggingface_hub

        # Create compatibility wrapper
        def cached_download(*args, **kwargs):
            """
            Compatibility wrapper for deprecated cached_download function
            Maps old API to new hf_hub_download API

            Old signature: cached_download(url, library_name=None, library_version=None, ...)
            New signature: hf_hub_download(repo_id, filename, ...)
            """
            # Handle both old and new API calls
            if len(args) > 0 and isinstance(args[0], str):
                # If first arg looks like a URL, it's old API
                if 'http' in args[0]:
                    # Extract repo_id and filename from URL
                    # Example: https://huggingface.co/tencent/Hunyuan3D-2/resolve/main/model.safetensors
                    url = args[0]
                    if '/resolve/main/' in url:
                        parts = url.split('/resolve/main/')
                        repo_id = parts[0].split('huggingface.co/')[-1]
                        filename = parts[1]
                        return hf_hub_download(repo_id=repo_id, filename=filename, **kwargs)

            # Otherwise, assume it's already new API format
            return hf_hub_download(*args, **kwargs)

        # Monkey patch the module
        huggingface_hub.cached_download = cached_download

        # Add to __all__ if it exists
        if hasattr(huggingface_hub, '__all__'):
            if 'cached_download' not in huggingface_hub.__all__:
                huggingface_hub.__all__.append('cached_download')

        # Also patch file_download module directly (where diffusers imports from)
        try:
            import huggingface_hub.file_download as file_download
            file_download.cached_download = cached_download
            print("[OK] HuggingFace compatibility layer applied to file_download module")
        except:
            pass

        print("[OK] HuggingFace compatibility layer applied: cached_download -> hf_hub_download")
        return True

    except Exception as e:
        print(f"[WARNING] Failed to apply HuggingFace compatibility layer: {e}")
        return False

# Apply patches immediately on import
apply_huggingface_compatibility()

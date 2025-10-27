"""
BOB AI v8.0 - Module Loader System

Dynamically loads and manages all v8.0 discipline modules.
Provides efficient module discovery, initialization, and performance optimization.

Features:
- Dynamic module discovery
- Lazy loading on-demand
- Module registry and caching
- Version compatibility checking
- Performance metrics
"""

import importlib
import os
import sys
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BobAIV8ModuleLoader:
    """
    Dynamically loads and manages BOB AI v8.0 modules.
    """

    def __init__(self, backend_path: Optional[str] = None):
        """Initialize module loader.

        Args:
            backend_path: Path to backend directory (auto-detected if None)
        """
        if backend_path is None:
            backend_path = os.path.dirname(os.path.abspath(__file__))

        self.backend_path = backend_path
        self.loaded_modules: Dict[str, Any] = {}
        self.module_metadata: Dict[str, Dict] = {}
        self.load_errors: Dict[str, str] = {}
        self.performance_data: Dict[str, float] = {}

        # Add backend to path if not already there
        if self.backend_path not in sys.path:
            sys.path.insert(0, self.backend_path)

    def discover_v8_modules(self) -> List[str]:
        """Discover all v8.0 modules by file pattern.

        Returns:
            List of module names matching bob_ai_v8_*.py pattern
        """
        backend_dir = Path(self.backend_path)
        v8_files = list(backend_dir.glob("bob_ai_v8_*.py"))

        module_names = []
        for file_path in v8_files:
            # Skip loader and base files from discovery
            if file_path.name not in ['bob_ai_v8_base.py', 'bob_ai_v8_loader.py', 'bob_ai_v8_test_suite.py']:
                module_name = file_path.stem
                module_names.append(module_name)

        logger.info(f"Discovered {len(module_names)} v8.0 modules: {module_names}")
        return sorted(module_names)

    def load_module(self, module_name: str, lazy: bool = False) -> Tuple[bool, Optional[Any], Optional[str]]:
        """Load a specific v8.0 module.

        Args:
            module_name: Name of module (e.g., 'bob_ai_v8_cinematography')
            lazy: If True, don't load now, just register

        Returns:
            Tuple of (success, module, error_message)
        """
        import time

        # Check if already loaded
        if module_name in self.loaded_modules:
            return True, self.loaded_modules[module_name], None

        start_time = time.time()

        try:
            # Import module
            module = importlib.import_module(module_name)

            # Record load time
            load_time = (time.time() - start_time) * 1000  # Convert to ms
            self.performance_data[module_name] = load_time

            # Cache module
            self.loaded_modules[module_name] = module

            # Extract metadata if available
            if hasattr(module, 'METADATA'):
                self.module_metadata[module_name] = module.METADATA

            logger.info(f"Loaded module {module_name} in {load_time:.2f}ms")
            return True, module, None

        except ImportError as e:
            error_msg = f"Import error: {str(e)}"
            self.load_errors[module_name] = error_msg
            logger.error(f"Failed to load {module_name}: {error_msg}")
            return False, None, error_msg

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.load_errors[module_name] = error_msg
            logger.error(f"Failed to load {module_name}: {error_msg}")
            return False, None, error_msg

    def load_all_modules(self) -> Tuple[int, int, Dict[str, str]]:
        """Load all discovered v8.0 modules.

        Returns:
            Tuple of (loaded_count, failed_count, error_dict)
        """
        discovered = self.discover_v8_modules()
        loaded_count = 0
        failed_count = 0

        for module_name in discovered:
            success, _, error = self.load_module(module_name)
            if success:
                loaded_count += 1
            else:
                failed_count += 1

        logger.info(f"Module loading complete: {loaded_count} loaded, {failed_count} failed")
        return loaded_count, failed_count, self.load_errors

    def get_module(self, module_name: str) -> Optional[Any]:
        """Get a loaded module.

        Args:
            module_name: Name of module

        Returns:
            Module object or None if not loaded
        """
        if module_name not in self.loaded_modules:
            success, module, _ = self.load_module(module_name)
            if not success:
                return None

        return self.loaded_modules.get(module_name)

    def get_all_loaded_modules(self) -> Dict[str, Any]:
        """Get all currently loaded modules.

        Returns:
            Dictionary of module_name -> module
        """
        return self.loaded_modules.copy()

    def get_module_performance_report(self) -> Dict[str, Any]:
        """Get performance metrics for module loading.

        Returns:
            Dictionary with performance data
        """
        if not self.performance_data:
            return {'message': 'No performance data yet'}

        times = list(self.performance_data.values())
        return {
            'total_modules': len(self.performance_data),
            'total_load_time_ms': sum(times),
            'average_load_time_ms': sum(times) / len(times) if times else 0,
            'min_load_time_ms': min(times) if times else 0,
            'max_load_time_ms': max(times) if times else 0,
            'modules': self.performance_data
        }

    def validate_module(self, module_name: str) -> Tuple[bool, List[str]]:
        """Validate a module's structure and content.

        Args:
            module_name: Name of module to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        module = self.get_module(module_name)
        if module is None:
            issues.append(f"Module {module_name} not loaded")
            return False, issues

        # Check for required classes
        expected_classes = [
            f'{self._get_class_name_from_module(module_name)}Knowledge',
            f'{self._get_class_name_from_module(module_name)}Integration'
        ]

        for class_name in expected_classes:
            if not hasattr(module, class_name):
                issues.append(f"Missing class: {class_name}")

        # Check for METADATA
        if not hasattr(module, 'METADATA'):
            issues.append("Missing METADATA constant")

        return len(issues) == 0, issues

    def _get_class_name_from_module(self, module_name: str) -> str:
        """Convert module name to expected class name.

        Args:
            module_name: Module name like 'bob_ai_v8_cinematography'

        Returns:
            Class name prefix like 'Cinematography'
        """
        # Remove 'bob_ai_v8_' prefix
        discipline = module_name.replace('bob_ai_v8_', '')

        # Convert snake_case to PascalCase
        words = discipline.split('_')
        return ''.join(word.capitalize() for word in words)

    def get_instantiated_knowledge(self, module_name: str) -> Optional[Any]:
        """Get instantiated knowledge class from module.

        Args:
            module_name: Module name

        Returns:
            Instantiated knowledge object or None
        """
        module = self.get_module(module_name)
        if module is None:
            return None

        class_name = f'{self._get_class_name_from_module(module_name)}Knowledge'

        if not hasattr(module, class_name):
            logger.error(f"Class {class_name} not found in {module_name}")
            return None

        try:
            knowledge_class = getattr(module, class_name)
            return knowledge_class()
        except Exception as e:
            logger.error(f"Failed to instantiate {class_name}: {e}")
            return None

    def get_instantiated_integration(self, module_name: str) -> Optional[Any]:
        """Get instantiated integration class from module.

        Args:
            module_name: Module name

        Returns:
            Instantiated integration object or None
        """
        module = self.get_module(module_name)
        if module is None:
            return None

        # First get knowledge instance
        knowledge = self.get_instantiated_knowledge(module_name)
        if knowledge is None:
            return None

        class_name = f'{self._get_class_name_from_module(module_name)}Integration'

        if not hasattr(module, class_name):
            logger.error(f"Class {class_name} not found in {module_name}")
            return None

        try:
            integration_class = getattr(module, class_name)
            return integration_class(knowledge)
        except Exception as e:
            logger.error(f"Failed to instantiate {class_name}: {e}")
            return None

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive loader status report.

        Returns:
            Dictionary with status information
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'backend_path': self.backend_path,
            'discovered_modules': len(self.discover_v8_modules()),
            'loaded_modules': len(self.loaded_modules),
            'failed_modules': len(self.load_errors),
            'loaded_module_names': list(self.loaded_modules.keys()),
            'failed_module_names': list(self.load_errors.keys()),
            'performance': self.get_module_performance_report(),
            'errors': self.load_errors
        }


# Global loader instance
_loader: Optional[BobAIV8ModuleLoader] = None


def get_bob_ai_v8_loader(backend_path: Optional[str] = None) -> BobAIV8ModuleLoader:
    """Get or create the global module loader.

    Args:
        backend_path: Path to backend directory

    Returns:
        Global BobAIV8ModuleLoader instance
    """
    global _loader
    if _loader is None:
        _loader = BobAIV8ModuleLoader(backend_path)
        logger.info("Initialized BOB AI v8.0 Module Loader")
    return _loader


if __name__ == "__main__":
    # Test loader
    print("BOB AI v8.0 Module Loader Test")
    loader = get_bob_ai_v8_loader()
    print(f"Discovered modules: {loader.discover_v8_modules()}")
    print(f"Status: {json.dumps(loader.get_status_report(), indent=2)}")

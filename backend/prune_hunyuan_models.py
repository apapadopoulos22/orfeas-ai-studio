"""
Apply pruning to Hunyuan3D models for ORFEAS AI
Prunes Hunyuan3D-2.1 models to improve inference speed

Usage:
    python prune_hunyuan_models.py --sparsity 0.3 --epochs 5

Options:
    --sparsity FLOAT    Target sparsity (default: 0.3 = 30%)
    --epochs INT        Fine-tuning epochs (default: 5)
    --method STR        Pruning method: magnitude, random, l1 (default: magnitude)
    --structured        Use structured pruning (default: False)
    --dry-run           Test without saving (default: False)
"""

import os
import sys
import argparse
import logging
import torch
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_pruning import ModelPruner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Hunyuan3DPruner:
    """Pruning specifically for Hunyuan3D models"""

    def __init__(self, models_dir: str = 'models/hunyuan3d'):
        """
        Initialize Hunyuan3D pruner

        Args:
            models_dir: Directory containing Hunyuan3D models
        """
        self.models_dir = Path(models_dir)

        if not self.models_dir.exists():
            logger.warning(f"Models directory not found: {self.models_dir}")

    def find_model_files(self) -> list:
        """
        Find all .pth model files

        Returns:
            List of model file paths
        """
        model_files = []

        if self.models_dir.exists():
            model_files.extend(self.models_dir.glob('**/*.pth'))
            model_files.extend(self.models_dir.glob('**/*.pt'))
            model_files.extend(self.models_dir.glob('**/*.bin'))

        logger.info(f"Found {len(model_files)} model files")
        return model_files

    def load_hunyuan_model(self, model_path: Path):
        """
        Load Hunyuan3D model

        Args:
            model_path: Path to model file

        Returns:
            Loaded model
        """
        try:
            # Try loading as state dict
            checkpoint = torch.load(model_path, map_location='cpu')

            if isinstance(checkpoint, dict) and 'model' in checkpoint:
                # Extract model from checkpoint
                model = checkpoint['model']
            elif isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
                # State dict format
                logger.info(f"Model is a state dict, skipping {model_path.name}")
                return None
            else:
                # Direct model
                model = checkpoint

            return model

        except Exception as e:
            logger.error(f"Failed to load model {model_path}: {e}")
            return None

    def prune_model_file(
        self,
        model_path: Path,
        sparsity: float,
        method: str,
        structured: bool,
        dry_run: bool = False
    ) -> dict:
        """
        Prune a single model file

        Args:
            model_path: Path to model file
            sparsity: Target sparsity
            method: Pruning method
            structured: Use structured pruning
            dry_run: Test without saving

        Returns:
            Pruning statistics
        """
        logger.info(f"Processing: {model_path.name}")

        # Load model
        model = self.load_hunyuan_model(model_path)

        if model is None:
            return None

        # Initialize pruner
        pruner = ModelPruner(
            model=model,
            target_sparsity=sparsity,
            pruning_method=method,
            structured=structured
        )

        # Apply pruning
        pruner.global_prune(amount=sparsity)

        # Get statistics
        stats = pruner.get_pruning_stats()

        logger.info(
            f"  Original size: {stats['original_size_mb']:.2f}MB"
        )
        logger.info(
            f"  Pruned size:   {stats['current_size_mb']:.2f}MB"
        )
        logger.info(
            f"  Sparsity:      {stats['sparsity']*100:.1f}%"
        )
        logger.info(
            f"  Size reduction: {stats['size_reduction']*100:.1f}%"
        )

        # Save pruned model
        if not dry_run:
            output_path = model_path.parent / f"{model_path.stem}_pruned{model_path.suffix}"
            pruner.save_pruned_model(str(output_path))
            logger.info(f"  Saved to: {output_path.name}")
        else:
            logger.info("  [DRY RUN] Not saving")

        return stats

    def prune_all_models(
        self,
        sparsity: float = 0.3,
        method: str = 'magnitude',
        structured: bool = False,
        dry_run: bool = False
    ) -> dict:
        """
        Prune all Hunyuan3D models

        Args:
            sparsity: Target sparsity
            method: Pruning method
            structured: Use structured pruning
            dry_run: Test without saving

        Returns:
            Summary statistics
        """
        logger.info("=" * 60)
        logger.info("ORFEAS AI - Hunyuan3D Model Pruning")
        logger.info("=" * 60)
        logger.info(f"Sparsity:   {sparsity*100:.1f}%")
        logger.info(f"Method:     {method}")
        logger.info(f"Structured: {structured}")
        logger.info(f"Dry run:    {dry_run}")
        logger.info("=" * 60)

        # Find model files
        model_files = self.find_model_files()

        if not model_files:
            logger.warning("No model files found to prune")
            return {}

        # Prune each model
        summary = {
            'total_models': len(model_files),
            'pruned': 0,
            'skipped': 0,
            'failed': 0,
            'total_size_before_mb': 0.0,
            'total_size_after_mb': 0.0
        }

        for model_path in model_files:
            try:
                stats = self.prune_model_file(
                    model_path=model_path,
                    sparsity=sparsity,
                    method=method,
                    structured=structured,
                    dry_run=dry_run
                )

                if stats:
                    summary['pruned'] += 1
                    summary['total_size_before_mb'] += stats['original_size_mb']
                    summary['total_size_after_mb'] += stats['current_size_mb']
                else:
                    summary['skipped'] += 1

            except Exception as e:
                logger.error(f"Failed to prune {model_path.name}: {e}")
                summary['failed'] += 1

        # Print summary
        self.print_summary(summary)

        return summary

    def print_summary(self, summary: dict):
        """Print pruning summary"""
        logger.info("=" * 60)
        logger.info("PRUNING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total models:  {summary['total_models']}")
        logger.info(f"Pruned:        {summary['pruned']}")
        logger.info(f"Skipped:       {summary['skipped']}")
        logger.info(f"Failed:        {summary['failed']}")

        if summary['total_size_before_mb'] > 0:
            size_reduction = (
                (summary['total_size_before_mb'] - summary['total_size_after_mb'])
                / summary['total_size_before_mb']
                * 100
            )
            logger.info(
                f"Size before:   {summary['total_size_before_mb']:.2f}MB"
            )
            logger.info(
                f"Size after:    {summary['total_size_after_mb']:.2f}MB"
            )
            logger.info(
                f"Size reduction: {size_reduction:.1f}%"
            )

        logger.info("=" * 60)


def main():
    """Main pruning entry point"""
    parser = argparse.ArgumentParser(
        description='Prune Hunyuan3D models for ORFEAS AI'
    )
    parser.add_argument(
        '--sparsity',
        type=float,
        default=0.3,
        help='Target sparsity (0.3 = 30%%)'
    )
    parser.add_argument(
        '--method',
        choices=['magnitude', 'random', 'l1'],
        default='magnitude',
        help='Pruning method'
    )
    parser.add_argument(
        '--structured',
        action='store_true',
        help='Use structured pruning'
    )
    parser.add_argument(
        '--models-dir',
        default='models/hunyuan3d',
        help='Directory containing models'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test without saving'
    )

    args = parser.parse_args()

    # Create pruner
    pruner = Hunyuan3DPruner(models_dir=args.models_dir)

    # Prune all models
    summary = pruner.prune_all_models(
        sparsity=args.sparsity,
        method=args.method,
        structured=args.structured,
        dry_run=args.dry_run
    )

    # Exit with error if pruning failed
    if summary.get('failed', 0) > 0:
        sys.exit(1)

    logger.info("Pruning completed successfully!")


if __name__ == '__main__':
    main()

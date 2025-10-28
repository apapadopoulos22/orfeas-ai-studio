"""
Model Versioning & Management System
Module: model_versioning.py

Purpose: Manage model versions, rollbacks, and version comparisons.

Features:
  - Version control for ensemble models
  - Rollback capability
  - Version comparison
  - Version metadata tracking
  - Production version management

Author: ORFEAS AI Studio - Phase 2 Task 1
Date: October 28, 2025
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import shutil
from enum import Enum

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class VersionStatus(Enum):
    """Status of a model version."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


@dataclass
class VersionMetadata:
    """Metadata for a model version."""

    version_id: str
    model_name: str
    created_at: str
    created_by: str
    status: str  # VersionStatus enum as string
    accuracy: float
    cross_val_score: float
    description: str
    parent_version: Optional[str] = None
    is_production: bool = False
    deployment_date: Optional[str] = None
    rollback_available: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ModelVersionManager:
    """Manages model versions, storage, and rollbacks."""

    def __init__(self, base_dir: str = "./models/versions"):
        """Initialize version manager."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.base_dir / "versions_metadata.json"
        self.versions: Dict[str, VersionMetadata] = {}
        self.production_version: Optional[str] = None

        self._load_metadata()
        logger.info(f"✅ Model Version Manager initialized: {base_dir}")

    def _load_metadata(self) -> None:
        """Load version metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    self.versions = {
                        v_id: VersionMetadata(**v_data)
                        for v_id, v_data in data.get('versions', {}).items()
                    }
                    self.production_version = data.get('production_version')
                logger.info(f"✅ Loaded {len(self.versions)} versions from metadata")
            except Exception as e:
                logger.error(f"❌ Failed to load metadata: {e}")
        else:
            logger.info("📝 No existing metadata found, starting fresh")

    def _save_metadata(self) -> None:
        """Save version metadata to disk."""
        data = {
            'versions': {
                v_id: v.to_dict()
                for v_id, v in self.versions.items()
            },
            'production_version': self.production_version,
            'last_updated': datetime.now().isoformat(),
        }

        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info("✅ Metadata saved")

    def create_version(
        self,
        model_name: str,
        accuracy: float,
        cross_val_score: float,
        description: str,
        created_by: str = "system",
        parent_version: Optional[str] = None,
    ) -> str:
        """
        Create a new model version.

        Args:
            model_name: Name of the model
            accuracy: Model accuracy score
            cross_val_score: Cross-validation score
            description: Version description
            created_by: Who created this version
            parent_version: Parent version ID

        Returns:
            Version ID
        """
        # Generate version ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_id = f"{model_name}_{timestamp}"

        # Create version metadata
        metadata = VersionMetadata(
            version_id=version_id,
            model_name=model_name,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            status=VersionStatus.DEVELOPMENT.value,
            accuracy=accuracy,
            cross_val_score=cross_val_score,
            description=description,
            parent_version=parent_version,
        )

        # Store version
        self.versions[version_id] = metadata
        self._save_metadata()

        logger.info(f"✅ Version created: {version_id} (accuracy: {accuracy:.4f})")
        return version_id

    def promote_version(
        self,
        version_id: str,
        new_status: VersionStatus,
    ) -> bool:
        """
        Promote version to new status.

        Args:
            version_id: Version to promote
            new_status: New status

        Returns:
            Success flag
        """
        if version_id not in self.versions:
            logger.error(f"❌ Version not found: {version_id}")
            return False

        old_status = self.versions[version_id].status
        self.versions[version_id].status = new_status.value
        self._save_metadata()

        logger.info(
            f"✅ Version promoted: {version_id} "
            f"({old_status} → {new_status.value})"
        )
        return True

    def deploy_to_production(self, version_id: str) -> bool:
        """
        Deploy version to production.

        Args:
            version_id: Version to deploy

        Returns:
            Success flag
        """
        if version_id not in self.versions:
            logger.error(f"❌ Version not found: {version_id}")
            return False

        # Update previous production version
        if self.production_version:
            prev_metadata = self.versions[self.production_version]
            prev_metadata.is_production = False
            prev_metadata.status = VersionStatus.ARCHIVED.value
            logger.info(
                f"📊 Archived previous production version: "
                f"{self.production_version}"
            )

        # Set new production version
        self.production_version = version_id
        metadata = self.versions[version_id]
        metadata.is_production = True
        metadata.status = VersionStatus.PRODUCTION.value
        metadata.deployment_date = datetime.now().isoformat()

        self._save_metadata()
        logger.info(f"✅ Deployed to production: {version_id}")

        return True

    def rollback_to_version(self, version_id: str) -> bool:
        """
        Rollback to a previous version.

        Args:
            version_id: Version to rollback to

        Returns:
            Success flag
        """
        if version_id not in self.versions:
            logger.error(f"❌ Version not found: {version_id}")
            return False

        metadata = self.versions[version_id]
        if not metadata.rollback_available:
            logger.error(
                f"❌ Rollback not available for version: {version_id}"
            )
            return False

        # Mark current production as archived
        if self.production_version:
            self.versions[self.production_version].is_production = False
            self.versions[self.production_version].status = (
                VersionStatus.ARCHIVED.value
            )

        # Activate rollback version
        self.production_version = version_id
        metadata.is_production = True
        metadata.status = VersionStatus.PRODUCTION.value
        metadata.deployment_date = datetime.now().isoformat()

        self._save_metadata()
        logger.warning(f"⚠️ Rolled back to version: {version_id}")

        return True

    def get_version_info(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific version."""
        if version_id not in self.versions:
            return None

        metadata = self.versions[version_id]
        return metadata.to_dict()

    def get_all_versions(
        self,
        model_name: Optional[str] = None,
        status: Optional[VersionStatus] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all versions matching criteria.

        Args:
            model_name: Filter by model name
            status: Filter by status

        Returns:
            List of version metadata
        """
        versions = list(self.versions.values())

        if model_name:
            versions = [v for v in versions if v.model_name == model_name]

        if status:
            versions = [v for v in versions if v.status == status.value]

        return [v.to_dict() for v in versions]

    def get_production_version(self) -> Optional[Dict[str, Any]]:
        """Get current production version."""
        if not self.production_version:
            return None

        return self.get_version_info(self.production_version)

    def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Compare two versions.

        Args:
            version_id_1: First version
            version_id_2: Second version

        Returns:
            Comparison data
        """
        v1 = self.get_version_info(version_id_1)
        v2 = self.get_version_info(version_id_2)

        if not v1 or not v2:
            return None

        accuracy_diff = v2['accuracy'] - v1['accuracy']
        cv_diff = v2['cross_val_score'] - v1['cross_val_score']

        return {
            'version_1': v1,
            'version_2': v2,
            'accuracy_improvement': accuracy_diff,
            'cv_improvement': cv_diff,
            'version_2_better': accuracy_diff > 0,
            'comparison_timestamp': datetime.now().isoformat(),
        }

    def get_version_history(
        self,
        model_name: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get version history.

        Args:
            model_name: Filter by model name
            limit: Maximum number of versions

        Returns:
            List of versions sorted by creation date
        """
        versions = self.get_all_versions(model_name)

        # Sort by creation date (newest first)
        versions = sorted(
            versions,
            key=lambda v: v['created_at'],
            reverse=True
        )

        return versions[:limit]

    def archive_version(self, version_id: str) -> bool:
        """Archive a version."""
        if version_id not in self.versions:
            logger.error(f"❌ Version not found: {version_id}")
            return False

        self.versions[version_id].status = VersionStatus.ARCHIVED.value
        self._save_metadata()

        logger.info(f"📦 Archived version: {version_id}")
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get version statistics."""
        total = len(self.versions)
        by_status = {}

        for version in self.versions.values():
            status = version.status
            by_status[status] = by_status.get(status, 0) + 1

        models = set(v.model_name for v in self.versions.values())

        # Calculate average accuracy
        avg_accuracy = (
            sum(v.accuracy for v in self.versions.values()) / total
            if total > 0 else 0
        )

        return {
            'total_versions': total,
            'unique_models': len(models),
            'production_version': self.production_version,
            'by_status': by_status,
            'average_accuracy': round(avg_accuracy, 4),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get version manager summary."""
        return {
            'base_directory': str(self.base_dir),
            'metadata_file': str(self.metadata_file),
            'total_versions': len(self.versions),
            'production_version': self.production_version,
            'statistics': self.get_statistics(),
        }


# Singleton instance
_version_manager: Optional[ModelVersionManager] = None


def get_version_manager(base_dir: str = "./models/versions") -> ModelVersionManager:
    """Get or create version manager singleton."""
    global _version_manager
    if _version_manager is None:
        _version_manager = ModelVersionManager(base_dir)
    return _version_manager


if __name__ == "__main__":
    # Example usage and testing
    logger.info("=" * 70)
    logger.info("MODEL VERSIONING SYSTEM - DEMO")
    logger.info("=" * 70)

    # Create manager
    logger.info("\n📝 Creating version manager...")
    manager = get_version_manager("./test_models/versions")

    # Create versions
    logger.info("\n🆕 Creating versions...")
    v1_id = manager.create_version(
        model_name="iris_classifier",
        accuracy=0.95,
        cross_val_score=0.94,
        description="Initial ensemble model",
        created_by="demo_user",
    )

    v2_id = manager.create_version(
        model_name="iris_classifier",
        accuracy=0.96,
        cross_val_score=0.955,
        description="Improved with better hyperparameters",
        created_by="demo_user",
        parent_version=v1_id,
    )

    v3_id = manager.create_version(
        model_name="iris_classifier",
        accuracy=0.965,
        cross_val_score=0.96,
        description="Further optimized with more data",
        created_by="demo_user",
        parent_version=v2_id,
    )

    # Promote versions
    logger.info("\n⬆️ Promoting versions...")
    manager.promote_version(v3_id, VersionStatus.TESTING)
    manager.promote_version(v3_id, VersionStatus.STAGING)
    manager.promote_version(v3_id, VersionStatus.PRODUCTION)

    # Deploy to production
    logger.info("\n🚀 Deploying to production...")
    manager.deploy_to_production(v3_id)

    # Get production version
    logger.info("\n📊 Current production version:")
    prod_version = manager.get_production_version()
    for key, value in prod_version.items():
        logger.info(f"  {key}: {value}")

    # Compare versions
    logger.info(f"\n🔍 Comparing {v1_id} vs {v3_id}...")
    comparison = manager.compare_versions(v1_id, v3_id)
    logger.info(f"  Accuracy improvement: {comparison['accuracy_improvement']:.4f}")
    logger.info(f"  CV improvement: {comparison['cv_improvement']:.4f}")
    logger.info(f"  v3 better: {comparison['version_2_better']}")

    # Get version history
    logger.info("\n📜 Version history (most recent first):")
    history = manager.get_version_history("iris_classifier")
    for i, v in enumerate(history, 1):
        logger.info(f"  {i}. {v['version_id']}: {v['status']} "
                    f"(accuracy: {v['accuracy']:.4f})")

    # Statistics
    logger.info("\n📈 Version statistics:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")

    # Rollback
    logger.info(f"\n⏮️ Rolling back to {v2_id}...")
    manager.rollback_to_version(v2_id)

    logger.info(f"\n📊 New production version: {manager.production_version}")

    # Summary
    logger.info("\n📋 Version Manager Summary:")
    summary = manager.get_summary()
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")

    logger.info("\n✅ Model Versioning System Demo Complete!")
    logger.info("=" * 70)

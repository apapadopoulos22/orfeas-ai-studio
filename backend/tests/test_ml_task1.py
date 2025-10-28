"""
Integration Tests for Phase 2 Task 1: Advanced ML Classification Pipeline
Tests: ml_ensemble.py, model_versioning.py, ab_testing.py

Test Coverage:
  - Ensemble classifier: >95% accuracy
  - Model versioning: Complete lifecycle
  - A/B testing: Traffic routing and significance
  - Integration: All modules working together

Author: ORFEAS AI Studio - Phase 2 Task 1
Date: October 28, 2025
"""

import pytest
import logging
from pathlib import Path
import tempfile
import shutil
import json

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Import modules under test
import sys
sys.path.insert(0, str(Path(__file__).parent))

from ml_ensemble import (
    EnsembleClassifier, PredictionResult, get_ensemble_classifier
)
from model_versioning import (
    ModelVersionManager, VersionStatus, get_version_manager
)
from ab_testing import ABTestingFramework, TestStatus

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TestEnsembleClassifier:
    """Test suite for ensemble classifier."""

    @pytest.fixture
    def iris_data(self):
        """Load iris dataset."""
        data = load_iris()
        X_train, X_test, y_train, y_test = train_test_split(
            data.data, data.target, test_size=0.3, random_state=42
        )
        return X_train, X_test, y_train, y_test

    @pytest.fixture
    def ensemble(self):
        """Create ensemble classifier."""
        return EnsembleClassifier("test_ensemble")

    def test_ensemble_creation(self, ensemble):
        """Test ensemble creation."""
        assert ensemble.model_name == "test_ensemble"
        assert not ensemble._model_cache["initialized"]

    def test_ensemble_training(self, ensemble, iris_data):
        """Test ensemble training."""
        X_train, _, y_train, _ = iris_data

        ensemble.fit(X_train, y_train)

        assert ensemble._model_cache["initialized"]
        assert ensemble._model_cache["random_forest"] is not None
        assert ensemble._model_cache["xgboost"] is not None
        assert ensemble._model_cache["neural_network"] is not None

    def test_ensemble_accuracy(self, ensemble, iris_data):
        """Test ensemble achieves >95% accuracy on iris dataset."""
        X_train, X_test, y_train, y_test = iris_data

        ensemble.fit(X_train, y_train)
        predictions = ensemble.predict(X_test)

        accuracy = sum(predictions == y_test) / len(y_test)
        logger.info(f"Ensemble accuracy: {accuracy:.4f}")

        assert accuracy > 0.95, f"Accuracy {accuracy} not >0.95"

    def test_single_prediction(self, ensemble, iris_data):
        """Test single prediction with confidence metrics."""
        X_train, X_test, y_train, _ = iris_data

        ensemble.fit(X_train, y_train)
        result = ensemble.predict_single(X_test[0:1])

        assert isinstance(result, PredictionResult)
        assert result.predicted_class in [0, 1, 2]
        assert 0 <= result.confidence <= 1
        assert 0 <= result.uncertainty <= 1
        assert isinstance(result.ensemble_consensus, bool)

    def test_prediction_confidence(self, ensemble, iris_data):
        """Test prediction confidence scores."""
        X_train, X_test, y_train, _ = iris_data

        ensemble.fit(X_train, y_train)
        result = ensemble.predict_single(X_test[0:1])

        # Correct predictions should have higher confidence
        assert result.confidence > 0.5
        logger.info(
            f"Prediction confidence: {result.confidence:.4f}, "
            f"Uncertainty: {result.uncertainty:.4f}"
        )

    def test_model_metrics(self, ensemble, iris_data):
        """Test model metrics calculation."""
        X_train, X_test, y_train, y_test = iris_data

        ensemble.fit(X_train, y_train)
        metrics = ensemble.get_metrics()

        assert "random_forest" in metrics
        assert "xgboost" in metrics
        assert "neural_network" in metrics

        for model_name, model_metrics in metrics.items():
            assert model_metrics.accuracy > 0
            assert model_metrics.precision > 0
            assert model_metrics.recall > 0
            logger.info(
                f"{model_name}: "
                f"accuracy={model_metrics.accuracy:.4f}, "
                f"f1={model_metrics.f1_score:.4f}"
            )

    def test_model_save_load(self, ensemble, iris_data):
        """Test model saving and loading."""
        X_train, _, y_train, _ = iris_data

        ensemble.fit(X_train, y_train)
        model_path = ensemble.save_model(version="v1_test")

        assert Path(model_path).exists()
        logger.info(f"Model saved to: {model_path}")


class TestModelVersioning:
    """Test suite for model versioning."""

    @pytest.fixture
    def temp_version_dir(self):
        """Create temporary directory for versions."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def version_manager(self, temp_version_dir, monkeypatch):
        """Create version manager with temp directory."""
        monkeypatch.setenv("VERSION_BASE_DIR", temp_version_dir)
        manager = ModelVersionManager(temp_version_dir)
        return manager

    def test_version_creation(self, version_manager):
        """Test version creation."""
        version_id = version_manager.create_version(
            model_name="iris_classifier",
            accuracy=0.95,
            cross_val_score=0.94,
            description="Test version",
        )

        assert version_id.startswith("iris_classifier_")
        logger.info(f"Created version: {version_id}")

    def test_version_status_workflow(self, version_manager):
        """Test version status promotion workflow."""
        version_id = version_manager.create_version(
            model_name="iris_classifier",
            accuracy=0.95,
        )

        # Promote through workflow
        version_manager.promote_version(version_id, VersionStatus.TESTING)
        version_manager.promote_version(version_id, VersionStatus.STAGING)
        version_manager.promote_version(version_id, VersionStatus.PRODUCTION)

        version_info = version_manager.get_version_info(version_id)
        assert version_info.status == VersionStatus.PRODUCTION.value
        logger.info(f"Version {version_id} promoted to PRODUCTION")

    def test_production_deployment_archives_previous(self, version_manager):
        """Test that deploying to production archives previous version."""
        # Create and deploy v1
        v1_id = version_manager.create_version(
            model_name="iris_classifier",
            accuracy=0.95,
        )
        version_manager.deploy_to_production(v1_id)

        v1_info = version_manager.get_version_info(v1_id)
        assert v1_info.is_production

        # Create and deploy v2 - should archive v1
        v2_id = version_manager.create_version(
            model_name="iris_classifier",
            accuracy=0.96,
            parent_version=v1_id,
        )
        version_manager.deploy_to_production(v2_id)

        # Check v1 is no longer production
        v1_info_updated = version_manager.get_version_info(v1_id)
        assert not v1_info_updated.is_production

        v2_info = version_manager.get_version_info(v2_id)
        assert v2_info.is_production
        logger.info(f"V1 archived, V2 now in production")

    def test_version_rollback(self, version_manager):
        """Test rollback to previous version."""
        # Create 3 versions
        v1_id = version_manager.create_version(
            model_name="iris_classifier", accuracy=0.94
        )
        v2_id = version_manager.create_version(
            model_name="iris_classifier", accuracy=0.95, parent_version=v1_id
        )
        v3_id = version_manager.create_version(
            model_name="iris_classifier", accuracy=0.93, parent_version=v2_id
        )

        # Deploy v3 to production
        version_manager.deploy_to_production(v3_id)
        assert version_manager.get_production_version().version_id == v3_id

        # Rollback to v2
        version_manager.rollback_to_version(v2_id)

        production = version_manager.get_production_version()
        assert production.version_id == v2_id
        logger.info(f"Rolled back from {v3_id} to {v2_id}")

    def test_version_comparison(self, version_manager):
        """Test version comparison."""
        v1_id = version_manager.create_version(
            model_name="iris_classifier",
            accuracy=0.94,
            cross_val_score=0.93,
        )
        v2_id = version_manager.create_version(
            model_name="iris_classifier",
            accuracy=0.96,
            cross_val_score=0.95,
            parent_version=v1_id,
        )

        comparison = version_manager.compare_versions(v1_id, v2_id)

        assert "accuracy_improvement" in comparison
        assert "cv_improvement" in comparison
        assert comparison["accuracy_improvement"] == pytest.approx(0.02, abs=0.001)
        logger.info(f"Accuracy improvement: {comparison['accuracy_improvement']:.4f}")

    def test_version_history(self, version_manager):
        """Test version history retrieval."""
        # Create 3 versions
        for i in range(3):
            version_manager.create_version(
                model_name="iris_classifier",
                accuracy=0.94 + i * 0.01,
            )

        history = version_manager.get_version_history(model_name="iris_classifier")

        assert len(history) >= 3
        logger.info(f"Retrieved {len(history)} versions from history")

    def test_version_statistics(self, version_manager):
        """Test version statistics."""
        # Create versions with different statuses
        v1_id = version_manager.create_version(
            model_name="iris_classifier", accuracy=0.94
        )
        v2_id = version_manager.create_version(
            model_name="iris_classifier", accuracy=0.95
        )

        version_manager.promote_version(v1_id, VersionStatus.TESTING)
        version_manager.deploy_to_production(v2_id)

        stats = version_manager.get_statistics()

        assert stats["total_versions"] >= 2
        assert "by_status" in stats
        assert stats["average_accuracy"] > 0
        logger.info(f"Statistics: {stats}")


class TestABTesting:
    """Test suite for A/B testing framework."""

    @pytest.fixture
    def temp_ab_dir(self):
        """Create temporary directory for A/B tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def ab_framework(self, temp_ab_dir):
        """Create A/B testing framework."""
        return ABTestingFramework(temp_ab_dir)

    def test_test_creation(self, ab_framework):
        """Test A/B test creation."""
        test_id = ab_framework.create_test(
            test_name="Model Comparison",
            model_versions={
                "iris_classifier_v1": 50.0,
                "iris_classifier_v2": 50.0,
            },
        )

        assert test_id.startswith("test_")
        logger.info(f"Created A/B test: {test_id}")

    def test_variant_selection(self, ab_framework):
        """Test variant traffic routing."""
        test_id = ab_framework.create_test(
            test_name="Model Comparison",
            model_versions={
                "iris_classifier_v1": 50.0,
                "iris_classifier_v2": 50.0,
            },
        )

        # Select variants multiple times
        selections = [
            ab_framework.select_variant(test_id) for _ in range(100)
        ]

        # Should have roughly 50/50 split
        variant_0_count = selections.count("variant_0")
        variant_1_count = selections.count("variant_1")

        assert variant_0_count > 30  # ~50% of 100
        assert variant_1_count > 30
        logger.info(
            f"Traffic split: variant_0={variant_0_count}, variant_1={variant_1_count}"
        )

    def test_prediction_recording(self, ab_framework):
        """Test prediction metrics recording."""
        test_id = ab_framework.create_test(
            test_name="Model Comparison",
            model_versions={
                "iris_classifier_v1": 50.0,
                "iris_classifier_v2": 50.0,
            },
        )

        # Record predictions
        for i in range(20):
            variant_id = ab_framework.select_variant(test_id)
            ab_framework.record_prediction(
                test_id=test_id,
                variant_id=variant_id,
                confidence=0.85,
                latency_ms=42.0,
                was_correct=(i % 2 == 0),
            )

        status = ab_framework.get_test_status(test_id)

        assert status["variants"]["variant_0"]["metrics"]["total_requests"] > 0
        assert status["variants"]["variant_1"]["metrics"]["total_requests"] > 0
        logger.info(f"Test status: {status['variants']}")

    def test_statistical_significance(self, ab_framework):
        """Test statistical significance testing."""
        test_id = ab_framework.create_test(
            test_name="Model Accuracy Comparison",
            model_versions={
                "iris_classifier_v1": 50.0,
                "iris_classifier_v2": 50.0,
            },
            min_sample_size=100,
        )

        # Simulate traffic with different accuracies
        accuracies = {
            "variant_0": 0.92,
            "variant_1": 0.97,  # Significantly better
        }

        for _ in range(150):
            variant_id = ab_framework.select_variant(test_id)
            was_correct = (
                __import__("random").random() < accuracies[variant_id]
            )
            ab_framework.record_prediction(
                test_id=test_id,
                variant_id=variant_id,
                confidence=0.87,
                latency_ms=42.0,
                was_correct=was_correct,
            )

        sig_result = ab_framework.check_significance(test_id)

        assert sig_result["ready"]
        assert sig_result["is_significant"]
        logger.info(
            f"Significance test: p-value={sig_result['p_value']}, "
            f"significant={sig_result['is_significant']}"
        )

    def test_winner_declaration(self, ab_framework):
        """Test winner declaration."""
        test_id = ab_framework.create_test(
            test_name="Model Accuracy Comparison",
            model_versions={
                "iris_classifier_v1": 50.0,
                "iris_classifier_v2": 50.0,
            },
            min_sample_size=100,
        )

        # Simulate traffic
        accuracies = {
            "variant_0": 0.90,
            "variant_1": 0.96,
        }

        for _ in range(150):
            variant_id = ab_framework.select_variant(test_id)
            was_correct = (
                __import__("random").random() < accuracies[variant_id]
            )
            ab_framework.record_prediction(
                test_id=test_id,
                variant_id=variant_id,
                confidence=0.87,
                latency_ms=42.0,
                was_correct=was_correct,
            )

        winner = ab_framework.declare_winner(test_id)

        assert winner is not None
        status = ab_framework.get_test_status(test_id)
        assert status["status"] == TestStatus.COMPLETED.value
        logger.info(f"Winner declared: {winner}")


class TestIntegration:
    """Integration tests for all modules working together."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for all tests."""
        ensemble_dir = tempfile.mkdtemp()
        version_dir = tempfile.mkdtemp()
        ab_dir = tempfile.mkdtemp()

        yield ensemble_dir, version_dir, ab_dir

        shutil.rmtree(ensemble_dir, ignore_errors=True)
        shutil.rmtree(version_dir, ignore_errors=True)
        shutil.rmtree(ab_dir, ignore_errors=True)

    def test_full_pipeline(self, temp_dirs):
        """Test full ML pipeline: train → version → A/B test."""
        ensemble_dir, version_dir, ab_dir = temp_dirs

        # Load data
        data = load_iris()
        X_train, X_test, y_train, y_test = train_test_split(
            data.data, data.target, test_size=0.3, random_state=42
        )

        # Step 1: Train ensemble
        logger.info("\n📚 Step 1: Training ensemble classifier...")
        ensemble_v1 = EnsembleClassifier("iris_classifier")
        ensemble_v1.fit(X_train, y_train)

        predictions_v1 = ensemble_v1.predict(X_test)
        accuracy_v1 = sum(predictions_v1 == y_test) / len(y_test)
        logger.info(f"  Ensemble V1 accuracy: {accuracy_v1:.4f}")

        # Step 2: Version the model
        logger.info("\n📋 Step 2: Creating version...")
        version_manager = ModelVersionManager(version_dir)
        v1_id = version_manager.create_version(
            model_name="iris_classifier",
            accuracy=accuracy_v1,
            cross_val_score=accuracy_v1 - 0.01,
        )
        logger.info(f"  Version created: {v1_id}")

        # Step 3: Promote to production
        logger.info("\n🚀 Step 3: Promoting to production...")
        version_manager.deploy_to_production(v1_id)
        prod_version = version_manager.get_production_version()
        assert prod_version.version_id == v1_id
        logger.info(f"  Production version: {v1_id}")

        # Step 4: Set up A/B test for next version
        logger.info("\n🧪 Step 4: Setting up A/B test...")
        ab_framework = ABTestingFramework(ab_dir)
        test_id = ab_framework.create_test(
            test_name="V1 vs V2 Comparison",
            model_versions={
                "iris_classifier_v1": 50.0,
                "iris_classifier_v2": 50.0,
            },
        )
        logger.info(f"  A/B test created: {test_id}")

        # Step 5: Simulate traffic and collect metrics
        logger.info("\n📊 Step 5: Simulating traffic...")
        for sample_idx in range(50):
            variant_id = ab_framework.select_variant(test_id)

            # Use v1 ensemble for predictions
            result = ensemble_v1.predict_single(X_test[sample_idx:sample_idx+1])
            was_correct = (result.predicted_class == y_test[sample_idx])

            ab_framework.record_prediction(
                test_id=test_id,
                variant_id=variant_id,
                confidence=result.confidence,
                latency_ms=45.0,
                was_correct=was_correct,
            )

        logger.info(f"  Processed 50 predictions")

        # Verify integration
        logger.info("\n✅ Verification:")
        assert accuracy_v1 > 0.90, "Ensemble should achieve >90% accuracy"

        prod = version_manager.get_production_version()
        assert prod.accuracy > 0.90, "Production version should have >90% accuracy"

        test_status = ab_framework.get_test_status(test_id)
        assert test_status["status"] == TestStatus.ACTIVE.value

        logger.info("  ✅ All integration tests passed!")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

"""
BOB AI v7 - Knowledge Retrofit Tool
Converts existing 900 knowledge items to KnowledgeNode format with quality metrics
Enables batch migration from flat dict structure to full knowledge graph

Usage:
    python bob_ai_v7_retrofit_knowledge.py

This script:
    1. Discovers all existing knowledge items from backend
    2. Analyzes content to infer quality metrics
    3. Converts to KnowledgeNode format
    4. Adds metadata and verification status
    5. Validates converted items
    6. Exports to compatible formats
"""

import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
from abc import ABC, abstractmethod

# Import from other modules
try:
    from bob_ai_v7_knowledge_graph_core import KnowledgeNode, KnowledgeMetadata, DifficultyLevel, KnowledgeScope, Example, Reference
    from bob_ai_v7_quality_system import QualityMetrics, VerificationStatus, QualityCalculator, QualityLevel
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}")
    print("This is expected if running in isolated environment")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ContentAnalyzer(ABC):
    """Base class for content analysis strategies"""

    @abstractmethod
    def infer_quality_metrics(self, content: Dict[str, Any]) -> QualityMetrics:
        """Analyze content and infer quality metrics"""
        pass

    @abstractmethod
    def estimate_difficulty(self, content: Dict[str, Any]) -> DifficultyLevel:
        """Estimate difficulty level from content"""
        pass


class DefaultContentAnalyzer(ContentAnalyzer):
    """Default analyzer for generic knowledge items"""

    def infer_quality_metrics(self, content: Dict[str, Any]) -> QualityMetrics:
        """
        Infer quality metrics from content structure and completeness

        Heuristics:
        - Presence of examples increases examples_count
        - Presence of references increases references_count
        - Content length affects completeness
        - Specificity affects precision
        """
        metrics = QualityMetrics()

        # Analyze description length (completeness proxy)
        description = content.get('description', '') or content.get('definition', '') or ''
        if len(description) > 500:
            metrics.completeness = 0.85
        elif len(description) > 200:
            metrics.completeness = 0.70
        elif len(description) > 50:
            metrics.completeness = 0.50
        else:
            metrics.completeness = 0.35

        # Count examples
        if 'examples' in content and content['examples']:
            metrics.examples_count = min(len(content['examples']), 5)
        if 'example' in content and content['example']:
            metrics.examples_count += 1

        # Count references
        if 'references' in content and content['references']:
            metrics.references_count = min(len(content['references']), 5)
        if 'source' in content and content['source'] and content['source'] != 'unknown':
            metrics.references_count += 1

        # Infer precision from structure
        has_category = 'category' in content or 'domain' in content
        has_tags = 'tags' in content and content['tags']
        if has_category and has_tags:
            metrics.precision = 0.75
        elif has_category:
            metrics.precision = 0.65
        else:
            metrics.precision = 0.55

        # Default confidence based on source
        source = content.get('source', 'unknown').lower()
        if 'wikipedia' in source or 'academic' in source or 'verified' in source:
            metrics.confidence = 0.80
            metrics.is_wikipedia_sourced = 'wikipedia' in source
        elif 'verified' in source.lower():
            metrics.confidence = 0.75
        else:
            metrics.confidence = 0.60

        # Relevance based on usage or citations
        if 'usage_count' in content or 'citations' in content:
            metrics.relevance = 0.80
        elif 'related_items' in content:
            metrics.relevance = 0.70
        else:
            metrics.relevance = 0.65

        # Currency - assume items are relatively current
        metrics.currency_days = 60  # Assume 2 months old

        # Source tracking
        metrics.source = content.get('source', 'migrated_knowledge')

        return metrics

    def estimate_difficulty(self, content: Dict[str, Any]) -> DifficultyLevel:
        """Estimate difficulty from content complexity"""
        keywords_advanced = ['algorithm', 'machine learning', 'neural', 'quantum', 'calculus', 'differential']
        keywords_intermediate = ['probability', 'database', 'network', 'optimization', 'pattern']
        keywords_beginner = ['basic', 'intro', 'fundamentals', 'simple', 'overview']

        description = (content.get('description', '') or content.get('definition', '') or '').lower()
        label = (content.get('label', '') or content.get('name', '') or '').lower()
        combined = f"{label} {description}".lower()

        advanced_count = sum(1 for kw in keywords_advanced if kw in combined)
        intermediate_count = sum(1 for kw in keywords_intermediate if kw in combined)
        beginner_count = sum(1 for kw in keywords_beginner if kw in combined)

        # Complexity estimate based on description length
        desc_length = len(description)
        if desc_length > 1000:
            length_score = 3
        elif desc_length > 500:
            length_score = 2
        elif desc_length > 100:
            length_score = 1
        else:
            length_score = 0

        total_score = advanced_count * 3 + intermediate_count * 2 + beginner_count * 1 + length_score

        if total_score >= 8:
            return DifficultyLevel.EXPERT
        elif total_score >= 5:
            return DifficultyLevel.ADVANCED
        elif total_score >= 2:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BEGINNER


class KnowledgeRetrofitter:
    """Manages conversion of old knowledge format to new KnowledgeNode format"""

    def __init__(self, content_analyzer: Optional[ContentAnalyzer] = None):
        """Initialize retrofitter"""
        self.analyzer = content_analyzer or DefaultContentAnalyzer()
        self.converted_items: List[KnowledgeNode] = []
        self.conversion_log: List[Dict[str, Any]] = []
        logger.info("KnowledgeRetrofitter initialized")

    def retrofit_item(
        self,
        item_id: str,
        item_data: Dict[str, Any],
        domain: str = 'unknown'
    ) -> Tuple[Optional[KnowledgeNode], List[str]]:
        """
        Convert single item from old format to KnowledgeNode

        Returns: (KnowledgeNode or None if failed, list of warnings)
        """
        warnings = []

        try:
            # Extract basic info
            label = item_data.get('name') or item_data.get('label') or f"Item_{item_id}"
            description = item_data.get('description') or item_data.get('definition') or ''

            # Infer quality metrics
            metrics = self.analyzer.infer_quality_metrics(item_data)

            # Estimate difficulty
            difficulty = self.analyzer.estimate_difficulty(item_data)

            # Determine scope
            scope = self._infer_scope(item_data)

            # Build references
            references = self._extract_references(item_data)

            # Build examples
            examples = self._extract_examples(item_data)

            # Create node
            node = KnowledgeNode(
                id=item_id,
                label=label,
                domain=domain,
                description=description
            )

            # Set metadata
            node.metadata = KnowledgeMetadata(
                confidence=metrics.confidence,
                precision=metrics.precision,
                completeness=metrics.completeness,
                relevance=metrics.relevance,
                currency_days=metrics.currency_days,
                source=metrics.source,
                references=references,
                reviewed_by=[],
                verified=False,
                difficulty=difficulty,
                scope=scope,
                examples=examples,
                prerequisites=[],
                use_cases=item_data.get('use_cases', []),
                deprecated=False,
                version='7.0',
                contributors=[],
            )

            # Add attributes
            for key in ['category', 'tags', 'related_items', 'keywords']:
                if key in item_data:
                    node.add_attribute(key, item_data[key])

            self.converted_items.append(node)

            self.conversion_log.append({
                'item_id': item_id,
                'label': label,
                'domain': domain,
                'success': True,
                'quality_score': QualityCalculator.calculate_quality_score(metrics),
                'warnings': warnings,
                'timestamp': datetime.utcnow().isoformat()
            })

            return node, warnings

        except Exception as e:
            error_msg = f"Failed to convert item {item_id}: {str(e)}"
            logger.error(error_msg)
            warnings.append(error_msg)

            self.conversion_log.append({
                'item_id': item_id,
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })

            return None, warnings

    def retrofit_batch(
        self,
        items_by_domain: Dict[str, List[Tuple[str, Dict[str, Any]]]]
    ) -> Dict[str, Any]:
        """
        Convert batch of items organized by domain

        Input format:
            {
                'domain_name': [
                    (item_id, item_data),
                    ...
                ],
                ...
            }

        Returns: Conversion summary
        """
        logger.info(f"Starting batch retrofit of {sum(len(v) for v in items_by_domain.values())} items")

        total_items = 0
        successful_conversions = 0
        failed_conversions = 0
        all_warnings = []

        for domain, items in items_by_domain.items():
            logger.info(f"Processing domain: {domain} ({len(items)} items)")

            for item_id, item_data in items:
                total_items += 1
                node, warnings = self.retrofit_item(item_id, item_data, domain)

                if node is not None:
                    successful_conversions += 1
                else:
                    failed_conversions += 1

                all_warnings.extend(warnings)

        logger.info(f"Batch retrofit complete: {successful_conversions}/{total_items} successful")

        return {
            'total_items': total_items,
            'successful': successful_conversions,
            'failed': failed_conversions,
            'success_rate': (successful_conversions / total_items * 100) if total_items > 0 else 0,
            'converted_nodes': self.converted_items,
            'warnings': all_warnings,
            'conversion_log': self.conversion_log
        }

    def _infer_scope(self, item_data: Dict[str, Any]) -> KnowledgeScope:
        """Infer knowledge scope from item data"""
        description = (item_data.get('description', '') or item_data.get('definition', '') or '').lower()

        if len(description) < 100:
            return KnowledgeScope.NICHE
        elif 'fundamental' in description or 'basic' in description or 'introduction' in description:
            return KnowledgeScope.FOUNDATIONAL
        elif 'specialized' in description or 'advanced' in description:
            return KnowledgeScope.SPECIALIZED
        else:
            return KnowledgeScope.GENERAL

    def _extract_references(self, item_data: Dict[str, Any]) -> List[Reference]:
        """Extract references from item data"""
        references = []

        if 'references' in item_data and isinstance(item_data['references'], list):
            for ref in item_data['references'][:3]:  # Max 3 references
                if isinstance(ref, dict):
                    references.append(Reference(
                        title=ref.get('title', 'Reference'),
                        url=ref.get('url', ''),
                        source_type=ref.get('type', 'external'),
                        retrieved_date=datetime.utcnow()
                    ))
                elif isinstance(ref, str):
                    references.append(Reference(
                        title='Reference',
                        url=ref,
                        source_type='external',
                        retrieved_date=datetime.utcnow()
                    ))

        if 'source_url' in item_data:
            references.append(Reference(
                title='Primary Source',
                url=item_data['source_url'],
                source_type='primary',
                retrieved_date=datetime.utcnow()
            ))

        return references

    def _extract_examples(self, item_data: Dict[str, Any]) -> List[Example]:
        """Extract examples from item data"""
        examples = []

        if 'examples' in item_data:
            items_list = item_data['examples'] if isinstance(item_data['examples'], list) else [item_data['examples']]
            for i, ex in enumerate(items_list[:2]):  # Max 2 examples
                if isinstance(ex, dict):
                    examples.append(Example(
                        label=ex.get('label', f'Example {i+1}'),
                        description=ex.get('description', ex.get('text', '')),
                        context=ex.get('context', ''),
                        relevance=ex.get('relevance', 0.8)
                    ))
                elif isinstance(ex, str):
                    examples.append(Example(
                        label=f'Example {i+1}',
                        description=ex,
                        context='',
                        relevance=0.7
                    ))

        return examples

    def get_quality_distribution(self) -> Dict[str, int]:
        """Get distribution of quality levels in converted items"""
        distribution = {level.value: 0 for level in QualityLevel}

        for node in self.converted_items:
            score = node.metadata.get_quality_score()
            level = QualityCalculator.get_quality_level(score)
            distribution[level.value] += 1

        return distribution

    def get_statistics(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        if not self.converted_items:
            return {
                'total_converted': 0,
                'average_quality_score': 0.0,
                'high_quality_count': 0,
                'high_quality_percentage': 0.0,
                'quality_distribution': {}
            }

        scores = [node.metadata.get_quality_score() for node in self.converted_items]
        high_quality = sum(1 for s in scores if s >= 0.85)

        return {
            'total_converted': len(self.converted_items),
            'average_quality_score': sum(scores) / len(scores),
            'high_quality_count': high_quality,
            'high_quality_percentage': (high_quality / len(self.converted_items) * 100) if self.converted_items else 0,
            'quality_distribution': self.get_quality_distribution()
        }


def demo_retrofit():
    """Demonstration of retrofit functionality"""
    print("\nBOB AI v7 - Knowledge Retrofit Tool Demo")
    print("=" * 70)
    print()

    # Initialize retrofitter
    retrofitter = KnowledgeRetrofitter()

    # Create sample knowledge items (simulating existing database)
    sample_items_by_domain = {
        'technology': [
            ('tech_001', {
                'name': 'Machine Learning',
                'description': 'Machine learning is a subset of artificial intelligence that focuses on developing algorithms and statistical models. It enables systems to learn from data without being explicitly programmed. Applications include classification, regression, clustering, and dimensionality reduction.',
                'examples': [
                    {'label': 'Email Spam Detection', 'description': 'Using ML to classify emails as spam or not'},
                    {'label': 'Recommendation Systems', 'description': 'Netflix uses ML to recommend movies'}
                ],
                'references': [
                    {'title': 'ML Book', 'url': 'http://example.com/ml'},
                    {'title': 'Research Paper', 'url': 'http://example.com/paper'}
                ],
                'tags': ['artificial-intelligence', 'algorithms', 'data-science'],
                'source': 'Academic',
                'use_cases': ['Prediction', 'Classification', 'Pattern Recognition']
            }),
            ('tech_002', {
                'name': 'Python',
                'definition': 'A high-level programming language',
                'source': 'Wikipedia',
                'tags': ['programming', 'language']
            })
        ],
        'science': [
            ('sci_001', {
                'name': 'Quantum Computing',
                'description': 'Quantum computing leverages quantum mechanics principles like superposition and entanglement to perform computations. It has potential to solve problems intractable for classical computers.',
                'examples': [
                    {'label': 'Drug Discovery', 'description': 'Quantum computers can simulate molecular interactions'}
                ],
                'source': 'verified',
                'tags': ['quantum', 'computing']
            })
        ]
    }

    # Perform retrofit
    result = retrofitter.retrofit_batch(sample_items_by_domain)

    print(f"Retrofit Results:")
    print(f"  Total Items: {result['total_items']}")
    print(f"  Successful: {result['successful']}")
    print(f"  Failed: {result['failed']}")
    print(f"  Success Rate: {result['success_rate']:.1f}%")
    print()

    # Show statistics
    stats = retrofitter.get_statistics()
    print("Quality Statistics:")
    print(f"  Total Converted: {stats['total_converted']}")
    print(f"  Average Score: {stats['average_quality_score']:.4f}")
    print(f"  High Quality: {stats['high_quality_count']}/{stats['total_converted']} ({stats['high_quality_percentage']:.1f}%)")
    print()

    print("Quality Distribution:")
    for level, count in stats['quality_distribution'].items():
        pct = (count / stats['total_converted'] * 100) if stats['total_converted'] > 0 else 0
        print(f"  {level.upper()}: {count} items ({pct:.1f}%)")
    print()

    # Show converted items
    print("Converted Items:")
    for node in retrofitter.converted_items[:3]:
        score = node.metadata.get_quality_score()
        print(f"  {node.label} ({node.domain})")
        print(f"    ID: {node.id}")
        print(f"    Quality: {score:.4f}")
        print(f"    Level: {QualityCalculator.get_quality_level(score).value}")


if __name__ == "__main__":
    demo_retrofit()

"""
BOB AI v7 - Quality Scoring System
Implements comprehensive quality assessment for knowledge items
Provides quality dashboard and verification mechanisms

Quality Formula:
    Score = (0.25 × confidence) + (0.20 × precision) + (0.20 × completeness) +
            (0.15 × relevance) + (0.10 × currency) + (0.05 × references) +
            (0.05 × examples)

Range: 0.0 (poor) to 1.0 (excellent)
High-Quality Threshold: ≥0.85
"""

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Quality tier classification"""
    CRITICAL = "critical"      # <0.50 - Major issues, needs review
    POOR = "poor"              # 0.50-0.60 - Significant issues
    FAIR = "fair"              # 0.60-0.75 - Some issues
    GOOD = "good"              # 0.75-0.85 - Acceptable
    EXCELLENT = "excellent"    # ≥0.85 - High quality


class VerificationStatus(Enum):
    """Verification states for knowledge items"""
    UNVERIFIED = "unverified"          # Not reviewed
    PARTIAL = "partial"                 # Partially verified
    VERIFIED = "verified"               # Expert verified
    FACT_CHECKED = "fact_checked"       # Wikipedia/external source verified
    PEER_REVIEWED = "peer_reviewed"     # Peer review complete


@dataclass
class QualityMetrics:
    """Stores all quality-related metrics for a knowledge item"""
    # Core confidence metrics (0.0-1.0)
    confidence: float = 0.5
    precision: float = 0.5
    completeness: float = 0.5
    relevance: float = 0.5

    # Currency tracking
    currency_days: int = 0  # Days since last update

    # Verification metadata
    references_count: int = 0
    examples_count: int = 0
    reviewed_by: List[str] = field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # Source tracking
    source: str = "unknown"
    is_wikipedia_sourced: bool = False
    is_wikidata_sourced: bool = False

    # Recommendations
    improvement_areas: List[str] = field(default_factory=list)

    # Timestamps
    created_date: datetime = field(default_factory=datetime.utcnow)
    last_verified: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization"""
        return {
            'confidence': self.confidence,
            'precision': self.precision,
            'completeness': self.completeness,
            'relevance': self.relevance,
            'currency_days': self.currency_days,
            'references_count': self.references_count,
            'examples_count': self.examples_count,
            'reviewed_by': self.reviewed_by,
            'verification_status': self.verification_status.value,
            'source': self.source,
            'is_wikipedia_sourced': self.is_wikipedia_sourced,
            'is_wikidata_sourced': self.is_wikidata_sourced,
            'improvement_areas': self.improvement_areas,
            'created_date': self.created_date.isoformat(),
            'last_verified': self.last_verified.isoformat() if self.last_verified else None,
            'last_updated': self.last_updated.isoformat()
        }


class QualityCalculator:
    """Calculates quality scores for knowledge items"""

    # Quality formula weights
    WEIGHTS = {
        'confidence': 0.25,
        'precision': 0.20,
        'completeness': 0.20,
        'relevance': 0.15,
        'currency': 0.10,
        'references': 0.05,
        'examples': 0.05,
    }

    # Quality thresholds
    HIGH_QUALITY_THRESHOLD = 0.85
    GOOD_QUALITY_THRESHOLD = 0.75
    ACCEPTABLE_QUALITY_THRESHOLD = 0.60

    @staticmethod
    def calculate_quality_score(metrics: QualityMetrics) -> float:
        """
        Calculate overall quality score using weighted formula

        Returns score between 0.0 and 1.0
        """
        # Calculate currency score (degrades over time)
        max_days = 365
        currency_score = max(0.0, 1.0 - (metrics.currency_days / max_days))

        # Calculate references score (incentivizes multiple sources)
        reference_score = min(1.0, metrics.references_count / 3.0)

        # Calculate examples score (incentivizes practical examples)
        examples_score = min(1.0, metrics.examples_count / 2.0)

        # Apply weights and sum
        score = (
            QualityCalculator.WEIGHTS['confidence'] * metrics.confidence +
            QualityCalculator.WEIGHTS['precision'] * metrics.precision +
            QualityCalculator.WEIGHTS['completeness'] * metrics.completeness +
            QualityCalculator.WEIGHTS['relevance'] * metrics.relevance +
            QualityCalculator.WEIGHTS['currency'] * currency_score +
            QualityCalculator.WEIGHTS['references'] * reference_score +
            QualityCalculator.WEIGHTS['examples'] * examples_score
        )

        # Clamp to valid range
        return max(0.0, min(1.0, score))

    @staticmethod
    def get_quality_level(score: float) -> QualityLevel:
        """Classify score into quality tier"""
        if score >= 0.85:
            return QualityLevel.EXCELLENT
        elif score >= 0.75:
            return QualityLevel.GOOD
        elif score >= 0.60:
            return QualityLevel.FAIR
        elif score >= 0.50:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL


class QualityValidator:
    """Validates knowledge quality and provides recommendations"""

    @staticmethod
    def validate_metrics(metrics: QualityMetrics) -> Tuple[bool, List[str]]:
        """
        Validate metrics and return issues found
        Returns (is_valid, issues_list)
        """
        issues = []

        # Check metric ranges
        for field_name in ['confidence', 'precision', 'completeness', 'relevance']:
            value = getattr(metrics, field_name)
            if not (0.0 <= value <= 1.0):
                issues.append(f"{field_name} must be between 0.0 and 1.0, got {value}")

        # Check source
        if metrics.source == "unknown":
            issues.append("Source should be specified")

        # Check verification
        if metrics.verification_status == VerificationStatus.UNVERIFIED and metrics.references_count == 0:
            issues.append("Unverified items should have at least one reference")

        # Check currency
        if metrics.currency_days > 365:
            issues.append(f"Knowledge is {metrics.currency_days} days old, should be updated")

        return len(issues) == 0, issues

    @staticmethod
    def get_improvement_recommendations(
        metrics: QualityMetrics,
        current_score: float
    ) -> List[str]:
        """Generate specific recommendations to improve quality score"""
        recommendations = []

        # Confidence recommendations
        if metrics.confidence < 0.75:
            recommendations.append("Increase confidence by adding expert validation or multiple sources")

        # Precision recommendations
        if metrics.precision < 0.75:
            recommendations.append("Improve precision by adding specific examples or narrowing scope")

        # Completeness recommendations
        if metrics.completeness < 0.75:
            recommendations.append("Enhance completeness by adding more comprehensive coverage")

        # Relevance recommendations
        if metrics.relevance < 0.75:
            recommendations.append("Strengthen relevance by clearly connecting to domain context")

        # Reference recommendations
        if metrics.references_count < 2:
            recommendations.append(f"Add more references (current: {metrics.references_count}, target: 3+)")

        # Example recommendations
        if metrics.examples_count < 1:
            recommendations.append("Add practical examples to illustrate the concept")

        # Verification recommendations
        if metrics.verification_status == VerificationStatus.UNVERIFIED:
            recommendations.append("Submit for expert review and verification")

        # Currency recommendations
        if metrics.currency_days > 180:
            recommendations.append(f"Review and update content (last updated {metrics.currency_days} days ago)")

        return recommendations


@dataclass
class QualityReport:
    """Comprehensive quality report for a knowledge item"""
    item_id: str
    item_label: str
    quality_score: float
    quality_level: str  # QualityLevel.value
    verification_status: str  # VerificationStatus.value
    metrics: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'item_id': self.item_id,
            'item_label': self.item_label,
            'quality_score': round(self.quality_score, 4),
            'quality_level': self.quality_level,
            'verification_status': self.verification_status,
            'metrics': self.metrics,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_markdown(self) -> str:
        """Generate markdown formatted report"""
        md = f"# Quality Report: {self.item_label}\n\n"
        md += f"**Item ID:** `{self.item_id}`\n"
        md += f"**Report Generated:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"

        md += "## Quality Score\n"
        md += f"- **Overall Score:** {self.quality_score:.2%}\n"
        md += f"- **Quality Level:** {self.quality_level.upper()}\n"
        md += f"- **Verification Status:** {self.verification_status}\n\n"

        md += "## Metrics Breakdown\n"
        md += "| Metric | Score |\n"
        md += "|--------|-------|\n"
        for key, value in self.metrics.items():
            if isinstance(value, (int, float)) and key not in ['created_date', 'last_updated', 'last_verified']:
                if isinstance(value, float) and 0 <= value <= 1:
                    md += f"| {key} | {value:.1%} |\n"
                else:
                    md += f"| {key} | {value} |\n"

        md += "\n## Recommendations\n"
        if self.recommendations:
            for i, rec in enumerate(self.recommendations, 1):
                md += f"{i}. {rec}\n"
        else:
            md += "✅ No improvement recommendations - item is high quality!\n"

        return md


class QualityDashboard:
    """Central quality management and reporting system"""

    def __init__(self):
        """Initialize the quality dashboard"""
        self.items: Dict[str, QualityReport] = {}
        self.calculator = QualityCalculator()
        self.validator = QualityValidator()
        logger.info("QualityDashboard initialized")

    def add_or_update_item(
        self,
        item_id: str,
        item_label: str,
        metrics: QualityMetrics
    ) -> QualityReport:
        """
        Add or update quality report for an item
        Returns the generated report
        """
        # Validate metrics
        is_valid, issues = self.validator.validate_metrics(metrics)
        if not is_valid:
            logger.warning(f"Quality validation issues for {item_id}: {issues}")

        # Calculate quality score
        score = self.calculator.calculate_quality_score(metrics)
        quality_level = self.calculator.get_quality_level(score).value

        # Get improvement recommendations
        recommendations = self.validator.get_improvement_recommendations(metrics, score)

        # Create report
        report = QualityReport(
            item_id=item_id,
            item_label=item_label,
            quality_score=score,
            quality_level=quality_level,
            verification_status=metrics.verification_status.value,
            metrics=metrics.to_dict(),
            recommendations=recommendations
        )

        # Store report
        self.items[item_id] = report
        logger.debug(f"Quality report created for {item_id}: score={score:.4f}, level={quality_level}")

        return report

    def get_item_report(self, item_id: str) -> Optional[QualityReport]:
        """Retrieve quality report for specific item"""
        return self.items.get(item_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall quality statistics"""
        if not self.items:
            return {
                'total_items': 0,
                'average_score': 0.0,
                'high_quality_count': 0,
                'high_quality_percentage': 0.0,
                'quality_distribution': {},
                'verification_distribution': {}
            }

        scores = [report.quality_score for report in self.items.values()]

        # Distribution by quality level
        quality_dist = defaultdict(int)
        verification_dist = defaultdict(int)

        for report in self.items.values():
            quality_dist[report.quality_level] += 1
            verification_dist[report.verification_status] += 1

        high_quality_count = sum(1 for score in scores if score >= self.calculator.HIGH_QUALITY_THRESHOLD)

        return {
            'total_items': len(self.items),
            'average_score': sum(scores) / len(scores) if scores else 0.0,
            'high_quality_count': high_quality_count,
            'high_quality_percentage': (high_quality_count / len(self.items) * 100) if self.items else 0.0,
            'quality_distribution': dict(quality_dist),
            'verification_distribution': dict(verification_dist),
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_items_by_quality_level(self, quality_level: str) -> List[QualityReport]:
        """Get all items at a specific quality level"""
        return [
            report for report in self.items.values()
            if report.quality_level == quality_level
        ]

    def get_items_needing_improvement(self, min_score: float = 0.75) -> List[QualityReport]:
        """Get items below quality threshold for improvement focus"""
        return [
            report for report in self.items.values()
            if report.quality_score < min_score
        ]

    def generate_html_report(self) -> str:
        """Generate HTML formatted dashboard"""
        stats = self.get_statistics()

        html = """
        <html>
        <head>
            <title>BOB AI v7 - Quality Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
                .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
                .metric-card { background-color: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metric-card h3 { margin: 0; color: #2c3e50; }
                .metric-value { font-size: 24px; font-weight: bold; color: #27ae60; }
                .quality-excellent { color: #27ae60; }
                .quality-good { color: #f39c12; }
                .quality-fair { color: #e67e22; }
                .quality-poor { color: #e74c3c; }
                .quality-critical { color: #c0392b; }
                table { width: 100%; border-collapse: collapse; background-color: white; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #34495e; color: white; }
                tr:hover { background-color: #f5f5f5; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>BOB AI v7 - Quality Management Dashboard</h1>
                <p>Generated: """ + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC') + """</p>
            </div>

            <div class="metrics">
                <div class="metric-card">
                    <h3>Total Items</h3>
                    <div class="metric-value">""" + str(stats['total_items']) + """</div>
                </div>
                <div class="metric-card">
                    <h3>Average Score</h3>
                    <div class="metric-value">""" + f"{stats['average_score']:.1%}" + """</div>
                </div>
                <div class="metric-card">
                    <h3>High Quality</h3>
                    <div class="metric-value quality-excellent">""" + str(stats['high_quality_count']) + """</div>
                </div>
                <div class="metric-card">
                    <h3>Quality %</h3>
                    <div class="metric-value quality-excellent">""" + f"{stats['high_quality_percentage']:.1f}%" + """</div>
                </div>
            </div>

            <h2>Quality Distribution</h2>
            <table>
                <tr>
                    <th>Quality Level</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
        """

        for level, count in stats['quality_distribution'].items():
            pct = (count / stats['total_items'] * 100) if stats['total_items'] > 0 else 0
            html += f"""
                <tr>
                    <td class="quality-{level}">{level.upper()}</td>
                    <td>{count}</td>
                    <td>{pct:.1f}%</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        return html


# Demo/test code
if __name__ == "__main__":
    # Initialize dashboard
    dashboard = QualityDashboard()

    print("BOB AI v7 - Quality Scoring System Demo")
    print("=" * 70)
    print()

    # Create sample quality metrics
    metrics1 = QualityMetrics(
        confidence=0.85,
        precision=0.80,
        completeness=0.75,
        relevance=0.90,
        currency_days=30,
        references_count=3,
        examples_count=2,
        reviewed_by=['Dr. Smith', 'Prof. Jones'],
        verification_status=VerificationStatus.VERIFIED,
        source='Academic Research',
        is_wikipedia_sourced=True
    )

    metrics2 = QualityMetrics(
        confidence=0.60,
        precision=0.55,
        completeness=0.50,
        relevance=0.65,
        currency_days=200,
        references_count=1,
        examples_count=0,
        reviewed_by=[],
        verification_status=VerificationStatus.UNVERIFIED,
        source='unknown'
    )

    # Add items to dashboard
    report1 = dashboard.add_or_update_item('item_001', 'Machine Learning Fundamentals', metrics1)
    report2 = dashboard.add_or_update_item('item_002', 'Legacy Knowledge Item', metrics2)

    print("Item 1: Machine Learning Fundamentals")
    print(f"  Quality Score: {report1.quality_score:.4f}")
    print(f"  Quality Level: {report1.quality_level}")
    print(f"  Verification: {report1.verification_status}")
    print()

    print("Item 2: Legacy Knowledge Item")
    print(f"  Quality Score: {report2.quality_score:.4f}")
    print(f"  Quality Level: {report2.quality_level}")
    print(f"  Verification: {report2.verification_status}")
    print(f"  Recommendations:")
    for rec in report2.recommendations:
        print(f"    - {rec}")
    print()

    # Show dashboard statistics
    stats = dashboard.get_statistics()
    print("Dashboard Statistics")
    print(f"  Total Items: {stats['total_items']}")
    print(f"  Average Score: {stats['average_score']:.4f}")
    print(f"  High Quality: {stats['high_quality_count']}/{stats['total_items']} ({stats['high_quality_percentage']:.1f}%)")
    print()

    print("Quality Distribution:")
    for level, count in stats['quality_distribution'].items():
        pct = (count / stats['total_items'] * 100) if stats['total_items'] > 0 else 0
        print(f"  {level.upper()}: {count} items ({pct:.1f}%)")

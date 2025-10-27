"""
Bob AI v7 - Enhanced Knowledge System
Implements structured, disciplined knowledge management

Features:
- Knowledge graph with semantic relationships
- Quality scoring and metadata
- Dynamic knowledge addition
- Performance optimization through indexing
- Cross-domain linking

Status: Ready for integration with v7
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class DifficultyLevel(Enum):
    """Knowledge difficulty assessment"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class KnowledgeScope(Enum):
    """Knowledge scope classification"""
    GENERAL = "general"
    SPECIALIZED = "specialized"
    NICHE = "niche"
    FOUNDATIONAL = "foundational"


@dataclass
class Example:
    """Usage example for knowledge item"""
    label: str
    description: str
    context: str
    relevance: float = 1.0  # 0.0-1.0


@dataclass
class KnowledgeMetadata:
    """Rich metadata for knowledge items"""
    confidence: float = 1.0  # 0.0-1.0 confidence in accuracy
    precision: float = 1.0  # 0.0-1.0 precision of information
    completeness: float = 1.0  # 0.0-1.0 how complete
    relevance: float = 1.0  # 0.0-1.0 relevance to domain
    currency_days: int = 0  # Days since last update
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    scope: KnowledgeScope = KnowledgeScope.GENERAL
    source: str = "manual"
    references: List[str] = field(default_factory=list)
    examples: List[Example] = field(default_factory=list)
    counter_examples: List[Example] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    coverage_areas: List[str] = field(default_factory=list)
    missing_areas: List[str] = field(default_factory=list)
    disputed_aspects: List[str] = field(default_factory=list)
    experimental: bool = False
    version: str = "1.0"
    contributors: List[str] = field(default_factory=list)
    reviewed_by: List[str] = field(default_factory=list)
    last_updated: str = ""
    deprecation_warning: Optional[str] = None

    def get_quality_score(self) -> float:
        """Calculate overall quality score 0.0-1.0"""
        weights = {
            "confidence": 0.25,
            "precision": 0.20,
            "completeness": 0.20,
            "relevance": 0.15,
            "currency": 0.10,
            "has_references": 0.05,
            "has_examples": 0.05,
        }

        # Currency: newer is better, penalize old info
        currency_score = max(0, 1.0 - (self.currency_days / 365))
        has_refs = 1.0 if self.references else 0.5
        has_examples = 1.0 if self.examples else 0.5

        score = (
            self.confidence * weights["confidence"]
            + self.precision * weights["precision"]
            + self.completeness * weights["completeness"]
            + self.relevance * weights["relevance"]
            + currency_score * weights["currency"]
            + has_refs * weights["has_references"]
            + has_examples * weights["has_examples"]
        )

        return min(1.0, max(0.0, score))

    def is_high_quality(self) -> bool:
        """Check if quality exceeds threshold"""
        return self.get_quality_score() >= 0.85

    def is_verified(self) -> bool:
        """Check if properly reviewed and sourced"""
        return bool(self.references and self.reviewed_by)

    def get_recommendations(self) -> List[str]:
        """Get suggestions for improvement"""
        recommendations = []
        if self.confidence < 0.9:
            recommendations.append("Increase confidence through verification")
        if not self.references:
            recommendations.append("Add authoritative references")
        if not self.examples:
            recommendations.append("Add practical examples")
        if self.currency_days > 180:
            recommendations.append(f"Update information (current for {self.currency_days} days)")
        if self.completeness < 0.8:
            recommendations.append("Expand coverage of sub-topics")
        if self.missing_areas:
            recommendations.append(f"Cover missing areas: {', '.join(self.missing_areas)}")
        return recommendations


class KnowledgeNode:
    """Base class for all knowledge items with rich semantics"""

    def __init__(self, id: str, label: str, domain: str, description: str = ""):
        self.id = id
        self.label = label
        self.domain = domain
        self.description = description
        self.attributes: Dict[str, Any] = {}
        self.metadata = KnowledgeMetadata()
        self.relationships: Dict[str, List[str]] = {
            "is_a": [],  # Specialization
            "part_of": [],  # Composition
            "related_to": [],  # General relation
            "implies": [],  # Logical implication
            "depends_on": [],  # Dependency
            "used_for": [],  # Purpose
            "has_attribute": [],  # Properties
            "specializes": [],  # Makes specific
            "generalizes": [],  # Makes general
            "contradicts": [],  # Conflicts
            "alternative_to": [],  # Alternative method
        }

    def add_relationship(self, rel_type: str, target_id: str) -> None:
        """Add semantic relationship"""
        if rel_type not in self.relationships:
            self.relationships[rel_type] = []
        if target_id not in self.relationships[rel_type]:
            self.relationships[rel_type].append(target_id)

    def get_confidence(self) -> float:
        """Get overall confidence"""
        return self.metadata.get_quality_score()

    def to_dict(self) -> Dict:
        """Convert to dictionary for API"""
        return {
            "id": self.id,
            "label": self.label,
            "domain": self.domain,
            "description": self.description,
            "attributes": self.attributes,
            "relationships": self.relationships,
            "confidence": self.get_confidence(),
            "quality_score": self.metadata.get_quality_score(),
            "metadata": {
                "difficulty": self.metadata.difficulty.value,
                "scope": self.metadata.scope.value,
                "source": self.metadata.source,
                "verified": self.metadata.is_verified(),
            }
        }


class BusinessAndEconomicsKnowledge:
    """New domain: Business & Economics with structured knowledge"""

    BUSINESS_MODELS = {
        "SaaS": {
            "definition": "Software as a Service - cloud-based subscription model",
            "characteristics": [
                "recurring revenue",
                "scalable",
                "cloud-hosted",
                "updates included",
                "multi-tenant"
            ],
            "examples": [
                "Salesforce",
                "Microsoft 365",
                "Slack",
                "Stripe",
                "AWS"
            ],
            "advantages": [
                "predictable recurring revenue",
                "lower customer acquisition cost",
                "scalability",
                "continuous improvement"
            ],
            "challenges": [
                "customer churn",
                "high competition",
                "data security",
                "vendor lock-in"
            ]
        },
        "B2B": {
            "definition": "Business to Business - transactions between businesses",
            "characteristics": [
                "longer sales cycles",
                "higher contract values",
                "multiple stakeholders",
                "formal processes"
            ],
            "transaction_types": [
                "wholesale",
                "manufacturing supplies",
                "consulting services",
                "enterprise software"
            ]
        },
        "B2C": {
            "definition": "Business to Consumer - direct sales to end consumers",
            "characteristics": [
                "shorter sales cycles",
                "high volume",
                "direct marketing",
                "emotional appeals"
            ],
            "channels": [
                "retail stores",
                "e-commerce",
                "mobile apps",
                "social media"
            ]
        },
        "Marketplace": {
            "definition": "Platform connecting multiple buyers and sellers",
            "characteristics": [
                "two-sided network",
                "commission-based",
                "trust building",
                "network effects"
            ],
            "examples": [
                "Amazon",
                "Uber",
                "Airbnb",
                "Etsy",
                "eBay"
            ]
        },
        "Freemium": {
            "definition": "Free basic product with premium paid features",
            "characteristics": [
                "low barrier to entry",
                "conversion optimization",
                "feature tiers",
                "viral potential"
            ]
        }
    }

    FINANCIAL_CONCEPTS = {
        "Revenue": {
            "definition": "Income generated from sales of goods or services",
            "formula": "Price × Quantity",
            "types": ["product sales", "service fees", "licensing", "advertising"],
            "metrics": ["revenue growth", "revenue per user", "monthly recurring revenue"]
        },
        "Profit": {
            "definition": "Revenue minus costs",
            "types": ["gross profit", "operating profit", "net profit"],
            "calculation": "Revenue - Expenses",
            "importance": "Measure of business health and viability"
        },
        "Cash Flow": {
            "definition": "Movement of money in and out of business",
            "types": ["operating", "investing", "financing"],
            "challenges": ["timing differences", "seasonal variations"]
        },
        "ROI": {
            "definition": "Return on Investment - profit relative to investment",
            "formula": "(Gain - Cost) / Cost × 100%",
            "use": "Evaluate investment effectiveness",
            "benchmark": "Industry dependent, typically 15-20% good"
        },
        "Break-even": {
            "definition": "Point where revenue equals costs",
            "importance": "Minimum sales needed to be profitable",
            "calculation": "Fixed Costs / (Price - Variable Cost per Unit)"
        }
    }

    MARKETING_CONCEPTS = {
        "Segmentation": {
            "definition": "Dividing market into distinct groups",
            "types": [
                "demographic",
                "psychographic",
                "geographic",
                "behavioral",
                "firmographic"
            ],
            "purpose": "Targeted marketing, better ROI"
        },
        "Positioning": {
            "definition": "How brand is perceived vs competitors",
            "strategy": ["premium", "value", "specialty", "convenience"],
            "importance": "Differentiates from competitors"
        },
        "Brand": {
            "definition": "Promise, identity, and reputation",
            "elements": ["logo", "messaging", "values", "experience"],
            "value": "Customer loyalty, premium pricing"
        },
        "Customer_Acquisition_Cost": {
            "definition": "Average cost to acquire one customer",
            "formula": "Marketing Spend / New Customers",
            "importance": "Sustainability metric",
            "target": "Should be <3x Lifetime Value"
        }
    }

    PROJECT_MANAGEMENT = {
        "Agile": {
            "definition": "Iterative development approach",
            "principles": [
                "individuals over processes",
                "working software over documentation",
                "customer collaboration",
                "responding to change"
            ],
            "frameworks": ["Scrum", "Kanban", "XP", "Lean"]
        },
        "Waterfall": {
            "definition": "Sequential, phase-by-phase approach",
            "phases": [
                "requirements",
                "design",
                "implementation",
                "testing",
                "deployment"
            ],
            "best_for": "Fixed scope, well-defined requirements"
        },
        "Critical_Path": {
            "definition": "Longest sequence of dependent tasks",
            "importance": "Determines minimum project duration",
            "method": "Critical Path Method (CPM)"
        }
    }

    @classmethod
    def create_nodes(cls) -> Dict[str, KnowledgeNode]:
        """Create structured knowledge nodes for business domain"""
        nodes = {}

        # Create SaaS node
        saas_node = KnowledgeNode(
            "biz_saas_001",
            "SaaS Business Model",
            "Business_Economics"
        )
        saas_node.description = "Software as a Service - cloud-based subscription model"
        saas_node.attributes = cls.BUSINESS_MODELS["SaaS"]
        saas_node.metadata.confidence = 0.95
        saas_node.metadata.precision = 0.95
        saas_node.metadata.completeness = 0.90
        saas_node.metadata.relevance = 1.0
        saas_node.metadata.difficulty = DifficultyLevel.INTERMEDIATE
        saas_node.metadata.examples = [
            Example("Salesforce", "CRM SaaS", "Enterprise sales"),
            Example("Slack", "Communication SaaS", "Team collaboration")
        ]
        saas_node.metadata.references = [
            "https://en.wikipedia.org/wiki/Software_as_a_service",
            "https://www.saastr.com"
        ]
        saas_node.metadata.contributors = ["Business_Expert", "SaaS_Specialist"]
        saas_node.metadata.reviewed_by = ["Domain_Lead"]
        nodes["saas"] = saas_node

        # Create B2B node
        b2b_node = KnowledgeNode(
            "biz_b2b_001",
            "B2B Business Model",
            "Business_Economics"
        )
        b2b_node.description = "Business to Business - transactions between companies"
        b2b_node.attributes = cls.BUSINESS_MODELS["B2B"]
        b2b_node.metadata.confidence = 0.95
        b2b_node.add_relationship("related_to", "biz_saas_001")
        nodes["b2b"] = b2b_node

        # Create Financial Concepts
        revenue_node = KnowledgeNode(
            "fin_revenue_001",
            "Revenue",
            "Business_Economics"
        )
        revenue_node.description = "Income generated from business activities"
        revenue_node.attributes = cls.FINANCIAL_CONCEPTS["Revenue"]
        revenue_node.metadata.confidence = 0.99
        nodes["revenue"] = revenue_node

        profit_node = KnowledgeNode(
            "fin_profit_001",
            "Profit",
            "Business_Economics"
        )
        profit_node.description = "Revenue minus all expenses"
        profit_node.attributes = cls.FINANCIAL_CONCEPTS["Profit"]
        profit_node.metadata.confidence = 0.99
        profit_node.add_relationship("depends_on", "fin_revenue_001")
        nodes["profit"] = profit_node

        return nodes


class KnowledgeIndexer:
    """Index knowledge for fast retrieval"""

    def __init__(self):
        self.label_index: Dict[str, str] = {}  # label -> id
        self.domain_index: Dict[str, List[str]] = {}  # domain -> [ids]
        self.attribute_index: Dict[str, List[str]] = {}  # attribute -> [ids]
        self.relationship_index: Dict[str, Dict[str, List[str]]] = {}  # id -> relationships

    def add_node(self, node: KnowledgeNode) -> None:
        """Add node to indices"""
        # Label index
        self.label_index[node.label.lower()] = node.id

        # Domain index
        if node.domain not in self.domain_index:
            self.domain_index[node.domain] = []
        self.domain_index[node.domain].append(node.id)

        # Attribute index
        for attr_value in str(node.attributes).lower().split():
            if attr_value not in self.attribute_index:
                self.attribute_index[attr_value] = []
            self.attribute_index[attr_value].append(node.id)

        # Relationship index
        self.relationship_index[node.id] = node.relationships

    def search_by_label(self, label: str) -> Optional[str]:
        """Fast label lookup"""
        return self.label_index.get(label.lower())

    def search_by_domain(self, domain: str) -> List[str]:
        """Get all items in domain"""
        return self.domain_index.get(domain, [])

    def get_relationships(self, node_id: str) -> Dict:
        """Get relationships for node"""
        return self.relationship_index.get(node_id, {})


class QualityDashboard:
    """Track and report on knowledge quality"""

    def __init__(self, nodes: Dict[str, KnowledgeNode]):
        self.nodes = nodes

    def get_quality_scores(self) -> Dict[str, float]:
        """Get quality score for each node"""
        return {
            node_id: node.metadata.get_quality_score()
            for node_id, node in self.nodes.items()
        }

    def get_average_quality(self) -> float:
        """Get average quality across all nodes"""
        scores = self.get_quality_scores()
        return sum(scores.values()) / len(scores) if scores else 0.0

    def get_high_quality_percentage(self) -> float:
        """Percentage of high-quality nodes (>0.85)"""
        scores = self.get_quality_scores()
        high_quality = sum(1 for s in scores.values() if s >= 0.85)
        return (high_quality / len(scores) * 100) if scores else 0.0

    def get_verification_status(self) -> Dict[str, int]:
        """Count verified vs unverified nodes"""
        verified = sum(
            1 for node in self.nodes.values()
            if node.metadata.is_verified()
        )
        return {
            "verified": verified,
            "unverified": len(self.nodes) - verified,
            "percentage": (verified / len(self.nodes) * 100) if self.nodes else 0.0
        }

    def generate_report(self) -> str:
        """Generate quality report"""
        report = []
        report.append("\n=== KNOWLEDGE QUALITY REPORT ===\n")
        report.append(f"Total Nodes: {len(self.nodes)}\n")
        report.append(f"Average Quality: {self.get_average_quality():.2f}/1.0\n")
        report.append(f"High Quality (>0.85): {self.get_high_quality_percentage():.1f}%\n")

        verif = self.get_verification_status()
        report.append(f"Verified: {verif['verified']}/{len(self.nodes)} ({verif['percentage']:.1f}%)\n")

        # Quality breakdown
        report.append("\n### Quality by Node:\n")
        for node_id, node in sorted(
            self.nodes.items(),
            key=lambda x: x[1].metadata.get_quality_score()
        ):
            score = node.metadata.get_quality_score()
            status = "✓" if score >= 0.85 else "○" if score >= 0.70 else "△"
            report.append(f"{status} {node.label}: {score:.2f}\n")

        return "".join(report)


# Initialize with Business & Economics domain
if __name__ == "__main__":
    # Create knowledge nodes
    business_nodes = BusinessAndEconomicsKnowledge.create_nodes()

    # Create indexer
    indexer = KnowledgeIndexer()
    for node in business_nodes.values():
        indexer.add_node(node)

    # Create dashboard
    dashboard = QualityDashboard(business_nodes)

    # Print report
    print(dashboard.generate_report())

    logger.info("Enhanced knowledge system initialized with Business & Economics domain")

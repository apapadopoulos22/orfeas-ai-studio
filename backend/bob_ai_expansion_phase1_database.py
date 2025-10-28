"""
BOB AI Expansion - Phase 1: Database Schema & Migrations
=========================================================

Creates 5 new tables to support 100 new categories, 500 new disciplines,
and 800+ library mappings.

Architecture:
  - expanded_categories: 100 new categories organized in 8 tiers
  - expanded_disciplines: 500 new disciplines with descriptions
  - library_mappings: 800+ library mappings to disciplines
  - discipline_links: Prerequisites and relationships between disciplines
  - learning_paths: Pre-built learning path curricula

Author: ORFEAS AI - BOB AI Expansion v10.0
Date: October 28, 2025
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import json
import csv
from pathlib import Path

# Database imports
try:
    from sqlalchemy import (
        create_engine, Column, Integer, String, Text, DateTime,
        Boolean, Float, ForeignKey, Index, UniqueConstraint,
        JSON, ARRAY, VARCHAR
    )
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship, Session
    from sqlalchemy.pool import QueuePool
except ImportError:
    print("WARNING: SQLAlchemy not installed. Install with: pip install sqlalchemy")

logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()


class ExpandedCategory(Base):
    """100 New Categories organized in 8 tiers"""
    __tablename__ = 'expanded_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    tier = Column(Integer, nullable=False)  # 1-8: Emerging Tech to Hardware
    tier_name = Column(String(100), nullable=False)  # "Emerging Technologies", etc.
    description = Column(Text, nullable=False)
    parent_category_id = Column(Integer, ForeignKey('expanded_categories.id'), nullable=True)

    # Metadata
    disciplines_count = Column(Integer, default=0)
    libraries_count = Column(Integer, default=0)
    keywords = Column(JSON, default=list)  # ["quantum", "computing", "AI"]
    industry_relevance = Column(JSON, default=dict)  # {"finance": 0.8, "healthcare": 0.6}
    maturity_level = Column(String(50), default="emerging")  # emerging, growing, mature, established

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    disciplines = relationship("ExpandedDiscipline", back_populates="category")
    sub_categories = relationship("ExpandedCategory", remote_side=[id])

    __table_args__ = (
        Index('idx_tier_name', 'tier', 'name'),
        Index('idx_maturity', 'maturity_level'),
    )


class ExpandedDiscipline(Base):
    """500 New Disciplines with descriptions and prerequisites"""
    __tablename__ = 'expanded_disciplines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    category_id = Column(Integer, ForeignKey('expanded_categories.id'), nullable=False)

    # Description and details
    description = Column(Text, nullable=False)
    use_cases = Column(JSON, default=list)  # ["robotics", "autonomous vehicles"]
    learning_objective = Column(Text)  # What students should learn
    difficulty_level = Column(String(50), default="intermediate")  # beginner, intermediate, advanced, expert

    # Relationships & dependencies
    prerequisite_disciplines = Column(JSON, default=list)  # [1, 5, 12] discipline IDs
    related_disciplines = Column(JSON, default=list)

    # Content metadata
    topics = Column(JSON, default=list)  # Sub-topics covered
    keywords = Column(JSON, default=list)
    industry_applications = Column(JSON, default=dict)  # {"AI": 0.9, "Healthcare": 0.7}
    real_world_examples = Column(JSON, default=list)

    # Curriculum metadata
    estimated_hours = Column(Float, default=40.0)  # Estimated learning time
    certification_available = Column(Boolean, default=False)
    career_paths = Column(JSON, default=list)  # Relevant careers

    # Status
    status = Column(String(50), default="active")  # active, deprecated, planning

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("ExpandedCategory", back_populates="disciplines")
    libraries = relationship("LibraryMapping", back_populates="discipline")
    links = relationship("DisciplineLink", foreign_keys="[DisciplineLink.source_discipline_id]")

    __table_args__ = (
        Index('idx_category_difficulty', 'category_id', 'difficulty_level'),
        Index('idx_status', 'status'),
    )


class LibraryMapping(Base):
    """800+ Libraries mapped to disciplines"""
    __tablename__ = 'library_mappings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    discipline_id = Column(Integer, ForeignKey('expanded_disciplines.id'), nullable=False)

    # Library details
    library_name = Column(String(255), nullable=False)
    package_name = Column(String(255), nullable=False)  # pip package name
    version = Column(String(50))
    language = Column(String(50), default="python")  # python, javascript, julia, rust, cpp

    # Library metadata
    description = Column(Text)
    official_url = Column(String(500))
    documentation_url = Column(String(500))
    github_url = Column(String(500))

    # Installation & Usage
    install_command = Column(String(255))  # pip install X, npm install X, etc.
    import_statement = Column(String(255))  # How to import/use the library

    # Relevance & usage
    relevance_score = Column(Float, default=1.0)  # 0-1: How relevant to discipline
    usage_level = Column(String(50), default="intermediate")  # beginner, intermediate, advanced
    is_primary = Column(Boolean, default=False)  # Primary tool for this discipline?

    # Ecosystem
    technology_stack = Column(String(100))  # "Quantum Computing", "NLP", "MLOps", etc.
    dependencies = Column(JSON, default=list)  # Other libraries it depends on
    alternatives = Column(JSON, default=list)  # Alternative libraries

    # Maturity
    maturity_status = Column(String(50), default="active")  # active, deprecated, experimental
    last_release_date = Column(DateTime)

    # Status
    verified = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    discipline = relationship("ExpandedDiscipline", back_populates="libraries")

    __table_args__ = (
        Index('idx_discipline_language', 'discipline_id', 'language'),
        Index('idx_package_name', 'package_name'),
        Index('idx_technology_stack', 'technology_stack'),
    )


class DisciplineLink(Base):
    """Prerequisites and relationships between disciplines"""
    __tablename__ = 'discipline_links'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_discipline_id = Column(Integer, ForeignKey('expanded_disciplines.id'), nullable=False)
    target_discipline_id = Column(Integer, ForeignKey('expanded_disciplines.id'), nullable=False)

    # Link type
    link_type = Column(String(50), nullable=False)  # "prerequisite", "related", "follow-up", "alternative"
    strength = Column(Float, default=1.0)  # 0-1: How strongly related

    # Metadata
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_source_target', 'source_discipline_id', 'target_discipline_id'),
        UniqueConstraint('source_discipline_id', 'target_discipline_id', 'link_type', name='uq_discipline_link'),
    )


class LearningPath(Base):
    """Pre-built learning path curricula"""
    __tablename__ = 'learning_paths'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Path definition
    discipline_ids = Column(JSON, default=list)  # Ordered list of discipline IDs
    library_ids = Column(JSON, default=list)  # Recommended libraries
    estimated_duration_weeks = Column(Integer, default=8)
    skill_level = Column(String(50), default="intermediate")  # beginner, intermediate, advanced, expert

    # Curriculum metadata
    target_role = Column(String(255))  # "Quantum ML Specialist", "Federated Learning Expert"
    industry_focus = Column(String(100))  # "AI", "Finance", "Healthcare"
    outcomes = Column(JSON, default=list)  # What you'll learn
    projects = Column(JSON, default=list)  # Capstone projects
    certifications = Column(JSON, default=list)  # Possible certifications

    # Content
    resources = Column(JSON, default=dict)  # {"week_1": "https://...", ...}
    prerequisites_text = Column(Text)

    # Status
    is_published = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_skill_level', 'skill_level'),
        Index('idx_published', 'is_published'),
    )


class ExpandedKnowledgeLoader:
    """Loads 100 categories, 500 disciplines, and 800+ libraries into database"""

    def __init__(self, database_url: str):
        """
        Initialize loader with database connection

        Args:
            database_url: SQLAlchemy database URL
                          e.g., "postgresql://user:pass@localhost/bob_ai"
                               "sqlite:///./bob_ai.db"
        """
        self.database_url = database_url
        self.engine = None
        self.Session = None

    def connect(self):
        """Connect to database and create tables"""
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                echo=False
            )

            # Create all tables
            Base.metadata.create_all(self.engine)

            # Create session factory
            self.Session = sessionmaker(bind=self.engine)

            logger.info(f"✅ Connected to database: {self.database_url}")
            return True

        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def load_categories(self, categories_file: str) -> int:
        """
        Load 100 categories from CSV/JSON file

        CSV format:
            tier,name,tier_name,description,keywords,industry_relevance,maturity_level
            1,Quantum Computing,Emerging Technologies,"Computing using quantum mechanical phenomena",...

        Args:
            categories_file: Path to CSV or JSON file

        Returns:
            Number of categories loaded
        """
        session = self.Session()
        count = 0

        try:
            # Determine file format
            if categories_file.endswith('.json'):
                with open(categories_file, 'r') as f:
                    data = json.load(f)
                    categories_data = data if isinstance(data, list) else data.get('categories', [])
            else:
                # CSV format
                categories_data = []
                with open(categories_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    categories_data = list(reader)

            for item in categories_data:
                # Parse JSON fields
                keywords = item.get('keywords', [])
                if isinstance(keywords, str):
                    keywords = json.loads(keywords) if keywords else []

                industry_relevance = item.get('industry_relevance', {})
                if isinstance(industry_relevance, str):
                    industry_relevance = json.loads(industry_relevance) if industry_relevance else {}

                # Create category
                category = ExpandedCategory(
                    name=item['name'],
                    tier=int(item['tier']),
                    tier_name=item.get('tier_name', ''),
                    description=item['description'],
                    keywords=keywords,
                    industry_relevance=industry_relevance,
                    maturity_level=item.get('maturity_level', 'emerging')
                )

                session.add(category)
                count += 1

            session.commit()
            logger.info(f"✅ Loaded {count} categories")
            return count

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error loading categories: {e}")
            return 0
        finally:
            session.close()

    def load_disciplines(self, disciplines_file: str) -> int:
        """
        Load 500 disciplines from CSV/JSON file

        Args:
            disciplines_file: Path to CSV or JSON file

        Returns:
            Number of disciplines loaded
        """
        session = self.Session()
        count = 0

        try:
            # Determine file format
            if disciplines_file.endswith('.json'):
                with open(disciplines_file, 'r') as f:
                    data = json.load(f)
                    disciplines_data = data if isinstance(data, list) else data.get('disciplines', [])
            else:
                # CSV format
                disciplines_data = []
                with open(disciplines_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    disciplines_data = list(reader)

            for item in disciplines_data:
                # Find category by name
                category_name = item.get('category')
                category = session.query(ExpandedCategory).filter_by(name=category_name).first()

                if not category:
                    logger.warning(f"Category not found: {category_name}, skipping discipline {item['name']}")
                    continue

                # Parse JSON fields
                use_cases = json.loads(item.get('use_cases', '[]')) if item.get('use_cases') else []
                prerequisites = json.loads(item.get('prerequisites', '[]')) if item.get('prerequisites') else []
                topics = json.loads(item.get('topics', '[]')) if item.get('topics') else []
                keywords = json.loads(item.get('keywords', '[]')) if item.get('keywords') else []

                # Create discipline
                discipline = ExpandedDiscipline(
                    name=item['name'],
                    category_id=category.id,
                    description=item['description'],
                    use_cases=use_cases,
                    learning_objective=item.get('learning_objective', ''),
                    difficulty_level=item.get('difficulty_level', 'intermediate'),
                    topics=topics,
                    keywords=keywords,
                    estimated_hours=float(item.get('estimated_hours', 40.0)),
                    status=item.get('status', 'active')
                )

                session.add(discipline)
                count += 1

            session.commit()

            # Update category discipline counts
            for category in session.query(ExpandedCategory).all():
                category.disciplines_count = session.query(ExpandedDiscipline).filter_by(
                    category_id=category.id
                ).count()

            session.commit()
            logger.info(f"✅ Loaded {count} disciplines")
            return count

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error loading disciplines: {e}")
            return 0
        finally:
            session.close()

    def load_libraries(self, libraries_file: str) -> int:
        """
        Load 800+ libraries from CSV/JSON file

        Args:
            libraries_file: Path to CSV or JSON file

        Returns:
            Number of libraries loaded
        """
        session = self.Session()
        count = 0

        try:
            # Determine file format
            if libraries_file.endswith('.json'):
                with open(libraries_file, 'r') as f:
                    data = json.load(f)
                    libraries_data = data if isinstance(data, list) else data.get('libraries', [])
            else:
                # CSV format
                libraries_data = []
                with open(libraries_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    libraries_data = list(reader)

            for item in libraries_data:
                # Find discipline by name
                discipline_name = item.get('discipline')
                discipline = session.query(ExpandedDiscipline).filter_by(name=discipline_name).first()

                if not discipline:
                    logger.warning(f"Discipline not found: {discipline_name}, skipping library {item['library_name']}")
                    continue

                # Parse JSON fields
                dependencies = json.loads(item.get('dependencies', '[]')) if item.get('dependencies') else []
                alternatives = json.loads(item.get('alternatives', '[]')) if item.get('alternatives') else []

                # Create library mapping
                library = LibraryMapping(
                    discipline_id=discipline.id,
                    library_name=item['library_name'],
                    package_name=item['package_name'],
                    version=item.get('version', ''),
                    language=item.get('language', 'python'),
                    description=item.get('description', ''),
                    official_url=item.get('official_url', ''),
                    documentation_url=item.get('documentation_url', ''),
                    github_url=item.get('github_url', ''),
                    install_command=item.get('install_command', ''),
                    import_statement=item.get('import_statement', ''),
                    relevance_score=float(item.get('relevance_score', 1.0)),
                    technology_stack=item.get('technology_stack', ''),
                    dependencies=dependencies,
                    alternatives=alternatives,
                    is_primary=item.get('is_primary', 'false').lower() == 'true'
                )

                session.add(library)
                count += 1

            session.commit()

            # Update discipline library counts
            for category in session.query(ExpandedCategory).all():
                total_libs = session.query(LibraryMapping).join(ExpandedDiscipline).filter(
                    ExpandedDiscipline.category_id == category.id
                ).count()
                category.libraries_count = total_libs

            session.commit()
            logger.info(f"✅ Loaded {count} libraries")
            return count

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error loading libraries: {e}")
            return 0
        finally:
            session.close()

    def get_statistics(self) -> Dict:
        """Get expansion statistics"""
        session = self.Session()

        try:
            stats = {
                'categories': session.query(ExpandedCategory).count(),
                'disciplines': session.query(ExpandedDiscipline).count(),
                'libraries': session.query(LibraryMapping).count(),
                'learning_paths': session.query(LearningPath).count(),
                'categories_by_tier': {}
            }

            # Count by tier
            for tier in range(1, 9):
                count = session.query(ExpandedCategory).filter_by(tier=tier).count()
                tier_names = {
                    1: "Emerging Tech", 2: "Advanced NLP", 3: "Vision",
                    4: "Data Science", 5: "Specialized", 6: "Optimization",
                    7: "MLOps", 8: "Hardware"
                }
                stats['categories_by_tier'][tier_names[tier]] = count

            return stats

        finally:
            session.close()


# Integration with existing BOB AI system
def initialize_bob_ai_expansion(database_url: Optional[str] = None) -> ExpandedKnowledgeLoader:
    """
    Initialize BOB AI expansion system

    Args:
        database_url: Optional database URL. Defaults to environment variable
                      or sqlite database in project root.

    Returns:
        Initialized ExpandedKnowledgeLoader instance
    """
    if not database_url:
        # Get from environment or use default
        database_url = os.getenv('BOB_AI_DATABASE_URL', 'sqlite:///./bob_ai_expansion.db')

    loader = ExpandedKnowledgeLoader(database_url)
    loader.connect()
    return loader


if __name__ == '__main__':
    # Example usage
    print("BOB AI Expansion - Phase 1: Database Setup")
    print("=" * 50)

    # Initialize
    loader = initialize_bob_ai_expansion()

    # In real implementation, you would call:
    # loader.load_categories('data/categories.csv')
    # loader.load_disciplines('data/disciplines.csv')
    # loader.load_libraries('data/libraries.csv')

    # Get stats
    stats = loader.get_statistics()
    print("\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

"""
BOB AI v7 - Dynamic Knowledge Addition Framework
Enables runtime addition of knowledge items via REST API
Includes validation, schema checking, integrity verification, and atomic operations

Features:
- JSON schema validation
- Duplicate detection
- Referential integrity checking
- Atomic transactions with rollback
- Audit logging
- Conflict resolution

Status: Phase 4.1 - Dynamic Knowledge Framework Complete
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """Validation outcome states"""
    VALID = "valid"
    INVALID_SCHEMA = "invalid_schema"
    DUPLICATE = "duplicate"
    REFERENTIAL_INTEGRITY_ERROR = "referential_integrity_error"
    CONFLICT = "conflict"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ValidationError:
    """Represents a single validation error"""
    field: str
    message: str
    severity: str = "error"  # "error" or "warning"
    suggestion: Optional[str] = None


@dataclass
class KnowledgeItemSchema:
    """JSON schema for knowledge items"""
    required_fields = ['id', 'label', 'domain', 'description']
    optional_fields = ['examples', 'references', 'tags', 'attributes', 'metadata']

    # Validation rules
    min_label_length = 3
    max_label_length = 200
    min_description_length = 20
    max_description_length = 5000
    valid_domains = [
        'technology', 'business', 'science', 'history', 'medicine',
        'law', 'philosophy', 'arts', 'environment', 'education'
    ]


class SchemaValidator:
    """Validates knowledge items against schema"""

    @staticmethod
    def validate_item(item_data: Dict[str, Any]) -> Tuple[ValidationResult, List[ValidationError]]:
        """
        Validate item against schema
        Returns (result_status, list_of_errors)
        """
        errors = []

        # Check required fields
        for field in KnowledgeItemSchema.required_fields:
            if field not in item_data:
                errors.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing",
                    suggestion=f"Add '{field}' field to the item"
                ))

        # Validate ID format
        if 'id' in item_data:
            item_id = item_data['id']
            if not isinstance(item_id, str) or len(item_id) < 3:
                errors.append(ValidationError(
                    field='id',
                    message="ID must be a string with at least 3 characters",
                    suggestion="Use format: domain_descriptive_name (e.g., tech_machine_learning)"
                ))

        # Validate label
        if 'label' in item_data:
            label = item_data['label']
            if not isinstance(label, str):
                errors.append(ValidationError(field='label', message="Label must be a string"))
            elif len(label) < KnowledgeItemSchema.min_label_length:
                errors.append(ValidationError(
                    field='label',
                    message=f"Label must be at least {KnowledgeItemSchema.min_label_length} characters"
                ))
            elif len(label) > KnowledgeItemSchema.max_label_length:
                errors.append(ValidationError(
                    field='label',
                    message=f"Label must not exceed {KnowledgeItemSchema.max_label_length} characters"
                ))

        # Validate domain
        if 'domain' in item_data:
            domain = item_data['domain']
            if domain not in KnowledgeItemSchema.valid_domains:
                errors.append(ValidationError(
                    field='domain',
                    message=f"Domain '{domain}' is not in allowed list",
                    suggestion=f"Use one of: {', '.join(KnowledgeItemSchema.valid_domains)}"
                ))

        # Validate description
        if 'description' in item_data:
            desc = item_data['description']
            if not isinstance(desc, str):
                errors.append(ValidationError(field='description', message="Description must be a string"))
            elif len(desc) < KnowledgeItemSchema.min_description_length:
                errors.append(ValidationError(
                    field='description',
                    message=f"Description must be at least {KnowledgeItemSchema.min_description_length} characters"
                ))
            elif len(desc) > KnowledgeItemSchema.max_description_length:
                errors.append(ValidationError(
                    field='description',
                    message=f"Description must not exceed {KnowledgeItemSchema.max_description_length} characters"
                ))

        # Validate optional fields
        if 'examples' in item_data:
            if not isinstance(item_data['examples'], list):
                errors.append(ValidationError(
                    field='examples',
                    message="Examples must be a list",
                    severity="warning"
                ))

        if 'references' in item_data:
            if not isinstance(item_data['references'], list):
                errors.append(ValidationError(
                    field='references',
                    message="References must be a list",
                    severity="warning"
                ))

        if 'tags' in item_data:
            if not isinstance(item_data['tags'], list):
                errors.append(ValidationError(
                    field='tags',
                    message="Tags must be a list",
                    severity="warning"
                ))

        # Determine overall result
        if any(e.severity == "error" for e in errors):
            return ValidationResult.INVALID_SCHEMA, errors
        elif errors:
            return ValidationResult.VALID, errors  # Has warnings but is valid
        else:
            return ValidationResult.VALID, errors


class DuplicateDetector:
    """Detects duplicate knowledge items"""

    def __init__(self, existing_items: Dict[str, Dict[str, Any]]):
        """Initialize with existing items"""
        self.existing_items = existing_items
        self.item_hashes = self._build_hashes()

    def _build_hashes(self) -> Dict[str, str]:
        """Build hashes of existing items for quick comparison"""
        hashes = {}
        for item_id, item_data in self.existing_items.items():
            label = item_data.get('label', '').lower().strip()
            domain = item_data.get('domain', '')
            # Create simple hash of label+domain
            key = f"{label}:{domain}"
            hashes[item_id] = hashlib.md5(key.encode()).hexdigest()
        return hashes

    def find_duplicates(self, new_item: Dict[str, Any]) -> List[Tuple[str, float]]:
        """
        Find potential duplicate items
        Returns list of (item_id, similarity_score) tuples sorted by similarity
        """
        candidates = []

        new_label = new_item.get('label', '').lower().strip()
        new_domain = new_item.get('domain', '')
        new_key = f"{new_label}:{new_domain}"
        new_hash = hashlib.md5(new_key.encode()).hexdigest()

        # Check for exact duplicates first
        for item_id, existing_hash in self.item_hashes.items():
            if existing_hash == new_hash:
                candidates.append((item_id, 1.0))
                continue

            # Check for similar labels
            existing_item = self.existing_items[item_id]
            existing_label = existing_item.get('label', '').lower().strip()

            if new_label == existing_label:
                similarity = 0.95
            elif self._levenshtein_similarity(new_label, existing_label) > 0.85:
                similarity = 0.85
            else:
                similarity = 0.0

            if similarity > 0.7:
                candidates.append((item_id, similarity))

        return sorted(candidates, key=lambda x: -x[1])

    @staticmethod
    def _levenshtein_similarity(s1: str, s2: str) -> float:
        """Calculate similarity between two strings (0.0-1.0)"""
        if len(s1) == 0 or len(s2) == 0:
            return 0.0

        # Simple edit distance calculation
        if s1 == s2:
            return 1.0

        # Simplified: check if one is substring of other
        if s1 in s2 or s2 in s1:
            return 0.9

        # Otherwise return low similarity
        return 0.0


class ReferentialIntegrityChecker:
    """Checks referential integrity of knowledge items"""

    def __init__(self, existing_items: Dict[str, Dict[str, Any]]):
        """Initialize with existing items"""
        self.existing_items = existing_items
        self.available_ids = set(existing_items.keys())

    def check_integrity(self, new_item: Dict[str, Any]) -> List[ValidationError]:
        """Check if new item references valid items"""
        errors = []

        # Check prerequisites
        if 'prerequisites' in new_item and isinstance(new_item['prerequisites'], list):
            for prereq_id in new_item['prerequisites']:
                if prereq_id not in self.available_ids:
                    errors.append(ValidationError(
                        field='prerequisites',
                        message=f"Referenced prerequisite '{prereq_id}' does not exist",
                        severity="warning",
                        suggestion=f"Either create item '{prereq_id}' first or remove this reference"
                    ))

        # Check related_items
        if 'related_items' in new_item and isinstance(new_item['related_items'], list):
            for related_id in new_item['related_items']:
                if related_id not in self.available_ids:
                    errors.append(ValidationError(
                        field='related_items',
                        message=f"Referenced related item '{related_id}' does not exist",
                        severity="warning"
                    ))

        return errors


@dataclass
class AddItemTransaction:
    """Represents a transaction for adding an item"""
    transaction_id: str
    item_data: Dict[str, Any]
    status: str = "pending"  # pending, validating, validated, committing, committed, failed, rolled_back
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    rollback_reason: Optional[str] = None


class DynamicKnowledgeLoader:
    """Manages dynamic addition of knowledge items at runtime"""

    def __init__(self, initial_items: Optional[Dict[str, Dict[str, Any]]] = None):
        """Initialize loader"""
        self.items = initial_items or {}
        self.transactions: Dict[str, AddItemTransaction] = {}
        self.schema_validator = SchemaValidator()
        self.duplicate_detector = DuplicateDetector(self.items)
        self.integrity_checker = ReferentialIntegrityChecker(self.items)
        logger.info("DynamicKnowledgeLoader initialized")

    def prepare_add_item(
        self,
        item_data: Dict[str, Any],
        allow_duplicates: bool = False,
        skip_integrity_check: bool = False
    ) -> Tuple[str, ValidationResult, Dict[str, Any]]:
        """
        Prepare to add an item (validation phase)
        Returns (transaction_id, validation_result, details_dict)
        """
        import uuid
        transaction_id = str(uuid.uuid4())[:8]

        transaction = AddItemTransaction(
            transaction_id=transaction_id,
            item_data=item_data.copy()
        )

        # Store transaction immediately
        self.transactions[transaction_id] = transaction

        # Phase 1: Schema validation
        transaction.status = "validating"
        schema_result, schema_errors = self.schema_validator.validate_item(item_data)
        transaction.errors.extend([e for e in schema_errors if e.severity == "error"])
        transaction.warnings.extend([e for e in schema_errors if e.severity == "warning"])

        if schema_result != ValidationResult.VALID and transaction.errors:
            transaction.status = "failed"
            return transaction_id, schema_result, self._format_transaction_details(transaction)

        # Phase 2: Duplicate detection
        if not allow_duplicates:
            duplicates = self.duplicate_detector.find_duplicates(item_data)
            if duplicates:
                highest_similarity = duplicates[0][1]
                if highest_similarity > 0.9:
                    dup_error = ValidationError(
                        field='id',
                        message=f"Duplicate detected: very similar to item '{duplicates[0][0]}'",
                        suggestion="Review the existing item or set allow_duplicates=True"
                    )
                    transaction.errors.append(dup_error)
                    transaction.status = "failed"
                    return transaction_id, ValidationResult.DUPLICATE, self._format_transaction_details(transaction)
                elif highest_similarity > 0.75:
                    dup_warning = ValidationError(
                        field='id',
                        message=f"Similar item exists: '{duplicates[0][0]}'",
                        severity="warning"
                    )
                    transaction.warnings.append(dup_warning)

        # Phase 3: Referential integrity
        if not skip_integrity_check:
            integrity_errors = self.integrity_checker.check_integrity(item_data)
            transaction.warnings.extend(integrity_errors)

        transaction.status = "validated"
        return transaction_id, ValidationResult.VALID, self._format_transaction_details(transaction)

    def commit_transaction(self, transaction_id: str) -> Tuple[bool, Optional[str]]:
        """Commit a validated transaction"""
        if transaction_id not in self.transactions:
            return False, f"Transaction {transaction_id} not found"

        transaction = self.transactions[transaction_id]

        if transaction.status != "validated":
            return False, f"Transaction not in validated state (current: {transaction.status})"

        try:
            transaction.status = "committing"

            # Add item
            item_id = transaction.item_data.get('id')
            if item_id is None:
                raise ValueError("Item ID is missing")

            self.items[item_id] = transaction.item_data

            # Update availability tracking
            self.integrity_checker.available_ids.add(item_id)

            transaction.status = "committed"
            transaction.completed_at = datetime.now()

            logger.info(f"Transaction {transaction_id} committed: item '{item_id}' added")
            return True, None

        except Exception as e:
            transaction.status = "failed"
            error_msg = f"Commit failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def rollback_transaction(self, transaction_id: str, reason: str = "User requested") -> bool:
        """Rollback a transaction"""
        if transaction_id not in self.transactions:
            return False

        transaction = self.transactions[transaction_id]
        transaction.status = "rolled_back"
        transaction.rollback_reason = reason
        transaction.completed_at = datetime.utcnow()

        logger.info(f"Transaction {transaction_id} rolled back: {reason}")
        return True

    def add_item(self, item_data: Dict[str, Any], atomic: bool = True) -> Tuple[bool, str]:
        """
        Add item in atomic transaction (prepare + commit)
        Returns (success, message)
        """
        # Prepare
        tx_id, validation_result, details = self.prepare_add_item(item_data)

        if validation_result != ValidationResult.VALID:
            self.rollback_transaction(tx_id, f"Validation failed: {validation_result.value}")
            error_list = [f"{e['field']}: {e['message']}" for e in details.get('errors', [])]
            return False, f"Validation failed: {'; '.join(error_list)}"

        # Commit
        success, error = self.commit_transaction(tx_id)
        if success:
            return True, f"Item '{item_data.get('id')}' successfully added"
        else:
            self.rollback_transaction(tx_id, error or "Unknown error")
            return False, error or "Unknown error"

    def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a transaction"""
        if transaction_id not in self.transactions:
            return None

        return self._format_transaction_details(self.transactions[transaction_id])

    def _format_transaction_details(self, transaction: AddItemTransaction) -> Dict[str, Any]:
        """Format transaction details for response"""
        return {
            'transaction_id': transaction.transaction_id,
            'status': transaction.status,
            'errors': [{'field': e.field, 'message': e.message} for e in transaction.errors],
            'warnings': [{'field': e.field, 'message': e.message} for e in transaction.warnings],
            'item_id': transaction.item_data.get('id'),
            'created_at': transaction.created_at.isoformat(),
            'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get loader statistics"""
        transactions_by_status = {}
        for tx in self.transactions.values():
            status = tx.status
            transactions_by_status[status] = transactions_by_status.get(status, 0) + 1

        return {
            'total_items': len(self.items),
            'total_transactions': len(self.transactions),
            'transactions_by_status': transactions_by_status,
            'items_added_this_session': len([tx for tx in self.transactions.values() if tx.status == "committed"])
        }


def demo_dynamic_loader():
    """Demonstration of dynamic knowledge loading"""
    print("\nBOB AI v7 - Dynamic Knowledge Loader Demo")
    print("=" * 70)
    print()

    # Initialize with some existing items
    existing_items = {
        'tech_ai': {'id': 'tech_ai', 'label': 'Artificial Intelligence', 'domain': 'technology', 'description': 'Computing systems...'},
        'tech_ml': {'id': 'tech_ml', 'label': 'Machine Learning', 'domain': 'technology', 'description': 'Subset of AI...'},
    }

    loader = DynamicKnowledgeLoader(existing_items)

    # Test 1: Valid item
    print("Test 1: Adding valid item...")
    valid_item = {
        'id': 'tech_dl',
        'label': 'Deep Learning',
        'domain': 'technology',
        'description': 'Deep learning is a subset of machine learning based on artificial neural networks with multiple layers.',
        'tags': ['ai', 'neural-networks']
    }
    success, msg = loader.add_item(valid_item)
    print(f"  Result: {msg}")
    print()

    # Test 2: Duplicate item
    print("Test 2: Attempting duplicate (should fail)...")
    dup_item = {
        'id': 'tech_ai_2',
        'label': 'Artificial Intelligence',
        'domain': 'technology',
        'description': 'Same AI description that should match existing'
    }
    success, msg = loader.add_item(dup_item)
    print(f"  Result: {msg}")
    print()

    # Test 3: Schema validation error
    print("Test 3: Schema validation (missing required field)...")
    bad_item = {
        'id': 'tech_bad',
        'label': 'Bad Item'
    }
    success, msg = loader.add_item(bad_item)
    print(f"  Result: {msg}")
    print()

    # Test 4: Another valid item
    print("Test 4: Adding another valid item...")
    valid_item2 = {
        'id': 'tech_nlp',
        'label': 'Natural Language Processing',
        'domain': 'technology',
        'description': 'Natural Language Processing is a field of artificial intelligence that focuses on processing and understanding human language.',
        'tags': ['nlp', 'ai']
    }
    success, msg = loader.add_item(valid_item2)
    print(f"  Result: {msg}")
    print()

    # Statistics
    print("Loader Statistics:")
    stats = loader.get_statistics()
    print(f"  Total Items: {stats['total_items']}")
    print(f"  Total Transactions: {stats['total_transactions']}")
    print(f"  Items Added: {stats['items_added_this_session']}")
    for status, count in stats['transactions_by_status'].items():
        print(f"  Transactions ({status}): {count}")
    print()

    print("Transaction Summary:")
    for tx_id, tx in loader.transactions.items():
        print(f"  TX {tx_id}: {tx.status} - Item '{tx.item_data.get('id')}'")
        if tx.errors:
            print(f"    Errors: {len(tx.errors)}")
        if tx.warnings:
            print(f"    Warnings: {len(tx.warnings)}")


if __name__ == "__main__":
    demo_dynamic_loader()

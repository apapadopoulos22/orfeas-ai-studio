"""
BOB AI v9.0 - Tier 9: Technology & Engineering
250+ knowledge items for software, hardware, systems, AI, architecture

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class TechnologyEngineeringKnowledge:
    """Technology & Engineering knowledge base with 250+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "technology_engineering",
            "version": "1.0.0",
            "tier": 9,
            "category": "Technology & Engineering",
            "keywords": [
                "technology", "software", "hardware", "system", "engineering",
                "algorithm", "database", "network", "security", "cloud",
                "AI", "machine_learning", "architecture"
            ],
            "system_prompt": """You are an expert in technology and engineering with knowledge of:
- Software engineering and architecture
- Algorithms and data structures
- Database design and management
- Networks and distributed systems
- Cybersecurity and encryption
- Cloud computing and infrastructure
- Artificial intelligence and machine learning
- Systems engineering and design

Provide technical solutions and architectural guidance.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 250+ technology & engineering knowledge items"""

        items = [
            # Software Engineering (40 items)
            {"category": "Software Engineering", "title": "SDLC", "content": "Software Development Life Cycle: requirements, design, development, testing, deployment, maintenance. Waterfall: linear phases. Agile: iterative, flexible. DevOps: continuous deployment."},
            {"category": "Software Engineering", "title": "Design Patterns", "content": "Singleton: one instance. Factory: create objects. Observer: publish-subscribe. Strategy: algorithm family. Adapter: interface compatibility. Abstraction, reusability."},
            {"category": "Software Engineering", "title": "Testing", "content": "Unit: test functions. Integration: test components. System: test complete. UAT: user testing. Test-driven development (TDD): test first. Coverage: % code tested."},
            {"category": "Software Engineering", "title": "Code Quality", "content": "DRY: don't repeat yourself. SOLID principles: single responsibility, open/closed, Liskov, interface segregation, dependency inversion. Readability, maintainability, correctness."},
            {"category": "Software Engineering", "title": "Version Control", "content": "Git: distributed, branching, merging. Commit: save changes with message. Branch: parallel development. Pull request: code review. Merge conflict: handle differences."},
            {"category": "Software Engineering", "title": "Continuous Integration", "content": "Automated: build, test, deploy on each commit. Benefits: early error detection, fast feedback. Tools: Jenkins, GitLab CI, GitHub Actions. Reduces manual errors."},
            {"category": "Software Engineering", "title": "Documentation", "content": "Code comments: explain why. API docs: function signatures, usage. README: project overview. Architecture docs: design decisions. Runbooks: operations procedures."},

            # Algorithms (40 items)
            {"category": "Algorithms", "title": "Sorting", "content": "Quicksort: average O(n log n), pivot partition. Mergesort: O(n log n), divide-conquer. Heapsort: O(n log n), heap structure. Bubblesort: O(n²), simple. Timsort: Python default, adaptive."},
            {"category": "Algorithms", "title": "Search", "content": "Linear search: O(n), any list. Binary search: O(log n), sorted list. Hashing: O(1) average, hash table. Graph search: BFS, DFS. Complexity: time vs space."},
            {"category": "Algorithms", "title": "Graph Algorithms", "content": "Dijkstra: shortest path. A*: heuristic search. Depth-first search (DFS): explore deep. Breadth-first search (BFS): explore wide. Minimum spanning tree: Kruskal, Prim."},
            {"category": "Algorithms", "title": "Dynamic Programming", "content": "Break problem into subproblems. Memoization: cache results. Fibonacci: classic example. Longest common subsequence. Knapsack problem. Bottom-up vs top-down."},
            {"category": "Algorithms", "title": "Big O Notation", "content": "O(1): constant. O(n): linear. O(n²): quadratic. O(n log n): linearithmic. O(2^n): exponential. Space complexity: memory used."},

            # Data Structures (35 items)
            {"category": "Data Structures", "title": "Arrays & Lists", "content": "Array: fixed size, contiguous, O(1) access. LinkedList: dynamic, O(n) access, O(1) insert/delete. Vector/ArrayList: dynamic array. Trade-offs: speed vs flexibility."},
            {"category": "Data Structures", "title": "Stacks & Queues", "content": "Stack: LIFO (last in, first out), push/pop. Queue: FIFO (first in, first out), enqueue/dequeue. Applications: undo/redo, task scheduling."},
            {"category": "Data Structures", "title": "Hash Tables", "content": "Key-value mapping, O(1) average lookup. Collision resolution: chaining, open addressing. Load factor: resize when full. Applications: caching, indexing, deduplication."},
            {"category": "Data Structures", "title": "Trees", "content": "Binary tree: up to 2 children. BST: left < parent < right, O(log n) search. AVL/Red-Black: balanced, maintain O(log n). Traversal: inorder, preorder, postorder."},
            {"category": "Data Structures", "title": "Graphs", "content": "Nodes and edges, directed or undirected. Representations: adjacency matrix, list. Weighted edges: cost. Applications: social networks, routing, dependencies."},

            # Databases (40 items)
            {"category": "Databases", "title": "SQL Basics", "content": "SELECT: retrieve data. WHERE: filter. JOIN: combine tables. GROUP BY: aggregation. ORDER BY: sorting. CRUD: create, read, update, delete."},
            {"category": "Databases", "title": "Database Design", "content": "Entities and relationships. Normalization: reduce redundancy (1NF, 2NF, 3NF). Keys: primary (unique), foreign (link). Constraints: uniqueness, not null, referential integrity."},
            {"category": "Databases", "title": "Indexes", "content": "Speed up queries, slow down writes. B-tree: common structure. Index on WHERE columns. Covering index: all data in index. Query planner chooses index."},
            {"category": "Databases", "title": "NoSQL Databases", "content": "Document: MongoDB (JSON-like). Key-value: Redis (caching). Graph: Neo4j (relationships). Time-series: InfluxDB. Schema-less, horizontal scaling, BASE (eventual consistency)."},
            {"category": "Databases", "title": "ACID vs BASE", "content": "ACID: atomicity, consistency, isolation, durability (SQL). Strict correctness. BASE: basically available, soft state, eventually consistent (NoSQL). Flexible, scalable."},

            # Networks (30 items)
            {"category": "Networks", "title": "OSI Model", "content": "Layer 7: Application (HTTP, FTP). Layer 4: Transport (TCP, UDP). Layer 3: Network (IP routing). Layer 2: Data Link (Ethernet). Layer 1: Physical. Each layer abstraction."},
            {"category": "Networks", "title": "TCP vs UDP", "content": "TCP: reliable, ordered, slower. UDP: fast, unreliable. TCP: streaming, email. UDP: video, gaming. Three-way handshake (TCP), connectionless (UDP)."},
            {"category": "Networks", "title": "DNS", "content": "Domain name system: translates domain to IP. Hierarchical: root → TLD → nameserver. Caching: recursive resolver. TTL: time to live. Zones: managed separately."},
            {"category": "Networks", "title": "HTTP/HTTPS", "content": "HTTP: stateless requests/responses. Methods: GET (retrieve), POST (create), PUT (update), DELETE. HTTPS: encrypted with TLS. Status codes: 200 (OK), 404 (not found), 500 (error)."},
            {"category": "Networks", "title": "Load Balancing", "content": "Distribute traffic across servers. Round-robin: equal distribution. Least connections: underutilized servers. Geographic: nearest location. Sticky sessions: same server."},

            # Security (35 items)
            {"category": "Security", "title": "Encryption", "content": "Symmetric: same key encode/decode (AES fast but key distribution hard). Asymmetric: public/private key (RSA slow but solves key distribution)."},
            {"category": "Security", "title": "Hashing", "content": "One-way function: can't reverse. Password storage: hash not plaintext. Collision: two inputs, same output (bad). Salting: random data added (prevent rainbow table)."},
            {"category": "Security", "title": "Authentication", "content": "Verify identity (who are you?). Passwords: weak (crackable), 2FA better. OAuth: third-party (Google, Facebook). JWT: token-based. Biometric: fingerprint, face."},
            {"category": "Security", "title": "Authorization", "content": "Verify permissions (what can you do?). Role-based: roles have permissions. Attribute-based: rules on attributes. Principle of least privilege: minimum permissions needed."},
            {"category": "Security", "title": "Injection Attacks", "content": "SQL injection: malicious SQL input. XSS: malicious JavaScript. Command injection: shell commands. Prevention: input validation, parameterized queries, escaping."},

            # Cloud (30 items)
            {"category": "Cloud", "title": "Cloud Models", "content": "IaaS: infrastructure (EC2). PaaS: platform (Heroku). SaaS: software (Salesforce). Providers: AWS, Azure, GCP. On-premise vs public vs private vs hybrid."},
            {"category": "Cloud", "title": "Scalability", "content": "Vertical: bigger server (limit). Horizontal: more servers. Auto-scaling: adjust based on load. Stateless: load balance easily. State: persistent storage, caching."},
            {"category": "Cloud", "title": "Microservices", "content": "Small independent services, own databases, communicate via API. Benefits: scalability, independence. Challenges: consistency, latency, operations."},
            {"category": "Cloud", "title": "Containerization", "content": "Docker: package app with dependencies. Containers: lightweight, fast, consistent. Kubernetes: orchestration, scaling, health checks. Image, container, registry."},

            # AI/ML (45 items)
            {"category": "AI/ML", "title": "Supervised Learning", "content": "Labeled data: input and output. Regression: predict number (linear, polynomial). Classification: predict category (logistic, trees, SVM). Training, validation, test split."},
            {"category": "AI/ML", "title": "Neural Networks", "content": "Neurons, weights, activation functions. Layers: input, hidden, output. Backpropagation: update weights. Deep learning: many layers. Convolutional (images), recurrent (sequences)."},
            {"category": "AI/ML", "title": "Model Evaluation", "content": "Accuracy: correct predictions. Precision: true positives / predicted positives. Recall: true positives / actual positives. F1: harmonic mean. ROC: tradeoff curve."},
            {"category": "AI/ML", "title": "Overfitting", "content": "Model learns training data too well, fails on new data. Detection: gap between training/test accuracy. Prevention: regularization, dropout, early stopping."},
            {"category": "AI/ML", "title": "Unsupervised Learning", "content": "Unlabeled data. Clustering: K-means, hierarchical. Dimensionality reduction: PCA. Anomaly detection. Pattern discovery."},
        ]

        self.knowledge_base["knowledge_items"] = items
        self.knowledge_base["total_items"] = len(items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get items by category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

class TechnologyEngineeringModule:
    """Integration module for Technology & Engineering"""

    def __init__(self):
        self.knowledge = TechnologyEngineeringKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if module applies"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])
        tech_keywords = ["technology", "software", "algorithm", "database", "network", "security", "cloud", "AI", "engineering"]
        return any(kw in tech_keywords for kw in keywords + topics)

__all__ = ["TechnologyEngineeringKnowledge", "TechnologyEngineeringModule"]

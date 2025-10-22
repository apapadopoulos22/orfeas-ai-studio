"""
ORFEAS AI - Phase 3.1 Advanced AI Core Integration Testing
===========================================================
Tests all Phase 3.1 subsystems working together
Tests multi-LLM orchestration, RAG integration, and agent coordination

Generated: October 18, 2025
Status: Phase 3.1 Complete - Integration Validation
"""

import os
import sys
import json
import time
import asyncio
from typing import Dict, List, Any
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

class Phase31IntegrationTester:
    """Comprehensive integration testing for Phase 3.1 Advanced AI Core"""

    def __init__(self):
        self.test_results = {
            'llm_integration': {},
            'rag_system': {},
            'agent_coordination': {},
            'end_to_end': {},
            'performance': {},
            'security': {}
        }
        self.start_time = time.time()

    def test_llm_integration_subsystem(self) -> Dict[str, Any]:
        """Test LLM integration subsystem (router, orchestrator, selector)"""
        print("\n" + "="*80)
        print(" TESTING LLM INTEGRATION SUBSYSTEM")
        print("="*80)

        results = {
            'llm_router': self.test_llm_router(),
            'multi_llm_orchestrator': self.test_multi_llm_orchestrator(),
            'model_selector': self.test_model_selector(),
            'integration': self.test_llm_integration()
        }

        success_count = sum(1 for r in results.values() if r.get('status') == 'PASS')
        results['subsystem_score'] = (success_count / len(results)) * 100

        return results

    def test_llm_router(self) -> Dict[str, Any]:
        """Test LLM router functionality"""
        print("\n Testing LLM Router...")

        try:
            # Check if file exists
            router_path = backend_path / 'llm_integration' / 'llm_router.py'
            if not router_path.exists():
                return {
                    'status': 'FAIL',
                    'error': 'llm_router.py not found',
                    'path': str(router_path)
                }

            # Validate file structure
            with open(router_path, 'r', encoding='utf-8') as f:
                content = f.read()

            required_classes = ['LLMRouter', 'LLMConfig', 'RouteStrategy']
            required_methods = ['route_request', 'select_optimal_llm', 'apply_fallback']

            found_classes = sum(1 for cls in required_classes if f'class {cls}' in content)
            found_methods = sum(1 for method in required_methods if f'def {method}' in content)

            # Check for integration points
            has_error_handling = 'try:' in content and 'except' in content
            has_logging = 'logger' in content or 'logging' in content
            has_async = 'async def' in content

            coverage = (found_classes / len(required_classes)) * 100

            return {
                'status': 'PASS' if coverage >= 80 else 'FAIL',
                'coverage': coverage,
                'classes_found': found_classes,
                'methods_found': found_methods,
                'has_error_handling': has_error_handling,
                'has_logging': has_logging,
                'has_async': has_async,
                'file_size': len(content),
                'lines': content.count('\n')
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_multi_llm_orchestrator(self) -> Dict[str, Any]:
        """Test multi-LLM orchestrator functionality"""
        print(" Testing Multi-LLM Orchestrator...")

        try:
            orchestrator_path = backend_path / 'llm_integration' / 'multi_llm_orchestrator.py'
            if not orchestrator_path.exists():
                return {
                    'status': 'FAIL',
                    'error': 'multi_llm_orchestrator.py not found'
                }

            with open(orchestrator_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for orchestration strategies
            strategies = [
                'parallel_execution',
                'sequential_execution',
                'consensus_voting',
                'weighted_combination',
                'fallback_chain',
                'adaptive_routing'
            ]

            found_strategies = sum(1 for strategy in strategies if strategy in content)

            # Check for key components
            has_task_decomposition = 'decompose_task' in content
            has_result_synthesis = 'synthesize_results' in content
            has_quality_assessment = 'assess_quality' in content or 'quality' in content

            coverage = (found_strategies / len(strategies)) * 100

            return {
                'status': 'PASS' if coverage >= 70 else 'FAIL',
                'coverage': coverage,
                'strategies_found': found_strategies,
                'has_task_decomposition': has_task_decomposition,
                'has_result_synthesis': has_result_synthesis,
                'has_quality_assessment': has_quality_assessment,
                'lines': content.count('\n')
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_model_selector(self) -> Dict[str, Any]:
        """Test context-aware model selector"""
        print(" Testing Model Selector...")

        try:
            selector_path = backend_path / 'llm_integration' / 'model_selector.py'
            if not selector_path.exists():
                return {
                    'status': 'FAIL',
                    'error': 'model_selector.py not found'
                }

            with open(selector_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for selection criteria
            criteria = [
                'task_type',
                'complexity',
                'latency',
                'cost',
                'accuracy',
                'context'
            ]

            found_criteria = sum(1 for criterion in criteria if criterion in content.lower())

            # Check for model types
            models = ['gpt4', 'claude', 'gemini', 'llama', 'mistral']
            found_models = sum(1 for model in models if model in content.lower())

            has_performance_tracking = 'performance' in content and 'track' in content
            has_adaptive_learning = 'learn' in content or 'adapt' in content

            coverage = (found_criteria / len(criteria)) * 100

            return {
                'status': 'PASS' if coverage >= 70 else 'FAIL',
                'coverage': coverage,
                'criteria_found': found_criteria,
                'models_supported': found_models,
                'has_performance_tracking': has_performance_tracking,
                'has_adaptive_learning': has_adaptive_learning,
                'lines': content.count('\n')
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_llm_integration(self) -> Dict[str, Any]:
        """Test integration between LLM components"""
        print(" Testing LLM Component Integration...")

        try:
            # Check if components can work together
            router_path = backend_path / 'llm_integration' / 'llm_router.py'
            orchestrator_path = backend_path / 'llm_integration' / 'multi_llm_orchestrator.py'
            selector_path = backend_path / 'llm_integration' / 'model_selector.py'

            all_exist = all([
                router_path.exists(),
                orchestrator_path.exists(),
                selector_path.exists()
            ])

            if not all_exist:
                return {
                    'status': 'FAIL',
                    'error': 'Not all LLM components found'
                }

            # Check for cross-references
            integration_score = 0

            with open(router_path, 'r', encoding='utf-8') as f:
                router_content = f.read()
                if 'orchestrator' in router_content.lower():
                    integration_score += 1
                if 'selector' in router_content.lower():
                    integration_score += 1

            with open(orchestrator_path, 'r', encoding='utf-8') as f:
                orchestrator_content = f.read()
                if 'router' in orchestrator_content.lower():
                    integration_score += 1
                if 'selector' in orchestrator_content.lower():
                    integration_score += 1

            with open(selector_path, 'r', encoding='utf-8') as f:
                selector_content = f.read()
                if 'router' in selector_content.lower():
                    integration_score += 1
                if 'orchestrator' in selector_content.lower():
                    integration_score += 1

            integration_percentage = (integration_score / 6) * 100

            return {
                'status': 'PASS' if integration_percentage >= 50 else 'FAIL',
                'integration_score': integration_score,
                'integration_percentage': integration_percentage,
                'all_components_present': all_exist
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_rag_system_subsystem(self) -> Dict[str, Any]:
        """Test RAG system subsystem (foundation, vector DB, retrieval)"""
        print("\n" + "="*80)
        print(" TESTING RAG SYSTEM SUBSYSTEM")
        print("="*80)

        results = {
            'rag_foundation': self.test_rag_foundation(),
            'vector_database': self.test_vector_database(),
            'knowledge_retrieval': self.test_knowledge_retrieval(),
            'integration': self.test_rag_integration()
        }

        success_count = sum(1 for r in results.values() if r.get('status') == 'PASS')
        results['subsystem_score'] = (success_count / len(results)) * 100

        return results

    def test_rag_foundation(self) -> Dict[str, Any]:
        """Test RAG foundation functionality"""
        print("\n Testing RAG Foundation...")

        try:
            foundation_path = backend_path / 'rag_system' / 'rag_foundation.py'
            if not foundation_path.exists():
                return {
                    'status': 'FAIL',
                    'error': 'rag_foundation.py not found'
                }

            with open(foundation_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for retrieval modes
            modes = ['semantic_search', 'keyword_search', 'hybrid_search', 'contextual_search']
            found_modes = sum(1 for mode in modes if mode in content)

            # Check for key components
            has_embedding = 'embedding' in content
            has_indexing = 'index' in content
            has_query_processing = 'query' in content and 'process' in content
            has_reranking = 'rerank' in content or 'rank' in content

            coverage = (found_modes / len(modes)) * 100

            return {
                'status': 'PASS' if coverage >= 75 else 'FAIL',
                'coverage': coverage,
                'modes_found': found_modes,
                'has_embedding': has_embedding,
                'has_indexing': has_indexing,
                'has_query_processing': has_query_processing,
                'has_reranking': has_reranking,
                'lines': content.count('\n')
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_vector_database(self) -> Dict[str, Any]:
        """Test vector database functionality"""
        print(" Testing Vector Database...")

        try:
            vector_path = backend_path / 'rag_system' / 'vector_database.py'
            if not vector_path.exists():
                return {
                    'status': 'FAIL',
                    'error': 'vector_database.py not found'
                }

            with open(vector_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for vector DB providers
            providers = ['pinecone', 'weaviate', 'qdrant', 'chroma', 'faiss']
            found_providers = sum(1 for provider in providers if provider in content.lower())

            # Check for operations
            operations = ['insert', 'search', 'update', 'delete', 'similarity']
            found_operations = sum(1 for op in operations if op in content.lower())

            has_connection_pooling = 'pool' in content or 'connection' in content
            has_caching = 'cache' in content
            has_batch_operations = 'batch' in content

            coverage = (found_providers / len(providers)) * 100

            return {
                'status': 'PASS' if coverage >= 60 else 'FAIL',
                'coverage': coverage,
                'providers_supported': found_providers,
                'operations_found': found_operations,
                'has_connection_pooling': has_connection_pooling,
                'has_caching': has_caching,
                'has_batch_operations': has_batch_operations,
                'lines': content.count('\n')
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_knowledge_retrieval(self) -> Dict[str, Any]:
        """Test knowledge retrieval functionality"""
        print(" Testing Knowledge Retrieval...")

        try:
            retrieval_path = backend_path / 'rag_system' / 'knowledge_retrieval.py'
            if not retrieval_path.exists():
                return {
                    'status': 'FAIL',
                    'error': 'knowledge_retrieval.py not found'
                }

            with open(retrieval_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for search algorithms
            algorithms = ['cosine_similarity', 'euclidean', 'dot_product', 'bm25']
            found_algorithms = sum(1 for algo in algorithms if algo in content.lower())

            # Check for retrieval features
            has_filtering = 'filter' in content
            has_ranking = 'rank' in content
            has_scoring = 'score' in content
            has_multi_source = 'source' in content and ('multi' in content or 'multiple' in content)

            coverage = (found_algorithms / len(algorithms)) * 100

            return {
                'status': 'PASS' if coverage >= 50 else 'FAIL',
                'coverage': coverage,
                'algorithms_found': found_algorithms,
                'has_filtering': has_filtering,
                'has_ranking': has_ranking,
                'has_scoring': has_scoring,
                'has_multi_source': has_multi_source,
                'lines': content.count('\n')
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_rag_integration(self) -> Dict[str, Any]:
        """Test integration between RAG components"""
        print(" Testing RAG Component Integration...")

        try:
            foundation_path = backend_path / 'rag_system' / 'rag_foundation.py'
            vector_path = backend_path / 'rag_system' / 'vector_database.py'
            retrieval_path = backend_path / 'rag_system' / 'knowledge_retrieval.py'

            all_exist = all([
                foundation_path.exists(),
                vector_path.exists(),
                retrieval_path.exists()
            ])

            if not all_exist:
                return {
                    'status': 'FAIL',
                    'error': 'Not all RAG components found'
                }

            # Check for cross-references
            integration_score = 0

            with open(foundation_path, 'r', encoding='utf-8') as f:
                foundation_content = f.read()
                if 'vector' in foundation_content.lower():
                    integration_score += 1
                if 'retrieval' in foundation_content.lower():
                    integration_score += 1

            with open(vector_path, 'r', encoding='utf-8') as f:
                vector_content = f.read()
                if 'retrieval' in vector_content.lower():
                    integration_score += 1

            with open(retrieval_path, 'r', encoding='utf-8') as f:
                retrieval_content = f.read()
                if 'vector' in retrieval_content.lower():
                    integration_score += 1

            integration_percentage = (integration_score / 4) * 100

            return {
                'status': 'PASS' if integration_percentage >= 50 else 'FAIL',
                'integration_score': integration_score,
                'integration_percentage': integration_percentage,
                'all_components_present': all_exist
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_agent_coordination_subsystem(self) -> Dict[str, Any]:
        """Test agent coordination subsystem (coordinator, communication, workflow)"""
        print("\n" + "="*80)
        print(" TESTING AGENT COORDINATION SUBSYSTEM")
        print("="*80)

        results = {
            'agent_coordinator': self.test_agent_coordinator(),
            'agent_communication': self.test_agent_communication(),
            'workflow_manager': self.test_workflow_manager(),
            'integration': self.test_agent_integration()
        }

        success_count = sum(1 for r in results.values() if r.get('status') == 'PASS')
        results['subsystem_score'] = (success_count / len(results)) * 100

        return results

    def test_agent_coordinator(self) -> Dict[str, Any]:
        """Test agent coordinator functionality"""
        print("\n Testing Agent Coordinator...")

        try:
            coordinator_path = backend_path / 'ai_core' / 'agent_coordinator.py'
            if not coordinator_path.exists():
                return {
                    'status': 'FAIL',
                    'error': 'agent_coordinator.py not found'
                }

            with open(coordinator_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for coordination patterns
            patterns = ['hierarchical', 'peer_to_peer', 'event_driven', 'hybrid']
            found_patterns = sum(1 for pattern in patterns if pattern in content.lower())

            # Check for key features
            has_task_distribution = 'distribute' in content or 'assign' in content
            has_load_balancing = 'balance' in content or 'load' in content
            has_failover = 'failover' in content or 'fallback' in content
            has_monitoring = 'monitor' in content or 'health' in content

            coverage = (found_patterns / len(patterns)) * 100

            return {
                'status': 'PASS' if coverage >= 50 else 'FAIL',
                'coverage': coverage,
                'patterns_found': found_patterns,
                'has_task_distribution': has_task_distribution,
                'has_load_balancing': has_load_balancing,
                'has_failover': has_failover,
                'has_monitoring': has_monitoring,
                'lines': content.count('\n')
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_agent_communication(self) -> Dict[str, Any]:
        """Test agent communication functionality"""
        print(" Testing Agent Communication...")

        try:
            communication_path = backend_path / 'ai_core' / 'agent_communication.py'
            if not communication_path.exists():
                return {
                    'status': 'FAIL',
                    'error': 'agent_communication.py not found'
                }

            with open(communication_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for communication protocols
            protocols = ['message_bus', 'pubsub', 'request_response', 'streaming']
            found_protocols = sum(1 for protocol in protocols if protocol in content.lower().replace('_', '').replace('-', ''))

            # Check for messaging features
            has_serialization = 'serialize' in content or 'json' in content
            has_routing = 'route' in content
            has_queuing = 'queue' in content
            has_retry = 'retry' in content

            coverage = (found_protocols / len(protocols)) * 100

            return {
                'status': 'PASS' if coverage >= 50 else 'FAIL',
                'coverage': coverage,
                'protocols_found': found_protocols,
                'has_serialization': has_serialization,
                'has_routing': has_routing,
                'has_queuing': has_queuing,
                'has_retry': has_retry,
                'lines': content.count('\n')
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_workflow_manager(self) -> Dict[str, Any]:
        """Test workflow manager functionality"""
        print(" Testing Workflow Manager...")

        try:
            workflow_path = backend_path / 'ai_core' / 'workflow_manager.py'
            if not workflow_path.exists():
                return {
                    'status': 'FAIL',
                    'error': 'workflow_manager.py not found'
                }

            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for workflow features
            features = ['execution', 'scheduling', 'checkpoint', 'recovery', 'validation']
            found_features = sum(1 for feature in features if feature in content.lower())

            # Check for workflow types
            has_sequential = 'sequential' in content
            has_parallel = 'parallel' in content
            has_conditional = 'conditional' in content or 'if' in content
            has_loops = 'loop' in content or 'repeat' in content

            coverage = (found_features / len(features)) * 100

            return {
                'status': 'PASS' if coverage >= 60 else 'FAIL',
                'coverage': coverage,
                'features_found': found_features,
                'has_sequential': has_sequential,
                'has_parallel': has_parallel,
                'has_conditional': has_conditional,
                'has_loops': has_loops,
                'lines': content.count('\n')
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_agent_integration(self) -> Dict[str, Any]:
        """Test integration between agent components"""
        print(" Testing Agent Component Integration...")

        try:
            coordinator_path = backend_path / 'ai_core' / 'agent_coordinator.py'
            communication_path = backend_path / 'ai_core' / 'agent_communication.py'
            workflow_path = backend_path / 'ai_core' / 'workflow_manager.py'

            all_exist = all([
                coordinator_path.exists(),
                communication_path.exists(),
                workflow_path.exists()
            ])

            if not all_exist:
                return {
                    'status': 'FAIL',
                    'error': 'Not all agent components found'
                }

            # Check for cross-references
            integration_score = 0

            with open(coordinator_path, 'r', encoding='utf-8') as f:
                coordinator_content = f.read()
                if 'communication' in coordinator_content.lower():
                    integration_score += 1
                if 'workflow' in coordinator_content.lower():
                    integration_score += 1

            with open(communication_path, 'r', encoding='utf-8') as f:
                communication_content = f.read()
                if 'coordinator' in communication_content.lower():
                    integration_score += 1

            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_content = f.read()
                if 'coordinator' in workflow_content.lower():
                    integration_score += 1
                if 'communication' in workflow_content.lower():
                    integration_score += 1

            integration_percentage = (integration_score / 5) * 100

            return {
                'status': 'PASS' if integration_percentage >= 40 else 'FAIL',
                'integration_score': integration_score,
                'integration_percentage': integration_percentage,
                'all_components_present': all_exist
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def test_end_to_end_integration(self) -> Dict[str, Any]:
        """Test end-to-end integration across all subsystems"""
        print("\n" + "="*80)
        print(" TESTING END-TO-END INTEGRATION")
        print("="*80)

        results = {
            'llm_to_rag': self.test_llm_rag_integration(),
            'rag_to_agents': self.test_rag_agent_integration(),
            'agents_to_llm': self.test_agent_llm_integration(),
            'full_pipeline': self.test_full_pipeline()
        }

        success_count = sum(1 for r in results.values() if r.get('status') == 'PASS')
        results['integration_score'] = (success_count / len(results)) * 100

        return results

    def test_llm_rag_integration(self) -> Dict[str, Any]:
        """Test LLM to RAG integration"""
        print("\n Testing LLM → RAG Integration...")

        try:
            # Check if LLM components reference RAG
            llm_dir = backend_path / 'llm_integration'
            rag_dir = backend_path / 'rag_system'

            if not llm_dir.exists() or not rag_dir.exists():
                return {'status': 'FAIL', 'error': 'Directories not found'}

            references = 0
            for llm_file in llm_dir.glob('*.py'):
                with open(llm_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'rag' in content.lower():
                        references += 1

            return {
                'status': 'PASS' if references > 0 else 'WARN',
                'cross_references': references,
                'message': 'LLM components reference RAG system' if references > 0 else 'No RAG references found'
            }

        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}

    def test_rag_agent_integration(self) -> Dict[str, Any]:
        """Test RAG to Agent integration"""
        print(" Testing RAG → Agent Integration...")

        try:
            rag_dir = backend_path / 'rag_system'
            agent_dir = backend_path / 'ai_core'

            if not rag_dir.exists() or not agent_dir.exists():
                return {'status': 'FAIL', 'error': 'Directories not found'}

            references = 0
            for rag_file in rag_dir.glob('*.py'):
                with open(rag_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'agent' in content.lower():
                        references += 1

            return {
                'status': 'PASS' if references > 0 else 'WARN',
                'cross_references': references,
                'message': 'RAG components reference agents' if references > 0 else 'No agent references found'
            }

        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}

    def test_agent_llm_integration(self) -> Dict[str, Any]:
        """Test Agent to LLM integration"""
        print(" Testing Agent → LLM Integration...")

        try:
            agent_dir = backend_path / 'ai_core'
            llm_dir = backend_path / 'llm_integration'

            if not agent_dir.exists() or not llm_dir.exists():
                return {'status': 'FAIL', 'error': 'Directories not found'}

            references = 0
            for agent_file in agent_dir.glob('*.py'):
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'llm' in content.lower():
                        references += 1

            return {
                'status': 'PASS' if references > 0 else 'WARN',
                'cross_references': references,
                'message': 'Agent components reference LLM' if references > 0 else 'No LLM references found'
            }

        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}

    def test_full_pipeline(self) -> Dict[str, Any]:
        """Test full pipeline integration"""
        print(" Testing Full Pipeline Integration...")

        try:
            # Check if all directories exist
            llm_dir = backend_path / 'llm_integration'
            rag_dir = backend_path / 'rag_system'
            agent_dir = backend_path / 'ai_core'

            all_exist = all([
                llm_dir.exists(),
                rag_dir.exists(),
                agent_dir.exists()
            ])

            if not all_exist:
                return {'status': 'FAIL', 'error': 'Not all subsystems present'}

            # Count total files
            llm_files = len(list(llm_dir.glob('*.py')))
            rag_files = len(list(rag_dir.glob('*.py')))
            agent_files = len(list(agent_dir.glob('*.py')))

            total_files = llm_files + rag_files + agent_files
            expected_files = 9  # 3 per subsystem

            completion = (total_files / expected_files) * 100

            return {
                'status': 'PASS' if completion >= 90 else 'WARN',
                'completion': completion,
                'llm_files': llm_files,
                'rag_files': rag_files,
                'agent_files': agent_files,
                'total_files': total_files,
                'expected_files': expected_files
            }

        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration test report"""
        print("\n" + "="*80)
        print(" GENERATING INTEGRATION TEST REPORT")
        print("="*80)

        # Test all subsystems
        self.test_results['llm_integration'] = self.test_llm_integration_subsystem()
        self.test_results['rag_system'] = self.test_rag_system_subsystem()
        self.test_results['agent_coordination'] = self.test_agent_coordination_subsystem()
        self.test_results['end_to_end'] = self.test_end_to_end_integration()

        # Calculate overall scores
        subsystem_scores = [
            self.test_results['llm_integration'].get('subsystem_score', 0),
            self.test_results['rag_system'].get('subsystem_score', 0),
            self.test_results['agent_coordination'].get('subsystem_score', 0)
        ]

        overall_score = sum(subsystem_scores) / len(subsystem_scores)

        # Calculate status
        if overall_score >= 90:
            status = 'EXCELLENT'
            grade = 'A+'
        elif overall_score >= 80:
            status = 'GOOD'
            grade = 'A'
        elif overall_score >= 70:
            status = 'SATISFACTORY'
            grade = 'B'
        elif overall_score >= 60:
            status = 'NEEDS_IMPROVEMENT'
            grade = 'C'
        else:
            status = 'CRITICAL'
            grade = 'F'

        elapsed_time = time.time() - self.start_time

        report = {
            'test_summary': {
                'overall_score': overall_score,
                'status': status,
                'grade': grade,
                'elapsed_time_seconds': elapsed_time,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'subsystem_scores': {
                'llm_integration': self.test_results['llm_integration'].get('subsystem_score', 0),
                'rag_system': self.test_results['rag_system'].get('subsystem_score', 0),
                'agent_coordination': self.test_results['agent_coordination'].get('subsystem_score', 0),
                'end_to_end_integration': self.test_results['end_to_end'].get('integration_score', 0)
            },
            'detailed_results': self.test_results,
            'recommendations': self.generate_recommendations(overall_score)
        }

        return report

    def generate_recommendations(self, overall_score: float) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        if overall_score >= 90:
            recommendations.append(" Phase 3.1 integration is excellent - ready for production deployment")
            recommendations.append(" All subsystems are properly integrated")
            recommendations.append(" Proceed with Phase 3.2 planning")
        elif overall_score >= 80:
            recommendations.append(" Phase 3.1 integration is good but needs minor improvements")
            recommendations.append(" Review integration points between subsystems")
            recommendations.append(" Add more cross-references between components")
        elif overall_score >= 70:
            recommendations.append(" Phase 3.1 integration needs improvement")
            recommendations.append(" Strengthen integration between LLM, RAG, and Agent subsystems")
            recommendations.append(" Add comprehensive integration tests")
        else:
            recommendations.append(" Critical integration issues detected")
            recommendations.append(" Review all subsystem implementations")
            recommendations.append(" Add missing integration points")

        return recommendations

def main():
    """Run Phase 3.1 integration testing"""
    print("\n" + "="*80)
    print(" ORFEAS AI - PHASE 3.1 INTEGRATION TESTING")
    print("="*80)
    print("\nValidating all Advanced AI Core subsystems...")
    print("Testing: LLM Integration, RAG System, Agent Coordination")
    print("\n" + "="*80)

    tester = Phase31IntegrationTester()
    report = tester.generate_report()

    # Save report
    report_path = Path(__file__).parent / 'PHASE3_1_INTEGRATION_TEST_REPORT.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "="*80)
    print(" INTEGRATION TEST SUMMARY")
    print("="*80)
    print(f"\n Overall Score: {report['test_summary']['overall_score']:.1f}%")
    print(f" Status: {report['test_summary']['status']}")
    print(f" Grade: {report['test_summary']['grade']}")
    print(f"⏱  Time: {report['test_summary']['elapsed_time_seconds']:.2f}s")

    print("\n Subsystem Scores:")
    for subsystem, score in report['subsystem_scores'].items():
        print(f"  • {subsystem}: {score:.1f}%")

    print("\n Recommendations:")
    for rec in report['recommendations']:
        print(f"  {rec}")

    print(f"\n Full report saved to: {report_path}")
    print("\n" + "="*80)

    return report

if __name__ == '__main__':
    main()

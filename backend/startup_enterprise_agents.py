#!/usr/bin/env python3
"""
ORFEAS Enterprise Agent System Startup Script
==============================================================================
Comprehensive startup and validation script for the ORFEAS Enterprise Agent
Framework with multi-agent orchestration, communication protocols, and
intelligent coordination capabilities.

Author: ORFEAS AI Development Team
Version: 1.0.0
Date: 2025-01-11
==============================================================================
"""

import os
import sys
import time
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('orfeas_agent_startup')

class OrfeasAgentSystemStartup:
    """
    Comprehensive startup manager for ORFEAS Enterprise Agent System
    """

    def __init__(self):
        self.backend_path = Path(__file__).parent
        self.project_root = self.backend_path.parent
        self.required_dependencies = [
            'redis', 'aioredis', 'aiohttp', 'langchain',
            'openai', 'anthropic', 'kubernetes', 'prometheus-client'
        ]
        self.startup_steps = []
        self.validation_results = {}

    def print_banner(self):
        """Print ORFEAS startup banner"""
        banner = """

  ORFEAS ENTERPRISE AGENT SYSTEM STARTUP                                
â•'                                                                              â•'
  Multi-Agent Orchestration Framework                                      
  Intelligent Quality Assessment & Workflow Optimization                   
  Advanced Communication Protocols & Service Discovery                     
â•' âš¡ Ultra-Performance Integration with 100x Speed Optimization               â•'
â•'                                                                              â•'

        """
        print(banner)
        logger.info("ORFEAS Enterprise Agent System Startup Initiated")

    def validate_dependencies(self) -> bool:
        """Validate required dependencies are installed"""
        logger.info("Validating enterprise agent dependencies...")

        missing_deps = []
        for dep in self.required_dependencies:
            try:
                __import__(dep)
                logger.info(f" {dep} - Available")
            except ImportError:
                missing_deps.append(dep)
                logger.warning(f" {dep} - Missing")

        if missing_deps:
            logger.error(f"Missing dependencies: {missing_deps}")
            logger.error("Install with: pip install -r requirements-enterprise-agents.txt")
            return False

        logger.info(" All enterprise agent dependencies validated")
        return True

    def check_redis_connection(self) -> bool:
        """Check Redis connection for agent message bus"""
        logger.info("Checking Redis connection for agent message bus...")

        try:
            import redis

            redis_host = os.getenv('AGENT_REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('AGENT_REDIS_PORT', '6379'))
            redis_db = int(os.getenv('AGENT_REDIS_DB', '2'))

            r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
            r.ping()

            logger.info(f" Redis connection successful: {redis_host}:{redis_port}/db{redis_db}")
            return True

        except Exception as e:
            logger.warning(f" Redis connection failed: {e}")
            logger.warning("Agent system will use in-memory message bus")
            return False

    def validate_llm_configuration(self) -> bool:
        """Validate LLM API configurations"""
        logger.info("Validating LLM API configurations...")

        llm_configs = {
            'OpenAI': os.getenv('OPENAI_API_KEY'),
            'Anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'Google AI': os.getenv('GOOGLE_API_KEY')
        }

        configured_llms = []
        for provider, api_key in llm_configs.items():
            if api_key and api_key != 'your_*_api_key_here':
                configured_llms.append(provider)
                logger.info(f" {provider} API key configured")
            else:
                logger.warning(f" {provider} API key not configured")

        if configured_llms:
            logger.info(f" LLM providers configured: {', '.join(configured_llms)}")
            return True
        else:
            logger.warning(" No LLM providers configured - using mock responses")
            return False

    def test_agent_imports(self) -> bool:
        """Test importing enterprise agent modules"""
        logger.info("Testing enterprise agent module imports...")

        try:
            # Test enterprise agent framework import
            sys.path.append(str(self.backend_path))
            from enterprise_agent_framework import (
                EnterpriseAgentBase,
                QualityAssessmentAgent,
                WorkflowOrchestrationAgent,
                PerformanceOptimizationAgent,
                EnterpriseAgentOrchestrator
            )
            logger.info(" Enterprise agent framework imported successfully")

            # Test agent communication import
            from agent_communication import (
                AgentMessageBus,
                AgentServiceDiscovery,
                AgentLoadBalancer,
                AgentCoordinationProtocol
            )
            logger.info(" Agent communication system imported successfully")

            return True

        except ImportError as e:
            logger.error(f" Agent module import failed: {e}")
            return False

    def validate_orfeas_integration(self) -> bool:
        """Validate integration with main ORFEAS system"""
        logger.info("Validating ORFEAS main system integration...")

        try:
            # Check if main.py exists and has agent integration
            main_py_path = self.backend_path / 'main.py'
            if not main_py_path.exists():
                logger.error(" main.py not found")
                return False

            with open(main_py_path, 'r', encoding='utf-8') as f:
                content = f.read()

            required_imports = [
                'enterprise_agent_framework',
                'agent_communication',
                'EnterpriseAgentOrchestrator'
            ]

            missing_imports = []
            for imp in required_imports:
                if imp not in content:
                    missing_imports.append(imp)

            if missing_imports:
                logger.error(f" Missing integrations in main.py: {missing_imports}")
                return False

            logger.info(" ORFEAS main system integration validated")
            return True

        except Exception as e:
            logger.error(f" ORFEAS integration validation failed: {e}")
            return False

    def check_gpu_compatibility(self) -> bool:
        """Check GPU compatibility for agent performance optimization"""
        logger.info("Checking GPU compatibility for agent optimization...")

        try:
            import torch

            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9

                logger.info(f" GPU detected: {gpu_name}")
                logger.info(f" GPU memory: {gpu_memory:.1f} GB")

                if gpu_memory >= 8.0:  # 8GB minimum for agent processing
                    logger.info(" GPU memory sufficient for agent processing")
                    return True
                else:
                    logger.warning(" GPU memory below recommended 8GB")
                    return False
            else:
                logger.warning(" No GPU detected - agents will use CPU mode")
                return False

        except ImportError:
            logger.warning(" PyTorch not available - cannot check GPU")
            return False

    async def test_agent_communication(self) -> bool:
        """Test agent communication system"""
        logger.info("Testing agent communication system...")

        try:
            from agent_communication import AgentMessageBus, AgentServiceDiscovery

            # Test message bus initialization
            message_bus = AgentMessageBus()
            await message_bus.initialize()

            # Test service discovery
            service_discovery = AgentServiceDiscovery()
            await service_discovery.initialize()

            logger.info(" Agent communication system test passed")
            return True

        except Exception as e:
            logger.error(f" Agent communication test failed: {e}")
            return False

    def create_startup_summary(self) -> Dict[str, Any]:
        """Create comprehensive startup summary"""
        return {
            'timestamp': time.time(),
            'dependencies_valid': self.validation_results.get('dependencies', False),
            'redis_available': self.validation_results.get('redis', False),
            'llm_configured': self.validation_results.get('llm', False),
            'agent_imports_ok': self.validation_results.get('imports', False),
            'orfeas_integration_ok': self.validation_results.get('integration', False),
            'gpu_available': self.validation_results.get('gpu', False),
            'communication_test_ok': self.validation_results.get('communication', False)
        }

    def print_startup_summary(self, summary: Dict[str, Any]):
        """Print comprehensive startup summary"""
        logger.info("=" * 80)
        logger.info("ORFEAS ENTERPRISE AGENT SYSTEM STARTUP SUMMARY")
        logger.info("=" * 80)

        status_items = [
            ("Dependencies", summary['dependencies_valid']),
            ("Redis Message Bus", summary['redis_available']),
            ("LLM Configuration", summary['llm_configured']),
            ("Agent Imports", summary['agent_imports_ok']),
            ("ORFEAS Integration", summary['orfeas_integration_ok']),
            ("GPU Availability", summary['gpu_available']),
            ("Communication Test", summary['communication_test_ok'])
        ]

        for item, status in status_items:
            status_icon = "" if status else ""
            logger.info(f"  {status_icon} {item}")

        logger.info("=" * 80)

        # Overall status
        all_critical_ok = all([
            summary['dependencies_valid'],
            summary['agent_imports_ok'],
            summary['orfeas_integration_ok']
        ])

        if all_critical_ok:
            logger.info(" ENTERPRISE AGENT SYSTEM READY FOR STARTUP")
            logger.info("   All critical components validated successfully")
        else:
            logger.warning(" ENTERPRISE AGENT SYSTEM HAS ISSUES")
            logger.warning("   Review failed validations above")

        logger.info("=" * 80)

    async def run_startup_validation(self) -> bool:
        """Run complete startup validation sequence"""
        logger.info("Starting comprehensive agent system validation...")

        # Run all validation steps
        self.validation_results['dependencies'] = self.validate_dependencies()
        self.validation_results['redis'] = self.check_redis_connection()
        self.validation_results['llm'] = self.validate_llm_configuration()
        self.validation_results['imports'] = self.test_agent_imports()
        self.validation_results['integration'] = self.validate_orfeas_integration()
        self.validation_results['gpu'] = self.check_gpu_compatibility()
        self.validation_results['communication'] = await self.test_agent_communication()

        # Create and print summary
        summary = self.create_startup_summary()
        self.print_startup_summary(summary)

        # Return success status
        return all([
            self.validation_results['dependencies'],
            self.validation_results['imports'],
            self.validation_results['integration']
        ])

def main():
    """Main startup function"""
    startup_manager = OrfeasAgentSystemStartup()
    startup_manager.print_banner()

    # Run validation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        success = loop.run_until_complete(startup_manager.run_startup_validation())

        if success:
            logger.info(" ORFEAS Enterprise Agent System validation completed successfully!")
            logger.info("   You can now start the ORFEAS server with agent support")
            logger.info("   Command: python backend/main.py")
            return 0
        else:
            logger.error(" ORFEAS Enterprise Agent System validation failed")
            logger.error("   Fix the issues above before starting the server")
            return 1

    except Exception as e:
        logger.error(f" Startup validation failed with exception: {e}")
        return 1
    finally:
        loop.close()

if __name__ == '__main__':
    sys.exit(main())

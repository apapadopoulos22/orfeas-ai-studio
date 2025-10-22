#!/usr/bin/env python3
"""
ORFEAS Enterprise Agent System - Production Load Testing
==============================================================================
Comprehensive load testing suite for the ORFEAS Enterprise Agent System
with realistic user behavior simulation, stress testing, and performance
monitoring under high concurrent load conditions.

Features:
- Realistic user behavior simulation
- Progressive load testing (ramp-up/ramp-down)
- Stress testing with extreme loads
- Agent system resilience testing
- Real-time performance monitoring
- Detailed load testing reports

Author: ORFEAS AI Development Team
Version: 1.0.0
Date: 2025-01-11
==============================================================================
"""

import os
import sys
import time
import json
import random
import asyncio
import logging
import statistics
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import concurrent.futures
from dataclasses import dataclass

# Load testing imports
try:
    import aiohttp
    import requests
    import psutil
    import numpy as np
    from locust import HttpUser, task, between, events
    from locust.env import Environment
    from locust.stats import stats_printer, stats_history
    from locust.log import setup_logging
except ImportError as e:
    print(f"Missing dependencies for load testing: {e}")
    print("Install with: pip install locust aiohttp requests psutil numpy")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('orfeas_load_test')

@dataclass
class LoadTestConfig:
    """Load test configuration"""
    users: int = 100
    spawn_rate: int = 10
    duration: int = 300  # 5 minutes
    host: str = "http://localhost:5000"
    ramp_up_time: int = 60
    steady_state_time: int = 180
    ramp_down_time: int = 60

class OrfeasAgentUser(HttpUser):
    """
    Locust user class simulating realistic ORFEAS agent system usage
    """

    wait_time = between(1, 5)  # Wait 1-5 seconds between requests

    def on_start(self):
        """Initialize user session"""
        self.session_id = f"user_{random.randint(1000, 9999)}"
        self.user_type = random.choice(['casual', 'power', 'enterprise'])
        self.test_images = self.generate_test_data()

    def generate_test_data(self):
        """Generate test data for different user types"""
        if self.user_type == 'casual':
            return ['simple_image.jpg']
        elif self.user_type == 'power':
            return ['medium_image.jpg', 'complex_image.jpg']
        else:  # enterprise
            return ['simple_image.jpg', 'medium_image.jpg', 'complex_image.jpg', 'ultra_image.jpg']

    @task(30)
    def check_agent_status(self):
        """Most common operation - check agent system status"""
        with self.client.get("/api/agents/status", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status check failed with {response.status_code}")

    @task(20)
    def check_coordination_status(self):
        """Check agent coordination system status"""
        with self.client.get("/api/agents/coordination/status", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Coordination status failed with {response.status_code}")

    @task(15)
    def get_communication_stats(self):
        """Get agent communication statistics"""
        with self.client.get("/api/agents/communication/message-stats", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Communication stats failed with {response.status_code}")

    @task(10)
    def submit_agent_task(self):
        """Submit task to agent system"""
        task_data = {
            'task_type': random.choice(['quality_assessment', 'workflow_optimization', 'performance_tuning']),
            'priority': random.choice(['low', 'normal', 'high']),
            'input_data': {
                'complexity_level': random.choice(['simple', 'medium', 'complex']),
                'quality_target': random.uniform(0.6, 0.9)
            },
            'timeout': 30,
            'user_session': self.session_id
        }

        with self.client.post("/api/agents/submit-task", json=task_data, catch_response=True) as response:
            if response.status_code in [200, 201, 202]:
                response.success()
            else:
                response.failure(f"Task submission failed with {response.status_code}")

    @task(5)
    def intelligent_generation(self):
        """Simulate intelligent 3D generation request (heaviest operation)"""
        # Simulate file upload
        files = {
            'image': ('test_image.jpg', b'fake_image_data', 'image/jpeg')
        }
        data = {
            'quality': random.randint(5, 9),
            'priority': self.user_type,
            'session_id': self.session_id
        }

        with self.client.post("/api/agents/intelligent-generation",
                             files=files, data=data,
                             catch_response=True, timeout=60) as response:
            if response.status_code in [200, 201, 202]:
                response.success()
            else:
                response.failure(f"Intelligent generation failed with {response.status_code}")

    @task(3)
    def health_check(self):
        """Basic health check"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed with {response.status_code}")

class EnterpriseAgentUser(OrfeasAgentUser):
    """
    Enterprise user with more demanding usage patterns
    """

    wait_time = between(0.5, 2)  # Faster requests for enterprise users

    @task(40)
    def batch_agent_operations(self):
        """Enterprise users often perform batch operations"""
        operations = [
            "/api/agents/status",
            "/api/agents/coordination/status",
            "/api/agents/communication/message-stats"
        ]

        for operation in operations:
            with self.client.get(operation, catch_response=True) as response:
                if response.status_code != 200:
                    response.failure(f"Batch operation {operation} failed")
                    break
            time.sleep(0.1)  # Small delay between batch operations

class OrfeasLoadTestRunner:
    """
    Main load test runner for ORFEAS Enterprise Agent System
    """

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.test_results = {}
        self.start_time = None
        self.system_metrics = []
        self.monitoring_active = False

    def print_banner(self):
        """Print load test banner"""
        banner = f"""

â•' âš¡ ORFEAS ENTERPRISE AGENT SYSTEM - PRODUCTION LOAD TESTING âš¡               â•'
â•'                                                                              â•'
  Concurrent Users: {self.config.users:<8}  Target Host: {self.config.host:<25} 
  Test Duration: {self.config.duration:<8}s  Spawn Rate: {self.config.spawn_rate:<8}/s         
  Ramp-up: {self.config.ramp_up_time:<8}s  Steady State: {self.config.steady_state_time:<8}s      
â•'                                                                              â•'

        """
        print(banner)
        logger.info("ORFEAS Enterprise Agent System Load Testing Started")

    def check_server_health(self) -> bool:
        """Pre-test server health check"""
        try:
            response = requests.get(f"{self.config.host}/health", timeout=10)
            if response.status_code == 200:
                logger.info(" Server health check passed")
                return True
            else:
                logger.error(f" Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f" Server not reachable: {e}")
            return False

    def monitor_system_resources(self):
        """Monitor system resources during load test"""
        self.monitoring_active = True

        while self.monitoring_active:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_io_counters()
                network = psutil.net_io_counters()

                metrics = {
                    'timestamp': time.time(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used_gb': memory.used / (1024**3),
                    'disk_read_mb': disk.read_bytes / (1024**2) if disk else 0,
                    'disk_write_mb': disk.write_bytes / (1024**2) if disk else 0,
                    'network_sent_mb': network.bytes_sent / (1024**2) if network else 0,
                    'network_recv_mb': network.bytes_recv / (1024**2) if network else 0
                }

                self.system_metrics.append(metrics)

            except Exception as e:
                logger.warning(f"Resource monitoring error: {e}")

            time.sleep(5)  # Sample every 5 seconds

    def setup_locust_environment(self) -> Environment:
        """Setup Locust environment for load testing"""
        # Setup logging
        setup_logging("INFO", None)

        # Create environment
        env = Environment(
            user_classes=[OrfeasAgentUser, EnterpriseAgentUser],
            host=self.config.host
        )

        # Add event listeners for detailed tracking
        @events.request.add_listener
        def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
            if exception:
                logger.warning(f"Request failed: {name} - {exception}")

        @events.user_error.add_listener
        def on_user_error(user_instance, exception, tb):
            logger.error(f"User error: {exception}")

        return env

    def run_progressive_load_test(self) -> Dict[str, Any]:
        """Run progressive load test with ramp-up, steady state, and ramp-down"""
        logger.info(" Starting progressive load test...")

        # Setup environment
        env = self.setup_locust_environment()

        # Start resource monitoring
        monitor_thread = threading.Thread(target=self.monitor_system_resources, daemon=True)
        monitor_thread.start()

        self.start_time = time.time()

        try:
            # Phase 1: Ramp-up
            logger.info(f" Phase 1: Ramping up to {self.config.users} users over {self.config.ramp_up_time}s")
            env.runner.start(user_count=self.config.users, spawn_rate=self.config.spawn_rate)
            time.sleep(self.config.ramp_up_time)

            # Phase 2: Steady state
            logger.info(f" Phase 2: Steady state with {self.config.users} users for {self.config.steady_state_time}s")
            time.sleep(self.config.steady_state_time)

            # Phase 3: Ramp-down
            logger.info(f" Phase 3: Ramping down over {self.config.ramp_down_time}s")
            env.runner.stop()
            time.sleep(self.config.ramp_down_time)

        except KeyboardInterrupt:
            logger.info(" Load test interrupted by user")
        finally:
            # Stop monitoring
            self.monitoring_active = False

            # Collect final stats
            stats = env.runner.stats

            return {
                'total_requests': stats.total.num_requests,
                'total_failures': stats.total.num_failures,
                'average_response_time': stats.total.avg_response_time,
                'median_response_time': stats.total.median_response_time,
                'p95_response_time': stats.total.get_response_time_percentile(0.95),
                'p99_response_time': stats.total.get_response_time_percentile(0.99),
                'max_response_time': stats.total.max_response_time,
                'requests_per_second': stats.total.total_rps,
                'failure_rate': stats.total.fail_ratio,
                'test_duration': time.time() - self.start_time
            }

    def run_stress_test(self, max_users: int = 500, duration: int = 180) -> Dict[str, Any]:
        """Run stress test to find breaking point"""
        logger.info(f" Running stress test up to {max_users} users for {duration}s")

        env = self.setup_locust_environment()

        # Start resource monitoring
        monitor_thread = threading.Thread(target=self.monitor_system_resources, daemon=True)
        monitor_thread.start()

        stress_results = []
        current_users = 50

        while current_users <= max_users:
            logger.info(f" Stress testing with {current_users} users...")

            # Start load
            env.runner.start(user_count=current_users, spawn_rate=20)

            # Run for a short period
            time.sleep(30)

            # Collect stats
            stats = env.runner.stats.total
            result = {
                'users': current_users,
                'requests_per_second': stats.total_rps,
                'failure_rate': stats.fail_ratio,
                'avg_response_time': stats.avg_response_time,
                'p95_response_time': stats.get_response_time_percentile(0.95)
            }
            stress_results.append(result)

            # Check if system is breaking down
            if stats.fail_ratio > 0.1 or stats.avg_response_time > 10000:  # >10s avg response
                logger.warning(f" System stress detected at {current_users} users")
                break

            current_users += 50

        env.runner.stop()
        self.monitoring_active = False

        return {
            'max_stable_users': max([r['users'] for r in stress_results if r['failure_rate'] < 0.05]),
            'breaking_point_users': current_users,
            'stress_test_results': stress_results
        }

    def analyze_system_metrics(self) -> Dict[str, Any]:
        """Analyze collected system metrics"""
        if not self.system_metrics:
            return {}

        cpu_values = [m['cpu_percent'] for m in self.system_metrics]
        memory_values = [m['memory_percent'] for m in self.system_metrics]

        return {
            'cpu_usage': {
                'mean': statistics.mean(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values),
                'p95': np.percentile(cpu_values, 95)
            },
            'memory_usage': {
                'mean': statistics.mean(memory_values),
                'max': max(memory_values),
                'min': min(memory_values),
                'p95': np.percentile(memory_values, 95)
            },
            'sample_count': len(self.system_metrics),
            'monitoring_duration': self.system_metrics[-1]['timestamp'] - self.system_metrics[0]['timestamp'] if self.system_metrics else 0
        }

    def generate_load_test_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive load test report"""
        report_lines = []

        report_lines.append("")
        report_lines.append("â•'                    ORFEAS ENTERPRISE AGENT LOAD TEST REPORT                 â•'")
        report_lines.append("")
        report_lines.append("")

        # Test Configuration
        report_lines.append(" TEST CONFIGURATION:")
        report_lines.append(f"   Target Host: {self.config.host}")
        report_lines.append(f"   Concurrent Users: {self.config.users}")
        report_lines.append(f"   Test Duration: {self.config.duration}s")
        report_lines.append(f"   Spawn Rate: {self.config.spawn_rate} users/second")
        report_lines.append("")

        # Load Test Results
        if 'load_test' in results:
            load_results = results['load_test']
            report_lines.append(" LOAD TEST RESULTS:")
            report_lines.append(f"   Total Requests: {load_results.get('total_requests', 0):,}")
            report_lines.append(f"   Total Failures: {load_results.get('total_failures', 0):,}")
            report_lines.append(f"   Failure Rate: {load_results.get('failure_rate', 0):.2%}")
            report_lines.append(f"   Requests/Second: {load_results.get('requests_per_second', 0):.2f}")
            report_lines.append("")

            report_lines.append(" RESPONSE TIME METRICS:")
            report_lines.append(f"   Average: {load_results.get('average_response_time', 0):.0f}ms")
            report_lines.append(f"   Median: {load_results.get('median_response_time', 0):.0f}ms")
            report_lines.append(f"   95th Percentile: {load_results.get('p95_response_time', 0):.0f}ms")
            report_lines.append(f"   99th Percentile: {load_results.get('p99_response_time', 0):.0f}ms")
            report_lines.append(f"   Maximum: {load_results.get('max_response_time', 0):.0f}ms")
            report_lines.append("")

        # Stress Test Results
        if 'stress_test' in results:
            stress_results = results['stress_test']
            report_lines.append(" STRESS TEST RESULTS:")
            report_lines.append(f"   Maximum Stable Users: {stress_results.get('max_stable_users', 0)}")
            report_lines.append(f"   Breaking Point: {stress_results.get('breaking_point_users', 0)} users")
            report_lines.append("")

        # System Resource Usage
        if 'system_metrics' in results:
            metrics = results['system_metrics']
            report_lines.append(" SYSTEM RESOURCE USAGE:")
            if 'cpu_usage' in metrics:
                cpu = metrics['cpu_usage']
                report_lines.append(f"   CPU - Mean: {cpu['mean']:.1f}%, Max: {cpu['max']:.1f}%, P95: {cpu['p95']:.1f}%")
            if 'memory_usage' in metrics:
                memory = metrics['memory_usage']
                report_lines.append(f"   Memory - Mean: {memory['mean']:.1f}%, Max: {memory['max']:.1f}%, P95: {memory['p95']:.1f}%")
            report_lines.append("")

        # Performance Assessment
        if 'load_test' in results:
            load_results = results['load_test']
            failure_rate = load_results.get('failure_rate', 1)
            avg_response = load_results.get('average_response_time', 10000)

            if failure_rate < 0.01 and avg_response < 1000:  # <1% errors, <1s response
                assessment = " EXCELLENT PERFORMANCE"
            elif failure_rate < 0.05 and avg_response < 3000:  # <5% errors, <3s response
                assessment = " GOOD PERFORMANCE"
            elif failure_rate < 0.1 and avg_response < 5000:  # <10% errors, <5s response
                assessment = " ACCEPTABLE PERFORMANCE"
            else:
                assessment = " PERFORMANCE ISSUES DETECTED"

            report_lines.append(f" OVERALL ASSESSMENT: {assessment}")

        report_lines.append("")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def save_results(self, results: Dict[str, Any], report: str):
        """Save load test results and report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON results
        results_file = f"load_test_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f" Load test results saved to: {results_file}")

        # Save text report
        report_file = f"load_test_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        logger.info(f" Load test report saved to: {report_file}")

    def run_comprehensive_load_test(self) -> Dict[str, Any]:
        """Run comprehensive load testing suite"""
        self.print_banner()

        # Pre-test health check
        if not self.check_server_health():
            logger.error(" Server health check failed - aborting load test")
            return {'error': 'Server not healthy'}

        results = {
            'test_start': datetime.now().isoformat(),
            'config': {
                'users': self.config.users,
                'duration': self.config.duration,
                'host': self.config.host,
                'spawn_rate': self.config.spawn_rate
            }
        }

        # Run progressive load test
        logger.info(" Running progressive load test...")
        results['load_test'] = self.run_progressive_load_test()

        # Run stress test (optional, shorter duration)
        logger.info(" Running stress test...")
        results['stress_test'] = self.run_stress_test(max_users=min(self.config.users * 2, 300), duration=120)

        # Analyze system metrics
        results['system_metrics'] = self.analyze_system_metrics()

        results['test_end'] = datetime.now().isoformat()

        # Generate and save report
        report = self.generate_load_test_report(results)
        print(report)
        self.save_results(results, report)

        return results

def main():
    """Main load test execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='ORFEAS Enterprise Agent System Load Testing')
    parser.add_argument('--users', type=int, default=100, help='Number of concurrent users')
    parser.add_argument('--duration', type=int, default=300, help='Test duration in seconds')
    parser.add_argument('--spawn-rate', type=int, default=10, help='User spawn rate per second')
    parser.add_argument('--host', default='http://localhost:5000', help='Target host URL')
    parser.add_argument('--rps', type=int, default=50, help='Target requests per second')

    args = parser.parse_args()

    # Create configuration
    config = LoadTestConfig(
        users=args.users,
        spawn_rate=args.spawn_rate,
        duration=args.duration,
        host=args.host
    )

    # Run load test
    runner = OrfeasLoadTestRunner(config)

    try:
        results = runner.run_comprehensive_load_test()

        # Determine exit code based on results
        if 'load_test' in results:
            failure_rate = results['load_test'].get('failure_rate', 1)
            avg_response = results['load_test'].get('average_response_time', 10000)

            # Success if <5% failures and <5s average response time
            exit_code = 0 if failure_rate < 0.05 and avg_response < 5000 else 1
        else:
            exit_code = 1

        print(f"\n Load test completed with exit code: {exit_code}")
        return exit_code

    except Exception as e:
        logger.error(f" Load test failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

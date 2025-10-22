"""
ORFEAS Load Testing - Shared Utilities
=======================================
Common functions and helpers for load testing

ORFEAS AI Project
"""

import time
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import requests
import logging

logger = logging.getLogger(__name__)


@dataclass
class RequestResult:
    """Single request result"""
    timestamp: datetime
    duration: float  # seconds
    status_code: int
    success: bool
    error: Optional[str] = None
    job_id: Optional[str] = None


@dataclass
class LoadTestMetrics:
    """Aggregated metrics from load test"""
    scenario_name: str
    start_time: datetime
    end_time: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    durations: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        """Total test duration"""
        return (self.end_time - self.start_time).total_seconds()

    @property
    def success_rate(self) -> float:
        """Success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def error_rate(self) -> float:
        """Error rate percentage"""
        return 100 - self.success_rate

    @property
    def avg_duration(self) -> float:
        """Average request duration"""
        return statistics.mean(self.durations) if self.durations else 0.0

    @property
    def min_duration(self) -> float:
        """Minimum request duration"""
        return min(self.durations) if self.durations else 0.0

    @property
    def max_duration(self) -> float:
        """Maximum request duration"""
        return max(self.durations) if self.durations else 0.0

    @property
    def p50_duration(self) -> float:
        """P50 (median) duration"""
        if not self.durations:
            return 0.0
        sorted_durations = sorted(self.durations)
        return sorted_durations[len(sorted_durations) // 2]

    @property
    def p95_duration(self) -> float:
        """P95 duration"""
        if not self.durations:
            return 0.0
        sorted_durations = sorted(self.durations)
        idx = int(len(sorted_durations) * 0.95)
        return sorted_durations[idx]

    @property
    def p99_duration(self) -> float:
        """P99 duration"""
        if not self.durations:
            return 0.0
        sorted_durations = sorted(self.durations)
        idx = int(len(sorted_durations) * 0.99)
        return sorted_durations[idx]

    @property
    def throughput(self) -> float:
        """Requests per minute"""
        if self.duration_seconds == 0:
            return 0.0
        return (self.total_requests / self.duration_seconds) * 60

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'scenario': self.scenario_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': self.duration_seconds,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': round(self.success_rate, 2),
            'error_rate': round(self.error_rate, 2),
            'avg_duration': round(self.avg_duration, 2),
            'min_duration': round(self.min_duration, 2),
            'max_duration': round(self.max_duration, 2),
            'p50_duration': round(self.p50_duration, 2),
            'p95_duration': round(self.p95_duration, 2),
            'p99_duration': round(self.p99_duration, 2),
            'throughput_rpm': round(self.throughput, 2),
            'top_errors': self._get_top_errors(5)
        }

    def _get_top_errors(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get top N most common errors"""
        error_counts = {}
        for error in self.errors:
            error_counts[error] = error_counts.get(error, 0) + 1

        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'error': err, 'count': cnt} for err, cnt in sorted_errors[:n]]


class LoadTestClient:
    """HTTP client for load testing"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'ORFEAS-LoadTest/1.0'})

    def health_check(self) -> bool:
        """Check if server is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def generate_3d(self, image_path: str, timeout: int = 300) -> RequestResult:
        """
        Submit 3D generation request

        Args:
            image_path: Path to image file
            timeout: Request timeout in seconds

        Returns:
            RequestResult with timing and status
        """
        start_time = datetime.now()

        try:
            with open(image_path, 'rb') as f:
                files = {'image': ('test.png', f, 'image/png')}
                data = {'format': 'stl', 'quality': 7}

                response = self.session.post(
                    f"{self.base_url}/api/generate-3d",
                    files=files,
                    data=data,
                    timeout=timeout
                )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            success = response.status_code in [200, 202]

            job_id = None
            if success and response.headers.get('Content-Type', '').startswith('application/json'):
                try:
                    json_data = response.json()
                    job_id = json_data.get('job_id')
                except:
                    pass

            return RequestResult(
                timestamp=start_time,
                duration=duration,
                status_code=response.status_code,
                success=success,
                error=None if success else f"HTTP {response.status_code}",
                job_id=job_id
            )

        except requests.Timeout:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            return RequestResult(
                timestamp=start_time,
                duration=duration,
                status_code=504,
                success=False,
                error="Request timeout"
            )

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            return RequestResult(
                timestamp=start_time,
                duration=duration,
                status_code=0,
                success=False,
                error=str(e)
            )

    def get_metrics(self) -> Optional[str]:
        """Get Prometheus metrics"""
        try:
            response = self.session.get(f"{self.base_url}/metrics", timeout=5)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return None

    def close(self):
        """Close session"""
        self.session.close()


def aggregate_results(results: List[RequestResult], scenario_name: str,
                     start_time: datetime, end_time: datetime) -> LoadTestMetrics:
    """
    Aggregate request results into metrics

    Args:
        results: List of request results
        scenario_name: Name of test scenario
        start_time: Test start time
        end_time: Test end time

    Returns:
        LoadTestMetrics with aggregated statistics
    """
    total = len(results)
    successful = sum(1 for r in results if r.success)
    failed = total - successful
    durations = [r.duration for r in results]
    errors = [r.error for r in results if r.error]

    return LoadTestMetrics(
        scenario_name=scenario_name,
        start_time=start_time,
        end_time=end_time,
        total_requests=total,
        successful_requests=successful,
        failed_requests=failed,
        durations=durations,
        errors=errors
    )


def print_metrics_summary(metrics: LoadTestMetrics):
    """Print formatted metrics summary"""
    print("\n" + "=" * 80)
    print(f"LOAD TEST RESULTS: {metrics.scenario_name}")
    print("=" * 80)
    print(f"Duration:           {metrics.duration_seconds:.1f}s")
    print(f"Total Requests:     {metrics.total_requests}")
    print(f"Successful:         {metrics.successful_requests} ({metrics.success_rate:.1f}%)")
    print(f"Failed:             {metrics.failed_requests} ({metrics.error_rate:.1f}%)")
    print(f"Throughput:         {metrics.throughput:.2f} requests/min")
    print("\nResponse Times:")
    print(f"  Average:          {metrics.avg_duration:.2f}s")
    print(f"  Min:              {metrics.min_duration:.2f}s")
    print(f"  Max:              {metrics.max_duration:.2f}s")
    print(f"  P50 (Median):     {metrics.p50_duration:.2f}s")
    print(f"  P95:              {metrics.p95_duration:.2f}s")
    print(f"  P99:              {metrics.p99_duration:.2f}s")

    if metrics.errors:
        print("\nTop Errors:")
        for error_info in metrics._get_top_errors(3):
            print(f"  - {error_info['error']} ({error_info['count']} times)")

    print("=" * 80 + "\n")


def save_results_json(metrics: LoadTestMetrics, output_path: str):
    """Save results to JSON file"""
    import json
    with open(output_path, 'w') as f:
        json.dump(metrics.to_dict(), f, indent=2)
    print(f"Results saved to: {output_path}")

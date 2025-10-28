import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from prometheus_metrics import (
    http_requests_total,
    http_request_duration_seconds,
    errors_total,
    successful_generations_total,
    failed_generations_total,
    gpu_memory_bytes,
    websocket_messages_sent_total,
    websocket_connections_active,
    cache_hits_total,
    cache_misses_total,
)

class TestPrometheusMetrics:
    def test_http_requests(self):
        http_requests_total.labels(method='GET', endpoint='/api/health', status=200).inc()
        assert True
    
    def test_http_duration(self):
        http_request_duration_seconds.labels(method='GET', endpoint='/api/health').observe(0.05)
        assert True
    
    def test_errors(self):
        errors_total.labels(type='ValidationError', endpoint='/api/upload').inc()
        assert True
    
    def test_generation_success(self):
        successful_generations_total.labels(type='model_3d').inc()
        assert True
    
    def test_generation_failed(self):
        failed_generations_total.labels(type='model_3d', reason='gpu_error').inc()
        assert True
    
    def test_gpu_memory(self):
        gpu_memory_bytes.labels(gpu_id='0', type='reserved').set(8000000000)
        assert True
    
    def test_websocket(self):
        websocket_messages_sent_total.labels(event_type='progress').inc()
        websocket_connections_active.labels(client_type='browser').set(10)
        assert True
    
    def test_cache(self):
        cache_hits_total.labels(cache_type='redis').inc()
        cache_misses_total.labels(cache_type='redis').inc()
        assert True

class TestMetricsIntegration:
    def test_full_workflow(self):
        http_requests_total.labels(method='POST', endpoint='/api/generate', status=202).inc()
        http_request_duration_seconds.labels(method='POST', endpoint='/api/generate').observe(2.5)
        successful_generations_total.labels(type='model_3d').inc()
        gpu_memory_bytes.labels(gpu_id='0', type='used').set(15000000000)
        assert True
    
    def test_error_workflow(self):
        errors_total.labels(type='GPUError', endpoint='/api/generate').inc()
        http_requests_total.labels(method='POST', endpoint='/api/generate', status=503).inc()
        failed_generations_total.labels(type='model_3d', reason='oom').inc()
        assert True

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

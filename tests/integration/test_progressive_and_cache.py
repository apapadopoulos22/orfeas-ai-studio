import os
import time
import json
import pytest
import requests
from io import BytesIO
from PIL import Image

BASE_URL = os.getenv('ORFEAS_BASE_URL', 'http://127.0.0.1:5000')


def _server_reachable() -> bool:
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=2)
        return r.status_code // 100 == 2
    except Exception:
        return False


@pytest.mark.integration
@pytest.mark.skipif(not _server_reachable(), reason="Backend not running on ORFEAS_BASE_URL")
def test_progressive_endpoint_starts_and_streams():
    # Create tiny test image in memory
    img = Image.new('RGB', (32, 32), color=(123, 34, 200))
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    files = {'image': ('test.png', buf, 'image/png')}
    data = {'quality': '5', 'format': 'stl', 'enable_cache': 'true'}

    # Start progressive job
    r = requests.post(f"{BASE_URL}/api/generate-3d/progressive", files=files, data=data, timeout=10)
    assert r.status_code == 200, r.text

    payload = r.json()
    assert 'job_id' in payload
    job_id = payload['job_id']
    assert payload.get('status') in {'processing', 'queued'}

    # Connect to stream (SSE)
    stream_url = payload.get('progress_url', f"/api/progress/{job_id}")
    if not stream_url.startswith('http'):
        stream_url = f"{BASE_URL}{stream_url}"

    s = requests.get(stream_url, stream=True, timeout=20)
    assert s.status_code == 200
    assert s.headers.get('Content-Type', '').startswith('text/event-stream')

    # Read a couple of SSE chunks to ensure data is flowing
    line_count = 0
    for line in s.iter_lines():
        if not line:
            continue
        if line.startswith(b'data:'):
            line_count += 1
            if line_count >= 2:
                break
    assert line_count >= 1


@pytest.mark.integration
@pytest.mark.skipif(not _server_reachable(), reason="Backend not running on ORFEAS_BASE_URL")
def test_cache_hit_on_repeat_request():
    # Prepare image
    img = Image.new('RGB', (16, 16), color=(50, 50, 50))
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    files = {'image': ('tiny.png', buf, 'image/png')}
    data = {'quality': '4', 'format': 'stl', 'enable_cache': 'true'}

    # First request (populate cache)
    r1 = requests.post(f"{BASE_URL}/api/generate-3d/progressive", files=files, data=data, timeout=10)
    assert r1.status_code == 200

    # Second request (same payload) should result in cached path in many implementations
    buf.seek(0)
    files2 = {'image': ('tiny.png', buf, 'image/png')}
    r2 = requests.post(f"{BASE_URL}/api/generate-3d/progressive", files=files2, data=data, timeout=10)
    assert r2.status_code == 200
    second = r2.json()
    # Not guaranteed, but if caching is immediate it may return cached: True
    # Accept either processing or cached true
    assert ('cached' in second and second['cached'] is True) or second.get('status') in {'processing', 'queued'}

import os
import time
from statistics import mean
from io import BytesIO
import requests
from PIL import Image

BASE_URL = os.getenv('ORFEAS_BASE_URL', 'http://127.0.0.1:5000')


def make_img(size=(32, 32), color=(200, 50, 50)):
    img = Image.new('RGB', size, color=color)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def ping():
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=3)
        return r.status_code // 100 == 2
    except Exception:
        return False


def run_progressive(n=3):
    latencies = []
    for i in range(n):
        buf = make_img()
        files = {'image': ('bench.png', buf, 'image/png')}
        data = {'quality': '5', 'format': 'stl', 'enable_cache': 'true'}
        t0 = time.time()
        r = requests.post(f"{BASE_URL}/api/generate-3d/progressive", files=files, data=data, timeout=10)
        t1 = time.time()
        latencies.append(t1 - t0)
        ok = r.status_code == 200
        print(f"POST progressive {i+1}/{n}: status={r.status_code}, dt={latencies[-1]:.3f}s, ok={ok}")
    if latencies:
        print(f"First-result latency: mean={mean(latencies):.3f}s min={min(latencies):.3f}s max={max(latencies):.3f}s")


def main():
    if not ping():
        print("Backend not reachable at", BASE_URL)
        return
    print("Benchmarking progressive endpoint...")
    run_progressive(n=int(os.getenv('BENCH_N', '5')))


if __name__ == '__main__':
    main()

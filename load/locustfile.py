import os
from io import BytesIO
from PIL import Image
from locust import HttpUser, task, between

BASE_PATH = os.getenv('ORFEAS_BASE_PATH', '')


def gen_image_bytes(w=32, h=32, color=(10, 120, 240)):
    img = Image.new('RGB', (w, h), color=color)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


class ProgressiveUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def progressive_generate(self):
        buf = gen_image_bytes()
        files = {'image': ('load.png', buf, 'image/png')}
        data = {'quality': '5', 'format': 'stl', 'enable_cache': 'true'}
        self.client.post(f"{BASE_PATH}/api/generate-3d/progressive", files=files, data=data)

    @task(1)
    def health(self):
        self.client.get(f"{BASE_PATH}/api/health")

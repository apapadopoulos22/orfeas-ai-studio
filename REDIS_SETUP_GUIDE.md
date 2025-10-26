# Redis Setup & Integration Guide - ORFEAS AI Studio

**Version**: 1.0
**Date**: October 26, 2025
**Purpose**: Distributed caching, session management, and job queuing

---

## Quick Start (5 Minutes)

### Local Development (Windows with WSL2)

```bash
# In WSL2 terminal
# Install Redis
sudo apt update
sudo apt install -y redis-server

# Start Redis service
sudo service redis-server start

# Verify running
redis-cli ping
# Output: PONG

# Create .env file in project root
cat > .env << 'EOF'
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
CACHE_TTL_MEDIUM=3600
CACHE_TTL_SHORT=300
CACHE_TTL_LONG=86400
EOF

# Install Python Redis package (if not already installed)
pip install redis
```

### Production (Ubuntu 20.04+)

```bash
# Follow Production Installation section below
```

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│              ORFEAS AI Studio - Redis Architecture       │
└──────────────────────────────────────────────────────────┘

Frontend (Browser)
    ↓
Nginx Reverse Proxy
    ↓
Gunicorn Workers (8x processes)
    ↓
Flask Application (main.py)
    ├─ Session Manager (RedisSessionManager)
    │   └─ Redis: job:{job_id}:session (TTL: 1 week)
    │
    ├─ Cache Layer (@redis_cache decorator)
    │   ├─ user_history (TTL: 6 hours)
    │   ├─ generation_settings (TTL: 1 hour)
    │   └─ ml_model_configs (TTL: 24 hours)
    │
    ├─ Job Queue (RedisJobQueue)
    │   ├─ queue:pending (FIFO)
    │   ├─ queue:processing (in-flight jobs)
    │   ├─ queue:completed (results, TTL: 7 days)
    │   └─ queue:failed (error tracking)
    │
    └─ Real-Time Progress (ProgressTracker)
        └─ job:{job_id}:progress (TTL: 24 hours)

Redis Server (localhost:6379 or cluster)
    ├─ Memory: 4-8 GB (configurable)
    ├─ Persistence: AOF + RDB snapshots
    ├─ Replication: Optional master-slave setup
    └─ Monitoring: Redis Exporter → Prometheus
```

---

## Installation

### Windows (Development - WSL2)

```bash
# Open WSL2 terminal (Ubuntu 20.04+)

# Step 1: Install Redis
sudo apt update
sudo apt install -y redis-server redis-tools

# Step 2: Verify installation
redis-server --version
redis-cli --version

# Step 3: Start Redis service
sudo service redis-server start

# Step 4: Verify it's running
sudo service redis-server status
redis-cli ping
```

### macOS

```bash
# Install Homebrew (if not already)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Redis
brew install redis

# Start Redis
brew services start redis

# Verify
redis-cli ping
```

### Ubuntu/Linux (Production)

```bash
# Install Redis from official repository
sudo apt update
sudo apt install -y redis-server redis-tools

# Start Redis
sudo systemctl start redis-server

# Enable on boot
sudo systemctl enable redis-server

# Verify
systemctl status redis-server
redis-cli ping
```

### Docker (Optional - Production with Docker Compose)

**Create `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: orfeas-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    restart: always
    networks:
      - orfeas

  app:
    build: .
    container_name: orfeas-app
    ports:
      - "5000:5000"
    depends_on:
      - redis
    environment:
      REDIS_HOST: redis
      REDIS_PORT: 6379
      DEVICE: cuda
    volumes:
      - ./backend:/app/backend
      - ./models:/app/models
    restart: always
    networks:
      - orfeas
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  redis_data:

networks:
  orfeas:
    driver: bridge
```

**Start with:**

```bash
docker-compose up -d
redis-cli -h localhost ping
```

---

## Configuration

### Redis Configuration File

**Location**: `/etc/redis/redis.conf` (Linux) or `redis.conf` (Windows/macOS)

**Key Settings:**

```ini
# ============================================
# Network
# ============================================
bind 127.0.0.1 192.168.1.100  # Bind to interfaces
port 6379                      # Default port

# ============================================
# Security
# ============================================
requirepass securepassword123  # Set password
maxclients 10000               # Max connections

# ============================================
# Memory
# ============================================
maxmemory 8gb                  # Max memory
maxmemory-policy allkeys-lru   # LRU eviction policy
# allkeys-lru: Remove any key using LRU (best for caching)
# allkeys-lfu: Remove any key using LFU (frequency-based)
# volatile-lru: Remove keys with TTL (safe, respects TTL)

# ============================================
# Persistence
# ============================================
# RDB Snapshots
save 900 1              # 1 change in 15 min
save 300 10             # 10 changes in 5 min
save 60 10000           # 10000 changes in 1 min

# AOF (Append-Only File) - recommended for production
appendonly yes
appendfsync everysec    # Sync every second (balance)
# appendfsync always    # Sync on every write (safe but slow)
# appendfsync no        # OS decides (fastest, risky)

# ============================================
# Replication (for HA)
# ============================================
# slaveof 192.168.1.50 6379  # Replicate from master
repl-diskless-sync no          # Save to disk before sync

# ============================================
# Logging
# ============================================
loglevel notice
logfile /var/log/redis/redis-server.log

# ============================================
# Advanced
# ============================================
tcp-keepalive 300      # Send PING after 300s idle
databases 16           # Number of databases (0-15)
```

### Environment Variables (`.env`)

Create `.env` in project root:

```bash
# ============================================
# Redis Connection
# ============================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=securepassword123  # Set if configured in redis.conf

# ============================================
# Connection Pool
# ============================================
REDIS_POOL_MIN_CONNECTIONS=5
REDIS_POOL_MAX_CONNECTIONS=50
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_SOCKET_TIMEOUT=5

# ============================================
# Cache TTL (Time-To-Live)
# ============================================
CACHE_TTL_SHORT=300             # 5 minutes
CACHE_TTL_MEDIUM=3600           # 1 hour
CACHE_TTL_LONG=604800           # 7 days

# ============================================
# Key Prefixes
# ============================================
REDIS_KEY_PREFIX=orfeas:
REDIS_SESSION_PREFIX=orfeas:session:
REDIS_CACHE_PREFIX=orfeas:cache:
REDIS_QUEUE_PREFIX=orfeas:queue:
REDIS_JOB_PREFIX=orfeas:job:

# ============================================
# Feature Flags
# ============================================
REDIS_ENABLED=true
REDIS_CACHING_ENABLED=true
REDIS_SESSION_ENABLED=true
REDIS_QUEUE_ENABLED=true
```

---

## Integration with ORFEAS

### 1. Import Redis Config

**In `backend/main.py` (after environment variable setup, before Flask creation):**

```python
from redis_config import initialize_redis, get_redis_client

# Initialize Redis (sets up connection pool, handles errors)
initialize_redis()

# Get client for operations
redis_client = get_redis_client()
```

### 2. Cache Decorators

**Example: Caching user generation history**

```python
from redis_config import redis_cache, redis_invalidate

@app.route('/api/user/history', methods=['GET'])
@redis_cache(ttl=3600)  # Cache for 1 hour
def get_user_history():
    """Get user's generation history (cached)"""
    user_id = request.headers.get('User-ID')
    # Query database
    history = db.query(f"SELECT * FROM generations WHERE user_id = {user_id}")
    return jsonify(history)

@app.route('/api/generation/create', methods=['POST'])
def create_generation():
    """Create new generation"""
    result = processor.generate_3d(...)

    # Invalidate cached history after new generation
    user_id = request.headers.get('User-ID')
    redis_invalidate(f'user_history:{user_id}')

    return jsonify(result)
```

### 3. Session Management

**In `backend/main.py`:**

```python
from redis_config import RedisSessionManager

session_manager = RedisSessionManager(redis_client)

@app.route('/api/generation/start', methods=['POST'])
def start_generation():
    """Start 3D generation with session tracking"""
    job_id = str(uuid.uuid4())

    # Save session
    session_data = {
        'user_id': request.headers.get('User-ID'),
        'start_time': datetime.now().isoformat(),
        'model_config': request.json.get('config'),
        'status': 'pending'
    }
    session_manager.set_session(job_id, session_data, ttl=3600)

    # Queue job
    job_queue.enqueue(job_id, task_type='3d_generation')

    return jsonify({'job_id': job_id})

@app.route('/api/generation/status/<job_id>', methods=['GET'])
def check_status(job_id):
    """Get generation status from session"""
    session = session_manager.get_session(job_id)
    if not session:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify(session)
```

### 4. Job Queue

**In `backend/main.py`:**

```python
from redis_config import RedisJobQueue

job_queue = RedisJobQueue(redis_client)

@app.route('/api/generation/submit', methods=['POST'])
def submit_generation():
    """Submit generation job to queue"""
    job_id = str(uuid.uuid4())

    # Enqueue job
    job_queue.enqueue(
        job_id=job_id,
        task_type='3d_generation',
        data={
            'image_url': request.json['image_url'],
            'settings': request.json.get('settings', {})
        },
        priority=request.json.get('priority', 'normal')
    )

    return jsonify({'job_id': job_id, 'status': 'queued'})

@app.route('/api/queue/status', methods=['GET'])
def queue_status():
    """Get queue statistics"""
    return jsonify({
        'pending': job_queue.get_pending_count(),
        'processing': job_queue.get_processing_count(),
        'completed': job_queue.get_completed_count(),
        'failed': job_queue.get_failed_count()
    })
```

---

## Testing Redis Connection

### Command Line

```bash
# Test basic connection
redis-cli ping
# Output: PONG

# Test with password
redis-cli -a password ping

# View all keys
redis-cli keys '*'

# View memory usage
redis-cli info memory

# Monitor commands in real-time
redis-cli monitor

# Check persistence
redis-cli info persistence

# Flush database (CAREFUL!)
redis-cli flushdb    # Current DB only
redis-cli flushall   # All DBs
```

### Python Script

**Create `test_redis.py`:**

```python
import redis
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Get Redis config
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

try:
    # Create connection
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=5
    )

    # Test PING
    print("[TEST 1] PING")
    result = r.ping()
    print(f"✅ PING: {result}\n")

    # Test SET/GET
    print("[TEST 2] SET/GET")
    r.set('test_key', 'test_value', ex=3600)
    value = r.get('test_key')
    print(f"✅ SET/GET: {value}\n")

    # Test Caching Decorator
    print("[TEST 3] Cache Decorator")
    from redis_config import redis_cache

    @redis_cache(ttl=60)
    def expensive_function(x):
        print(f"  [Computing] x={x}")
        return x * 2

    print("First call (computes):")
    result1 = expensive_function(5)
    print(f"  Result: {result1}")

    print("Second call (cached):")
    result2 = expensive_function(5)
    print(f"  Result: {result2}\n")

    # Test Session Manager
    print("[TEST 4] Session Manager")
    from redis_config import RedisSessionManager

    session_mgr = RedisSessionManager(r)
    session_data = {'user_id': 'user123', 'status': 'pending'}
    session_mgr.set_session('job_001', session_data, ttl=3600)
    retrieved = session_mgr.get_session('job_001')
    print(f"✅ Session saved and retrieved: {retrieved}\n")

    # Test Job Queue
    print("[TEST 5] Job Queue")
    from redis_config import RedisJobQueue

    job_queue = RedisJobQueue(r)
    job_queue.enqueue('job_002', 'test_task', {'data': 'value'})
    pending = job_queue.get_pending_count()
    print(f"✅ Job queued. Pending jobs: {pending}\n")

    # Show memory usage
    print("[TEST 6] Memory Usage")
    info = r.info('memory')
    print(f"✅ Memory used: {info['used_memory_human']}")
    print(f"   Memory peak: {info['used_memory_peak_human']}\n")

    print("=" * 50)
    print("✅ ALL TESTS PASSED - Redis is ready!")
    print("=" * 50)

except redis.ConnectionError as e:
    print(f"❌ Connection Error: {e}")
    print("\nTroubleshooting:")
    print("1. Is Redis running? sudo systemctl status redis-server")
    print("2. Is correct port? redis-cli -p 6379 ping")
    print("3. Check password? REDIS_PASSWORD in .env")
except Exception as e:
    print(f"❌ Error: {e}")
```

**Run:**

```bash
python test_redis.py
```

---

## Monitoring & Maintenance

### View Redis Status

```bash
# Connection info
redis-cli info server

# Memory usage
redis-cli info memory

# Keys overview
redis-cli info keyspace

# Real-time command monitoring
redis-cli monitor

# Top keys by size
redis-cli --bigkeys

# Find slow commands
redis-cli slowlog get 10
```

### Redis CLI Tips

```bash
# Connect
redis-cli
redis-cli -a password

# Select database
redis-cli -n 0  # DB 0
redis-cli -n 1  # DB 1

# Get value
redis-cli GET key_name

# Set with TTL
redis-cli SET key_name value EX 3600

# List all keys
redis-cli KEYS '*'

# List keys matching pattern
redis-cli KEYS 'orfeas:job:*'

# Get key count
redis-cli DBSIZE

# Delete key
redis-cli DEL key_name

# Expire key (delete after N seconds)
redis-cli EXPIRE key_name 3600

# View TTL
redis-cli TTL key_name

# Clear database
redis-cli FLUSHDB

# Persist changes
redis-cli SAVE
redis-cli BGSAVE  # Background save
```

### Backup & Recovery

```bash
# Create snapshot
redis-cli BGSAVE
# Snapshot saved to /var/lib/redis/dump.rdb

# List snapshots
ls -lh /var/lib/redis/dump.rdb

# Backup to S3
aws s3 cp /var/lib/redis/dump.rdb s3://backup-bucket/redis/dump.rdb

# Restore from snapshot
# 1. Stop Redis
sudo systemctl stop redis-server

# 2. Copy backup
sudo cp dump.rdb /var/lib/redis/

# 3. Start Redis (will load from RDB)
sudo systemctl start redis-server

# Verify
redis-cli DBSIZE
```

---

## Performance Tuning

### Connection Pooling

**In `redis_config.py` (already configured):**

```python
pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    max_connections=50,  # Increase for high traffic
    socket_connect_timeout=5,
    socket_timeout=5
)
```

### Eviction Policies

```bash
# View current policy
redis-cli CONFIG GET maxmemory-policy

# Set LRU eviction (best for caching)
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Set LFU eviction (frequency-based)
redis-cli CONFIG SET maxmemory-policy allkeys-lfu

# Volatile (only keys with TTL)
redis-cli CONFIG SET maxmemory-policy volatile-lru
```

### Persistence Tuning

```bash
# RDB snapshots less frequently (faster)
redis-cli CONFIG SET save "900 1 300 10"

# AOF rewrite frequency
redis-cli CONFIG SET auto-aof-rewrite-percentage 100
redis-cli CONFIG SET auto-aof-rewrite-min-size 64mb

# Lazy freeing (prevents blocking)
redis-cli CONFIG SET lazyfree-lazy-eviction yes
redis-cli CONFIG SET lazyfree-lazy-expire yes
```

---

## Troubleshooting

### Redis Won't Start

```bash
# Check service status
sudo systemctl status redis-server

# View logs
sudo journalctl -u redis-server -n 50

# Try manual start
sudo redis-server

# Fix permissions
sudo chown -R redis:redis /var/lib/redis
sudo chmod -R 755 /var/lib/redis
```

### Connection Timeout

```bash
# Check if Redis is listening
netstat -tlnp | grep 6379

# Test connection
redis-cli -h localhost -p 6379 ping

# Check firewall
sudo ufw status
sudo ufw allow 6379/tcp
```

### Out of Memory

```bash
# View memory usage
redis-cli info memory

# Check max memory setting
redis-cli CONFIG GET maxmemory

# Increase if needed
redis-cli CONFIG SET maxmemory 16gb

# View eviction policy
redis-cli CONFIG GET maxmemory-policy

# Set LRU if needed
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Slow Queries

```bash
# View slow log
redis-cli slowlog get 10

# Get log length
redis-cli slowlog len

# Reset log
redis-cli slowlog reset

# Adjust slow threshold (microseconds, default 10000)
redis-cli CONFIG SET slowlog-log-slower-than 1000
```

---

## Production Checklist

- [ ] Redis installed and running
- [ ] Password set in `redis.conf`
- [ ] Persistence enabled (RDB + AOF)
- [ ] Memory limit configured
- [ ] Eviction policy set (allkeys-lru recommended)
- [ ] Systemd service enabled
- [ ] Firewall configured (port 6379)
- [ ] Backups scheduled
- [ ] Monitoring enabled
- [ ] `.env` configured with connection details
- [ ] `redis_config.py` integrated into `main.py`
- [ ] Cache decorators applied to endpoints
- [ ] Session manager initialized
- [ ] Job queue initialized
- [ ] Tests passing (`test_redis.py`)

---

**Next Steps:**

1. ✅ Install and start Redis
2. ✅ Configure `.env` with Redis credentials
3. ➡️ Run `test_redis.py` to verify connection
4. ➡️ Update `backend/main.py` to import and initialize Redis
5. ➡️ Add `@redis_cache` decorators to endpoints
6. ➡️ Test caching and session management

**Redis is now ready for ORFEAS AI Studio!** 🚀

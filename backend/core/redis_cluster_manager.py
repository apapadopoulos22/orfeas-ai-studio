"""
ORFEAS AI Studio - Redis Cluster Manager
=========================================

Distributed caching with Redis Cluster:
- Automatic sharding across nodes
- High availability with replication
- Failover handling
- Connection pooling
- Consistent hashing

Author: ORFEAS AI Team
Date: October 28, 2025
"""

import logging
import hashlib
from typing import Optional, List, Dict, Any
import redis
from redis.cluster import RedisCluster, ClusterNode
from redis.exceptions import RedisClusterException, RedisError

logger = logging.getLogger(__name__)


class RedisClusterManager:
    """
    Manages Redis Cluster connections with automatic failover
    and connection pooling.
    """

    def __init__(
        self,
        nodes: List[Dict[str, Any]],
        password: Optional[str] = None,
        max_connections: int = 50,
        socket_timeout: int = 5,
        socket_keepalive: bool = True,
        retry_on_timeout: bool = True
    ):
        """
        Initialize Redis Cluster manager.

        Args:
            nodes: List of cluster nodes [{'host': 'localhost', 'port': 7000}, ...]
            password: Redis password
            max_connections: Maximum connections per node
            socket_timeout: Socket timeout in seconds
            socket_keepalive: Enable TCP keepalive
            retry_on_timeout: Retry on timeout
        """
        self.nodes = nodes
        self.password = password
        self.max_connections = max_connections
        self.socket_timeout = socket_timeout
        self.socket_keepalive = socket_keepalive
        self.retry_on_timeout = retry_on_timeout

        self.cluster: Optional[RedisCluster] = None
        self._connect()

    def _connect(self):
        """Connect to Redis Cluster"""
        try:
            startup_nodes = [
                ClusterNode(host=node['host'], port=node['port'])
                for node in self.nodes
            ]

            self.cluster = RedisCluster(
                startup_nodes=startup_nodes,
                password=self.password,
                decode_responses=False,
                skip_full_coverage_check=True,
                max_connections_per_node=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_keepalive=self.socket_keepalive,
                retry_on_timeout=self.retry_on_timeout
            )

            # Test connection
            self.cluster.ping()
            logger.info(f"Connected to Redis Cluster with {len(self.nodes)} nodes")

        except RedisClusterException as e:
            logger.error(f"Failed to connect to Redis Cluster: {e}")
            self.cluster = None
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis Cluster: {e}")
            self.cluster = None

    def get(self, key: str) -> Optional[bytes]:
        """
        Get value from Redis Cluster.

        Args:
            key: Cache key

        Returns:
            Value as bytes or None
        """
        if not self.cluster:
            logger.warning("Redis Cluster not connected")
            return None

        try:
            return self.cluster.get(key)
        except RedisError as e:
            logger.error(f"Redis Cluster get error: {e}")
            return None

    def set(
        self,
        key: str,
        value: bytes,
        ex: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """
        Set value in Redis Cluster.

        Args:
            key: Cache key
            value: Value as bytes
            ex: Expiration in seconds
            nx: Only set if key doesn't exist

        Returns:
            True if successful
        """
        if not self.cluster:
            logger.warning("Redis Cluster not connected")
            return False

        try:
            result = self.cluster.set(key, value, ex=ex, nx=nx)
            return bool(result)
        except RedisError as e:
            logger.error(f"Redis Cluster set error: {e}")
            return False

    def delete(self, *keys: str) -> int:
        """
        Delete keys from Redis Cluster.

        Args:
            *keys: Keys to delete

        Returns:
            Number of keys deleted
        """
        if not self.cluster:
            logger.warning("Redis Cluster not connected")
            return 0

        try:
            return self.cluster.delete(*keys)
        except RedisError as e:
            logger.error(f"Redis Cluster delete error: {e}")
            return 0

    def exists(self, *keys: str) -> int:
        """
        Check if keys exist in Redis Cluster.

        Args:
            *keys: Keys to check

        Returns:
            Number of existing keys
        """
        if not self.cluster:
            return 0

        try:
            return self.cluster.exists(*keys)
        except RedisError as e:
            logger.error(f"Redis Cluster exists error: {e}")
            return 0

    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment counter in Redis Cluster.

        Args:
            key: Counter key
            amount: Increment amount

        Returns:
            New counter value or None
        """
        if not self.cluster:
            return None

        try:
            return self.cluster.incrby(key, amount)
        except RedisError as e:
            logger.error(f"Redis Cluster incr error: {e}")
            return None

    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get Redis Cluster information.

        Returns:
            Cluster info dictionary
        """
        if not self.cluster:
            return {'status': 'disconnected'}

        try:
            info = self.cluster.cluster_info()
            nodes_info = self.cluster.cluster_nodes()

            return {
                'status': 'connected',
                'cluster_state': info.get(b'cluster_state', b'unknown').decode(),
                'cluster_size': info.get(b'cluster_size', 0),
                'cluster_known_nodes': info.get(b'cluster_known_nodes', 0),
                'nodes': len(self.nodes),
                'nodes_info': nodes_info
            }
        except Exception as e:
            logger.error(f"Error getting cluster info: {e}")
            return {'status': 'error', 'error': str(e)}

    def get_node_for_key(self, key: str) -> Optional[str]:
        """
        Get cluster node responsible for key.

        Args:
            key: Cache key

        Returns:
            Node address (host:port) or None
        """
        if not self.cluster:
            return None

        try:
            # Get slot for key
            slot = self.cluster.keyslot(key)

            # Get node for slot
            node = self.cluster.nodes_manager.slots[slot][0]
            return f"{node.host}:{node.port}"
        except Exception as e:
            logger.error(f"Error getting node for key: {e}")
            return None

    def pipeline(self):
        """
        Create pipeline for batched operations.

        Returns:
            Redis Cluster pipeline
        """
        if not self.cluster:
            raise RedisClusterException("Redis Cluster not connected")

        return self.cluster.pipeline()

    def health_check(self) -> bool:
        """
        Check if Redis Cluster is healthy.

        Returns:
            True if healthy
        """
        if not self.cluster:
            return False

        try:
            self.cluster.ping()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def reconnect(self):
        """Attempt to reconnect to Redis Cluster"""
        logger.info("Attempting to reconnect to Redis Cluster...")
        self._connect()


class ConsistentHashRing:
    """
    Consistent hashing ring for distributed caching.
    Used when Redis Cluster is not available.
    """

    def __init__(self, nodes: List[str], virtual_nodes: int = 150):
        """
        Initialize consistent hash ring.

        Args:
            nodes: List of node addresses
            virtual_nodes: Number of virtual nodes per physical node
        """
        self.nodes = nodes
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self._build_ring()

    def _hash(self, key: str) -> int:
        """Hash key to integer"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def _build_ring(self):
        """Build the hash ring with virtual nodes"""
        self.ring.clear()

        for node in self.nodes:
            for i in range(self.virtual_nodes):
                virtual_key = f"{node}:{i}"
                hash_value = self._hash(virtual_key)
                self.ring[hash_value] = node

    def get_node(self, key: str) -> str:
        """
        Get node for key using consistent hashing.

        Args:
            key: Cache key

        Returns:
            Node address
        """
        if not self.ring:
            raise ValueError("Hash ring is empty")

        key_hash = self._hash(key)

        # Find first node with hash >= key_hash
        sorted_hashes = sorted(self.ring.keys())

        for node_hash in sorted_hashes:
            if node_hash >= key_hash:
                return self.ring[node_hash]

        # Wrap around to first node
        return self.ring[sorted_hashes[0]]

    def add_node(self, node: str):
        """Add node to hash ring"""
        if node not in self.nodes:
            self.nodes.append(node)

            for i in range(self.virtual_nodes):
                virtual_key = f"{node}:{i}"
                hash_value = self._hash(virtual_key)
                self.ring[hash_value] = node

    def remove_node(self, node: str):
        """Remove node from hash ring"""
        if node in self.nodes:
            self.nodes.remove(node)

            # Remove all virtual nodes
            keys_to_remove = [k for k, v in self.ring.items() if v == node]
            for key in keys_to_remove:
                del self.ring[key]


# Global Redis Cluster manager instance
_redis_cluster_manager: Optional[RedisClusterManager] = None


def get_redis_cluster_manager(
    nodes: Optional[List[Dict[str, Any]]] = None
) -> Optional[RedisClusterManager]:
    """
    Get global Redis Cluster manager instance.

    Args:
        nodes: List of cluster nodes (only used on first call)

    Returns:
        RedisClusterManager instance or None
    """
    global _redis_cluster_manager

    if _redis_cluster_manager is None and nodes:
        try:
            _redis_cluster_manager = RedisClusterManager(
                nodes=nodes,
                max_connections=50,
                socket_timeout=5
            )
        except Exception as e:
            logger.error(f"Failed to initialize Redis Cluster manager: {e}")
            return None

    return _redis_cluster_manager


if __name__ == "__main__":
    print("Testing Redis Cluster Manager...")

    # Test consistent hashing
    print("\n1. Testing Consistent Hash Ring:")
    ring = ConsistentHashRing(['node1:6379', 'node2:6379', 'node3:6379'])

    test_keys = ['user:123', 'session:abc', 'cache:xyz']
    for key in test_keys:
        node = ring.get_node(key)
        print(f"   Key '{key}' -> Node '{node}'")

    # Test node addition
    print("\n2. Testing Node Addition:")
    ring.add_node('node4:6379')
    for key in test_keys:
        node = ring.get_node(key)
        print(f"   Key '{key}' -> Node '{node}' (after adding node4)")

    print("\n✅ Redis Cluster manager test complete")

"""
ORFEAS AI 2D→3D Studio - Context Manager
=======================================
Intelligent context handling for AI-driven decision making and process optimization.

Features:
- Comprehensive context building and analysis
- Contextual recommendations and insights
- Context persistence and learning
- Multi-dimensional context analysis
"""

import os
import json
import time
import hashlib
import sqlite3
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProcessingContext:
    """Structured processing context"""
    input_analysis: Dict[str, Any]
    user_context: Dict[str, Any]
    system_context: Dict[str, Any]
    historical_context: Dict[str, Any]
    resource_context: Dict[str, Any]
    quality_context: Dict[str, Any]
    timestamp: str
    context_hash: str

class IntelligentContextManager:
    """
    Advanced context handling for AI-driven decision making
    """

    def __init__(self):
        self.context_store = {}
        self.session_contexts = {}
        self.global_context = {
            'system_performance': {},
            'user_preferences': {},
            'model_performance_history': {},
            'resource_availability': {}
        }
        self.context_db = self.initialize_context_database()
        self.context_cache = {}
        self.cache_lock = threading.Lock()

    def initialize_context_database(self) -> sqlite3.Connection:
        """Initialize context persistence database"""
        try:
            db_path = os.getenv('CONTEXT_DB_PATH', 'data/context.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    context_data TEXT NOT NULL,
                    context_hash TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    processing_time REAL,
                    quality_score REAL,
                    model_used TEXT,
                    resource_usage TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_hash ON context_history(context_hash);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON context_history(timestamp);
            """)
            conn.commit()

            logger.info("[ORFEAS] Context database initialized successfully")
            return conn

        except Exception as e:
            logger.error(f"[ORFEAS] Context database initialization failed: {e}")
            raise

    def build_processing_context(self, request_data: Dict) -> ProcessingContext:
        """Build comprehensive context for AI processing decisions"""

        logger.info("[ORFEAS] Building comprehensive processing context")

        try:
            # 1. Input analysis
            input_analysis = self.analyze_input_characteristics(request_data)

            # 2. User context
            user_context = self.get_user_context(request_data.get('user_id'))

            # 3. System context
            system_context = self.get_system_context()

            # 4. Historical context
            historical_context = self.get_historical_performance()

            # 5. Resource context
            resource_context = self.get_resource_availability()

            # 6. Quality context
            quality_context = self.get_quality_requirements(request_data)

            # Create structured context
            context = ProcessingContext(
                input_analysis=input_analysis,
                user_context=user_context,
                system_context=system_context,
                historical_context=historical_context,
                resource_context=resource_context,
                quality_context=quality_context,
                timestamp=datetime.utcnow().isoformat(),
                context_hash=self.generate_context_hash(input_analysis, user_context, system_context)
            )

            logger.info(f"[ORFEAS] Context built successfully - Hash: {context.context_hash[:8]}")
            return context

        except Exception as e:
            logger.error(f"[ORFEAS] Context building failed: {e}")
            raise

    def analyze_input_characteristics(self, request_data: Dict) -> Dict[str, Any]:
        """Analyze input to determine processing requirements"""

        analysis = {
            'input_type': 'unknown',
            'complexity_score': 0.5,
            'quality_requirements': {},
            'processing_priority': 'normal',
            'estimated_resources': {}
        }

        try:
            # Classify input type
            if 'image' in request_data:
                analysis['input_type'] = 'image'
                # Estimate image complexity (simulated)
                analysis['complexity_score'] = 0.7
                analysis['estimated_resources'] = {'gpu_memory': 6000, 'processing_time': 30}
            elif 'text' in request_data:
                analysis['input_type'] = 'text'
                analysis['complexity_score'] = 0.4
                analysis['estimated_resources'] = {'gpu_memory': 2000, 'processing_time': 5}
            elif 'model' in request_data:
                analysis['input_type'] = '3d_model'
                analysis['complexity_score'] = 0.8
                analysis['estimated_resources'] = {'gpu_memory': 8000, 'processing_time': 45}

            # Extract quality requirements
            analysis['quality_requirements'] = {
                'target_quality': request_data.get('quality', 7),
                'deadline': request_data.get('deadline'),
                'accuracy_priority': request_data.get('accuracy_priority', False)
            }

            # Determine processing priority
            if request_data.get('priority') == 'high':
                analysis['processing_priority'] = 'high'
            elif request_data.get('deadline') and int(request_data['deadline']) < 30:
                analysis['processing_priority'] = 'urgent'

            return analysis

        except Exception as e:
            logger.warning(f"[ORFEAS] Input analysis failed: {e}")
            return analysis

    def get_user_context(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Get user-specific context and preferences"""

        if not user_id:
            return {'type': 'anonymous', 'preferences': {}, 'history': []}

        try:
            # Retrieve user preferences (simulated)
            user_context = {
                'user_id': user_id,
                'type': 'registered',
                'preferences': {
                    'quality_preference': 'high',
                    'speed_preference': 'balanced',
                    'style_preference': 'realistic'
                },
                'history': [],
                'subscription_tier': 'professional',
                'usage_quota': {'used': 45, 'limit': 100}
            }

            return user_context

        except Exception as e:
            logger.warning(f"[ORFEAS] User context retrieval failed: {e}")
            return {'type': 'anonymous', 'preferences': {}, 'history': []}

    def get_system_context(self) -> Dict[str, Any]:
        """Get current system state and performance metrics"""

        try:
            system_context = {
                'current_load': 0.6,  # Simulated
                'available_workers': 3,
                'queue_length': 2,
                'average_response_time': 150,  # ms
                'error_rate': 0.02,
                'uptime': 99.95,
                'active_models': ['hunyuan3d', 'stable_diffusion'],
                'maintenance_mode': False
            }

            return system_context

        except Exception as e:
            logger.warning(f"[ORFEAS] System context retrieval failed: {e}")
            return {'current_load': 0.5, 'available_workers': 1}

    def get_historical_performance(self) -> Dict[str, Any]:
        """Get historical performance data for context"""

        try:
            # Query recent performance data
            cursor = self.context_db.cursor()
            cursor.execute("""
                SELECT model_used, AVG(processing_time), AVG(quality_score), COUNT(*)
                FROM context_history
                WHERE timestamp > ? AND success = 1
                GROUP BY model_used
            """, (time.time() - 86400,))  # Last 24 hours

            performance_data = {}
            for row in cursor.fetchall():
                model, avg_time, avg_quality, count = row
                performance_data[model] = {
                    'average_processing_time': avg_time,
                    'average_quality_score': avg_quality,
                    'usage_count': count
                }

            return {
                'model_performance': performance_data,
                'trend_analysis': self.analyze_performance_trends(),
                'success_rate': self.calculate_recent_success_rate()
            }

        except Exception as e:
            logger.warning(f"[ORFEAS] Historical context retrieval failed: {e}")
            return {'model_performance': {}, 'success_rate': 0.95}

    def get_resource_availability(self) -> Dict[str, Any]:
        """Get current resource availability"""

        try:
            import psutil

            # Get system resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            resource_context = {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'available_memory': memory.available // (1024**3),  # GB
                'disk_usage': psutil.disk_usage('/').percent,
                'network_activity': 'normal'  # Simulated
            }

            # Get GPU resources if available
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

                resource_context.update({
                    'gpu_available': True,
                    'gpu_memory_used': mem_info.used // (1024**2),  # MB
                    'gpu_memory_free': mem_info.free // (1024**2),  # MB
                    'gpu_memory_total': mem_info.total // (1024**2),  # MB
                    'gpu_utilization': pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                })

            except ImportError:
                resource_context['gpu_available'] = False
                resource_context['gpu_memory_free'] = 8000  # Simulated

            return resource_context

        except Exception as e:
            logger.warning(f"[ORFEAS] Resource context retrieval failed: {e}")
            return {
                'cpu_usage': 50.0,
                'memory_usage': 60.0,
                'available_memory': 8,
                'gpu_available': True,
                'gpu_memory_free': 12000
            }

    def get_quality_requirements(self, request_data: Dict) -> Dict[str, Any]:
        """Extract quality requirements from request"""

        quality_context = {
            'target_quality': request_data.get('quality', 7),
            'quality_priority': request_data.get('quality_priority', 'balanced'),
            'accuracy_threshold': 0.85,
            'performance_threshold': 0.80,
            'deadline_constraint': request_data.get('deadline'),
            'budget_constraint': request_data.get('budget_limit')
        }

        # Adjust thresholds based on requirements
        if quality_context['quality_priority'] == 'accuracy':
            quality_context['accuracy_threshold'] = 0.95
        elif quality_context['quality_priority'] == 'speed':
            quality_context['performance_threshold'] = 0.95

        return quality_context

    def generate_context_hash(self, *context_parts) -> str:
        """Generate unique hash for context matching"""

        context_string = json.dumps(context_parts, sort_keys=True)
        return hashlib.md5(context_string.encode()).hexdigest()

    def get_contextual_recommendations(self, context: ProcessingContext) -> Dict[str, Any]:
        """Generate intelligent recommendations based on context"""

        logger.info(f"[ORFEAS] Generating contextual recommendations")

        try:
            recommendations = {
                'optimal_model': self.recommend_model(context),
                'processing_parameters': self.recommend_parameters(context),
                'quality_settings': self.recommend_quality_settings(context),
                'resource_allocation': self.recommend_resources(context),
                'fallback_strategies': self.recommend_fallbacks(context),
                'confidence_score': 0.85
            }

            return recommendations

        except Exception as e:
            logger.error(f"[ORFEAS] Recommendation generation failed: {e}")
            return {'optimal_model': 'hunyuan3d_balanced', 'confidence_score': 0.5}

    def recommend_model(self, context: ProcessingContext) -> str:
        """Recommend optimal model based on context"""

        complexity = context.input_analysis['complexity_score']
        available_vram = context.resource_context.get('gpu_memory_free', 8000)
        quality_target = context.quality_context['target_quality']

        if complexity > 0.8 and available_vram > 12000 and quality_target >= 8:
            return 'hunyuan3d_ultra_quality'
        elif complexity > 0.6 and available_vram > 8000:
            return 'hunyuan3d_high_quality'
        elif context.system_context['current_load'] > 0.8:
            return 'hunyuan3d_fast'
        else:
            return 'hunyuan3d_balanced'

    def recommend_parameters(self, context: ProcessingContext) -> Dict[str, Any]:
        """Recommend optimal processing parameters"""

        params = {
            'inference_steps': 50,
            'guidance_scale': 7.5,
            'batch_size': 1,
            'precision': 'fp16'
        }

        # Adjust based on context
        if context.quality_context['quality_priority'] == 'speed':
            params['inference_steps'] = 25
            params['guidance_scale'] = 5.0
        elif context.quality_context['quality_priority'] == 'accuracy':
            params['inference_steps'] = 100
            params['guidance_scale'] = 10.0

        return params

    def recommend_quality_settings(self, context: ProcessingContext) -> Dict[str, Any]:
        """Recommend quality settings based on context"""

        return {
            'target_quality': context.quality_context['target_quality'],
            'enable_refinement': context.quality_context['target_quality'] >= 8,
            'quality_validation': True,
            'auto_enhancement': context.user_context.get('subscription_tier') == 'professional'
        }

    def recommend_resources(self, context: ProcessingContext) -> Dict[str, Any]:
        """Recommend resource allocation based on context"""

        estimated_resources = context.input_analysis['estimated_resources']
        available_resources = context.resource_context

        return {
            'gpu_memory': min(estimated_resources.get('gpu_memory', 6000),
                            available_resources.get('gpu_memory_free', 8000) * 0.8),
            'cpu_threads': 4 if available_resources.get('cpu_usage', 50) < 70 else 2,
            'processing_timeout': estimated_resources.get('processing_time', 30) * 2
        }

    def recommend_fallbacks(self, context: ProcessingContext) -> List[str]:
        """Recommend fallback strategies"""

        fallbacks = ['hunyuan3d_balanced']

        if context.system_context['current_load'] > 0.8:
            fallbacks.extend(['instant_mesh', 'stable_diffusion_3d'])

        if context.resource_context.get('gpu_memory_free', 8000) < 4000:
            fallbacks.append('cpu_fallback')

        return fallbacks

    def persist_context(self, session_id: str, context: ProcessingContext,
                       result: Optional[Dict] = None):
        """Persist context for learning and analysis"""

        try:
            success = result is not None and result.get('success', False)
            processing_time = result.get('processing_time', 0) if result else 0
            quality_score = result.get('quality_score', 0) if result else 0
            model_used = result.get('model_used', '') if result else ''

            cursor = self.context_db.cursor()
            cursor.execute("""
                INSERT INTO context_history
                (session_id, timestamp, context_data, context_hash, success,
                 processing_time, quality_score, model_used, resource_usage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                time.time(),
                json.dumps(asdict(context)),
                context.context_hash,
                success,
                processing_time,
                quality_score,
                model_used,
                json.dumps(context.resource_context)
            ))
            self.context_db.commit()

            logger.info(f"[ORFEAS] Context persisted successfully - Session: {session_id}")

        except Exception as e:
            logger.error(f"[ORFEAS] Context persistence failed: {e}")

    def get_contextual_insights(self, current_context: ProcessingContext) -> Dict[str, Any]:
        """Get insights based on historical context analysis"""

        try:
            # Find similar contexts
            similar_contexts = self.find_similar_contexts(current_context.context_hash)

            if not similar_contexts:
                return {
                    'success_probability': 0.85,
                    'estimated_processing_time': 30,
                    'confidence': 0.3
                }

            # Calculate insights
            success_rate = sum(1 for ctx in similar_contexts if ctx['success']) / len(similar_contexts)
            avg_processing_time = sum(ctx['processing_time'] for ctx in similar_contexts) / len(similar_contexts)

            insights = {
                'success_probability': success_rate,
                'estimated_processing_time': avg_processing_time,
                'similar_contexts_count': len(similar_contexts),
                'confidence': min(len(similar_contexts) / 10.0, 1.0),
                'optimal_parameters': self.extract_optimal_parameters(similar_contexts),
                'potential_issues': self.identify_potential_issues(similar_contexts)
            }

            return insights

        except Exception as e:
            logger.warning(f"[ORFEAS] Contextual insights generation failed: {e}")
            return {'success_probability': 0.85, 'confidence': 0.3}

    def find_similar_contexts(self, context_hash: str, threshold: float = 0.8) -> List[Dict]:
        """Find similar historical contexts"""

        try:
            cursor = self.context_db.cursor()
            cursor.execute("""
                SELECT * FROM context_history
                WHERE timestamp > ?
                ORDER BY timestamp DESC LIMIT 100
            """, (time.time() - 604800,))  # Last week

            # Simple similarity matching (in production, use vector similarity)
            similar_contexts = []
            for row in cursor.fetchall():
                # Add similarity logic here
                similar_contexts.append({
                    'context_hash': row[3],
                    'success': row[4],
                    'processing_time': row[5],
                    'quality_score': row[6]
                })

            return similar_contexts[:10]  # Return top 10

        except Exception as e:
            logger.warning(f"[ORFEAS] Similar context search failed: {e}")
            return []

    def extract_optimal_parameters(self, contexts: List[Dict]) -> Dict[str, Any]:
        """Extract optimal parameters from successful contexts"""

        successful_contexts = [ctx for ctx in contexts if ctx['success']]

        if not successful_contexts:
            return {}

        # Extract common patterns (simplified)
        return {
            'average_quality': sum(ctx['quality_score'] for ctx in successful_contexts) / len(successful_contexts),
            'success_rate': len(successful_contexts) / len(contexts)
        }

    def identify_potential_issues(self, contexts: List[Dict]) -> List[str]:
        """Identify potential issues based on context history"""

        issues = []

        failed_contexts = [ctx for ctx in contexts if not ctx['success']]
        if len(failed_contexts) / len(contexts) > 0.2:
            issues.append("High failure rate detected for similar contexts")

        long_processing = [ctx for ctx in contexts if ctx['processing_time'] > 60]
        if len(long_processing) / len(contexts) > 0.3:
            issues.append("Processing time may exceed expected duration")

        return issues

    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""

        # Simplified trend analysis
        return {
            'quality_trend': 'improving',
            'performance_trend': 'stable',
            'error_rate_trend': 'decreasing'
        }

    def calculate_recent_success_rate(self) -> float:
        """Calculate recent success rate"""

        try:
            cursor = self.context_db.cursor()
            cursor.execute("""
                SELECT AVG(CAST(success AS REAL)) FROM context_history
                WHERE timestamp > ?
            """, (time.time() - 86400,))  # Last 24 hours

            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0.95

        except Exception:
            return 0.95

    def cleanup_old_contexts(self, days: int = 30):
        """Clean up old context data"""

        try:
            cutoff_time = time.time() - (days * 86400)
            cursor = self.context_db.cursor()
            cursor.execute("DELETE FROM context_history WHERE timestamp < ?", (cutoff_time,))
            self.context_db.commit()

            deleted_count = cursor.rowcount
            logger.info(f"[ORFEAS] Cleaned up {deleted_count} old context records")

        except Exception as e:
            logger.error(f"[ORFEAS] Context cleanup failed: {e}")

    def __del__(self):
        """Cleanup database connection"""
        try:
            if hasattr(self, 'context_db'):
                self.context_db.close()
        except Exception:
            pass

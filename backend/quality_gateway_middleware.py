"""
ORFEAS AI 2D→3D Studio - Quality Gateway Middleware
===================================================
Quality gate enforcement middleware for all requests.

Features:
- Pre-request quality gates
- Post-request quality validation
- Quality metrics collection
- Automated quality enforcement
- Quality-based request routing
- Real-time quality monitoring
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps
from flask import Flask, request, g, jsonify, abort
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class QualityGate:
    """Quality gate configuration"""
    gate_id: str
    name: str
    enabled: bool
    threshold: float
    metric_type: str  # 'performance', 'reliability', 'security', 'user_satisfaction'
    enforcement_level: str  # 'warning', 'blocking', 'adaptive'
    bypass_conditions: List[str]
    remediation_actions: List[str]

@dataclass
class QualityCheck:
    """Quality check result"""
    gate_id: str
    passed: bool
    score: float
    threshold: float
    message: str
    timestamp: float
    remediation_suggested: List[str]

class QualityGatewayMiddleware:
    """
    Quality gate enforcement middleware for Flask applications
    """

    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.quality_gates = {}
        self.quality_history = deque(maxlen=10000)
        self.quality_metrics = defaultdict(list)
        self.bypass_tokens = set()
        self.middleware_enabled = True
        self.setup_default_gates()

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize middleware with Flask app"""
        self.app = app

        # Register middleware hooks
        app.before_request(self.before_request_quality_gate)
        app.after_request(self.after_request_quality_validation)
        app.teardown_request(self.teardown_request_cleanup)

        logger.info("[ORFEAS] Quality Gateway Middleware initialized")

    def setup_default_gates(self):
        """Setup default quality gates"""

        # Performance quality gate
        self.add_quality_gate(QualityGate(
            gate_id="performance_gate",
            name="Performance Quality Gate",
            enabled=True,
            threshold=0.8,
            metric_type="performance",
            enforcement_level="adaptive",
            bypass_conditions=["admin_user", "emergency_mode"],
            remediation_actions=["enable_caching", "optimize_processing"]
        ))

        # Reliability quality gate
        self.add_quality_gate(QualityGate(
            gate_id="reliability_gate",
            name="Reliability Quality Gate",
            enabled=True,
            threshold=0.95,
            metric_type="reliability",
            enforcement_level="warning",
            bypass_conditions=["maintenance_mode"],
            remediation_actions=["check_system_health", "restart_services"]
        ))

        # Security quality gate
        self.add_quality_gate(QualityGate(
            gate_id="security_gate",
            name="Security Quality Gate",
            enabled=True,
            threshold=0.9,
            metric_type="security",
            enforcement_level="blocking",
            bypass_conditions=[],  # No bypass for security
            remediation_actions=["enhance_security", "alert_security_team"]
        ))

        # User satisfaction quality gate
        self.add_quality_gate(QualityGate(
            gate_id="satisfaction_gate",
            name="User Satisfaction Quality Gate",
            enabled=True,
            threshold=0.85,
            metric_type="user_satisfaction",
            enforcement_level="warning",
            bypass_conditions=["beta_testing", "experimental_feature"],
            remediation_actions=["improve_user_experience", "gather_feedback"]
        ))

    def add_quality_gate(self, gate: QualityGate):
        """Add quality gate configuration"""
        self.quality_gates[gate.gate_id] = gate
        logger.info(f"[ORFEAS] Added quality gate: {gate.gate_id}")

    def before_request_quality_gate(self):
        """Execute quality gates before request processing"""

        if not self.middleware_enabled:
            return

        try:
            # Initialize request quality context
            g.quality_context = {
                'start_time': time.time(),
                'gate_results': [],
                'quality_score': 1.0,
                'bypass_active': False,
                'remediation_applied': []
            }

            # Check for bypass conditions
            if self.check_bypass_conditions():
                g.quality_context['bypass_active'] = True
                logger.debug("[ORFEAS] Quality gates bypassed for request")
                return

            # Execute all enabled quality gates
            for gate_id, gate in self.quality_gates.items():
                if gate.enabled:
                    check_result = self.execute_quality_gate(gate)
                    g.quality_context['gate_results'].append(check_result)

                    # Handle gate failure
                    if not check_result.passed:
                        self.handle_gate_failure(gate, check_result)

            # Calculate overall quality score
            if g.quality_context['gate_results']:
                scores = [result.score for result in g.quality_context['gate_results']]
                g.quality_context['quality_score'] = sum(scores) / len(scores)

            # Log quality gate results
            self.log_quality_gate_results(g.quality_context)

        except Exception as e:
            logger.error(f"[ORFEAS] Quality gate execution failed: {e}")
            # Don't block request on middleware failure
            g.quality_context = {'bypass_active': True, 'error': str(e)}

    def execute_quality_gate(self, gate: QualityGate) -> QualityCheck:
        """Execute individual quality gate"""

        try:
            # Get current quality metric
            current_metric = self.get_current_quality_metric(gate.metric_type)

            # Check against threshold
            passed = current_metric >= gate.threshold

            # Generate message
            if passed:
                message = f"Quality gate '{gate.name}' passed: {current_metric:.3f} >= {gate.threshold}"
            else:
                message = f"Quality gate '{gate.name}' failed: {current_metric:.3f} < {gate.threshold}"

            # Suggest remediation if needed
            remediation = gate.remediation_actions if not passed else []

            return QualityCheck(
                gate_id=gate.gate_id,
                passed=passed,
                score=current_metric,
                threshold=gate.threshold,
                message=message,
                timestamp=time.time(),
                remediation_suggested=remediation
            )

        except Exception as e:
            logger.error(f"[ORFEAS] Quality gate execution failed: {gate.gate_id}: {e}")
            # Return failing check on error
            return QualityCheck(
                gate_id=gate.gate_id,
                passed=False,
                score=0.0,
                threshold=gate.threshold,
                message=f"Quality gate execution failed: {str(e)}",
                timestamp=time.time(),
                remediation_suggested=gate.remediation_actions
            )

    def get_current_quality_metric(self, metric_type: str) -> float:
        """Get current quality metric value"""

        try:
            if metric_type == "performance":
                return self.calculate_current_performance_score()
            elif metric_type == "reliability":
                return self.calculate_current_reliability_score()
            elif metric_type == "security":
                return self.calculate_current_security_score()
            elif metric_type == "user_satisfaction":
                return self.calculate_current_satisfaction_score()
            else:
                logger.warning(f"[ORFEAS] Unknown metric type: {metric_type}")
                return 0.8  # Default score

        except Exception as e:
            logger.error(f"[ORFEAS] Metric calculation failed: {metric_type}: {e}")
            return 0.5  # Low score on error

    def calculate_current_performance_score(self) -> float:
        """Calculate current performance score"""

        try:
            # Get recent response times
            recent_times = self.get_recent_response_times(minutes=5)

            if not recent_times:
                return 0.8  # Default score

            avg_time = sum(recent_times) / len(recent_times)

            # Score based on response time (target: <10s)
            if avg_time < 5:
                return 1.0
            elif avg_time < 10:
                return 0.9
            elif avg_time < 20:
                return 0.8
            elif avg_time < 30:
                return 0.7
            else:
                return max(0.5, 0.7 - (avg_time - 30) / 60)

        except Exception:
            return 0.8

    def calculate_current_reliability_score(self) -> float:
        """Calculate current reliability score"""

        try:
            # Get recent error rate
            error_rate = self.get_recent_error_rate(minutes=15)

            # Score based on error rate
            if error_rate < 0.001:  # < 0.1%
                return 1.0
            elif error_rate < 0.005:  # < 0.5%
                return 0.95
            elif error_rate < 0.01:  # < 1%
                return 0.90
            elif error_rate < 0.05:  # < 5%
                return 0.80
            else:
                return max(0.5, 0.8 - error_rate * 10)

        except Exception:
            return 0.95

    def calculate_current_security_score(self) -> float:
        """Calculate current security score"""

        try:
            # Check for recent security events
            security_events = self.get_recent_security_events(minutes=60)

            base_score = 0.95

            # Reduce score based on security events
            for event in security_events:
                severity = event.get('severity', 'low')
                if severity == 'critical':
                    base_score -= 0.2
                elif severity == 'high':
                    base_score -= 0.1
                elif severity == 'medium':
                    base_score -= 0.05

            return max(0.5, base_score)

        except Exception:
            return 0.9

    def calculate_current_satisfaction_score(self) -> float:
        """Calculate current user satisfaction score"""

        try:
            # Get recent user feedback
            recent_feedback = self.get_recent_user_feedback(minutes=120)

            if not recent_feedback:
                return 0.85  # Default score

            # Calculate average rating
            total_ratings = len(recent_feedback)
            avg_rating = sum(feedback.get('rating', 3) for feedback in recent_feedback) / total_ratings

            # Convert 5-star rating to 0-1 scale
            return min(1.0, avg_rating / 5.0)

        except Exception:
            return 0.85

    def handle_gate_failure(self, gate: QualityGate, check_result: QualityCheck):
        """Handle quality gate failure"""

        try:
            if gate.enforcement_level == "blocking":
                # Block request immediately
                logger.warning(f"[ORFEAS] Blocking request due to quality gate failure: {gate.gate_id}")
                abort(503, f"Service temporarily unavailable: {check_result.message}")

            elif gate.enforcement_level == "adaptive":
                # Apply adaptive measures
                self.apply_adaptive_measures(gate, check_result)

            elif gate.enforcement_level == "warning":
                # Log warning but continue
                logger.warning(f"[ORFEAS] Quality gate warning: {check_result.message}")

            # Apply remediation actions
            self.apply_remediation_actions(gate, check_result)

        except Exception as e:
            logger.error(f"[ORFEAS] Gate failure handling failed: {e}")

    def apply_adaptive_measures(self, gate: QualityGate, check_result: QualityCheck):
        """Apply adaptive measures for quality gate failure"""

        try:
            # Determine severity of failure
            score_deficit = gate.threshold - check_result.score

            if score_deficit > 0.2:  # Severe failure
                # Reduce service quality but continue
                g.quality_context['service_degraded'] = True
                g.quality_context['degradation_level'] = 'high'
                logger.warning(f"[ORFEAS] High degradation applied: {gate.gate_id}")

            elif score_deficit > 0.1:  # Moderate failure
                # Minor service degradation
                g.quality_context['service_degraded'] = True
                g.quality_context['degradation_level'] = 'medium'
                logger.info(f"[ORFEAS] Medium degradation applied: {gate.gate_id}")

            else:  # Minor failure
                # Minimal impact
                g.quality_context['service_degraded'] = True
                g.quality_context['degradation_level'] = 'low'
                logger.debug(f"[ORFEAS] Low degradation applied: {gate.gate_id}")

        except Exception as e:
            logger.error(f"[ORFEAS] Adaptive measures failed: {e}")

    def apply_remediation_actions(self, gate: QualityGate, check_result: QualityCheck):
        """Apply remediation actions for quality issues"""

        try:
            for action in check_result.remediation_suggested:
                if self.execute_remediation_action(action):
                    g.quality_context['remediation_applied'].append(action)
                    logger.info(f"[ORFEAS] Applied remediation: {action}")

        except Exception as e:
            logger.error(f"[ORFEAS] Remediation application failed: {e}")

    def execute_remediation_action(self, action: str) -> bool:
        """Execute specific remediation action"""

        try:
            if action == "enable_caching":
                # Enable aggressive caching
                g.quality_context['enable_caching'] = True
                return True

            elif action == "optimize_processing":
                # Enable fast processing mode
                g.quality_context['fast_mode'] = True
                return True

            elif action == "check_system_health":
                # Trigger system health check
                self.trigger_health_check()
                return True

            elif action == "enhance_security":
                # Enable enhanced security monitoring
                g.quality_context['enhanced_security'] = True
                return True

            elif action == "improve_user_experience":
                # Enable UX optimizations
                g.quality_context['ux_optimized'] = True
                return True

            else:
                logger.warning(f"[ORFEAS] Unknown remediation action: {action}")
                return False

        except Exception as e:
            logger.error(f"[ORFEAS] Remediation execution failed: {action}: {e}")
            return False

    def check_bypass_conditions(self) -> bool:
        """Check if quality gates should be bypassed"""

        try:
            # Check for bypass token
            bypass_token = request.headers.get('X-Quality-Bypass')
            if bypass_token in self.bypass_tokens:
                return True

            # Check for admin user
            user_role = request.headers.get('X-User-Role', '').lower()
            if user_role == 'admin':
                return True

            # Check for emergency mode
            if os.getenv('EMERGENCY_MODE', 'false').lower() == 'true':
                return True

            # Check for maintenance mode
            if os.getenv('MAINTENANCE_MODE', 'false').lower() == 'true':
                return True

            return False

        except Exception as e:
            logger.error(f"[ORFEAS] Bypass condition check failed: {e}")
            return False

    def after_request_quality_validation(self, response):
        """Validate quality after request processing"""

        if not self.middleware_enabled or not hasattr(g, 'quality_context'):
            return response

        try:
            # Calculate processing time
            processing_time = time.time() - g.quality_context.get('start_time', time.time())

            # Update quality metrics
            self.update_quality_metrics(response, processing_time)

            # Add quality headers to response
            if not g.quality_context.get('bypass_active', False):
                response.headers['X-Quality-Score'] = str(g.quality_context.get('quality_score', 1.0))
                response.headers['X-Quality-Gates'] = str(len(g.quality_context.get('gate_results', [])))

                if g.quality_context.get('service_degraded', False):
                    response.headers['X-Service-Degraded'] = g.quality_context.get('degradation_level', 'unknown')

            # Store quality history
            self.store_quality_history(g.quality_context, response, processing_time)

        except Exception as e:
            logger.error(f"[ORFEAS] Post-request quality validation failed: {e}")

        return response

    def teardown_request_cleanup(self, error=None):
        """Cleanup after request processing"""

        try:
            # Clean up quality context
            if hasattr(g, 'quality_context'):
                # Log any errors
                if error:
                    logger.error(f"[ORFEAS] Request failed with quality context: {error}")

                # Clear context
                delattr(g, 'quality_context')

        except Exception as e:
            logger.error(f"[ORFEAS] Quality context cleanup failed: {e}")

    def update_quality_metrics(self, response, processing_time: float):
        """Update quality metrics based on request outcome"""

        try:
            timestamp = time.time()

            # Performance metrics
            self.quality_metrics['response_times'].append({
                'timestamp': timestamp,
                'value': processing_time
            })

            # Reliability metrics
            success = response.status_code < 400
            self.quality_metrics['requests'].append({
                'timestamp': timestamp,
                'success': success,
                'status_code': response.status_code
            })

            # Cleanup old metrics (keep last hour)
            cutoff_time = timestamp - 3600
            for metric_type in self.quality_metrics:
                self.quality_metrics[metric_type] = [
                    m for m in self.quality_metrics[metric_type]
                    if m['timestamp'] > cutoff_time
                ]

        except Exception as e:
            logger.error(f"[ORFEAS] Quality metrics update failed: {e}")

    def store_quality_history(self, quality_context: Dict, response, processing_time: float):
        """Store quality history for analysis"""

        try:
            history_entry = {
                'timestamp': time.time(),
                'quality_score': quality_context.get('quality_score', 1.0),
                'gate_results': [asdict(result) for result in quality_context.get('gate_results', [])],
                'processing_time': processing_time,
                'status_code': response.status_code,
                'success': response.status_code < 400,
                'bypass_active': quality_context.get('bypass_active', False),
                'service_degraded': quality_context.get('service_degraded', False),
                'remediation_applied': quality_context.get('remediation_applied', [])
            }

            self.quality_history.append(history_entry)

        except Exception as e:
            logger.error(f"[ORFEAS] Quality history storage failed: {e}")

    def get_recent_response_times(self, minutes: int = 5) -> List[float]:
        """Get recent response times"""

        try:
            cutoff_time = time.time() - (minutes * 60)
            recent_metrics = [
                m['value'] for m in self.quality_metrics['response_times']
                if m['timestamp'] > cutoff_time
            ]
            return recent_metrics if recent_metrics else [15.0]  # Default

        except Exception:
            return [15.0]

    def get_recent_error_rate(self, minutes: int = 15) -> float:
        """Get recent error rate"""

        try:
            cutoff_time = time.time() - (minutes * 60)
            recent_requests = [
                m for m in self.quality_metrics['requests']
                if m['timestamp'] > cutoff_time
            ]

            if not recent_requests:
                return 0.0

            failed_requests = len([r for r in recent_requests if not r['success']])
            return failed_requests / len(recent_requests)

        except Exception:
            return 0.0

    def get_recent_security_events(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get recent security events"""
        # Placeholder - would integrate with security monitoring
        return []

    def get_recent_user_feedback(self, minutes: int = 120) -> List[Dict[str, Any]]:
        """Get recent user feedback"""
        # Placeholder - would integrate with feedback system
        return [{'rating': 4.2}, {'rating': 4.5}]

    def trigger_health_check(self):
        """Trigger system health check"""
        # Placeholder - would trigger actual health check
        logger.info("[ORFEAS] System health check triggered")

    def add_bypass_token(self, token: str):
        """Add bypass token for quality gates"""
        self.bypass_tokens.add(token)
        logger.info(f"[ORFEAS] Added quality gate bypass token")

    def remove_bypass_token(self, token: str):
        """Remove bypass token"""
        self.bypass_tokens.discard(token)
        logger.info(f"[ORFEAS] Removed quality gate bypass token")

    def enable_middleware(self):
        """Enable quality gateway middleware"""
        self.middleware_enabled = True
        logger.info("[ORFEAS] Quality gateway middleware enabled")

    def disable_middleware(self):
        """Disable quality gateway middleware"""
        self.middleware_enabled = False
        logger.warning("[ORFEAS] Quality gateway middleware disabled")

    def get_quality_status(self) -> Dict[str, Any]:
        """Get current quality status"""

        try:
            current_scores = {
                'performance': self.calculate_current_performance_score(),
                'reliability': self.calculate_current_reliability_score(),
                'security': self.calculate_current_security_score(),
                'user_satisfaction': self.calculate_current_satisfaction_score()
            }

            overall_score = sum(current_scores.values()) / len(current_scores)

            # Get recent gate results
            recent_history = list(self.quality_history)[-100:]  # Last 100 requests
            gate_pass_rate = len([h for h in recent_history if h['quality_score'] >= 0.85]) / len(recent_history) if recent_history else 1.0

            return {
                'middleware_enabled': self.middleware_enabled,
                'overall_quality_score': overall_score,
                'dimension_scores': current_scores,
                'gate_pass_rate': gate_pass_rate,
                'total_gates': len(self.quality_gates),
                'enabled_gates': len([g for g in self.quality_gates.values() if g.enabled]),
                'recent_requests': len(recent_history),
                'bypass_tokens_active': len(self.bypass_tokens),
                'last_updated': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"[ORFEAS] Quality status retrieval failed: {e}")
            return {
                'middleware_enabled': self.middleware_enabled,
                'error': str(e)
            }

    def log_quality_gate_results(self, quality_context: Dict):
        """Log quality gate results"""

        try:
            if quality_context.get('bypass_active'):
                logger.debug("[ORFEAS] Quality gates bypassed")
                return

            gate_results = quality_context.get('gate_results', [])
            passed_gates = len([r for r in gate_results if r.passed])
            total_gates = len(gate_results)
            overall_score = quality_context.get('quality_score', 1.0)

            if overall_score < 0.8:
                log_level = logging.WARNING
            elif overall_score < 0.9:
                log_level = logging.INFO
            else:
                log_level = logging.DEBUG

            logger.log(
                log_level,
                f"[ORFEAS] Quality gates: {passed_gates}/{total_gates} passed, "
                f"overall score: {overall_score:.3f}"
            )

            # Log failed gates
            for result in gate_results:
                if not result.passed:
                    logger.warning(f"[ORFEAS] Quality gate failed: {result.message}")

        except Exception as e:
            logger.error(f"[ORFEAS] Quality gate logging failed: {e}")

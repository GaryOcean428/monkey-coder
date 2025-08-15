"""
Advanced Security & Audit System
================================

Enterprise-grade security framework with comprehensive audit logging,
threat detection, and automated security compliance checking.
"""

import asyncio
import hashlib
import hmac
import time
import json
import logging
from typing import Dict, List, Any, Optional, Set, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import re
from contextlib import asynccontextmanager
import threading

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security clearance levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class ThreatLevel(Enum):
    """Threat assessment levels."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditEventType(Enum):
    """Types of audit events."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_ACCESS = "system_access"
    SECURITY_VIOLATION = "security_violation"
    CONFIGURATION_CHANGE = "configuration_change"
    API_CALL = "api_call"

@dataclass
class SecurityContext:
    """Security context for operations."""
    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    permissions: Set[str]
    security_level: SecurityLevel
    expires_at: datetime
    mfa_verified: bool = False
    
    def is_expired(self) -> bool:
        """Check if security context is expired."""
        return datetime.utcnow() > self.expires_at
    
    def has_permission(self, permission: str) -> bool:
        """Check if context has specific permission."""
        return permission in self.permissions or "admin" in self.permissions

@dataclass
class AuditEvent:
    """Audit trail event."""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    resource: str
    action: str
    outcome: str  # success, failure, blocked
    details: Dict[str, Any]
    threat_level: ThreatLevel = ThreatLevel.NONE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'resource': self.resource,
            'action': self.action,
            'outcome': self.outcome,
            'details': self.details,
            'threat_level': self.threat_level.value
        }

@dataclass
class SecurityRule:
    """Security rule definition."""
    name: str
    description: str
    condition: Callable[[SecurityContext, str], bool]
    action: str  # allow, deny, monitor, alert
    priority: int = 0

class ThreatDetector:
    """Advanced threat detection system."""
    
    def __init__(self):
        self._failed_attempts: Dict[str, List[datetime]] = {}
        self._suspicious_ips: Set[str] = set()
        self._blocked_ips: Set[str] = set()
        self._rate_limits: Dict[str, List[datetime]] = {}
        self._lock = threading.RLock()
        
        # Threat patterns
        self._sql_injection_patterns = [
            r"union\s+select", r"drop\s+table", r"insert\s+into",
            r"delete\s+from", r"update\s+.*set", r"exec\s*\(",
            r"xp_cmdshell", r"sp_executesql"
        ]
        
        self._xss_patterns = [
            r"<script", r"javascript:", r"on\w+\s*=",
            r"eval\s*\(", r"alert\s*\(", r"document\.cookie"
        ]
        
        self._path_traversal_patterns = [
            r"\.\./", r"\.\.\\", r"~", r"/etc/passwd",
            r"/windows/system32", r"\.\.%2f", r"\.\.%5c"
        ]
    
    def assess_threat_level(self, security_context: SecurityContext, 
                          request_data: Dict[str, Any]) -> ThreatLevel:
        """Assess threat level for a request."""
        threat_score = 0
        
        # Check for suspicious IP
        if self._is_suspicious_ip(security_context.ip_address):
            threat_score += 30
        
        # Check rate limiting
        if self._check_rate_limit_violation(security_context.user_id, security_context.ip_address):
            threat_score += 20
        
        # Check for attack patterns in request data
        for key, value in request_data.items():
            if isinstance(value, str):
                if self._detect_sql_injection(value):
                    threat_score += 50
                if self._detect_xss(value):
                    threat_score += 40
                if self._detect_path_traversal(value):
                    threat_score += 45
        
        # Check authentication failures
        failed_count = self._get_recent_failed_attempts(security_context.ip_address)
        if failed_count > 10:
            threat_score += 35
        elif failed_count > 5:
            threat_score += 20
        
        # Convert score to threat level
        if threat_score >= 80:
            return ThreatLevel.CRITICAL
        elif threat_score >= 60:
            return ThreatLevel.HIGH
        elif threat_score >= 40:
            return ThreatLevel.MEDIUM
        elif threat_score >= 20:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.NONE
    
    def _detect_sql_injection(self, input_str: str) -> bool:
        """Detect SQL injection patterns."""
        input_lower = input_str.lower()
        return any(re.search(pattern, input_lower, re.IGNORECASE) 
                  for pattern in self._sql_injection_patterns)
    
    def _detect_xss(self, input_str: str) -> bool:
        """Detect XSS patterns."""
        input_lower = input_str.lower()
        return any(re.search(pattern, input_lower, re.IGNORECASE) 
                  for pattern in self._xss_patterns)
    
    def _detect_path_traversal(self, input_str: str) -> bool:
        """Detect path traversal patterns."""
        return any(re.search(pattern, input_str, re.IGNORECASE) 
                  for pattern in self._path_traversal_patterns)
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious."""
        return ip_address in self._suspicious_ips or ip_address in self._blocked_ips
    
    def _check_rate_limit_violation(self, user_id: str, ip_address: str) -> bool:
        """Check for rate limit violations."""
        now = datetime.utcnow()
        window_minutes = 5
        max_requests = 100
        
        with self._lock:
            # Check user rate limit
            user_key = f"user:{user_id}"
            if user_key not in self._rate_limits:
                self._rate_limits[user_key] = []
            
            # Clean old entries
            cutoff = now - timedelta(minutes=window_minutes)
            self._rate_limits[user_key] = [
                timestamp for timestamp in self._rate_limits[user_key] 
                if timestamp > cutoff
            ]
            
            if len(self._rate_limits[user_key]) > max_requests:
                return True
            
            # Check IP rate limit (stricter)
            ip_key = f"ip:{ip_address}"
            if ip_key not in self._rate_limits:
                self._rate_limits[ip_key] = []
            
            self._rate_limits[ip_key] = [
                timestamp for timestamp in self._rate_limits[ip_key] 
                if timestamp > cutoff
            ]
            
            return len(self._rate_limits[ip_key]) > max_requests * 2
    
    def _get_recent_failed_attempts(self, ip_address: str) -> int:
        """Get count of recent failed authentication attempts."""
        if ip_address not in self._failed_attempts:
            return 0
        
        cutoff = datetime.utcnow() - timedelta(hours=1)
        recent_attempts = [
            attempt for attempt in self._failed_attempts[ip_address] 
            if attempt > cutoff
        ]
        return len(recent_attempts)
    
    def record_failed_attempt(self, ip_address: str):
        """Record a failed authentication attempt."""
        with self._lock:
            if ip_address not in self._failed_attempts:
                self._failed_attempts[ip_address] = []
            self._failed_attempts[ip_address].append(datetime.utcnow())
            
            # Auto-block after too many failures
            if len(self._failed_attempts[ip_address]) > 20:
                self._blocked_ips.add(ip_address)
                logger.warning(f"IP {ip_address} auto-blocked due to excessive failed attempts")

class SecurityAuditLogger:
    """Comprehensive security audit logging system."""
    
    def __init__(self, max_events: int = 100000):
        self._events: List[AuditEvent] = []
        self._max_events = max_events
        self._lock = threading.RLock()
        self._threat_detector = ThreatDetector()
    
    def log_event(self, event_type: AuditEventType, resource: str, action: str,
                  outcome: str, security_context: Optional[SecurityContext] = None,
                  details: Optional[Dict[str, Any]] = None,
                  request_data: Optional[Dict[str, Any]] = None) -> str:
        """Log a security audit event."""
        event_id = self._generate_event_id()
        timestamp = datetime.utcnow()
        
        if details is None:
            details = {}
            
        if request_data is None:
            request_data = {}
        
        # Assess threat level
        threat_level = ThreatLevel.NONE
        if security_context and request_data:
            threat_level = self._threat_detector.assess_threat_level(security_context, request_data)
        
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=timestamp,
            user_id=security_context.user_id if security_context else None,
            session_id=security_context.session_id if security_context else None,
            ip_address=security_context.ip_address if security_context else None,
            resource=resource,
            action=action,
            outcome=outcome,
            details=details,
            threat_level=threat_level
        )
        
        with self._lock:
            self._events.append(event)
            
            # Trim events if needed
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events:]
        
        # Log high-threat events immediately
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            logger.error(f"HIGH THREAT DETECTED: {event.to_dict()}")
        
        return event_id
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = str(int(time.time() * 1000000))
        return hashlib.md5(timestamp.encode()).hexdigest()[:16]
    
    def get_events(self, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   event_type: Optional[AuditEventType] = None,
                   user_id: Optional[str] = None,
                   threat_level: Optional[ThreatLevel] = None,
                   limit: int = 1000) -> List[AuditEvent]:
        """Query audit events with filters."""
        with self._lock:
            events = list(self._events)
        
        # Apply filters
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if threat_level:
            events = [e for e in events if e.threat_level == threat_level]
        
        # Sort by timestamp (newest first) and limit
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]
    
    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get security summary for the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_events = self.get_events(start_time=cutoff_time)
        
        summary = {
            'time_window_hours': hours,
            'total_events': len(recent_events),
            'events_by_type': {},
            'events_by_outcome': {},
            'threat_levels': {},
            'top_users': {},
            'top_resources': {},
            'suspicious_activity': []
        }
        
        # Analyze events
        for event in recent_events:
            # By type
            event_type = event.event_type.value
            summary['events_by_type'][event_type] = summary['events_by_type'].get(event_type, 0) + 1
            
            # By outcome
            summary['events_by_outcome'][event.outcome] = summary['events_by_outcome'].get(event.outcome, 0) + 1
            
            # By threat level
            threat_level = event.threat_level.value
            summary['threat_levels'][threat_level] = summary['threat_levels'].get(threat_level, 0) + 1
            
            # By user
            if event.user_id:
                summary['top_users'][event.user_id] = summary['top_users'].get(event.user_id, 0) + 1
            
            # By resource
            summary['top_resources'][event.resource] = summary['top_resources'].get(event.resource, 0) + 1
            
            # Suspicious activity
            if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                summary['suspicious_activity'].append({
                    'event_id': event.event_id,
                    'timestamp': event.timestamp.isoformat(),
                    'user_id': event.user_id,
                    'ip_address': event.ip_address,
                    'action': event.action,
                    'threat_level': event.threat_level.value
                })
        
        return summary

class AccessController:
    """Advanced access control system."""
    
    def __init__(self):
        self._security_rules: List[SecurityRule] = []
        self._audit_logger = SecurityAuditLogger()
        self._jwt_secret = "your-secret-key"  # Should be configurable
        self._lock = threading.RLock()
    
    def add_security_rule(self, rule: SecurityRule):
        """Add a security rule."""
        with self._lock:
            self._security_rules.append(rule)
            self._security_rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Added security rule: {rule.name}")
    
    async def check_access(self, security_context: SecurityContext, 
                          resource: str, action: str,
                          request_data: Optional[Dict[str, Any]] = None) -> bool:
        """Check if access should be granted."""
        if request_data is None:
            request_data = {}
        
        # Check if context is expired
        if security_context.is_expired():
            await self._log_access_attempt(
                security_context, resource, action, "denied", 
                {"reason": "expired_context"}, request_data
            )
            return False
        
        # Evaluate security rules
        for rule in self._security_rules:
            try:
                if rule.condition(security_context, resource):
                    if rule.action == "deny":
                        await self._log_access_attempt(
                            security_context, resource, action, "denied",
                            {"reason": f"blocked_by_rule_{rule.name}"}, request_data
                        )
                        return False
                    elif rule.action == "allow":
                        await self._log_access_attempt(
                            security_context, resource, action, "allowed",
                            {"reason": f"allowed_by_rule_{rule.name}"}, request_data
                        )
                        return True
                    # If monitor or alert, continue evaluation
            except Exception as e:
                logger.error(f"Error evaluating security rule {rule.name}: {e}")
        
        # Default to permission-based access
        has_access = security_context.has_permission(f"{resource}:{action}")
        outcome = "allowed" if has_access else "denied"
        reason = "permission_check"
        
        await self._log_access_attempt(
            security_context, resource, action, outcome,
            {"reason": reason}, request_data
        )
        
        return has_access
    
    async def _log_access_attempt(self, security_context: SecurityContext,
                                 resource: str, action: str, outcome: str,
                                 details: Dict[str, Any],
                                 request_data: Dict[str, Any]):
        """Log an access attempt."""
        self._audit_logger.log_event(
            event_type=AuditEventType.AUTHORIZATION,
            resource=resource,
            action=action,
            outcome=outcome,
            security_context=security_context,
            details=details,
            request_data=request_data
        )
    
    def create_security_context(self, user_id: str, ip_address: str, 
                               user_agent: str, permissions: Set[str],
                               security_level: SecurityLevel = SecurityLevel.INTERNAL,
                               duration_hours: int = 8) -> SecurityContext:
        """Create a new security context."""
        session_id = self._generate_session_id()
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        context = SecurityContext(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            permissions=permissions,
            security_level=security_level,
            expires_at=expires_at
        )
        
        self._audit_logger.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            resource="session",
            action="create",
            outcome="success",
            security_context=context,
            details={"duration_hours": duration_hours}
        )
        
        return context
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = str(int(time.time() * 1000000))
        return hashlib.sha256(timestamp.encode()).hexdigest()[:32]
    
    def get_audit_logger(self) -> SecurityAuditLogger:
        """Get the audit logger instance."""
        return self._audit_logger

# Global access controller instance
_global_access_controller: Optional[AccessController] = None

def get_access_controller() -> AccessController:
    """Get the global access controller instance."""
    global _global_access_controller
    if _global_access_controller is None:
        _global_access_controller = AccessController()
    return _global_access_controller

def setup_default_security_rules():
    """Setup default security rules."""
    controller = get_access_controller()
    
    # Block access from suspicious IPs
    controller.add_security_rule(SecurityRule(
        name="block_suspicious_ips",
        description="Block access from known suspicious IP addresses",
        condition=lambda ctx, resource: ctx.ip_address in ["192.168.1.100"],  # Example
        action="deny",
        priority=100
    ))
    
    # Require MFA for sensitive operations
    controller.add_security_rule(SecurityRule(
        name="require_mfa_sensitive",
        description="Require MFA for sensitive operations",
        condition=lambda ctx, resource: resource.startswith("admin/") and not ctx.mfa_verified,
        action="deny",
        priority=90
    ))
    
    # Block expired sessions
    controller.add_security_rule(SecurityRule(
        name="block_expired_sessions",
        description="Block access from expired sessions",
        condition=lambda ctx, resource: ctx.is_expired(),
        action="deny",
        priority=95
    ))

# Decorators for easy integration
def require_security_context(func):
    """Decorator to require security context for function calls."""
    async def wrapper(*args, **kwargs):
        # This would typically extract security context from request
        # For now, it's a placeholder
        security_context = kwargs.get('security_context')
        if not security_context:
            raise PermissionError("Security context required")
        
        controller = get_access_controller()
        resource = kwargs.get('resource', func.__name__)
        action = kwargs.get('action', 'execute')
        
        if not await controller.check_access(security_context, resource, action):
            raise PermissionError(f"Access denied to {resource}:{action}")
        
        return await func(*args, **kwargs)
    return wrapper
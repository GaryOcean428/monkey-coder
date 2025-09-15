"""
Production Logging Configuration

Enhanced logging configuration for Railway deployment with:
- Structured JSON logging for production monitoring
- Error tracking integration with Sentry
- Performance logging and request tracing
- Security audit logging
"""

import os
import sys
import json
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.asyncio import AsyncioIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging in production.
    
    Formats log records as JSON for better parsing by log aggregation tools.
    """
    
    def format(self, record):
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'execution_time'):
            log_entry['execution_time_ms'] = record.execution_time
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        
        # Add exception information
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add stack info if available
        if record.stack_info:
            log_entry['stack_info'] = record.stack_info
        
        return json.dumps(log_entry, ensure_ascii=False)


class SecurityAuditLogger:
    """
    Security audit logger for tracking authentication and authorization events.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('monkey_coder.security.audit')
        self.logger.setLevel(logging.INFO)
        
        # Create separate handler for security logs
        if os.getenv('ENVIRONMENT') == 'production':
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)
    
    def log_authentication_attempt(self, user_id: str, success: bool, 
                                 method: str, ip_address: str = None):
        """Log authentication attempt."""
        self.logger.info(
            f"Authentication attempt: {'SUCCESS' if success else 'FAILED'}",
            extra={
                'user_id': user_id,
                'auth_method': method,
                'ip_address': ip_address,
                'event_type': 'authentication',
                'success': success
            }
        )
    
    def log_api_key_usage(self, key_id: str, endpoint: str, 
                         success: bool, rate_limited: bool = False):
        """Log API key usage."""
        self.logger.info(
            f"API key usage: {endpoint}",
            extra={
                'key_id': key_id,
                'endpoint': endpoint,
                'success': success,
                'rate_limited': rate_limited,
                'event_type': 'api_key_usage'
            }
        )
    
    def log_permission_check(self, user_id: str, permission: str, 
                           granted: bool, resource: str = None):
        """Log permission check."""
        self.logger.info(
            f"Permission check: {permission} {'GRANTED' if granted else 'DENIED'}",
            extra={
                'user_id': user_id,
                'permission': permission,
                'resource': resource,
                'granted': granted,
                'event_type': 'permission_check'
            }
        )
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], 
                          severity: str = 'INFO'):
        """Log generic security event."""
        level = getattr(logging, severity.upper(), logging.INFO)
        self.logger.log(
            level,
            f"Security event: {event_type}",
            extra={
                'event_type': event_type,
                'severity': severity,
                **details
            }
        )


class PerformanceLogger:
    """
    Performance logger for tracking request times and system metrics.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('monkey_coder.performance')
        self.logger.setLevel(logging.INFO)
    
    def log_request_performance(self, endpoint: str, method: str, 
                              execution_time: float, status_code: int,
                              user_id: str = None, request_id: str = None):
        """Log request performance metrics."""
        self.logger.info(
            f"Request performance: {method} {endpoint}",
            extra={
                'endpoint': endpoint,
                'method': method,
                'execution_time': execution_time,
                'status_code': status_code,
                'user_id': user_id,
                'request_id': request_id,
                'event_type': 'request_performance'
            }
        )
    
    def log_ai_provider_performance(self, provider: str, model: str,
                                  tokens_used: int, response_time: float,
                                  success: bool, cost: float = None):
        """Log AI provider performance."""
        self.logger.info(
            f"AI provider performance: {provider}/{model}",
            extra={
                'provider': provider,
                'model': model,
                'tokens_used': tokens_used,
                'response_time': response_time,
                'success': success,
                'cost': cost,
                'event_type': 'ai_provider_performance'
            }
        )
    
    def log_database_performance(self, operation: str, table: str,
                               execution_time: float, rows_affected: int = None):
        """Log database operation performance."""
        self.logger.info(
            f"Database performance: {operation} on {table}",
            extra={
                'operation': operation,
                'table': table,
                'execution_time': execution_time,
                'rows_affected': rows_affected,
                'event_type': 'database_performance'
            }
        )


def setup_production_logging(enable_sentry: bool = True) -> Dict[str, Any]:
    """
    Setup production logging configuration.
    
    Configures structured JSON logging, Sentry integration, and performance tracking.
    
    Returns:
        Dict with logging configuration status
    """
    config_status = {
        'json_logging': False,
        'sentry_integration': False,
        'security_audit': False,
        'performance_logging': False,
        'log_level': 'INFO'
    }
    
    # Get configuration from environment
    environment = os.getenv('ENVIRONMENT', 'development')
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    sentry_dsn = os.getenv('SENTRY_DSN')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    if environment == 'production':
        # Use JSON formatter for production
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        root_logger.addHandler(handler)
        config_status['json_logging'] = True
        
        # Configure structured logging for specific modules
        for logger_name in [
            'monkey_coder.app',
            'monkey_coder.core',
            'monkey_coder.database',
            'monkey_coder.auth',
            'monkey_coder.providers'
        ]:
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, log_level))
            logger.propagate = True
    
    else:
        # Use simple formatter for development
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    
    # Setup Sentry integration
    if enable_sentry and sentry_dsn and SENTRY_AVAILABLE:
        try:
            sentry_logging = LoggingIntegration(
                level=logging.INFO,        # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors as events
            )
            
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[sentry_logging, AsyncioIntegration()],
                traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
                environment=environment,
                release=os.getenv('RAILWAY_DEPLOYMENT_ID', 'unknown'),
                attach_stacktrace=True,
                send_default_pii=False  # Don't send personally identifiable information
            )
            
            config_status['sentry_integration'] = True
            logging.info("Sentry integration configured successfully")
            
        except Exception as e:
            logging.warning(f"Failed to configure Sentry: {e}")
    
    # Suppress noisy third-party loggers in production
    if environment == 'production':
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # Initialize specialized loggers
    config_status['security_audit'] = True
    config_status['performance_logging'] = True
    config_status['log_level'] = log_level
    
    logging.info(f"Production logging configured: {config_status}")
    return config_status


def get_security_audit_logger() -> SecurityAuditLogger:
    """Get global security audit logger instance."""
    if not hasattr(get_security_audit_logger, '_instance'):
        get_security_audit_logger._instance = SecurityAuditLogger()
    return get_security_audit_logger._instance


def get_performance_logger() -> PerformanceLogger:
    """Get global performance logger instance."""
    if not hasattr(get_performance_logger, '_instance'):
        get_performance_logger._instance = PerformanceLogger()
    return get_performance_logger._instance


def create_request_logger(request_id: str) -> logging.LoggerAdapter:
    """
    Create a logger adapter with request context.
    
    Automatically includes request ID in all log messages.
    """
    logger = logging.getLogger('monkey_coder.request')
    return logging.LoggerAdapter(logger, {'request_id': request_id})


# Auto-configure logging on import in production
if os.getenv('ENVIRONMENT') == 'production':
    setup_production_logging()
from . import quantum_performance  # re-export for easy import path

# Import BillingTracker and MetricsCollector from the sibling monitoring.py module
# These are used by the main app but defined in the standalone monitoring.py
# Use lazy import to avoid circular import issues
def _get_monitoring_classes():
    """Lazy import monitoring classes to avoid circular imports."""
    try:
        from .monitoring import BillingTracker as RealBillingTracker, MetricsCollector as RealMetricsCollector
        return RealBillingTracker, RealMetricsCollector
    except (ImportError, AttributeError):
        # Fallback classes for development environments
        class MetricsCollector:
            def __init__(self):
                pass
            def start_execution(self, request):
                return "placeholder"
            def complete_execution(self, execution_id, response):
                pass
            def record_error(self, execution_id, error):
                pass
            def record_http_request(self, method, endpoint, status, duration):
                pass
            def get_prometheus_metrics(self):
                return b"# Metrics collector not available\n"
        
        class BillingTracker:
            def __init__(self):
                pass
            async def track_usage(self, api_key, usage):
                pass
            async def get_usage(self, api_key, start_date, end_date, granularity):
                return {}
        
        return BillingTracker, MetricsCollector

BillingTracker, MetricsCollector = _get_monitoring_classes()

def __getattr__(name):
    """Support lazy loading of monitoring classes."""
    if name == "BillingTracker":
        return BillingTracker
    elif name == "MetricsCollector":
        return MetricsCollector
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["quantum_performance", "BillingTracker", "MetricsCollector"]

from . import quantum_performance  # re-export for easy import path

# Import BillingTracker and MetricsCollector from the parent monitoring module
# These are used by the main app but defined in the standalone monitoring.py
# Use lazy import to avoid circular import issues
def _get_monitoring_classes():
    """Lazy import monitoring classes to avoid circular imports."""
    try:
        from .. import monitoring as parent_monitoring
        return parent_monitoring.BillingTracker, parent_monitoring.MetricsCollector
    except (ImportError, AttributeError):
        # Fallback classes for development environments
        class MetricsCollector:
            def __init__(self):
                pass
            def record_execution(self, *args, **kwargs):
                pass
        
        class BillingTracker:
            def __init__(self):
                pass
            def track_usage(self, *args, **kwargs):
                pass
        
        return BillingTracker, MetricsCollector

# Lazy loading
BillingTracker = None
MetricsCollector = None

def __getattr__(name):
    """Support lazy loading of monitoring classes."""
    global BillingTracker, MetricsCollector
    if name in ("BillingTracker", "MetricsCollector") and BillingTracker is None:
        BillingTracker, MetricsCollector = _get_monitoring_classes()
    
    if name == "BillingTracker":
        return BillingTracker
    elif name == "MetricsCollector":
        return MetricsCollector
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["quantum_performance", "BillingTracker", "MetricsCollector"]

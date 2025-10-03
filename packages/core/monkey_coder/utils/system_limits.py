"""
System Resource Limits Utility

Probes and logs system resource limits at runtime to detect potential issues
before they cause crashes in production.

Common issues prevented:
- Undici socket errors under load (Node.js/FastAPI)
- Headless browser/WASM OOM despite low app usage
- Blank pages / builds passing but runtime silently failing
"""

import os
import subprocess
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


def _load_limits_config() -> Dict[str, Any]:
    """Load system limits configuration from shared config file."""
    try:
        # Try to find config relative to this file
        config_paths = [
            Path(__file__).parents[4] / "config" / "system-limits.config.json",  # From packages/core/monkey_coder/utils
            Path(__file__).parents[3] / "config" / "system-limits.config.json",  # Fallback
            Path.cwd() / "config" / "system-limits.config.json",  # From project root
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        
        # Fallback to hardcoded defaults if config not found
        logger.warning("System limits config file not found, using defaults")
        return {
            "limits": {
                "open_files": {"min": 65535, "warning_template": "Open files limit is low ({value}). Recommended: ≥{min}."},
                "virtual_memory": {"expected": "unlimited", "warning_template": "Virtual memory limit is restricted ({value}). Recommended: {expected}."},
                "threadpool_size": {"min": 64, "default": 4, "warning_template": "UV_THREADPOOL_SIZE not set or too low ({value}). Recommended: {min}."}
            }
        }
    except Exception as e:
    nofile = subprocess.check_output(
        ['sh', '-c', 'ulimit -n'],
        stderr=subprocess.DEVNULL,
        encoding='utf-8'
    ).strip()
    
    # Get virtual memory limit
    vmem = subprocess.check_output(
        ['sh', '-c', 'ulimit -v'],
        stderr=subprocess.DEVNULL,
        encoding='utf-8'
    ).strip()
    
    # Try to get max processes
    max_proc = "unavailable"
    try:
        max_proc = subprocess.check_output(
            ['sh', '-c', 'ulimit -u'],
            stderr=subprocess.DEVNULL,
    max_processes: str = "unavailable"
    threadpool_size: Optional[int] = None
    available: bool = False
    

@dataclass
class LimitCheckResult:
    """Result of system limits check."""
    limits: SystemLimits
    warnings: List[str] = field(default_factory=list)
    ok: bool = True


def probe_system_limits() -> SystemLimits:
    """
    Probe system resource limits using ulimit command.
    
    Returns:
        SystemLimits object with current limits or unavailable status
    """
    try:
        # Get open files limit
        nofile = subprocess.check_output(
            ['bash', '-c', 'ulimit -n'],
            stderr=subprocess.DEVNULL,
            encoding='utf-8'
        ).strip()
        
        # Get virtual memory limit
        vmem = subprocess.check_output(
            ['bash', '-c', 'ulimit -v'],
            stderr=subprocess.DEVNULL,
            encoding='utf-8'
        ).strip()
        
        # Try to get max processes
        max_proc = "unavailable"
        try:
            max_proc = subprocess.check_output(
                ['bash', '-c', 'ulimit -u'],
                stderr=subprocess.DEVNULL,
                encoding='utf-8'
            ).strip()
        except subprocess.CalledProcessError:
            # Not available on all systems
            pass
        
        # Get UV_THREADPOOL_SIZE if set (Node.js environment variable)
        threadpool_size = None
        if 'UV_THREADPOOL_SIZE' in os.environ:
            try:
                threadpool_size = int(os.environ['UV_THREADPOOL_SIZE'])
            except (ValueError, TypeError):
                pass
        
        return SystemLimits(
            open_files=nofile,
            virtual_memory=vmem,
            max_processes=max_proc,
            threadpool_size=threadpool_size,
            available=True
        )
        
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
        logger.debug(f"Unable to probe system limits: {e}")
        return SystemLimits(available=False)


def check_system_limits() -> LimitCheckResult:
    """
    Check if system limits meet recommended thresholds using shared configuration.
    
    Returns:
        LimitCheckResult with limits, warnings, and ok status
    """
    limits = probe_system_limits()
    warnings = []
    
    if not limits.available:
        return LimitCheckResult(
            limits=limits,
            warnings=['Unable to probe system limits (ulimit not available in this environment)'],
            ok=True  # Don't fail if we can't check
        )
    
    config_limits = _CONFIG.get("limits", {})
    
    # Check open files limit
    open_files_config = config_limits.get("open_files", {})
    min_open_files = open_files_config.get("min", 65535)
    try:
        nofile = int(limits.open_files)
        if nofile < min_open_files:
            template = open_files_config.get("warning_template", "Open files limit is low ({value}). Recommended: ≥{min}.")
            warning = template.format(value=nofile, min=min_open_files)
            warnings.append(warning)
    except (ValueError, TypeError):
        pass
    
    # Check virtual memory limit
    vmem_config = config_limits.get("virtual_memory", {})
    expected_vmem = vmem_config.get("expected", "unlimited")
    vmem = limits.virtual_memory
    if vmem not in (expected_vmem, 'unavailable'):
        try:
            vmem_num = int(vmem)
            if vmem_num > 0:
                template = vmem_config.get("warning_template", "Virtual memory limit is restricted ({value}). Recommended: {expected}.")
                warning = template.format(value=vmem, expected=expected_vmem)
                warnings.append(warning)
        except (ValueError, TypeError):
            pass
    
    # Check UV_THREADPOOL_SIZE for Node.js I/O performance
    threadpool_config = config_limits.get("threadpool_size", {})
    min_threadpool = threadpool_config.get("min", 64)
    default_threadpool = threadpool_config.get("default", 4)
    
    if not limits.threadpool_size or limits.threadpool_size < min_threadpool:
        template = threadpool_config.get("warning_template", "UV_THREADPOOL_SIZE not set or too low ({value}). Recommended: {min}.")
        value_display = limits.threadpool_size or f'default {default_threadpool}'
        warning = template.format(value=value_display, min=min_threadpool)
        warnings.append(warning)
    
    return LimitCheckResult(
        limits=limits,
        warnings=warnings,
        ok=len(warnings) == 0
    )


def log_system_limits(prefix: str = "[preflight]") -> None:
    """
    Log system limits information to logger.
    
    Args:
        prefix: Prefix for log messages
    """
    result = check_system_limits()
    
    if not result.limits.available:
        logger.info(f"{prefix} ulimit probe not available in this environment")
        return
    
    logger.info(f"{prefix} System Resource Limits:")
    logger.info(f"{prefix}   open files      = {result.limits.open_files}")
    logger.info(f"{prefix}   virtual memory  = {result.limits.virtual_memory}")
    if result.limits.max_processes != "unavailable":
        logger.info(f"{prefix}   max processes   = {result.limits.max_processes}")
    if result.limits.threadpool_size is not None:
        logger.info(f"{prefix}   threadpool size = {result.limits.threadpool_size}")
    
    if result.warnings:
        logger.warning(f"{prefix} ⚠️  Resource limit warnings:")
        for warning in result.warnings:
            logger.warning(f"{prefix}   - {warning}")
    else:
        logger.info(f"{prefix} ✅ All resource limits are properly configured")


def get_system_limits_info() -> Dict[str, Any]:
    """
    Get formatted system limits for structured logging.
    
    Returns:
        Dictionary with limits, warnings, and ok status
    """
    result = check_system_limits()
    return {
        "limits": {
            "open_files": result.limits.open_files,
            "virtual_memory": result.limits.virtual_memory,
            "max_processes": result.limits.max_processes,
            "threadpool_size": result.limits.threadpool_size,
            "available": result.limits.available,
        },
        "warnings": result.warnings,
        "ok": result.ok,
    }


# Convenience function for startup logging
def log_startup_limits() -> None:
    """Log system limits at application startup."""
    log_system_limits("[startup]")

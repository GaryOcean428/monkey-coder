#!/usr/bin/env python3
"""
Railway Provisioning Orchestrator
---------------------------------
High-level automation entrypoint for preparing and validating a Monkey Coder
deployment on Railway. This tool consolidates environment verification,
frontend build integrity checks, and (placeholder) Railway API interactions.

Scope (Phase 1 - Local Validation Only):
  * Load and validate required environment variables (.env.railway / process)
  * Confirm frontend static export integrity (strict Option A enforcement)
  * Provide actionable diff of missing / weak env vars before remote provisioning
  * Generate a provisioning plan JSON for visibility

Future (Phase 2 - Remote Operations):
  * Use Railway MCP API integration to: list projects, create service, set env vars,
    trigger deployment, stream build logs, validate status.

Design Principles:
  * Idempotent: running multiple times should not mutate local state unexpectedly
  * Read-first: collects context before any destructive / remote actions
  * Extensible: clear separation between validation and remote API layer

Exit Codes:
  0 = All green / ready for remote provisioning
  1 = Missing required variables or frontend build invalid
  2 = Unexpected internal error
"""

from __future__ import annotations

import os
import sys
import json
import hashlib
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("railway_provisioning")


def load_env_files() -> None:
    """Best-effort load of env files (.env, .env.railway, .env.local).

    This is intentionally minimal (not a full dotenv parser). Lines of the form
    KEY=VALUE are exported if the key is not already in the environment.
    Quotes are stripped. Comments (#) and blank lines skipped.
    Precedence: existing os.environ wins over files.
    """
    candidate_files = [
        Path('.env.railway'),
        Path('.env'),
        Path('.env.local'),
        Path('.env.production'),
    ]
    for f in candidate_files:
        if not f.exists():
            continue
        try:
            for line in f.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                key, val = line.split('=', 1)
                key = key.strip()
                if key and key not in os.environ:
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val
        except Exception as e:  # pragma: no cover
            logger.warning(f"Failed parsing {f}: {e}")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

@dataclass
class EnvCheckResult:
    name: str
    present: bool
    value_preview: Optional[str]
    required: bool
    secret: bool
    default_used: bool

@dataclass
class FrontendIntegrityResult:
    present: bool
    index_hash: Optional[str]
    files_count: int
    missing_reason: Optional[str]

@dataclass
class ProvisioningAssessment:
    env_summary: Dict[str, Any]
    frontend: FrontendIntegrityResult
    ready: bool
    missing_required: List[str]
    recommendations: List[str]


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REQUIRED_ENV = [
    ("NODE_ENV", True, False, "production"),
    ("PYTHON_ENV", True, False, "production"),
    ("JWT_SECRET_KEY", True, True, None),
    ("NEXTAUTH_SECRET", True, True, None),
    ("NEXTAUTH_URL", True, False, "https://coder.fastmonkey.au"),
    ("NEXT_PUBLIC_API_URL", True, False, "https://coder.fastmonkey.au"),
    ("NEXT_PUBLIC_APP_URL", True, False, "https://coder.fastmonkey.au"),
    ("NEXT_OUTPUT_EXPORT", True, False, "true"),
    ("NEXT_TELEMETRY_DISABLED", True, False, "1"),
]

OPTIONAL_ENV = [
    ("OPENAI_API_KEY", False, True, None),
    ("ANTHROPIC_API_KEY", False, True, None),
    ("GOOGLE_API_KEY", False, True, None),
    ("GROQ_API_KEY", False, True, None),
]

FRONTEND_OUT_DIR = Path("packages/web/out")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _preview(value: Optional[str], secret: bool) -> Optional[str]:
    if value is None:
        return None
    if secret and len(value) >= 8:
        return value[:4] + "..." + value[-4:]
    return value if len(value) <= 40 else value[:37] + "..."


def check_environment() -> Dict[str, EnvCheckResult]:
    results: Dict[str, EnvCheckResult] = {}
    for name, required, secret, default in REQUIRED_ENV + OPTIONAL_ENV:
        raw = os.getenv(name)
        present = raw is not None and raw.strip() != ""
        default_used = False
        if not present and default is not None:
            default_used = True
        results[name] = EnvCheckResult(
            name=name,
            present=present,
            value_preview=_preview(raw, secret),
            required=required,
            secret=secret,
            default_used=default_used,
        )
    return results


def check_frontend_integrity() -> FrontendIntegrityResult:
    if not FRONTEND_OUT_DIR.exists():
        return FrontendIntegrityResult(False, None, 0, "out directory missing")
    index_path = FRONTEND_OUT_DIR / "index.html"
    next_dir = FRONTEND_OUT_DIR / "_next"
    if not index_path.exists():
        return FrontendIntegrityResult(False, None, 0, "index.html missing")
    if not next_dir.exists():
        return FrontendIntegrityResult(False, None, 0, "_next directory missing")
    try:
        digest = hashlib.sha256(index_path.read_bytes()).hexdigest()
    except Exception as e:  # pragma: no cover (unlikely)
        return FrontendIntegrityResult(False, None, 0, f"hash failure: {e}")
    files_count = sum(1 for _ in FRONTEND_OUT_DIR.rglob("*") if _.is_file())
    return FrontendIntegrityResult(True, digest, files_count, None)


def assess() -> ProvisioningAssessment:
    # Load env files first (non-destructive for existing live vars)
    load_env_files()
    env_results = check_environment()
    missing_required = [n for n, r in env_results.items() if r.required and not r.present]
    frontend = check_frontend_integrity()
    ready = len(missing_required) == 0 and frontend.present
    recommendations: List[str] = []
    if missing_required:
        recommendations.append("Set all missing required environment variables before provisioning")
    if not frontend.present:
        recommendations.append("Run frontend export: yarn workspace @monkey-coder/web run export (verify out/index.html & _next)")
    if any(r.default_used for r in env_results.values() if r.required):
        recommendations.append("Replace default fallbacks with explicit values for production consistency")
    return ProvisioningAssessment(
        env_summary={k: asdict(v) for k, v in env_results.items()},
        frontend=frontend,
        ready=ready,
        missing_required=missing_required,
        recommendations=recommendations,
    )


def write_plan(assessment: ProvisioningAssessment, path: Path) -> None:
    payload = {
        "version": 1,
        "ready": assessment.ready,
        "missing_required": assessment.missing_required,
        "frontend": asdict(assessment.frontend),
        "environment": assessment.env_summary,
        "recommendations": assessment.recommendations,
    }
    path.write_text(json.dumps(payload, indent=2))
    logger.info(f"Provisioning plan written to {path}")


def main() -> int:
    logger.info("Running Railway provisioning preflight assessment (Phase 1)")
    assessment = assess()
    plan_path = Path("railway_provisioning_plan.json")
    write_plan(assessment, plan_path)

    # Human-readable summary
    logger.info("--- Summary ---")
    logger.info(f"Frontend build present: {assessment.frontend.present}")
    if assessment.frontend.present:
        logger.info(f"index.html sha256: {assessment.frontend.index_hash}")
        logger.info(f"Frontend files: {assessment.frontend.files_count}")
    if assessment.missing_required:
        logger.warning(f"Missing required env vars: {', '.join(assessment.missing_required)}")
    for rec in assessment.recommendations:
        logger.info(f"Recommendation: {rec}")

    if assessment.ready:
        logger.info("✅ Environment appears READY for remote Railway provisioning.")
        return 0
    logger.error("❌ Environment NOT ready. Resolve issues above before remote operations.")
    return 1


if __name__ == "__main__":  # pragma: no cover
    try:
        sys.exit(main())
    except Exception as exc:  # pragma: no cover
        logger.exception("Unexpected failure: %s", exc)
        sys.exit(2)

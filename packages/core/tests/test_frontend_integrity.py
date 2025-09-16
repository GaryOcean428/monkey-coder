import pytest
from pathlib import Path

FRONTEND_OUT = Path('packages/web/out')

@pytest.mark.smoke
def test_frontend_build_integrity_present():
    """If frontend build directory missing, mark as skipped (handled by provisioning)."""
    if not FRONTEND_OUT.exists():
        pytest.skip('Frontend export not present; provisioning will enforce.')
    index = FRONTEND_OUT / 'index.html'
    assets_dir = FRONTEND_OUT / '_next'
    assert index.exists(), 'index.html missing in exported frontend'
    assert assets_dir.exists(), '_next assets directory missing'

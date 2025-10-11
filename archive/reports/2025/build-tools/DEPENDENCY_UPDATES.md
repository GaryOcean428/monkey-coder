# Dependency Updates Guide

## Updating Python Dependencies

When major dependencies like PyTorch require updates:

1. **Check PyPI for Python version compatibility**
   - Visit https://pypi.org/ and check the package's supported Python versions
   - Review the package's changelog for breaking changes

2. **Update pyproject.toml with version range (not pin)**
   ```toml
   # ✅ GOOD - Version range allows patch updates
   "torch>=2.5.0,<2.9.0",
   
   # ❌ BAD - Pinned version blocks security patches
   "torch==2.3.0",
   ```

3. **Regenerate lockfile**
   ```bash
   uv pip compile pyproject.toml -o requirements.txt
   ```

4. **Update all railpack*.json to match Python version**
   ```bash
   # Verify all railpack files show correct Python version
   jq '.build.packages.python' railpack*.json
   ```

5. **Test locally with matching Python version**
   ```bash
   python --version  # Should match Railway's Python version
   python -m venv .venv
   .venv/bin/pip install -r requirements.txt
   .venv/bin/python -c "import torch; print(torch.__version__)"
   ```

6. **Monitor Railway deployments post-merge**
   ```bash
   railway logs --service monkey-coder-ml --tail
   ```

## Python Version Policy

### Railway Platform Behavior
- **Railway defaults to latest stable Python** (currently 3.13)
- All dependencies must support Railway's default Python version
- `railpack.json` Python specifications are **documentation-only**
- Railway ignores the `packages.python` field in current implementation

### Project Policy
- **Update dependencies proactively, not reactively**
- Monitor Python release schedule and plan updates in advance
- Test compatibility with upcoming Python versions before they become default
- Maintain forward compatibility with at least the current and next Python version

## PyTorch Version Compatibility Matrix

| Python Version | Minimum PyTorch Version | Notes |
|---------------|------------------------|-------|
| 3.12 | 2.3.0 | cp312 wheels available |
| 3.13 | 2.5.0 | cp313 wheels available, native support |

## Common Issues and Solutions

### Issue: "No matching distribution found for torch==X.X.X"

**Cause:** PyTorch version doesn't support the Python version Railway is using

**Solution:**
1. Check PyTorch compatibility: https://pytorch.org/get-started/locally/
2. Update to compatible version in `pyproject.toml`
3. Regenerate `requirements.txt` with uv
4. Commit and deploy

### Issue: "propcache 0.4.0 has been yanked"

**Cause:** Dependency version has been removed from PyPI

**Solution:**
Add exclusion to `pyproject.toml`:
```toml
"propcache!=0.4.0",  # Yanked due to memory leak
```

### Issue: Build takes 25+ minutes

**Cause:** PyTorch and CUDA libraries are ~2.5GB

**Solution:**
- This is expected for ML service
- Enable Railway build caching in `railpack-ml.json`
- Consider using pre-built Docker images for faster deploys

## Automated CI Checks

Add these checks to `.github/workflows/ci.yml`:

```yaml
- name: Verify Python 3.13+ compatibility
  run: |
    python -c "import sys; assert sys.version_info >= (3, 13), 'Python 3.13+ required'"
    
- name: Verify PyTorch version
  run: |
    python -c "import torch; v = tuple(map(int, torch.__version__.split('.')[:2])); assert v >= (2, 5), 'PyTorch 2.5.0+ required'"
```

## Emergency Rollback

If a dependency update breaks production:

1. **Identify the breaking version:**
   ```bash
   git log --oneline requirements.txt
   ```

2. **Revert the change:**
   ```bash
   git revert <commit-hash>
   git push
   ```

3. **Railway will auto-deploy the reverted version**

4. **Investigate and fix the issue locally** before re-deploying

## Version Update Timeline

- **Quarterly:** Review all dependencies for security updates
- **Monthly:** Check for minor version updates of critical dependencies
- **Weekly:** Monitor Railway platform updates and Python version changes
- **Immediately:** Apply security patches for critical vulnerabilities

## Resources

- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [Python Release Schedule](https://peps.python.org/pep-0602/)
- [Railway Documentation](https://docs.railway.app/)
- [UV Documentation](https://github.com/astral-sh/uv)

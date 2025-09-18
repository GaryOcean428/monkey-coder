import json

from railway_provisioning_orchestrator import REQUIRED_ENV, OPTIONAL_ENV


def test_required_env_schema_minimum_fields():
    # Ensure each tuple contains expected structure
    for item in REQUIRED_ENV:
        assert len(item) == 4, 'REQUIRED_ENV tuple must have 4 elements (name, required_bool, secret_bool, default)'
        name, required, secret, default = item
        assert isinstance(name, str) and name, 'Name must be non-empty string'
        assert required is True, 'Required list should mark all as required'
        assert isinstance(secret, bool), 'Secret flag must be bool'


def test_optional_env_schema_structure():
    for item in OPTIONAL_ENV:
        assert len(item) == 4
        name, required, secret, default = item
        assert isinstance(name, str)
        assert required is False
        assert isinstance(secret, bool)


def test_provisioning_plan_writable(tmp_path):
    # Simulate writing a provisioning plan snippet
    sample = {
        'ready': False,
        'missing_required': ['NODE_ENV'],
        'frontend': {'present': True},
    }
    path = tmp_path / 'plan.json'
    path.write_text(json.dumps(sample))
    loaded = json.loads(path.read_text())
    assert loaded['missing_required'] == ['NODE_ENV']

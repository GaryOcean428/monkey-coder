"""Minimal quantum routing smoke tests.

Purpose: Ensure core quantum routing components import and basic behaviors work.
Full Phase 2 test suite is intentionally deferred while stabilizing environment.
"""

import pytest
import numpy as np

from monkey_coder.quantum import (
    DQNRoutingAgent,
    RoutingState,
    RoutingAction,
)
from monkey_coder.quantum.router_integration import QuantumRouterIntegration  # Alias to DQNRouterBridge
from monkey_coder.models import (
    ProviderType,
    ExecuteRequest,
    TaskType,
    ExecutionContext,
    PersonaConfig,
    PersonaType,
)


def test_routing_state_vector_dimensions():
    """State vector should be stable (length 21) for baseline configuration."""
    state = RoutingState(
        task_complexity=0.4,
        context_type="code_generation",
        provider_availability={"openai": True},
        historical_performance={"openai": 0.9},
        resource_constraints={"cost_weight": 0.3, "time_weight": 0.4, "quality_weight": 0.3},
        user_preferences={"preference_strength": 0.6},
    )
    vec = state.to_vector()
    assert isinstance(vec, np.ndarray)
    assert vec.shape[0] == 21


def test_dqn_agent_action_and_memory():
    """Agent should produce a RoutingAction and store experience."""
    agent = DQNRoutingAgent(state_size=21, action_size=12, exploration_rate=1.0, memory_size=5)
    s = RoutingState(
        task_complexity=0.2,
        context_type="code_generation",
        provider_availability={"openai": True},
        historical_performance={"openai": 0.8},
        resource_constraints={"cost_weight": 0.3, "time_weight": 0.3, "quality_weight": 0.4},
        user_preferences={"preference_strength": 0.5},
    )
    action = agent.act(s)
    assert isinstance(action, RoutingAction)
    agent.remember(s, action, reward=1.0, next_state=s, done=False)
    assert len(agent.memory) == 1


def test_quantum_router_integration_basic_route():
    """Integration layer should return a decision with provider + state vector."""
    bridge = QuantumRouterIntegration(use_advanced_encoding=False)
    req = ExecuteRequest(
        prompt="Generate a helper function",
        task_type=TaskType.CODE_GENERATION,
        files=None,
        context=ExecutionContext(user_id="tester", session_id=None, workspace_id=None),
        persona_config=PersonaConfig(persona=PersonaType.DEVELOPER, custom_instructions=None),
    )
    decision = bridge.route_request(req)
    assert decision.original_decision.provider in list(ProviderType)
    assert decision.state_vector is not None


@pytest.mark.quantum_phase2
@pytest.mark.skip(reason="Full quantum suite deferred")
def test_full_phase2_placeholder():
    """Placeholder for reintroducing comprehensive Phase 2 quantum tests later."""
    assert True

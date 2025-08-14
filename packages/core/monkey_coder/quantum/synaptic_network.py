"""
Synaptic Network for Quantum Parallel Information Sharing.

This module implements a neural synaptic network that enables information
sharing between parallel quantum execution threads, similar to how neurons
communicate in biological neural networks.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np
from collections import deque, defaultdict
import json

logger = logging.getLogger(__name__)

class NeurotransmitterType(str, Enum):
    """Types of information that can be transmitted between threads."""
    EXCITATORY = "excitatory"  # Increases activity
    INHIBITORY = "inhibitory"  # Decreases activity
    MODULATORY = "modulatory"  # Modifies behavior
    INFORMATIONAL = "informational"  # Pure information transfer
    SYNCHRONIZING = "synchronizing"  # Synchronizes threads

@dataclass
class Signal:
    """Represents a signal transmitted through synaptic connection."""
    signal_id: str = field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:8]}")
    source: str = ""
    target: str = ""
    neurotransmitter: NeurotransmitterType = NeurotransmitterType.INFORMATIONAL
    payload: Any = None
    strength: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    decay_rate: float = 0.1  # How quickly signal weakens
    
    def decay(self, time_elapsed: float) -> float:
        """Calculate decayed signal strength."""
        return self.strength * np.exp(-self.decay_rate * time_elapsed)

@dataclass
class Synapse:
    """Enhanced synaptic connection with neurotransmitter dynamics."""
    synapse_id: str = field(default_factory=lambda: f"syn_{uuid.uuid4().hex[:8]}")
    pre_synaptic: str = ""  # Source neuron/thread
    post_synaptic: str = ""  # Target neuron/thread
    weight: float = 1.0  # Connection strength (0-1)
    plasticity: float = 0.1  # Learning rate
    neurotransmitter_type: NeurotransmitterType = NeurotransmitterType.INFORMATIONAL
    
    # Synaptic dynamics
    release_probability: float = 0.8  # Probability of successful transmission
    vesicle_pool: int = 100  # Available neurotransmitter vesicles
    max_vesicles: int = 100
    recharge_rate: float = 0.1  # Vesicle replenishment rate
    
    # History
    signal_history: deque = field(default_factory=lambda: deque(maxlen=100))
    last_activation: Optional[datetime] = None
    total_activations: int = 0
    
    def can_transmit(self) -> bool:
        """Check if synapse can transmit signal."""
        return self.vesicle_pool > 0 and np.random.random() < self.release_probability
    
    def transmit(self, signal: Signal) -> Optional[Signal]:
        """Transmit signal through synapse."""
        if not self.can_transmit():
            return None
        
        # Consume vesicles
        vesicles_used = min(10, self.vesicle_pool)
        self.vesicle_pool -= vesicles_used
        
        # Modify signal strength based on synapse weight and vesicles
        transmitted_signal = Signal(
            source=self.pre_synaptic,
            target=self.post_synaptic,
            neurotransmitter=self.neurotransmitter_type,
            payload=signal.payload,
            strength=signal.strength * self.weight * (vesicles_used / 10),
            decay_rate=signal.decay_rate
        )
        
        # Record activation
        self.last_activation = datetime.now()
        self.total_activations += 1
        self.signal_history.append(transmitted_signal)
        
        return transmitted_signal
    
    def recharge(self, time_elapsed: float):
        """Replenish neurotransmitter vesicles."""
        recharge_amount = int(self.recharge_rate * time_elapsed * self.max_vesicles)
        self.vesicle_pool = min(self.max_vesicles, self.vesicle_pool + recharge_amount)
    
    def potentiate(self, amount: float = 0.1):
        """Long-term potentiation (strengthen connection)."""
        self.weight = min(1.0, self.weight + amount * self.plasticity)
        self.release_probability = min(1.0, self.release_probability + amount * 0.05)
    
    def depress(self, amount: float = 0.05):
        """Long-term depression (weaken connection)."""
        self.weight = max(0.0, self.weight - amount * self.plasticity)
        self.release_probability = max(0.1, self.release_probability - amount * 0.02)

@dataclass
class Neuron:
    """Represents a processing node in the synaptic network."""
    neuron_id: str = field(default_factory=lambda: f"neu_{uuid.uuid4().hex[:8]}")
    thread_id: Optional[str] = None  # Associated quantum thread
    
    # Membrane potential (activation state)
    membrane_potential: float = -70.0  # mV (resting potential)
    threshold: float = -55.0  # mV (action potential threshold)
    refractory_period: float = 2.0  # ms
    last_spike: Optional[datetime] = None
    
    # Input/output connections
    dendrites: List[str] = field(default_factory=list)  # Incoming synapses
    axon_terminals: List[str] = field(default_factory=list)  # Outgoing synapses
    
    # Signal processing
    input_buffer: deque = field(default_factory=lambda: deque(maxlen=100))
    output_buffer: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def integrate_signal(self, signal: Signal):
        """Integrate incoming signal into membrane potential."""
        if signal.neurotransmitter == NeurotransmitterType.EXCITATORY:
            self.membrane_potential += signal.strength * 15  # Depolarize
        elif signal.neurotransmitter == NeurotransmitterType.INHIBITORY:
            self.membrane_potential -= signal.strength * 10  # Hyperpolarize
        elif signal.neurotransmitter == NeurotransmitterType.MODULATORY:
            # Modulate threshold instead of potential
            self.threshold -= signal.strength * 2
        
        self.input_buffer.append(signal)
    
    def check_activation(self) -> bool:
        """Check if neuron should fire (action potential)."""
        # Check refractory period
        if self.last_spike:
            time_since_spike = (datetime.now() - self.last_spike).total_seconds() * 1000
            if time_since_spike < self.refractory_period:
                return False
        
        # Check threshold
        if self.membrane_potential >= self.threshold:
            self.last_spike = datetime.now()
            self.membrane_potential = -70.0  # Reset
            return True
        
        return False
    
    def decay_potential(self, time_elapsed: float):
        """Decay membrane potential back to resting state."""
        decay_rate = 0.1
        self.membrane_potential += (-70.0 - self.membrane_potential) * decay_rate * time_elapsed

class SynapticNetwork:
    """
    Neural synaptic network for quantum thread communication.
    
    Implements biological neural network principles for information
    sharing between parallel execution threads.
    """
    
    def __init__(self, enable_stdp: bool = True):
        """
        Initialize synaptic network.
        
        Args:
            enable_stdp: Enable Spike-Timing-Dependent Plasticity
        """
        self.neurons: Dict[str, Neuron] = {}
        self.synapses: Dict[str, Synapse] = {}
        self.network_graph: Dict[str, Set[str]] = defaultdict(set)  # neuron -> connected neurons
        
        self.enable_stdp = enable_stdp
        self.global_time = 0.0
        self.signal_queue: deque = deque()
        
        # Network metrics
        self.total_signals = 0
        self.successful_transmissions = 0
        self.network_synchrony = 0.0
    
    def create_neuron(self, thread_id: Optional[str] = None) -> str:
        """Create a new neuron in the network."""
        neuron = Neuron(thread_id=thread_id)
        self.neurons[neuron.neuron_id] = neuron
        return neuron.neuron_id
    
    def connect_neurons(
        self,
        pre_synaptic_id: str,
        post_synaptic_id: str,
        weight: float = 0.5,
        neurotransmitter: NeurotransmitterType = NeurotransmitterType.EXCITATORY
    ) -> str:
        """Create synaptic connection between neurons."""
        if pre_synaptic_id not in self.neurons or post_synaptic_id not in self.neurons:
            raise ValueError("Both neurons must exist in network")
        
        synapse = Synapse(
            pre_synaptic=pre_synaptic_id,
            post_synaptic=post_synaptic_id,
            weight=weight,
            neurotransmitter_type=neurotransmitter
        )
        
        self.synapses[synapse.synapse_id] = synapse
        
        # Update neuron connections
        self.neurons[pre_synaptic_id].axon_terminals.append(synapse.synapse_id)
        self.neurons[post_synaptic_id].dendrites.append(synapse.synapse_id)
        
        # Update network graph
        self.network_graph[pre_synaptic_id].add(post_synaptic_id)
        
        return synapse.synapse_id
    
    def create_mesh_network(self, neuron_ids: List[str], connection_probability: float = 0.3):
        """Create a mesh network between neurons."""
        for i, pre_id in enumerate(neuron_ids):
            for j, post_id in enumerate(neuron_ids):
                if i != j and np.random.random() < connection_probability:
                    # Determine neurotransmitter type based on position
                    if abs(i - j) == 1:
                        # Adjacent neurons: strong excitatory
                        nt_type = NeurotransmitterType.EXCITATORY
                        weight = 0.8
                    elif abs(i - j) < 3:
                        # Nearby neurons: modulatory
                        nt_type = NeurotransmitterType.MODULATORY
                        weight = 0.5
                    else:
                        # Distant neurons: weak or inhibitory
                        nt_type = np.random.choice([
                            NeurotransmitterType.INHIBITORY,
                            NeurotransmitterType.INFORMATIONAL
                        ])
                        weight = 0.3
                    
                    self.connect_neurons(pre_id, post_id, weight, nt_type)
    
    async def propagate_signal(self, source_neuron_id: str, payload: Any):
        """Propagate signal from a neuron through the network."""
        if source_neuron_id not in self.neurons:
            return
        
        source_neuron = self.neurons[source_neuron_id]
        
        # Create initial signal
        signal = Signal(
            source=source_neuron_id,
            target="broadcast",
            neurotransmitter=NeurotransmitterType.EXCITATORY,
            payload=payload,
            strength=1.0
        )
        
        # Queue signal for processing
        self.signal_queue.append(signal)
        self.total_signals += 1
        
        # Process signal through axon terminals
        for synapse_id in source_neuron.axon_terminals:
            synapse = self.synapses[synapse_id]
            transmitted = synapse.transmit(signal)
            
            if transmitted:
                target_neuron = self.neurons[synapse.post_synaptic]
                target_neuron.integrate_signal(transmitted)
                self.successful_transmissions += 1
                
                # Check if target neuron fires
                if target_neuron.check_activation():
                    # Cascade: target neuron fires
                    await self.propagate_signal(synapse.post_synaptic, payload)
                
                # Apply STDP if enabled
                if self.enable_stdp:
                    self._apply_stdp(synapse, source_neuron, target_neuron)
    
    def _apply_stdp(self, synapse: Synapse, pre_neuron: Neuron, post_neuron: Neuron):
        """Apply Spike-Timing-Dependent Plasticity."""
        if not (pre_neuron.last_spike and post_neuron.last_spike):
            return
        
        # Calculate time difference
        pre_spike_time = pre_neuron.last_spike.timestamp()
        post_spike_time = post_neuron.last_spike.timestamp()
        dt = post_spike_time - pre_spike_time  # in seconds
        
        # STDP window (in milliseconds)
        dt_ms = dt * 1000
        tau_plus = 20.0  # ms
        tau_minus = 20.0  # ms
        A_plus = 0.01
        A_minus = 0.01
        
        if dt_ms > 0:
            # Pre before post: potentiation
            delta_w = A_plus * np.exp(-dt_ms / tau_plus)
            synapse.potentiate(delta_w)
        else:
            # Post before pre: depression
            delta_w = A_minus * np.exp(dt_ms / tau_minus)
            synapse.depress(delta_w)
    
    async def synchronize_network(self):
        """Synchronize network activity across all neurons."""
        # Send synchronizing signals
        sync_signal = Signal(
            source="network",
            target="all",
            neurotransmitter=NeurotransmitterType.SYNCHRONIZING,
            payload={"sync_time": self.global_time},
            strength=1.0
        )
        
        # Reset all neurons to similar state
        for neuron in self.neurons.values():
            neuron.membrane_potential = -65.0  # Slight depolarization
            neuron.threshold = -55.0  # Reset threshold
        
        # Calculate network synchrony (Kuramoto order parameter)
        if len(self.neurons) > 1:
            phases = []
            for neuron in self.neurons.values():
                # Convert membrane potential to phase
                phase = (neuron.membrane_potential + 70) / 15 * 2 * np.pi
                phases.append(np.exp(1j * phase))
            
            # Calculate order parameter
            mean_phase = np.mean(phases)
            self.network_synchrony = abs(mean_phase)
    
    async def update_network(self, time_delta: float):
        """Update network state over time."""
        self.global_time += time_delta
        
        # Update all neurons
        for neuron in self.neurons.values():
            neuron.decay_potential(time_delta)
        
        # Recharge all synapses
        for synapse in self.synapses.values():
            synapse.recharge(time_delta)
        
        # Process queued signals
        while self.signal_queue:
            signal = self.signal_queue.popleft()
            age = (datetime.now() - signal.timestamp).total_seconds()
            
            # Apply signal decay
            if signal.decay(age) > 0.1:  # Threshold for signal viability
                # Process signal...
                pass
    
    def get_network_state(self) -> Dict[str, Any]:
        """Get current network state and metrics."""
        active_neurons = sum(1 for n in self.neurons.values() 
                           if n.membrane_potential > -65)
        
        avg_synapse_weight = np.mean([s.weight for s in self.synapses.values()]) \
                           if self.synapses else 0
        
        return {
            'total_neurons': len(self.neurons),
            'active_neurons': active_neurons,
            'total_synapses': len(self.synapses),
            'avg_synapse_weight': avg_synapse_weight,
            'total_signals': self.total_signals,
            'successful_transmissions': self.successful_transmissions,
            'transmission_rate': self.successful_transmissions / max(self.total_signals, 1),
            'network_synchrony': self.network_synchrony,
            'global_time': self.global_time
        }
    
    def visualize_activity(self) -> str:
        """Generate ASCII visualization of network activity."""
        if not self.neurons:
            return "Empty network"
        
        lines = []
        lines.append("Synaptic Network Activity")
        lines.append("=" * 40)
        
        for neuron_id, neuron in list(self.neurons.items())[:10]:  # Show first 10
            # Activity bar based on membrane potential
            activity = (neuron.membrane_potential + 70) / 15  # Normalize to 0-1
            bar_length = int(activity * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            lines.append(f"{neuron_id[:8]}: [{bar}] {neuron.membrane_potential:.1f}mV")
        
        lines.append("-" * 40)
        lines.append(f"Network Synchrony: {self.network_synchrony:.2%}")
        lines.append(f"Transmission Rate: {self.successful_transmissions}/{self.total_signals}")
        
        return "\n".join(lines)
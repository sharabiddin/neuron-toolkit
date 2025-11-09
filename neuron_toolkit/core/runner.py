from typing import Dict
import numpy as np
from neuron import h
from ..config.models import ExperimentConfig
from .builder import NeuronModelBuilder
from .stimuli import StimulusManager
from .recordings import RecordingManager


class SimulationRunner:
    """Runs NEURON simulations from configuration."""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.sections: Dict[str, h.Section] = {}
        self.builder = NeuronModelBuilder(config)
        self.stimulus_manager = None
        self.recording_manager = None
    
    def run_simulation(self) -> Dict[str, np.ndarray]:
        """Run complete simulation and return recorded data."""
        try:
            self.setup_model()
            self.setup_stimuli()
            self.setup_recordings()
            self.configure_simulation()
            self.run_neuron_simulation()
            return self.get_results()
        finally:
            self.cleanup()
    
    def setup_model(self) -> None:
        """Build the NEURON model."""
        self.sections = self.builder.build_model()
    
    def setup_stimuli(self) -> None:
        """Set up current injection stimuli."""
        self.stimulus_manager = StimulusManager(self.sections)
        self.stimulus_manager.create_stimuli(self.config.stimuli)
    
    def setup_recordings(self) -> None:
        """Set up voltage and current recordings."""
        self.recording_manager = RecordingManager(self.sections)
        self.recording_manager.setup_recordings(self.config.recordings)
    
    def configure_simulation(self) -> None:
        """Configure simulation parameters."""
        h.dt = self.config.simulation.dt_ms
        h.tstop = self.config.simulation.tstop_ms
        h.v_init = -65.0
        h.celsius = self.config.environment.temperature_celsius
        
        h.cvode_active(0)
    
    def run_neuron_simulation(self) -> None:
        """Execute the NEURON simulation."""
        h.finitialize(h.v_init)
        h.run()
    
    def get_results(self) -> Dict[str, np.ndarray]:
        """Get simulation results."""
        if self.recording_manager is None:
            raise RuntimeError("Recording manager not initialized")
        return self.recording_manager.get_recording_data()
    
    def cleanup(self) -> None:
        """Clean up simulation objects."""
        if self.stimulus_manager:
            self.stimulus_manager.cleanup()
        if self.recording_manager:
            self.recording_manager.cleanup()
        
        self.sections.clear()
from typing import Dict, List
import numpy as np
from neuron import h
from ..config.models import Recording


class RecordingManager:
    """Manages voltage and current recordings."""
    
    def __init__(self, sections: Dict[str, h.Section]):
        self.sections = sections
        self.recording_vectors: Dict[str, h.Vector] = {}
        self.time_vector: h.Vector = h.Vector()
        self.recording_configs: List[Recording] = []
    
    def setup_recordings(self, recording_configs: List[Recording]) -> None:
        """Set up all recordings from configuration."""
        self.recording_configs = recording_configs
        
        self.time_vector.record(h._ref_t)
        
        for recording_config in recording_configs:
            self.create_recording(recording_config)
    
    def create_recording(self, config: Recording) -> None:
        """Create a single recording."""
        if config.section not in self.sections:
            raise ValueError(f"Section '{config.section}' not found for recording '{config.name}'")
        
        section = self.sections[config.section]
        
        vector = h.Vector()
        
        if config.variable == "v":
            vector.record(section(config.loc)._ref_v)
        elif config.variable == "i":
            vector.record(section(config.loc)._ref_i_membrane)
        else:
            try:
                ref_attr = f"_ref_{config.variable}"
                if hasattr(section(config.loc), ref_attr):
                    vector.record(getattr(section(config.loc), ref_attr))
                else:
                    raise ValueError(f"Variable '{config.variable}' not found in section '{config.section}'")
            except Exception as e:
                raise ValueError(f"Failed to record variable '{config.variable}': {str(e)}")
        
        self.recording_vectors[config.name] = vector
    
    def get_recording_data(self) -> Dict[str, np.ndarray]:
        """Get all recorded data as numpy arrays."""
        data = {
            'time': np.array(self.time_vector)
        }
        
        for name, vector in self.recording_vectors.items():
            data[name] = np.array(vector)
        
        return data
    
    def get_recording_configs(self) -> List[Recording]:
        """Get recording configurations."""
        return self.recording_configs
    
    def cleanup(self) -> None:
        """Clean up recordings."""
        self.recording_vectors.clear()
        self.time_vector = h.Vector()
        self.recording_configs = []
from typing import Dict, List
from neuron import h
from ..config.models import Stimulus


class StimulusManager:
    """Manages current injection stimuli."""
    
    def __init__(self, sections: Dict[str, h.Section]):
        self.sections = sections
        self.stimuli: List[h.IClamp] = []
    
    def create_stimuli(self, stimulus_configs: List[Stimulus]) -> List[h.IClamp]:
        """Create all stimuli from configuration."""
        self.stimuli = []
        for stim_config in stimulus_configs:
            stimulus = self.create_stimulus(stim_config)
            self.stimuli.append(stimulus)
        return self.stimuli
    
    def create_stimulus(self, config: Stimulus) -> h.IClamp:
        """Create a single current injection stimulus."""
        if config.section not in self.sections:
            raise ValueError(f"Section '{config.section}' not found for stimulus '{config.name}'")
        
        section = self.sections[config.section]
        
        if config.type == "IClamp":
            return self.create_iclamp(section, config)
        else:
            raise ValueError(f"Unsupported stimulus type: {config.type}")
    
    def create_iclamp(self, section: h.Section, config: Stimulus) -> h.IClamp:
        """Create an IClamp stimulus."""
        stimulus = h.IClamp(section(config.loc))
        stimulus.delay = config.delay_ms
        stimulus.dur = config.duration_ms
        stimulus.amp = config.amplitude_nA
        return stimulus
    
    def get_stimuli(self) -> List[h.IClamp]:
        """Get all created stimuli."""
        return self.stimuli
    
    def cleanup(self) -> None:
        """Clean up stimuli."""
        for stimulus in self.stimuli:
            stimulus = None
        self.stimuli = []
from typing import Dict, List
import neuron
from neuron import h
h.load_file("stdrun.hoc")
from ..config.models import ExperimentConfig, SectionConfig, BiophysicsConfig, Connection


class NeuronModelBuilder:
    """Builds NEURON models from configuration."""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.sections: Dict[str, h.Section] = {}
        self.morphology = config.get_morphology()
        self.biophysics = config.get_biophysics()
    
    def build_model(self) -> Dict[str, h.Section]:
        """Build complete NEURON model."""
        self.create_sections()
        self.connect_sections()
        self.apply_biophysics()
        self.set_environment()
        return self.sections
    
    def create_sections(self) -> None:
        """Create all sections defined in morphology."""
        for section_name, section_config in self.morphology.sections.items():
            self.sections[section_name] = self.create_section(section_name, section_config)
    
    def create_section(self, name: str, config: SectionConfig) -> h.Section:
        """Create a single NEURON section."""
        sec = h.Section(name=name)
        sec.L = config.L
        sec.diam = config.diam
        sec.nseg = config.nseg
        return sec
    
    def connect_sections(self) -> None:
        """Connect sections according to morphology connections."""
        for connection in self.morphology.connections:
            self.connect_section(connection)
    
    def connect_section(self, connection: Connection) -> None:
        """Connect two sections."""
        parent_sec = self.sections[connection.parent]
        child_sec = self.sections[connection.child]
        child_sec.connect(parent_sec(connection.parent_loc), connection.child_loc)
    
    def apply_biophysics(self) -> None:
        """Apply biophysical properties to all sections."""
        for section_name, biophys_config in self.biophysics.items():
            if section_name in self.sections:
                self.apply_section_biophysics(self.sections[section_name], biophys_config)
    
    def apply_section_biophysics(self, section: h.Section, config: BiophysicsConfig) -> None:
        """Apply biophysical properties to a section."""
        section.Ra = config.Ra
        section.cm = config.cm
        
        for mech_name, params in config.mechanisms.items():
            section.insert(mech_name)
            
            if mech_name == "hh":
                self.apply_hh_parameters(section, params)
            elif mech_name == "pas":
                self.apply_passive_parameters(section, params)
            else:
                self.apply_generic_parameters(section, mech_name, params)
    
    def apply_hh_parameters(self, section: h.Section, params: Dict[str, float]) -> None:
        """Apply Hodgkin-Huxley mechanism parameters with defaults."""
        hh_defaults = {
            'gnabar_hh': 0.12,
            'gkbar_hh': 0.036,
            'gl_hh': 0.0003,
            'el_hh': -54.3
        }
        
        for param_name, default_value in hh_defaults.items():
            value = params.get(param_name, default_value)
            setattr(section, param_name, value)
    
    def apply_passive_parameters(self, section: h.Section, params: Dict[str, float]) -> None:
        """Apply passive mechanism parameters."""
        pas_defaults = {
            'g_pas': 0.001,
            'e_pas': -65.0
        }
        
        for param_name, default_value in pas_defaults.items():
            value = params.get(param_name, default_value)
            setattr(section, param_name, value)
    
    def apply_generic_parameters(self, section: h.Section, mech_name: str, params: Dict[str, float]) -> None:
        """Apply parameters for generic mechanisms."""
        for param_name, value in params.items():
            full_param_name = f"{param_name}_{mech_name}"
            if hasattr(section, full_param_name):
                setattr(section, full_param_name, value)
            else:
                setattr(section, param_name, value)
    
    def set_environment(self) -> None:
        """Set global environment parameters."""
        h.celsius = self.config.environment.temperature_celsius
        
        if self.config.environment.random_seed is not None:
            h.Random().MCellRan4(self.config.environment.random_seed)
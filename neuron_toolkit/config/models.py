from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field, model_validator


class SectionConfig(BaseModel):
    L: float = Field(..., description="Section length in micrometers")
    diam: float = Field(..., description="Section diameter in micrometers")
    nseg: int = Field(1, description="Number of segments")


class Connection(BaseModel):
    parent: str = Field(..., description="Parent section name")
    child: str = Field(..., description="Child section name")
    parent_loc: float = Field(1.0, description="Connection location on parent (0-1)")
    child_loc: float = Field(0.0, description="Connection location on child (0-1)")


class Morphology(BaseModel):
    type: Literal["single_compartment", "multi_section"] = Field(..., description="Morphology type")
    sections: Dict[str, SectionConfig] = Field(..., description="Section configurations")
    connections: Optional[List[Connection]] = Field(default=[], description="Section connections")


class BiophysicsConfig(BaseModel):
    Ra: float = Field(100.0, description="Axial resistance in Ohm*cm")
    cm: float = Field(1.0, description="Membrane capacitance in uF/cm^2")
    mechanisms: Dict[str, Dict[str, float]] = Field(default={}, description="Membrane mechanisms and parameters")


class Stimulus(BaseModel):
    name: str = Field(..., description="Stimulus name")
    type: Literal["IClamp"] = Field("IClamp", description="Stimulus type")
    section: str = Field(..., description="Target section name")
    loc: float = Field(0.5, description="Location on section (0-1)")
    delay_ms: float = Field(..., description="Delay in milliseconds")
    duration_ms: float = Field(..., description="Duration in milliseconds")
    amplitude_nA: float = Field(..., description="Amplitude in nanoamperes")


class Recording(BaseModel):
    name: str = Field(..., description="Recording name")
    variable: str = Field(..., description="Variable to record (e.g., 'v', 'i')")
    section: str = Field(..., description="Target section name")
    loc: float = Field(0.5, description="Location on section (0-1)")


class SimulationConfig(BaseModel):
    tstop_ms: float = Field(..., description="Simulation end time in milliseconds")
    dt_ms: float = Field(0.025, description="Time step in milliseconds")


class PlotConfig(BaseModel):
    enabled: bool = Field(True, description="Enable plotting")
    variables: List[str] = Field(..., description="Variables to plot")
    save_as: str = Field("voltage.png", description="Plot filename")


class OutputConfig(BaseModel):
    directory: str = Field("results", description="Output directory")
    save_traces: Dict[str, str] = Field({"format": "csv"}, description="Trace saving configuration")
    plot: Optional[PlotConfig] = Field(None, description="Plot configuration")


class Environment(BaseModel):
    temperature_celsius: float = Field(36.0, description="Temperature in Celsius")
    random_seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    mechanisms: List[str] = Field(default=[], description="Required NEURON mechanisms")


class Metadata(BaseModel):
    name: str = Field(..., description="Experiment name")
    description: str = Field("", description="Experiment description")
    version: str = Field("1.0.0", description="Version")


class ExperimentConfig(BaseModel):
    metadata: Metadata = Field(..., description="Experiment metadata")
    environment: Environment = Field(default=Environment(), description="Environment configuration")
    model: Dict[str, Any] = Field(..., description="Model configuration containing morphology and biophysics")
    stimuli: List[Stimulus] = Field(..., description="Current stimuli")
    recordings: List[Recording] = Field(..., description="Recording configurations")
    simulation: SimulationConfig = Field(..., description="Simulation parameters")
    outputs: OutputConfig = Field(default=OutputConfig(), description="Output configuration")

    def get_morphology(self) -> Morphology:
        return Morphology(**self.model["morphology"])

    def get_biophysics(self) -> Dict[str, BiophysicsConfig]:
        biophysics_data = self.model.get("biophysics", {})
        return {
            section_name: BiophysicsConfig(**section_config)
            for section_name, section_config in biophysics_data.items()
        }
    
    @model_validator(mode='after')
    def validate_section_references(self) -> 'ExperimentConfig':
        """Validate that all section references in stimuli and recordings exist in morphology."""
        # Get available sections
        morphology = self.get_morphology()
        available_sections = set(morphology.sections.keys())
        
        # Check stimuli section references
        for stimulus in self.stimuli:
            if stimulus.section not in available_sections:
                raise ValueError(
                    f"Stimulus '{stimulus.name}' references section '{stimulus.section}' "
                    f"which doesn't exist in morphology. Available sections: {sorted(available_sections)}"
                )
        
        # Check recordings section references
        for recording in self.recordings:
            if recording.section not in available_sections:
                raise ValueError(
                    f"Recording '{recording.name}' references section '{recording.section}' "
                    f"which doesn't exist in morphology. Available sections: {sorted(available_sections)}"
                )
        
        # Check biophysics section references
        biophysics_sections = set(self.model.get("biophysics", {}).keys())
        for section_name in biophysics_sections:
            if section_name not in available_sections:
                raise ValueError(
                    f"Biophysics defined for section '{section_name}' "
                    f"which doesn't exist in morphology. Available sections: {sorted(available_sections)}"
                )
        
        # Check connections reference valid sections
        for connection in morphology.connections:
            if connection.parent not in available_sections:
                raise ValueError(
                    f"Connection references parent section '{connection.parent}' "
                    f"which doesn't exist in morphology. Available sections: {sorted(available_sections)}"
                )
            if connection.child not in available_sections:
                raise ValueError(
                    f"Connection references child section '{connection.child}' "
                    f"which doesn't exist in morphology. Available sections: {sorted(available_sections)}"
                )
        
        return self
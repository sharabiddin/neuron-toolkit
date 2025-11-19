# NEURON YAML Reproducibility Toolkit

A toolkit for declarative NEURON simulations using YAML configuration files, enabling reproducible computational neuroscience experiments.

## Features

- **YAML-based experiment definitions** - Define your NEURON experiments declaratively
- **JSON Schema validation** - Live validation in VS Code and runtime validation
- **Multiple morphologies** - Support for single compartment and multi-section neurons
- **Flexible stimuli** - Multiple IClamp current injections
- **Multi-location recordings** - Record from any section and location
- **Automated outputs** - CSV export and matplotlib plotting
- **CLI interface** - Simple command-line tools for validation and execution

## Installation

### From source

```bash
cd phd-neuron
pip install -e .
```

### Requirements

- Python >= 3.8
- NEURON >= 8.0
- See `requirements.txt` for full dependency list

## Quick Start

### 1. Run an example experiment

```bash
nrnexp run neuron_toolkit/examples/hh_single.yaml
```

### 2. Validate a configuration

```bash
nrnexp validate neuron_toolkit/examples/hh_single.yaml
```

### 3. Create your own experiment

Create a YAML file following the schema:

```yaml
metadata:
  name: "My Experiment"
  description: "Custom HH simulation"

model:
  morphology:
    type: "single_compartment"
    sections:
      soma:
        L: 20
        diam: 20
        nseg: 1
  
  biophysics:
    soma:
      Ra: 100
      cm: 1
      mechanisms:
        hh:
          gnabar_hh: 0.12
          gkbar_hh: 0.036

stimuli:
  - name: "stim1"
    section: "soma"
    delay_ms: 10
    duration_ms: 40
    amplitude_nA: 0.1

recordings:
  - name: "soma_v"
    variable: "v"
    section: "soma"

simulation:
  tstop_ms: 60
  dt_ms: 0.025

outputs:
  directory: "results/my_experiment"
  plot:
    enabled: true
    variables: ["soma_v"]
```

## VS Code Integration

### Automatic Setup (Recommended)
The project includes `.vscode/settings.json` with schema associations. Simply open the project in VS Code and you'll get:
- ✅ Real-time YAML validation
- ✅ Auto-completion
- ✅ Hover documentation
- ✅ Error highlighting

### Manual Setup
If you need custom schema associations, add to your VS Code settings.json:

```json
{
  "yaml.schemas": {
    "./neuron_toolkit/config/schema.json": [
      "**/neuron_toolkit/examples/*.yaml",
      "**/*experiment*.yaml",
      "**/*neuron*.yaml"
    ]
  },
  "yaml.validate": true,
  "yaml.completion": true
}
```

### Schema Comments in YAML Files
All example files include schema references for real-time validation:
```yaml
# yaml-language-server: $schema=../config/schema.json
```

### Testing Real-Time Validation
1. **Open `demo_validation.yaml`** in VS Code
2. **Follow the comments** and try invalid edits like:
   - Change `temperature_celsius: 36.0` to `999` (red underline: too hot)
   - Change `variable: "v"` to `"invalid"` (red underline: not in enum)  
   - Change `tstop_ms: 60` to `999999` (red underline: exceeds maximum)
3. **See immediate error highlighting** with detailed error messages

### Real-Time Features
- ✅ **Instant error detection** as you type
- ✅ **Enum auto-completion** (Ctrl+Space shows valid options)
- ✅ **Hover documentation** for all properties
- ✅ **Range validation** with min/max values
- ✅ **Pattern validation** for identifiers and paths

### Validation Levels
1. **JSON Schema (VS Code real-time)**: Basic syntax, types, ranges, enums
2. **Pydantic (CLI validation)**: Advanced cross-field validation including:
   - ✅ **Section reference validation**: Stimuli/recordings must reference existing morphology sections
   - ✅ **Connection validation**: Parent/child sections must exist in morphology
   - ✅ **Biophysics validation**: All biophysics sections must exist in morphology

## Examples

The toolkit includes three example configurations:

- `hh_single.yaml` - Single compartment Hodgkin-Huxley model
- `hh_two_section.yaml` - Two-section model (soma + axon)  
- `passive.yaml` - Passive membrane model

## CLI Reference

### Run experiments

```bash
nrnexp run experiment.yaml [--output-dir DIR] [--verbose]
```

### Validate configurations

```bash
nrnexp validate experiment.yaml [--verbose]
```

## Architecture

```
neuron_toolkit/
├── config/          # Configuration loading and validation
├── core/            # NEURON simulation components  
├── utils/           # Utilities and logging
└── examples/        # Example YAML configurations
```

## Supported Features

### Morphologies
- Single compartment neurons
- Multi-section neurons with connections

### Biophysics
- Hodgkin-Huxley (hh) mechanisms with standard parameters
- Passive (pas) mechanisms
- Custom mechanism parameters

### Stimuli
- Multiple IClamp current injections
- Configurable timing and amplitude

### Recordings
- Membrane voltage (v)
- Membrane current (i)
- Custom variables
- Multiple locations per experiment

### Outputs
- CSV trace export
- Matplotlib voltage plots
- Configurable output directories

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Citation

If you use this toolkit in your research, please cite:

```
NEURON YAML Reproducibility Toolkit
Sharabiddin Ahmayev
https://github.com/sharabiddin/neuron-toolkit
```
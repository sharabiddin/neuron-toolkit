# NEURON YAML Reproducibility Toolkit – Development Specification  
### (Option A + Selected Option B Enhancements)

This document defines the full technical specification for implementing the **NEURON YAML Reproducibility Toolkit**.  
It is written for a **developer** who will build the system.  
The goal: allow users to define NEURON experiments using a simple YAML file, validate it, and run the simulation with full reproducibility.

---

# 1. Project Overview

The toolkit enables:

- Declarative **YAML-based experiment definitions**
- JSON Schema + VS Code **live validation**
- Python **runtime validation** (Pydantic)
- NEURON **model builder + runner**
- Support for:
  - HH or passive **single-compartment neuron**
  - **Two-section morphology** (soma + axon)
  - **Multiple IClamp stimuli**
  - **Multiple recordings**
- Result export to **CSV + PNG**
- CLI interface:  
  ```bash
  nrnexp run experiment.yaml
  nrnexp validate experiment.yaml
  ```

Scope is 1-month-friendly.

---

# 2. Folder Structure

```
neuron_toolkit/
│
├── cli.py
├── main.py
├── config/
│   ├── schema.json
│   ├── loader.py
│   ├── validator.py
│   └── models.py
│
├── core/
│   ├── builder.py
│   ├── stimuli.py
│   ├── recordings.py
│   ├── runner.py
│   └── outputs.py
│
├── examples/
│   ├── hh_single.yaml
│   ├── hh_two_section.yaml
│   └── passive.yaml
│
└── utils/
    ├── logging.py
    └── conversions.py
```

---

# 3. YAML Specification (Simplified)

Example YAML:

```yaml
metadata:
  name: "HH Soma Example"
  description: "Classic HH simulation."
  version: "1.0.0"

environment:
  temperature_celsius: 36.0
  random_seed: 1234
  mechanisms: ["hh"]

model:
  morphology:
    type: "multi_section"
    sections:
      soma:
        L: 20
        diam: 20
        nseg: 1
      axon:
        L: 300
        diam: 1
        nseg: 9
    connections:
      - parent: "soma"
        child: "axon"
        parent_loc: 1.0
        child_loc: 0.0

  biophysics:
    soma:
      Ra: 100
      cm: 1
      mechanisms:
        hh:
          gnabar_hh: 0.12
          gkbar_hh: 0.036
          gl_hh: 0.0003
          el_hh: -54.3
    axon:
      Ra: 100
      cm: 1
      mechanisms:
        hh: {}

stimuli:
  - name: "stim1"
    type: "IClamp"
    section: "soma"
    loc: 0.5
    delay_ms: 10
    duration_ms: 40
    amplitude_nA: 0.1

  - name: "stim2"
    type: "IClamp"
    section: "axon"
    loc: 0.5
    delay_ms: 20
    duration_ms: 20
    amplitude_nA: 0.05

recordings:
  - name: "soma_v"
    variable: "v"
    section: "soma"
    loc: 0.5

  - name: "axon_v"
    variable: "v"
    section: "axon"
    loc: 0.5

simulation:
  tstop_ms: 60
  dt_ms: 0.025

outputs:
  directory: "results/hh_soma"
  save_traces:
    format: "csv"
  plot:
    enabled: true
    variables: ["soma_v", "axon_v"]
    save_as: "voltage.png"
```

---

# 4. JSON Schema Validation

The developer will:

- Create **schema.json** based on YAML structure
- Integrate with VS Code:

```jsonc
"yaml.schemas": {
  "schemas/schema.json": "examples/*.yaml"
}
```

- Use `jsonschema` or Pydantic in Python for runtime validation.

---

# 5. Python Models (Pydantic)

Example:

```python
class SectionConfig(BaseModel):
    L: float
    diam: float
    nseg: int

class Morphology(BaseModel):
    type: Literal["single_compartment","multi_section"]
    sections: Dict[str, SectionConfig]
    connections: Optional[List[Connection]] = []

class Biophysics(BaseModel):
    Ra: float
    cm: float
    mechanisms: Dict[str, Dict[str, float]]
```

Toolkit loads YAML → validates → creates strong typed model.

---

# 6. NEURON Model Builder

Core responsibilities:

### 6.1 Create Sections
```python
sec = h.Section(name=name)
sec.L = cfg.L
sec.diam = cfg.diam
sec.nseg = cfg.nseg
```

### 6.2 Connect Morphology
```python
child.connect(parent(cfg.parent_loc), cfg.child_loc)
```

### 6.3 Insert Biophysics
```python
sec.insert("hh")
sec.gnabar_hh = value
```

### 6.4 Insert Passive
```python
sec.insert("pas")
sec.g_pas = 0.001
sec.e_pas = -65
```

---

# 7. Stimuli Support (Multiple IClamp)

```python
stim = h.IClamp(sec(loc))
stim.delay = delay
stim.dur = duration
stim.amp = amplitude
```

- Support multiple entries in YAML.

---

# 8. Recordings (Multi-Location)

Support recording:

- membrane voltage: `v`
- current injection: `i`

Example:

```python
vec = h.Vector().record(sec(loc)._ref_v)
```

---

# 9. Simulation Runner

```python
h.celsius = cfg.temperature_celsius
h.tstop = cfg.tstop_ms
h.dt = cfg.dt_ms
h.finitialize(-65)
h.run()
```

---

# 10. Output & Plotting

### Save traces (CSV)
```python
df.to_csv(output_path)
```

### Plotting
Use matplotlib:

```python
plt.plot(t, soma_v)
plt.savefig("voltage.png")
```

---

# 11. CLI Interface

Two commands:

### Run experiment:
```bash
nrnexp run experiment.yaml
```

### Validate experiment:
```bash
nrnexp validate experiment.yaml
```

Implement via:

```python
import argparse
```

---

# 12. Hodgkin–Huxley Standard Parameters

For correctness, HH defaults:

| Parameter | Value |
|----------|-------|
| gnabar_hh | 0.12 |
| gkbar_hh | 0.036 |
| gl_hh | 0.0003 |
| el_hh | –54.3 |

Developer should override YAML values into section objects.

---

# 13. Developer Roadmap (1 Month)

### Week 1  
- Config models  
- YAML → Python loader  
- JSON schema  
- VS Code validation  
- Basic CLI

### Week 2  
- Model builder  
- Biophysics insertion  
- Single IClamp  
- Single recording

### Week 3  
- Multi-section morphology  
- Multiple stimuli  
- Multiple recordings  
- Full runner

### Week 4  
- CSV + plots  
- Documentation  
- Example YAML  
- Packaging (pip installable)

---

# 14. Deliverables

- Python package (`neuron_toolkit`)
- JSON schema + YAML examples
- CLI tool
- Documentation + diagrams
- Reproducible experiment examples

---

This document gives the full technical plan required for development within 1 month.

import yaml
from pathlib import Path
from typing import Dict, Any
from .models import ExperimentConfig


def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Load YAML configuration from file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def load_experiment_config(file_path: str) -> ExperimentConfig:
    """Load and validate experiment configuration from YAML file."""
    config_data = load_yaml_config(file_path)
    return ExperimentConfig(**config_data)


def save_yaml_config(config: Dict[str, Any], file_path: str) -> None:
    """Save configuration to YAML file."""
    with open(file_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
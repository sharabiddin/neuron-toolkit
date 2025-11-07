"""
NEURON YAML Reproducibility Toolkit

A toolkit for declarative NEURON simulations using YAML configuration files.
"""

__version__ = "1.0.0"
__author__ = "Sharabiddin Ahmayev"
__email__ = "main@iamsh.info"

from .main import run_experiment, validate_experiment
from .config.loader import load_experiment_config
from .config.validator import validate_experiment_config, is_valid_config
from .config.models import ExperimentConfig

__all__ = [
    "run_experiment",
    "validate_experiment", 
    "load_experiment_config",
    "validate_experiment_config",
    "is_valid_config",
    "ExperimentConfig",
]
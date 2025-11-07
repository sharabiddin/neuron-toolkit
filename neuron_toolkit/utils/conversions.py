from typing import Dict, Any, Union
import numpy as np


def ms_to_s(time_ms: float) -> float:
    """Convert milliseconds to seconds."""
    return time_ms / 1000.0


def s_to_ms(time_s: float) -> float:
    """Convert seconds to milliseconds."""
    return time_s * 1000.0


def nA_to_uA(current_nA: float) -> float:
    """Convert nanoamperes to microamperes."""
    return current_nA / 1000.0


def uA_to_nA(current_uA: float) -> float:
    """Convert microamperes to nanoamperes."""
    return current_uA * 1000.0


def mV_to_V(voltage_mV: float) -> float:
    """Convert millivolts to volts."""
    return voltage_mV / 1000.0


def V_to_mV(voltage_V: float) -> float:
    """Convert volts to millivolts."""
    return voltage_V * 1000.0


def um_to_cm(length_um: float) -> float:
    """Convert micrometers to centimeters."""
    return length_um / 10000.0


def cm_to_um(length_cm: float) -> float:
    """Convert centimeters to micrometers."""
    return length_cm * 10000.0


def normalize_units(config: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize units in configuration for NEURON compatibility."""
    normalized = config.copy()
    
    return normalized


def validate_numeric_range(value: Union[int, float], min_val: float, max_val: float, name: str) -> None:
    """Validate that a numeric value is within specified range."""
    if not min_val <= value <= max_val:
        raise ValueError(f"{name} must be between {min_val} and {max_val}, got {value}")


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
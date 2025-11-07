import jsonschema
import json
from pathlib import Path
from typing import Dict, Any, List
from .models import ExperimentConfig
from .loader import load_yaml_config


def get_schema_path() -> Path:
    """Get path to JSON schema file."""
    return Path(__file__).parent / "schema.json"


def load_json_schema() -> Dict[str, Any]:
    """Load JSON schema for validation."""
    schema_path = get_schema_path()
    with open(schema_path, 'r') as f:
        return json.load(f)


def validate_with_json_schema(config_data: Dict[str, Any]) -> List[str]:
    """Validate configuration using JSON schema."""
    schema = load_json_schema()
    validator = jsonschema.Draft7Validator(schema)
    errors = []
    
    for error in validator.iter_errors(config_data):
        errors.append(f"{'.'.join(str(p) for p in error.absolute_path)}: {error.message}")
    
    return errors


def validate_with_pydantic(config_data: Dict[str, Any]) -> List[str]:
    """Validate configuration using Pydantic models."""
    try:
        ExperimentConfig(**config_data)
        return []
    except Exception as e:
        return [str(e)]


def validate_experiment_config(file_path: str) -> Dict[str, List[str]]:
    """Validate experiment configuration file with both JSON schema and Pydantic."""
    try:
        config_data = load_yaml_config(file_path)
    except Exception as e:
        return {"file_errors": [f"Failed to load YAML: {str(e)}"]}
    
    validation_results = {
        "schema_errors": validate_with_json_schema(config_data),
        "pydantic_errors": validate_with_pydantic(config_data)
    }
    
    return validation_results


def is_valid_config(file_path: str) -> bool:
    """Check if configuration is valid."""
    results = validate_experiment_config(file_path)
    return all(len(errors) == 0 for errors in results.values())
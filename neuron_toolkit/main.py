from pathlib import Path
from typing import Optional
from .config.loader import load_experiment_config
from .config.validator import validate_experiment_config, is_valid_config
from .core.runner import SimulationRunner
from .core.outputs import OutputManager
from .utils.logging import setup_logging, get_logger


def run_experiment(config_file: str, output_dir: Optional[str] = None, log_level: str = "INFO") -> bool:
    """Run a NEURON experiment from YAML configuration."""
    
    logger = setup_logging(log_level)
    
    try:
        logger.info(f"Loading experiment configuration from: {config_file}")
        
        if not is_valid_config(config_file):
            logger.error("Configuration validation failed")
            validation_results = validate_experiment_config(config_file)
            for error_type, errors in validation_results.items():
                if errors:
                    logger.error(f"{error_type}: {errors}")
            return False
        
        config = load_experiment_config(config_file)
        logger.info(f"Loaded experiment: {config.metadata.name}")
        
        if output_dir:
            config.outputs.directory = output_dir
        
        logger.info("Starting simulation...")
        runner = SimulationRunner(config)
        results = runner.run_simulation()
        logger.info("Simulation completed successfully")
        
        logger.info("Saving results...")
        output_manager = OutputManager(config)
        output_manager.save_results(results)
        output_manager.save_metadata()
        
        logger.info(f"Results saved to: {output_manager.get_output_directory()}")
        return True
        
    except Exception as e:
        logger.error(f"Experiment failed: {str(e)}")
        return False


def validate_experiment(config_file: str, log_level: str = "INFO") -> bool:
    """Validate a NEURON experiment configuration."""
    
    logger = setup_logging(log_level)
    
    try:
        logger.info(f"Validating configuration: {config_file}")
        
        validation_results = validate_experiment_config(config_file)
        
        all_valid = True
        for error_type, errors in validation_results.items():
            if errors:
                all_valid = False
                logger.error(f"{error_type}:")
                for error in errors:
                    logger.error(f"  - {error}")
        
        if all_valid:
            logger.info("Configuration is valid!")
            
            try:
                config = load_experiment_config(config_file)
                logger.info(f"Successfully loaded: {config.metadata.name}")
                logger.info(f"Description: {config.metadata.description}")
                logger.info(f"Sections: {list(config.get_morphology().sections.keys())}")
                logger.info(f"Stimuli: {len(config.stimuli)}")
                logger.info(f"Recordings: {len(config.recordings)}")
                logger.info(f"Simulation time: {config.simulation.tstop_ms} ms")
            except Exception as e:
                logger.warning(f"Configuration loaded but with warnings: {str(e)}")
                return False
        
        return all_valid
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        return False
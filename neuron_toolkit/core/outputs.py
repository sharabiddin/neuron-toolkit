import os
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ..config.models import ExperimentConfig, OutputConfig, PlotConfig


class OutputManager:
    """Manages simulation output and plotting."""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.output_config = config.outputs
        self.output_dir = Path(self.output_config.directory)
    
    def save_results(self, data: Dict[str, np.ndarray]) -> None:
        """Save simulation results."""
        self.create_output_directory()
        self.save_traces(data)
        
        if self.output_config.plot and self.output_config.plot.enabled:
            self.create_plots(data)
    
    def create_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_traces(self, data: Dict[str, np.ndarray]) -> None:
        """Save trace data to CSV files."""
        if self.output_config.save_traces.get("format") == "csv":
            self.save_traces_csv(data)
    
    def save_traces_csv(self, data: Dict[str, np.ndarray]) -> None:
        """Save traces as CSV file."""
        df = pd.DataFrame(data)
        
        csv_path = self.output_dir / "traces.csv"
        df.to_csv(csv_path, index=False)
        print(f"Traces saved to: {csv_path}")
    
    def create_plots(self, data: Dict[str, np.ndarray]) -> None:
        """Create and save plots."""
        if not self.output_config.plot:
            return
        
        plot_config = self.output_config.plot
        
        if "time" not in data:
            print("Warning: No time data available for plotting")
            return
        
        time = data["time"]
        
        plt.figure(figsize=(12, 8))
        
        for i, var_name in enumerate(plot_config.variables):
            if var_name in data:
                plt.subplot(len(plot_config.variables), 1, i + 1)
                plt.plot(time, data[var_name], linewidth=2, label=var_name)
                plt.ylabel("Voltage (mV)" if var_name.endswith("_v") else var_name)
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                if i == len(plot_config.variables) - 1:
                    plt.xlabel("Time (ms)")
            else:
                print(f"Warning: Variable '{var_name}' not found in data")
        
        plt.suptitle(f"{self.config.metadata.name} - Simulation Results")
        plt.tight_layout()
        
        plot_path = self.output_dir / plot_config.save_as
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Plot saved to: {plot_path}")
    
    def create_voltage_plot(self, data: Dict[str, np.ndarray], variables: List[str]) -> None:
        """Create voltage-specific plots."""
        if "time" not in data:
            return
        
        time = data["time"]
        
        plt.figure(figsize=(10, 6))
        
        for var_name in variables:
            if var_name in data and var_name.endswith("_v"):
                plt.plot(time, data[var_name], linewidth=2, label=var_name.replace("_v", ""))
        
        plt.xlabel("Time (ms)")
        plt.ylabel("Voltage (mV)")
        plt.title(f"{self.config.metadata.name} - Voltage Traces")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plot_path = self.output_dir / "voltage_traces.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Voltage plot saved to: {plot_path}")
    
    def save_metadata(self) -> None:
        """Save experiment metadata."""
        metadata_path = self.output_dir / "metadata.yaml"
        
        metadata_dict = {
            "experiment": {
                "name": self.config.metadata.name,
                "description": self.config.metadata.description,
                "version": self.config.metadata.version
            },
            "environment": {
                "temperature_celsius": self.config.environment.temperature_celsius,
                "random_seed": self.config.environment.random_seed
            },
            "simulation": {
                "tstop_ms": self.config.simulation.tstop_ms,
                "dt_ms": self.config.simulation.dt_ms
            }
        }
        
        import yaml
        with open(metadata_path, 'w') as f:
            yaml.dump(metadata_dict, f, default_flow_style=False, indent=2)
        
        print(f"Metadata saved to: {metadata_path}")
    
    def get_output_directory(self) -> Path:
        """Get output directory path."""
        return self.output_dir
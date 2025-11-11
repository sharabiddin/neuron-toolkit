#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from .main import run_experiment, validate_experiment
from .utils.logging import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="nrnexp",
        description="NEURON YAML Reproducibility Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nrnexp run experiment.yaml
  nrnexp run experiment.yaml --output-dir results/my_experiment
  nrnexp validate experiment.yaml
  nrnexp validate experiment.yaml --verbose
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser(
        "run",
        help="Run NEURON experiment from YAML configuration"
    )
    run_parser.add_argument(
        "config_file",
        help="Path to YAML configuration file"
    )
    run_parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for results (overrides config)"
    )
    run_parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    run_parser.add_argument(
        "--verbose", "-v",
        action="store_const",
        const="DEBUG",
        dest="log_level",
        help="Enable verbose output (equivalent to --log-level DEBUG)"
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate YAML configuration file"
    )
    validate_parser.add_argument(
        "config_file",
        help="Path to YAML configuration file"
    )
    validate_parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    validate_parser.add_argument(
        "--verbose", "-v",
        action="store_const",
        const="DEBUG",
        dest="log_level",
        help="Enable verbose output (equivalent to --log-level DEBUG)"
    )
    
    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Validate config file exists
    config_file = Path(args.config_file)
    if not config_file.exists():
        print(f"Error: Configuration file '{args.config_file}' not found", file=sys.stderr)
        return 1
    
    if not config_file.suffix.lower() in ['.yaml', '.yml']:
        print(f"Warning: File '{args.config_file}' doesn't have .yaml or .yml extension", file=sys.stderr)
    
    try:
        if args.command == "run":
            success = run_experiment(
                str(config_file),
                args.output_dir,
                args.log_level
            )
            return 0 if success else 1
            
        elif args.command == "validate":
            success = validate_experiment(
                str(config_file),
                args.log_level
            )
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
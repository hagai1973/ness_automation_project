"""
Configuration management for the automation system.
"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path


class Config:
    """Manages configuration for the automation system."""

    def __init__(self, config_path: str = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration file. If None, uses default config.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "config.yaml"
        )

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            return self._get_default_config()

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config or {}

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "automation": {
                "enabled": True,
                "log_level": "INFO",
                "max_retries": 3,
            },
            "scheduler": {
                "check_interval": 60,
            },
            "tasks": {
                "default_timeout": 300,
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation, e.g., 'automation.enabled')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self, path: str = None) -> None:
        """
        Save configuration to file.

        Args:
            path: Path to save configuration. If None, uses current config_path.
        """
        save_path = path or self.config_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

"""Tests for the config module."""

import pytest
import tempfile
import os
from ness_automation.config import Config


def test_config_default():
    """Test default configuration."""
    config = Config('/tmp/nonexistent_config.yaml')
    assert config.get('automation.enabled') is True
    assert config.get('automation.log_level') == 'INFO'


def test_config_get():
    """Test getting configuration values."""
    config = Config()
    
    # Test nested key access
    assert config.get('automation.enabled') is not None
    assert config.get('scheduler.check_interval') is not None
    
    # Test default value
    assert config.get('nonexistent.key', 'default') == 'default'


def test_config_set():
    """Test setting configuration values."""
    config = Config()
    
    config.set('automation.enabled', False)
    assert config.get('automation.enabled') is False
    
    config.set('new.nested.value', 'test')
    assert config.get('new.nested.value') == 'test'


def test_config_save_load():
    """Test saving and loading configuration."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name

    try:
        config1 = Config()
        config1.set('test.value', 'test123')
        config1.save(temp_path)
        
        config2 = Config(temp_path)
        assert config2.get('test.value') == 'test123'
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

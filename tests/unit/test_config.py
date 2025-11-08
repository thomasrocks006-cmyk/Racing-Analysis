"""Tests for configuration management"""

import os
from src.utils.config import Settings


def test_settings_defaults():
    """Test that settings have sensible defaults"""
    settings = Settings()
    
    assert settings.environment == "dev"
    assert settings.model_type == "catboost"
    assert settings.kelly_fraction == 0.25
    assert settings.commission_rate == 0.05


def test_settings_from_env(monkeypatch):
    """Test loading settings from environment variables"""
    monkeypatch.setenv("MODEL_TYPE", "lightgbm")
    monkeypatch.setenv("KELLY_FRACTION", "0.5")
    
    settings = Settings()
    
    assert settings.model_type == "lightgbm"
    assert settings.kelly_fraction == 0.5

# Generated-by: Cursor (claude-4-sonnet)
"""
Unit tests for the main module.
"""

import logging

from mcp_prometheus_server.main import main


def test_main_basic():
    """Test that main runs without errors."""
    result = main([])
    assert result == 0


def test_main_with_logging(caplog):
    """Test main with logging."""
    with caplog.at_level(logging.INFO):
        result = main([])
        assert result == 0
        # Check that the expected log messages were recorded
        assert "MCP Prometheus Server" in caplog.text

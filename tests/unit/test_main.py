# Generated-by: Cursor (claude-4-sonnet)
"""
Unit tests for the main module.
"""

import logging

import pytest

from mcp_prometheus_server.main import main
from tests.constants import (
    SYSTEM_EXIT_ERROR_CODE,
    TEST_UNICODE_TOKEN,
)


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


def test_main_with_prometheus_url():
    """Test main function with custom Prometheus URL."""
    result = main(["--prometheus-url", "https://prometheus.example.com"])
    assert result == 0


def test_main_with_auth_token():
    """Test main function with authentication token."""
    result = main(["--auth-token", "test-token"])
    assert result == 0


def test_main_with_all_arguments():
    """Test main function with all arguments."""
    result = main(
        [
            "--log-level",
            "WARNING",
            "--prometheus-url",
            "https://prometheus.example.com",
            "--auth-token",
            "test-token",
        ]
    )
    assert result == 0


def test_main_with_invalid_log_level():
    """Test main function with invalid log level."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--log-level", "INVALID"])
    assert exc_info.value.code == SYSTEM_EXIT_ERROR_CODE


def test_main_with_empty_arguments():
    """Test main function with empty argument list."""
    result = main([])
    assert result == 0


def test_main_with_none_arguments():
    """Test main function with None arguments."""
    with pytest.raises(SystemExit) as exc_info:
        main(None)
    assert exc_info.value.code == SYSTEM_EXIT_ERROR_CODE


def test_main_with_extra_arguments():
    """Test main function with extra unknown arguments."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--unknown-arg", "value"])
    assert exc_info.value.code == SYSTEM_EXIT_ERROR_CODE


def test_main_with_very_long_url():
    """Test main function with very long Prometheus URL."""
    long_url = "https://" + "a" * 1000 + ".example.com"
    result = main(["--prometheus-url", long_url])
    assert result == 0


def test_main_with_special_characters_in_url():
    """Test main function with special characters in URL."""
    special_url = "https://prometheus.example.com:9090/path?query=value&other=test"
    result = main(["--prometheus-url", special_url])
    assert result == 0


def test_main_with_unicode_in_token():
    """Test main function with unicode characters in auth token."""
    unicode_token = TEST_UNICODE_TOKEN
    result = main(["--auth-token", unicode_token])
    assert result == 0


def test_main_with_empty_string_arguments():
    """Test main function with empty string arguments."""
    result = main(["--prometheus-url", "", "--auth-token", ""])
    assert result == 0


def test_main_with_whitespace_arguments():
    """Test main function with whitespace-only arguments."""
    result = main(["--prometheus-url", "   ", "--auth-token", "\t\n"])
    assert result == 0


def test_main_with_duplicate_arguments():
    """Test main function with duplicate arguments."""
    result = main(
        [
            "--log-level",
            "DEBUG",
            "--log-level",
            "INFO",  # Second one should override
        ]
    )
    assert result == 0


def test_main_with_mixed_case_arguments():
    """Test main function with mixed case arguments."""
    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "--LOG-LEVEL",
                "debug",
                "--PROMETHEUS-URL",
                "https://example.com",
                "--AUTH-TOKEN",
                "token",
            ]
        )
    assert exc_info.value.code == SYSTEM_EXIT_ERROR_CODE


def test_main_with_short_arguments():
    """Test main function with short form arguments (if supported)."""
    # Note: argparse doesn't support short forms by default, but test the behavior
    with pytest.raises(SystemExit) as exc_info:
        main(["-h"])  # This should trigger help and exit
    assert exc_info.value.code == 0  # Help exit with code 0


def test_main_with_positional_arguments():
    """Test main function with positional arguments."""
    with pytest.raises(SystemExit) as exc_info:
        main(["positional_arg1", "positional_arg2"])
    assert exc_info.value.code == SYSTEM_EXIT_ERROR_CODE


def test_main_with_boolean_like_arguments():
    """Test main function with boolean-like string arguments."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--log-level", "true", "--prometheus-url", "false", "--auth-token", "0"])
    assert exc_info.value.code == SYSTEM_EXIT_ERROR_CODE


def test_main_with_numeric_arguments():
    """Test main function with numeric arguments."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--log-level", "1", "--prometheus-url", "2", "--auth-token", "3"])
    assert exc_info.value.code == SYSTEM_EXIT_ERROR_CODE


def test_main_with_special_shell_characters():
    """Test main function with special shell characters."""
    result = main(
        [
            "--prometheus-url",
            "https://example.com; rm -rf /",
            "--auth-token",
            "token && echo 'hacked'",
        ]
    )
    assert result == 0


def test_main_with_very_long_argument_list():
    """Test main function with very long argument list."""
    args = []
    for i in range(1000):
        args.extend([f"--arg{i}", f"value{i}"])

    with pytest.raises(SystemExit) as exc_info:
        main(args)
    assert exc_info.value.code == SYSTEM_EXIT_ERROR_CODE


def test_main_with_unicode_arguments():
    """Test main function with unicode arguments."""
    result = main(
        ["--prometheus-url", "https://服务器.example.com", "--auth-token", "токен-тест"]
    )
    assert result == 0


def test_main_with_newline_characters():
    """Test main function with newline characters in arguments."""
    result = main(
        ["--prometheus-url", "https://example.com\n", "--auth-token", "token\r\n"]
    )
    assert result == 0


def test_main_with_tab_characters():
    """Test main function with tab characters in arguments."""
    result = main(
        ["--prometheus-url", "https://example.com\t", "--auth-token", "token\t"]
    )
    assert result == 0


def test_main_with_quoted_arguments():
    """Test main function with quoted arguments."""
    result = main(
        ["--prometheus-url", '"https://example.com"', "--auth-token", "'token'"]
    )
    assert result == 0


def test_main_with_escaped_characters():
    """Test main function with escaped characters."""
    result = main(
        ["--prometheus-url", "https://example.com\\", "--auth-token", "token\\n"]
    )
    assert result == 0

# Generated-by: Cursor (claude-4-sonnet)
"""
Main application module for MCP Prometheus Server.

This module provides a CLI interface for the MCP Prometheus server.
"""

import argparse
import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main(args: list[str] | None = None) -> int:
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="MCP Prometheus Server",
        epilog="MCP server for querying Prometheus metrics with relative time support.",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level",
    )
    parser.add_argument(
        "--prometheus-url",
        default="http://localhost:9090",
        help="Prometheus server URL",
    )
    parser.add_argument(
        "--auth-token",
        help="Authentication token for Prometheus",
    )

    parsed_args = parser.parse_args(args)
    setup_logging(parsed_args.log_level)

    logger = logging.getLogger(__name__)
    logger.info("Starting MCP Prometheus Server")
    logger.info("Prometheus URL: %s", parsed_args.prometheus_url)

    if parsed_args.auth_token:
        logger.info("Authentication token provided")

    logger.info("Use 'mcp-prometheus-server' command to run the MCP server")
    logger.info("Or run: python -m mcp_prometheus_server.mcp_server")

    return 0


if __name__ == "__main__":
    sys.exit(main())

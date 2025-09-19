# MCP Prometheus Server

[![Test](https://github.com/jewzaam/mcp-prometheus-server/workflows/Test/badge.svg)](https://github.com/jewzaam/mcp-prometheus-server/actions/workflows/test.yml)
[![Coverage](https://github.com/jewzaam/mcp-prometheus-server/workflows/Coverage%20Check/badge.svg)](https://github.com/jewzaam/mcp-prometheus-server/actions/workflows/coverage.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

An MCP (Model Context Protocol) server that enables AI assistants to query Prometheus metrics. Provides four tools for monitoring data access with relative time support.

## What This Does

This server acts as a bridge between AI assistants and Prometheus monitoring systems. It exposes Prometheus data through MCP tools that AI assistants can use to:

- Query current metric values for specific instances
- Retrieve historical time series data
- Execute PromQL queries with relative time expressions
- Discover available metrics

## MCP Tools

### 1. `query_metric`
Execute any PromQL query with relative time support.
- **Parameters**: `query` (PromQL string), `relative_time` (optional, default: "5m")
- **Example**: Query CPU usage for the last hour

### 2. `get_instance_value` 
Get current metric value for a specific instance.
- **Parameters**: `metric_name`, `instance`, `relative_time` (optional)
- **Example**: Get CPU usage for server "web-01"

### 3. `get_metric_history`
Retrieve historical data over a time range.
- **Parameters**: `metric_name`, `relative_time` (default: "1h"), `step` (default: "1m")
- **Example**: Get CPU usage history for the last 24 hours

### 4. `list_available_metrics`
Query available metrics with optional filtering.
- **Parameters**: `pattern` (optional regex filter)
- **Example**: List all metrics matching "cpu.*"

## Relative Time Support

All tools support relative time expressions:
- **Minutes**: `1m`, `5m`, `30m`
- **Hours**: `1h`, `6h`, `24h` 
- **Days**: `1d`, `7d`, `30d`
- **Weeks**: `1w`, `2w`, `4w`

## Quick Start

### Installation
```bash
git clone <your-repo-url> mcp-prometheus-server
cd mcp-prometheus-server
make requirements-dev
```

### Configuration
```bash
# Basic configuration
export PROMETHEUS_URL="http://localhost:9090"

# Authentication options (choose one):
# Option 1: Bearer token
export PROMETHEUS_AUTH_TOKEN="your-bearer-token"

# Option 2: Basic authentication
export PROMETHEUS_USERNAME="your-username"
export PROMETHEUS_PASSWORD="your-password"
```

### Authentication Methods

The server supports multiple authentication methods:

1. **No Authentication** (default): Works with unsecured Prometheus instances
2. **Bearer Token**: Use `PROMETHEUS_AUTH_TOKEN` for token-based auth
3. **Basic Authentication**: Use `PROMETHEUS_USERNAME` and `PROMETHEUS_PASSWORD` for basic auth

**Note**: Bearer token takes precedence over basic auth if both are provided.

### Running
```bash
# Run the MCP server
python -m mcp_prometheus_server.mcp_server

# Or use the installed script
mcp-prometheus-server
```

### Cursor IDE Integration
```bash
make install-cursor
python scripts/test_mcp_client.py
# Restart Cursor to use the MCP server
```

## Development

```bash
make test          # Run all tests
make lint          # Run linting and type checking
make format        # Format code
make coverage      # Run tests with coverage report
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make lint test coverage` to ensure quality
5. Submit a pull request
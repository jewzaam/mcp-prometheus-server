# MCP Prometheus Server Requirements

## Overview
This MCP server enables AI assistants to query Prometheus metrics through four core tools with relative time support.

## Core Functionality

### 1. Query Tools
- **`query_metric`**: Execute any PromQL query with relative time support
- **`get_instance_value`**: Get current metric value for a specific instance
- **`get_metric_history`**: Retrieve historical time series data over configurable ranges
- **`list_available_metrics`**: Discover available metrics with optional filtering

### 2. Relative Time Support
- All queries use relative time expressions (5m, 1h, 24h, 7d)
- No absolute timestamps - focus on relative time from now
- Support for minutes, hours, days, and weeks

### 3. Prometheus Integration
- Full PromQL support for complex queries and aggregations
- Instance-specific data retrieval by hostname, IP, or instance label
- Time series data for trend analysis and visualization

## Technical Requirements

### Configuration
- **Prometheus URL**: Configurable endpoint (default: http://localhost:9090)
- **Authentication**: Optional bearer token support
- **Environment Variables**: PROMETHEUS_URL, PROMETHEUS_AUTH_TOKEN

### Error Handling
- Connection errors with clear messages
- PromQL error parsing and reporting
- Input parameter validation
- Graceful timeout handling

### Dependencies
- `prometheus-api-client`: Prometheus API interaction
- `mcp`: Model Context Protocol server framework
- `httpx`: Async HTTP client
- `pydantic`: Data validation

### Testing
- Unit tests for all functions
- Integration tests with real Prometheus
- >90% code coverage target
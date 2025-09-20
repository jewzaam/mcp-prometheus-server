# Generated-by: Cursor (claude-4-sonnet)
"""
MCP Prometheus Server implementation.

Provides tools for querying Prometheus metrics with relative time support,
instance value reading, and historical data access.
"""

import asyncio
import logging
import os
from typing import Any

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

from .prometheus_client import PrometheusClient

# Constants

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("mcp-prometheus-server")

# Initialize Prometheus client
prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
auth_token = os.getenv("PROMETHEUS_AUTH_TOKEN")
username = os.getenv("PROMETHEUS_USERNAME")
password = os.getenv("PROMETHEUS_PASSWORD")
prometheus_client = PrometheusClient(
    prometheus_url=prometheus_url,
    auth_token=auth_token,
    username=username,
    password=password,
)


@server.list_tools()  # type: ignore[misc]
async def handle_list_tools() -> list[Tool]:
    """List available Prometheus tools."""
    return [
        Tool(
            name="query_metric",
            description="Execute any PromQL query against Prometheus. This is the primary tool for all Prometheus interactions. Use it for instant queries, range queries, aggregations, filtering, and complex analysis. Examples: 'cpu_usage{instance=\"server1\"}', 'rate(http_requests_total[5m])', 'up == 0', '{__name__=~\".*\"}' to list all metrics, 'cpu_usage[1h:5m]' for historical data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "PromQL query string. Supports instant queries, range queries, aggregations, functions, and operators. Use 'query_metric' with 'get_promql_docs' for help with syntax.",
                    },
                    "relative_time": {
                        "type": "string",
                        "description": "Time offset from now for the query (e.g., '5m', '1h', '24h'). For range queries, use '[time_range:step]' syntax. Default: '5m'",
                        "default": "5m",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_promql_docs",
            description="Get PromQL documentation and examples. Use this to learn PromQL syntax, find functions, understand operators, and see query examples. Essential for writing effective Prometheus queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Specific PromQL topic to get documentation for (e.g., 'functions', 'operators', 'selectors', 'aggregations', 'rate', 'sum', 'histogram_quantile'). Leave empty for general overview.",
                        "default": "",
                    },
                },
                "required": [],
            },
        ),
    ]


def _raise_validation_error(message: str) -> None:
    """Raise a validation error with the given message."""
    raise ValueError(message)


async def _handle_query_metric(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle query_metric tool call."""
    query = arguments.get("query", "")
    relative_time = arguments.get("relative_time", "5m")

    if not query:
        _raise_validation_error("Query parameter is required")

    result = await prometheus_client.query_metric(query, relative_time)
    return [
        TextContent(
            type="text", text=f"Query Result:\n{_format_query_result(result)}"
        )
    ]


async def _handle_get_promql_docs(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle get_promql_docs tool call."""
    topic = arguments.get("topic", "").lower().strip()

    # PromQL documentation organized by topic
    docs = {
        "": _get_promql_overview(),
        "overview": _get_promql_overview(),
        "functions": _get_promql_functions(),
        "operators": _get_promql_operators(),
        "selectors": _get_promql_selectors(),
        "aggregations": _get_promql_aggregations(),
        "rate": _get_promql_rate_function(),
        "sum": _get_promql_sum_function(),
        "histogram_quantile": _get_promql_histogram_quantile(),
        "instant_vs_range": _get_promql_instant_vs_range(),
        "examples": _get_promql_examples(),
    }

    if topic in docs:
        content = docs[topic]
    else:
        # Try to find partial matches
        matches = [k for k in docs if topic in k and k]
        if matches:
            content = f"Found topics matching '{topic}': {', '.join(matches)}\n\n"
            for match in matches[:3]:  # Show first 3 matches
                content += f"## {match.title()}\n{docs[match]}\n\n"
        else:
            content = f"Topic '{topic}' not found. Available topics: {', '.join(sorted(docs.keys()))}\n\n"
            content += docs[""]

    return [TextContent(type="text", text=content)]


@server.call_tool()  # type: ignore[misc]
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[TextContent]:
    """Handle Prometheus tool calls."""
    if not arguments:
        arguments = {}

    try:
        if name == "query_metric":
            return await _handle_query_metric(arguments)
        if name == "get_promql_docs":
            return await _handle_get_promql_docs(arguments)

        _raise_validation_error(f"Unknown tool: {name}")
        return []  # This line will never be reached, but satisfies mypy

    except Exception as e:
        logger.exception("Tool call failed")
        return [TextContent(type="text", text=f"Error: {e!s}")]


def _format_query_result(result: dict[str, Any]) -> str:
    """Return Prometheus query result as structured JSON."""
    import json
    return json.dumps(result, indent=2)


# PromQL Documentation Functions

def _get_promql_overview() -> str:
    """Get PromQL overview documentation."""
    return """# PromQL Overview

PromQL (Prometheus Query Language) is a powerful query language for Prometheus time series data.

## Query Types
- **Instant Queries**: Single point in time (e.g., `cpu_usage`)
- **Range Queries**: Time series over a range (e.g., `cpu_usage[5m]`)

## Basic Syntax
- **Metrics**: `metric_name` or `{__name__="metric_name"}`
- **Label Selectors**: `{label="value"}` or `{label=~"regex"}`
- **Functions**: `rate(metric[5m])`, `sum(metric)`
- **Operators**: `+`, `-`, `*`, `/`, `==`, `!=`, `>`, `<`

## Common Patterns
- List all metrics: `{__name__=~".*"}`
- Filter by instance: `cpu_usage{instance="server1"}`
- Rate calculation: `rate(http_requests_total[5m])`
- Aggregations: `sum(cpu_usage) by (instance)`

## Time Ranges
- `[5m]` - 5 minutes
- `[1h]` - 1 hour
- `[1d]` - 1 day
- `[1h:5m]` - 1 hour range with 5-minute steps

Use `get_promql_docs` with specific topics for detailed information."""

def _get_promql_functions() -> str:
    """Get PromQL functions documentation."""
    return """# PromQL Functions

## Rate Functions
- `rate(metric[5m])` - Per-second rate of increase
- `irate(metric[5m])` - Instant rate (last two points)
- `increase(metric[5m])` - Total increase over time

## Aggregation Functions
- `sum(metric)` - Sum across dimensions
- `avg(metric)` - Average across dimensions
- `min(metric)` - Minimum value
- `max(metric)` - Maximum value
- `count(metric)` - Count of series

## Time Functions
- `time()` - Current timestamp
- `timestamp(metric)` - Timestamp of metric
- `year(metric)` - Extract year
- `month(metric)` - Extract month

## Math Functions
- `abs(metric)` - Absolute value
- `ceil(metric)` - Round up
- `floor(metric)` - Round down
- `round(metric)` - Round to nearest integer

## Histogram Functions
- `histogram_quantile(0.95, metric)` - 95th percentile
- `histogram_quantile(0.50, metric)` - 50th percentile (median)

## Examples
- `rate(http_requests_total[5m])` - Request rate
- `sum(rate(http_requests_total[5m])) by (job)` - Rate by job
- `histogram_quantile(0.95, http_request_duration_seconds_bucket)` - 95th percentile latency"""

def _get_promql_operators() -> str:
    """Get PromQL operators documentation."""
    return """# PromQL Operators

## Arithmetic Operators
- `+` - Addition
- `-` - Subtraction
- `*` - Multiplication
- `/` - Division
- `%` - Modulo
- `^` - Power

## Comparison Operators
- `==` - Equal
- `!=` - Not equal
- `>` - Greater than
- `<` - Less than
- `>=` - Greater than or equal
- `<=` - Less than or equal

## Logical Operators
- `and` - Logical AND
- `or` - Logical OR
- `unless` - Logical UNLESS

## Vector Matching
- `on(label1, label2)` - Match on specific labels
- `ignoring(label1, label2)` - Ignore specific labels
- `group_left` - One-to-many matching
- `group_right` - Many-to-one matching

## Examples
- `cpu_usage > 0.8` - CPU usage above 80%
- `http_requests_total{code="200"} / http_requests_total` - Success rate
- `rate(http_requests_total[5m]) and up == 1` - Request rate where instance is up"""

def _get_promql_selectors() -> str:
    """Get PromQL selectors documentation."""
    return """# PromQL Selectors

## Label Selectors
- `{label="value"}` - Exact match
- `{label=~"regex"}` - Regex match
- `{label!="value"}` - Not equal
- `{label!~"regex"}` - Not regex match

## Metric Selectors
- `metric_name` - Single metric
- `{__name__="metric_name"}` - Explicit metric name
- `{__name__=~"cpu.*"}` - Regex on metric name

## Multiple Labels
- `{job="api", instance="server1"}` - AND logic
- `{job=~"api|web"}` - OR logic with regex

## Special Labels
- `{__name__}` - Metric name
- `{__name__=~".*"}` - All metrics
- `{__name__=~"cpu.*"}` - Metrics starting with "cpu"

## Examples
- `cpu_usage{instance="server1"}` - CPU usage for specific instance
- `{__name__=~"http_.*", code="200"}` - All HTTP metrics with 200 status
- `{job=~"api|web", instance!="server1"}` - API or web jobs, not server1"""

def _get_promql_aggregations() -> str:
    """Get PromQL aggregations documentation."""
    return """# PromQL Aggregations

## Basic Aggregations
- `sum(metric)` - Sum all values
- `avg(metric)` - Average all values
- `min(metric)` - Minimum value
- `max(metric)` - Maximum value
- `count(metric)` - Count of series

## Grouping
- `by (label1, label2)` - Group by labels
- `without (label1, label2)` - Group by all labels except these

## Quantiles
- `quantile(0.95, metric)` - 95th percentile
- `quantile(0.50, metric)` - 50th percentile (median)

## Top/Bottom
- `topk(5, metric)` - Top 5 values
- `bottomk(5, metric)` - Bottom 5 values

## Count
- `count_values("label", metric)` - Count unique values
- `count(metric)` - Count series

## Examples
- `sum(rate(http_requests_total[5m])) by (job)` - Request rate by job
- `avg(cpu_usage) by (instance)` - Average CPU by instance
- `topk(10, rate(http_requests_total[5m]))` - Top 10 request rates
- `quantile(0.95, http_request_duration_seconds)` - 95th percentile latency"""

def _get_promql_rate_function() -> str:
    """Get detailed rate function documentation."""
    return """# PromQL rate() Function

## Syntax
`rate(metric[time_range])`

## Description
Calculates the per-second average rate of increase of a counter metric over a time range.

## Parameters
- `metric` - Counter metric (monotonically increasing)
- `time_range` - Time range (e.g., `5m`, `1h`, `1d`)

## Important Notes
- Only works with counter metrics
- Returns per-second rate
- Handles counter resets automatically
- Minimum time range should be 4x the scrape interval

## Examples
- `rate(http_requests_total[5m])` - HTTP request rate
- `rate(cpu_seconds_total[5m])` - CPU usage rate
- `sum(rate(http_requests_total[5m])) by (job)` - Total rate by job

## Common Patterns
- `rate(metric[5m]) > 0` - Only series with activity
- `rate(metric[5m]) * 60` - Rate per minute
- `rate(metric[5m]) * 3600` - Rate per hour"""

def _get_promql_sum_function() -> str:
    """Get detailed sum function documentation."""
    return """# PromQL sum() Function

## Syntax
`sum(metric) [by (label1, label2)]`

## Description
Sums all values of a metric across all series.

## Parameters
- `metric` - Any metric
- `by (labels)` - Optional grouping labels

## Examples
- `sum(cpu_usage)` - Total CPU usage across all instances
- `sum(rate(http_requests_total[5m])) by (job)` - Total request rate by job
- `sum(rate(http_requests_total[5m])) by (job, instance)` - Rate by job and instance

## Common Patterns
- `sum(metric) by (job)` - Group by job
- `sum(metric) without (instance)` - Sum across all instances
- `sum(rate(metric[5m]))` - Sum of rates"""

def _get_promql_histogram_quantile() -> str:
    """Get detailed histogram_quantile function documentation."""
    return """# PromQL histogram_quantile() Function

## Syntax
`histogram_quantile(quantile, histogram_metric)`

## Description
Calculates quantiles from histogram metrics.

## Parameters
- `quantile` - Quantile value (0.0 to 1.0)
- `histogram_metric` - Histogram bucket metric (usually ends with `_bucket`)

## Common Quantiles
- `0.50` - 50th percentile (median)
- `0.95` - 95th percentile
- `0.99` - 99th percentile
- `0.999` - 99.9th percentile

## Examples
- `histogram_quantile(0.95, http_request_duration_seconds_bucket)` - 95th percentile latency
- `histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))` - Median rate
- `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` - 99th percentile with grouping

## Important Notes
- Requires `le` label for bucket boundaries
- Often used with `rate()` for time-based calculations
- Use `sum()` to aggregate across dimensions"""

def _get_promql_instant_vs_range() -> str:
    """Get instant vs range query documentation."""
    return """# PromQL Instant vs Range Queries

## Instant Queries
Single point in time evaluation.

### Syntax
`metric_name` or `metric_name[time_offset]`

### Examples
- `cpu_usage` - Current CPU usage
- `cpu_usage[5m]` - CPU usage 5 minutes ago
- `rate(http_requests_total[5m])` - Current request rate

## Range Queries
Time series over a range with regular intervals.

### Syntax
`metric_name[start:end:step]`

### Parameters
- `start` - Start time (relative or absolute)
- `end` - End time (relative or absolute)
- `step` - Query resolution step

### Examples
- `cpu_usage[1h:5m]` - CPU usage over 1 hour with 5-minute steps
- `rate(http_requests_total[5m])[1h:1m]` - Request rate over 1 hour with 1-minute steps

## Time Formats
- `5m` - 5 minutes
- `1h` - 1 hour
- `1d` - 1 day
- `1w` - 1 week

## Use Cases
- **Instant**: Current values, alerts, single data points
- **Range**: Graphing, trend analysis, historical data"""

def _get_promql_examples() -> str:
    """Get comprehensive PromQL examples."""
    return """# PromQL Examples

## Basic Queries
- `up` - Instance status
- `cpu_usage` - CPU usage metric
- `{__name__=~".*"}` - All metrics

## Filtering
- `cpu_usage{instance="server1"}` - CPU for specific instance
- `http_requests_total{code="200"}` - Successful requests
- `{job="api", instance=~"web.*"}` - API job, web instances

## Rate Calculations
- `rate(http_requests_total[5m])` - Request rate
- `rate(cpu_seconds_total[5m])` - CPU usage rate
- `irate(http_requests_total[5m])` - Instant rate

## Aggregations
- `sum(cpu_usage)` - Total CPU usage
- `avg(cpu_usage) by (instance)` - Average by instance
- `sum(rate(http_requests_total[5m])) by (job)` - Total rate by job

## Percentiles
- `histogram_quantile(0.95, http_request_duration_seconds_bucket)` - 95th percentile latency
- `histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))` - Median rate

## Alerts
- `cpu_usage > 0.8` - High CPU usage
- `up == 0` - Instance down
- `rate(http_requests_total[5m]) > 100` - High request rate

## Complex Queries
- `sum(rate(http_requests_total[5m])) by (job) / sum(rate(http_requests_total[5m]))` - Request distribution
- `topk(5, rate(http_requests_total[5m]))` - Top 5 request rates
- `rate(http_requests_total[5m]) and up == 1` - Request rate where instance is up"""


async def main() -> None:
    """Run the MCP Prometheus server."""
    logger.info("Starting MCP Prometheus server...")
    logger.info("Prometheus URL: %s", prometheus_url)

    # Log authentication method
    if auth_token:
        logger.info("Using Bearer token authentication")
    elif username and password:
        logger.info("Using basic authentication for user: %s", username)
    else:
        logger.info("No authentication configured")

    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-prometheus-server",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,  # type: ignore[arg-type]
                        experimental_capabilities=None,  # type: ignore[arg-type]
                    ),
                ),
            )
    finally:
        await prometheus_client.close()


if __name__ == "__main__":
    asyncio.run(main())

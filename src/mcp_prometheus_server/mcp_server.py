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


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available Prometheus tools."""
    return [
        Tool(
            name="query_metric",
            description="Execute any PromQL query against Prometheus. Use this for complex queries, aggregations, or when you need specific metric combinations. Returns both current values and time series data depending on the query type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "PromQL query string (e.g., 'cpu_usage{instance=\"server1\"}', 'rate(http_requests_total[5m])', 'up == 0')"
                    },
                    "relative_time": {
                        "type": "string",
                        "description": "Time offset from now for the query (e.g., '5m', '1h', '24h'). Default: '5m'",
                        "default": "5m",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_instance_value",
            description="Get the current value of a specific metric for a particular instance. Use this when you know the exact metric name and instance identifier. Returns a single numeric value with timestamp.",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric_name": {
                        "type": "string",
                        "description": "Exact name of the metric (e.g., 'cpu_usage', 'memory_used_bytes', 'http_requests_total')",
                    },
                    "instance": {
                        "type": "string",
                        "description": "Instance identifier from the 'instance' label (e.g., 'server1:8080', '192.168.1.100:9090', 'web-01')",
                    },
                    "relative_time": {
                        "type": "string",
                        "description": "Time offset from now for the query (e.g., '5m', '1h', '24h'). Default: '5m'",
                        "default": "5m",
                    },
                },
                "required": ["metric_name", "instance"],
            },
        ),
        Tool(
            name="get_metric_history",
            description="Get historical time series data for a metric over a specified time range. Use this to analyze trends, create graphs, or understand how a metric has changed over time. Returns multiple data points with timestamps.",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric_name": {
                        "type": "string",
                        "description": "Exact name of the metric (e.g., 'cpu_usage', 'memory_used_bytes', 'http_requests_total')",
                    },
                    "relative_time": {
                        "type": "string",
                        "description": "Time range to look back from now (e.g., '1h', '24h', '7d'). Default: '1h'",
                        "default": "1h",
                    },
                    "step": {
                        "type": "string",
                        "description": "Data point interval - how often to sample the metric (e.g., '1m', '5m', '1h'). Smaller steps = more data points. Default: '1m'",
                        "default": "1m",
                    },
                },
                "required": ["metric_name"],
            },
        ),
        Tool(
            name="list_available_metrics",
            description="Discover available metrics in Prometheus. Use this to find metric names when you don't know the exact names, or to explore what metrics are available. Returns a list of metric names matching the pattern.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Optional regex pattern to filter metrics (e.g., 'cpu.*', 'memory.*', 'http_.*'). If not provided, returns all available metrics.",
                    }
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[TextContent]:
    """Handle Prometheus tool calls."""
    if not arguments:
        arguments = {}

    try:
        if name == "query_metric":
            query = arguments.get("query", "")
            relative_time = arguments.get("relative_time", "5m")

            if not query:
                raise ValueError("Query parameter is required")

            result = await prometheus_client.query_metric(query, relative_time)

            return [
                TextContent(
                    type="text", text=f"Query Result:\n{_format_query_result(result)}"
                )
            ]

        if name == "get_instance_value":
            metric_name = arguments.get("metric_name", "")
            instance = arguments.get("instance", "")
            relative_time = arguments.get("relative_time", "5m")

            if not metric_name or not instance:
                raise ValueError("metric_name and instance parameters are required")

            value = await prometheus_client.get_instance_value(
                metric_name, instance, relative_time
            )

            if value is not None:
                return [
                    TextContent(
                        type="text",
                        text=f"Instance '{instance}' metric '{metric_name}' value: {value}",
                    )
                ]
            return [
                TextContent(
                    type="text",
                    text=f"No value found for metric '{metric_name}' on instance '{instance}'",
                )
            ]

        if name == "get_metric_history":
            metric_name = arguments.get("metric_name", "")
            relative_time = arguments.get("relative_time", "1h")
            step = arguments.get("step", "1m")

            if not metric_name:
                raise ValueError("metric_name parameter is required")

            history = await prometheus_client.get_metric_history(
                metric_name, relative_time, step
            )

            if history:
                history_text = (
                    f"Historical data for '{metric_name}' ({relative_time}):\n"
                )
                for data_point in history[-10:]:  # Show last 10 points
                    timestamp = data_point["timestamp"]
                    value = data_point["value"]
                    labels = data_point["labels"]
                    history_text += f"  {timestamp}: {value} {labels}\n"

                return [TextContent(type="text", text=history_text)]
            return [
                TextContent(
                    type="text",
                    text=f"No historical data found for metric '{metric_name}'",
                )
            ]

        if name == "list_available_metrics":
            pattern = arguments.get("pattern")

            metrics = await prometheus_client.list_available_metrics(pattern)

            if metrics:
                metrics_text = f"Available metrics ({len(metrics)} found):\n"
                for metric in metrics[:20]:  # Show first 20 metrics
                    metrics_text += f"  {metric}\n"

                if len(metrics) > 20:
                    metrics_text += f"  ... and {len(metrics) - 20} more"

                return [TextContent(type="text", text=metrics_text)]
            return [TextContent(type="text", text="No metrics found")]

        raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool call failed: {e}")
        return [TextContent(type="text", text=f"Error: {e!s}")]


def _format_query_result(result: dict[str, Any]) -> str:
    """Format Prometheus query result for display."""
    if result.get("status") != "success":
        return f"Query failed: {result.get('error', 'Unknown error')}"

    data = result.get("data", {})
    result_type = data.get("resultType", "")
    results = data.get("result", [])

    if not results:
        return "No data returned"

    formatted = f"Result type: {result_type}\n"

    for i, series in enumerate(results[:5]):  # Show first 5 series
        metric = series.get("metric", {})
        formatted += f"\nSeries {i + 1}:\n"
        formatted += f"  Labels: {metric}\n"

        if "value" in series:
            # Instant query result
            timestamp, value = series["value"]
            formatted += f"  Value: {value} (at {timestamp})\n"
        elif "values" in series:
            # Range query result
            values = series["values"]
            formatted += f"  Data points: {len(values)}\n"
            if values:
                latest = values[-1]
                formatted += f"  Latest: {latest[1]} (at {latest[0]})\n"

    if len(results) > 5:
        formatted += f"\n... and {len(results) - 5} more series"

    return formatted


async def main() -> None:
    """Run the MCP Prometheus server."""
    logger.info("Starting MCP Prometheus server...")
    logger.info(f"Prometheus URL: {prometheus_url}")
    
    # Log authentication method
    if auth_token:
        logger.info("Using Bearer token authentication")
    elif username and password:
        logger.info(f"Using basic authentication for user: {username}")
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
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )
    finally:
        await prometheus_client.close()


if __name__ == "__main__":
    asyncio.run(main())

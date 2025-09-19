# Generated-by: Cursor (claude-4-sonnet)
"""
Tests for mcp_server module.

Comprehensive tests covering MCP server functionality,
tool registration, and error handling.
"""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_prometheus_server.mcp_server import (
    _format_query_result,
    handle_call_tool,
    handle_list_tools,
)


class TestMCPServerTools:
    """Test cases for MCP server tools."""

    @pytest.mark.asyncio
    async def test_handle_list_tools(self):
        """Test tool listing functionality."""
        tools = await handle_list_tools()

        assert len(tools) == 4

        tool_names = [tool.name for tool in tools]
        assert "query_metric" in tool_names
        assert "get_instance_value" in tool_names
        assert "get_metric_history" in tool_names
        assert "list_available_metrics" in tool_names

    @pytest.mark.asyncio
    async def test_query_metric_tool_schema(self):
        """Test query_metric tool schema."""
        tools = await handle_list_tools()
        query_tool = next(tool for tool in tools if tool.name == "query_metric")

        assert (
            query_tool.description
            == "Execute any PromQL query against Prometheus. Use this for complex queries, aggregations, or when you need specific metric combinations. Returns both current values and time series data depending on the query type."
        )
        assert "query" in query_tool.inputSchema["required"]
        assert "relative_time" in query_tool.inputSchema["properties"]
        assert query_tool.inputSchema["properties"]["relative_time"]["default"] == "5m"

    @pytest.mark.asyncio
    async def test_get_instance_value_tool_schema(self):
        """Test get_instance_value tool schema."""
        tools = await handle_list_tools()
        instance_tool = next(
            tool for tool in tools if tool.name == "get_instance_value"
        )

        assert (
            instance_tool.description
            == "Get the current value of a specific metric for a particular instance. Use this when you know the exact metric name and instance identifier. Returns a single numeric value with timestamp."
        )
        required = instance_tool.inputSchema["required"]
        assert "metric_name" in required
        assert "instance" in required

    @pytest.mark.asyncio
    async def test_get_metric_history_tool_schema(self):
        """Test get_metric_history tool schema."""
        tools = await handle_list_tools()
        history_tool = next(tool for tool in tools if tool.name == "get_metric_history")

        assert (
            history_tool.description
            == "Get historical time series data for a metric over a specified time range. Use this to analyze trends, create graphs, or understand how a metric has changed over time. Returns multiple data points with timestamps."
        )
        assert "metric_name" in history_tool.inputSchema["required"]
        assert (
            history_tool.inputSchema["properties"]["relative_time"]["default"] == "1h"
        )
        assert history_tool.inputSchema["properties"]["step"]["default"] == "1m"

    @pytest.mark.asyncio
    async def test_list_available_metrics_tool_schema(self):
        """Test list_available_metrics tool schema."""
        tools = await handle_list_tools()
        list_tool = next(
            tool for tool in tools if tool.name == "list_available_metrics"
        )

        assert (
            list_tool.description == "Discover available metrics in Prometheus. Use this to find metric names when you don't know the exact names, or to explore what metrics are available. Returns a list of metric names matching the pattern."
        )
        assert list_tool.inputSchema["required"] == []


class TestMCPToolCalls:
    """Test cases for MCP tool call handling."""

    @pytest.mark.asyncio
    async def test_query_metric_success(self):
        """Test successful query_metric tool call."""
        mock_result = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server1"},
                        "value": [1640995200, "85.5"],
                    }
                ],
            },
        }

        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.query_metric = AsyncMock(return_value=mock_result)

            result = await handle_call_tool(
                "query_metric", {"query": "cpu_usage", "relative_time": "5m"}
            )

            assert len(result) == 1
            assert result[0].type == "text"
            assert "Query Result:" in result[0].text
            assert "cpu_usage" in result[0].text

    @pytest.mark.asyncio
    async def test_query_metric_missing_query(self):
        """Test query_metric tool call with missing query parameter."""
        result = await handle_call_tool("query_metric", {"relative_time": "5m"})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text
        assert "Query parameter is required" in result[0].text

    @pytest.mark.asyncio
    async def test_get_instance_value_success(self):
        """Test successful get_instance_value tool call."""
        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.get_instance_value = AsyncMock(return_value=85.5)

            result = await handle_call_tool(
                "get_instance_value",
                {
                    "metric_name": "cpu_usage",
                    "instance": "server1",
                    "relative_time": "5m",
                },
            )

            assert len(result) == 1
            assert result[0].type == "text"
            assert "Instance 'server1' metric 'cpu_usage' value: 85.5" in result[0].text

    @pytest.mark.asyncio
    async def test_get_instance_value_not_found(self):
        """Test get_instance_value tool call when no value found."""
        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.get_instance_value = AsyncMock(return_value=None)

            result = await handle_call_tool(
                "get_instance_value",
                {"metric_name": "cpu_usage", "instance": "server1"},
            )

            assert len(result) == 1
            assert result[0].type == "text"
            assert "No value found" in result[0].text

    @pytest.mark.asyncio
    async def test_get_instance_value_missing_params(self):
        """Test get_instance_value tool call with missing parameters."""
        result = await handle_call_tool(
            "get_instance_value", {"metric_name": "cpu_usage"}
        )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text
        assert "metric_name and instance parameters are required" in result[0].text

    @pytest.mark.asyncio
    async def test_get_metric_history_success(self):
        """Test successful get_metric_history tool call."""
        mock_history = [
            {
                "timestamp": 1640995200,
                "value": 85.5,
                "labels": {"__name__": "cpu_usage", "instance": "server1"},
            },
            {
                "timestamp": 1640995260,
                "value": 87.2,
                "labels": {"__name__": "cpu_usage", "instance": "server1"},
            },
        ]

        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.get_metric_history = AsyncMock(return_value=mock_history)

            result = await handle_call_tool(
                "get_metric_history",
                {"metric_name": "cpu_usage", "relative_time": "1h"},
            )

            assert len(result) == 1
            assert result[0].type == "text"
            assert "Historical data for 'cpu_usage'" in result[0].text
            assert "85.5" in result[0].text
            assert "87.2" in result[0].text

    @pytest.mark.asyncio
    async def test_get_metric_history_empty(self):
        """Test get_metric_history tool call with no data."""
        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.get_metric_history = AsyncMock(return_value=[])

            result = await handle_call_tool(
                "get_metric_history", {"metric_name": "cpu_usage"}
            )

            assert len(result) == 1
            assert result[0].type == "text"
            assert "No historical data found" in result[0].text

    @pytest.mark.asyncio
    async def test_get_metric_history_missing_metric(self):
        """Test get_metric_history tool call with missing metric_name."""
        result = await handle_call_tool("get_metric_history", {"relative_time": "1h"})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text
        assert "metric_name parameter is required" in result[0].text

    @pytest.mark.asyncio
    async def test_list_available_metrics_success(self):
        """Test successful list_available_metrics tool call."""
        mock_metrics = ["cpu_usage", "memory_usage", "disk_usage"]

        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.list_available_metrics = AsyncMock(return_value=mock_metrics)

            result = await handle_call_tool("list_available_metrics", {})

            assert len(result) == 1
            assert result[0].type == "text"
            assert "Available metrics (3 found)" in result[0].text
            assert "cpu_usage" in result[0].text

    @pytest.mark.asyncio
    async def test_list_available_metrics_with_pattern(self):
        """Test list_available_metrics tool call with pattern."""
        mock_metrics = ["cpu_usage", "cpu_temperature"]

        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.list_available_metrics = AsyncMock(return_value=mock_metrics)

            result = await handle_call_tool(
                "list_available_metrics", {"pattern": "cpu.*"}
            )

            assert len(result) == 1
            assert result[0].type == "text"
            assert "Available metrics (2 found)" in result[0].text

    @pytest.mark.asyncio
    async def test_list_available_metrics_empty(self):
        """Test list_available_metrics tool call with no metrics."""
        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.list_available_metrics = AsyncMock(return_value=[])

            result = await handle_call_tool("list_available_metrics", {})

            assert len(result) == 1
            assert result[0].type == "text"
            assert "No metrics found" in result[0].text

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test handling of unknown tool."""
        result = await handle_call_tool("unknown_tool", {"param": "value"})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text
        assert "Unknown tool: unknown_tool" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_call_with_none_arguments(self):
        """Test tool call with None arguments."""
        result = await handle_call_tool("query_metric", None)

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text
        assert "Query parameter is required" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_call_exception_handling(self):
        """Test exception handling in tool calls."""
        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.query_metric = AsyncMock(
                side_effect=Exception("Connection failed")
            )

            result = await handle_call_tool("query_metric", {"query": "cpu_usage"})

            assert len(result) == 1
            assert result[0].type == "text"
            assert "Error:" in result[0].text
            assert "Connection failed" in result[0].text


class TestFormatQueryResult:
    """Test cases for query result formatting."""

    def test_format_successful_vector_result(self):
        """Test formatting successful vector result."""
        result = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server1"},
                        "value": [1640995200, "85.5"],
                    }
                ],
            },
        }

        formatted = _format_query_result(result)

        assert "Result type: vector" in formatted
        assert "Series 1:" in formatted
        assert "Labels: {'__name__': 'cpu_usage', 'instance': 'server1'}" in formatted
        assert "Value: 85.5" in formatted

    def test_format_successful_matrix_result(self):
        """Test formatting successful matrix result."""
        result = {
            "status": "success",
            "data": {
                "resultType": "matrix",
                "result": [
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server1"},
                        "values": [[1640995200, "85.5"], [1640995260, "87.2"]],
                    }
                ],
            },
        }

        formatted = _format_query_result(result)

        assert "Result type: matrix" in formatted
        assert "Data points: 2" in formatted
        assert "Latest: 87.2" in formatted

    def test_format_failed_result(self):
        """Test formatting failed query result."""
        result = {"status": "error", "error": "Invalid query syntax"}

        formatted = _format_query_result(result)

        assert "Query failed: Invalid query syntax" in formatted

    def test_format_empty_result(self):
        """Test formatting empty result."""
        result = {"status": "success", "data": {"resultType": "vector", "result": []}}

        formatted = _format_query_result(result)

        assert "No data returned" in formatted

    def test_format_multiple_series(self):
        """Test formatting result with multiple series."""
        result = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server1"},
                        "value": [1640995200, "85.5"],
                    },
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server2"},
                        "value": [1640995200, "90.2"],
                    },
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server3"},
                        "value": [1640995200, "78.1"],
                    },
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server4"},
                        "value": [1640995200, "92.8"],
                    },
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server5"},
                        "value": [1640995200, "88.3"],
                    },
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server6"},
                        "value": [1640995200, "95.1"],
                    },
                ],
            },
        }

        formatted = _format_query_result(result)

        assert "Series 1:" in formatted
        assert "Series 2:" in formatted
        assert "Series 3:" in formatted
        assert "Series 4:" in formatted
        assert "Series 5:" in formatted
        assert "... and 1 more" in formatted

    def test_format_missing_data_fields(self):
        """Test formatting result with missing data fields."""
        result = {"status": "success", "data": {}}

        formatted = _format_query_result(result)

        assert "No data returned" in formatted

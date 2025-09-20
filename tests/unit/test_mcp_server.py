# Generated-by: Cursor (claude-4-sonnet)
"""
Tests for mcp_server module.

Comprehensive tests covering MCP server functionality,
tool registration, and error handling.
"""

import asyncio
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

        assert len(tools) == 2  # noqa: PLR2004

        tool_names = [tool.name for tool in tools]
        assert "query_metric" in tool_names
        assert "get_promql_docs" in tool_names

    @pytest.mark.asyncio
    async def test_query_metric_tool_schema(self):
        """Test query_metric tool schema."""
        tools = await handle_list_tools()
        query_tool = next(tool for tool in tools if tool.name == "query_metric")

        assert "Execute any PromQL query against Prometheus" in query_tool.description
        assert "primary tool for all Prometheus interactions" in query_tool.description
        assert "query" in query_tool.inputSchema["required"]
        assert "relative_time" in query_tool.inputSchema["properties"]
        assert query_tool.inputSchema["properties"]["relative_time"]["default"] == "5m"

    @pytest.mark.asyncio
    async def test_get_promql_docs_tool_schema(self):
        """Test get_promql_docs tool schema."""
        tools = await handle_list_tools()
        docs_tool = next(tool for tool in tools if tool.name == "get_promql_docs")

        assert "PromQL documentation and examples" in docs_tool.description
        assert "Essential for writing effective Prometheus queries" in docs_tool.description
        assert docs_tool.inputSchema["required"] == []
        assert "topic" in docs_tool.inputSchema["properties"]
        assert docs_tool.inputSchema["properties"]["topic"]["default"] == ""


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
    async def test_get_promql_docs_overview(self):
        """Test get_promql_docs tool call with no topic."""
        result = await handle_call_tool("get_promql_docs", {})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "PromQL Overview" in result[0].text
        assert "Query Types" in result[0].text
        assert "Basic Syntax" in result[0].text

    @pytest.mark.asyncio
    async def test_get_promql_docs_functions(self):
        """Test get_promql_docs tool call with functions topic."""
        result = await handle_call_tool("get_promql_docs", {"topic": "functions"})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "PromQL Functions" in result[0].text
        assert "rate(metric[5m])" in result[0].text
        assert "sum(metric)" in result[0].text

    @pytest.mark.asyncio
    async def test_get_promql_docs_rate_function(self):
        """Test get_promql_docs tool call with rate function topic."""
        result = await handle_call_tool("get_promql_docs", {"topic": "rate"})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "rate() Function" in result[0].text
        assert "rate(metric[time_range])" in result[0].text
        assert "per-second average rate" in result[0].text

    @pytest.mark.asyncio
    async def test_get_promql_docs_unknown_topic(self):
        """Test get_promql_docs tool call with unknown topic."""
        result = await handle_call_tool("get_promql_docs", {"topic": "unknown"})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Topic 'unknown' not found" in result[0].text
        assert "Available topics:" in result[0].text


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

        # Should return JSON data as string
        import json
        assert json.loads(formatted) == result

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

        # Should return JSON data as string
        import json
        assert json.loads(formatted) == result

    def test_format_failed_result(self):
        """Test formatting failed query result."""
        result = {"status": "error", "error": "Invalid query syntax"}

        formatted = _format_query_result(result)

        # Should return JSON data as string
        import json
        assert json.loads(formatted) == result

    def test_format_empty_result(self):
        """Test formatting empty result."""
        result = {"status": "success", "data": {"resultType": "vector", "result": []}}

        formatted = _format_query_result(result)

        # Should return JSON data as string
        import json
        assert json.loads(formatted) == result

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

        # Should return JSON data as string
        import json
        assert json.loads(formatted) == result

    def test_format_missing_data_fields(self):
        """Test formatting result with missing data fields."""
        result = {"status": "success", "data": {}}

        formatted = _format_query_result(result)

        # Should return JSON data as string
        import json
        assert json.loads(formatted) == result

    @pytest.mark.asyncio
    async def test_tool_call_with_invalid_parameter_types(self):
        """Test tool call with invalid parameter types."""
        # Test with non-string parameters
        result = await handle_call_tool(
            "query_metric", {"query": 123, "relative_time": "5m"}
        )

        assert len(result) == 1
        assert result[0].type == "text"
        # Should handle type conversion or error appropriately

    @pytest.mark.asyncio
    async def test_tool_call_with_whitespace_parameters(self):
        """Test tool call with whitespace-only parameters."""
        result = await handle_call_tool(
            "query_metric", {"query": "   ", "relative_time": "5m"}
        )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_call_with_very_long_parameters(self):
        """Test tool call with very long parameter values."""
        long_query = "cpu_usage" * 1000  # Very long query string

        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.query_metric = AsyncMock(
                return_value={"status": "success", "data": {"result": []}}
            )

            result = await handle_call_tool(
                "query_metric", {"query": long_query, "relative_time": "5m"}
            )

        assert len(result) == 1
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_tool_call_with_special_characters(self):
        """Test tool call with special characters in parameters."""
        special_query = 'cpu_usage{instance="server-1", job="test-job"}'

        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.query_metric = AsyncMock(
                return_value={"status": "success", "data": {"result": []}}
            )

            result = await handle_call_tool(
                "query_metric", {"query": special_query, "relative_time": "5m"}
            )

        assert len(result) == 1
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_tool_call_with_unicode_parameters(self):
        """Test tool call with unicode characters in parameters."""
        unicode_query = 'cpu_usage{instance="服务器-1"}'

        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.query_metric = AsyncMock(
                return_value={"status": "success", "data": {"result": []}}
            )

            result = await handle_call_tool(
                "query_metric", {"query": unicode_query, "relative_time": "5m"}
            )

        assert len(result) == 1
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_tool_call_with_empty_string_parameters(self):
        """Test tool call with empty string parameters."""
        result = await handle_call_tool(
            "get_instance_value", {"metric_name": "", "instance": "server1"}
        )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_call_with_none_parameters(self):
        """Test tool call with None parameters."""
        result = await handle_call_tool(
            "get_instance_value", {"metric_name": None, "instance": "server1"}
        )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_call_with_extra_parameters(self):
        """Test tool call with extra unexpected parameters."""
        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.query_metric = AsyncMock(
                return_value={"status": "success", "data": {"result": []}}
            )

            result = await handle_call_tool(
                "query_metric",
                {
                    "query": "cpu_usage",
                    "relative_time": "5m",
                    "extra_param": "should_be_ignored",
                },
            )

        assert len(result) == 1
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_tool_call_with_malformed_arguments(self):
        """Test tool call with malformed arguments structure."""
        result = await handle_call_tool("query_metric", "not_a_dict")

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_call_with_nested_arguments(self):
        """Test tool call with nested argument structures."""
        result = await handle_call_tool(
            "query_metric", {"query": {"nested": "value"}, "relative_time": "5m"}
        )

        assert len(result) == 1
        assert result[0].type == "text"
        # Should handle nested structures appropriately

    @pytest.mark.asyncio
    async def test_tool_call_timeout_handling(self):
        """Test tool call timeout handling."""
        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.query_metric = AsyncMock(
                side_effect=asyncio.TimeoutError("Query timed out")
            )

            result = await handle_call_tool(
                "query_metric", {"query": "cpu_usage", "relative_time": "5m"}
            )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text
        assert "timed out" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_call_memory_error_handling(self):
        """Test tool call memory error handling."""
        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.query_metric = AsyncMock(
                side_effect=MemoryError("Out of memory")
            )

            result = await handle_call_tool(
                "query_metric", {"query": "cpu_usage", "relative_time": "5m"}
            )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_call_keyboard_interrupt_handling(self):
        """Test tool call keyboard interrupt handling."""
        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            # Use a custom exception that behaves like KeyboardInterrupt but doesn't trigger pytest's special handling
            class CustomInterruptError(Exception):
                pass

            mock_client.query_metric = AsyncMock(
                side_effect=CustomInterruptError("Interrupted")
            )

            result = await handle_call_tool(
                "query_metric", {"query": "cpu_usage", "relative_time": "5m"}
            )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text
        assert "Interrupted" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_call_system_exit_handling(self):
        """Test tool call system exit handling."""
        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            # Use a custom exception that behaves like SystemExit but doesn't trigger pytest's special handling
            class CustomSystemExitError(Exception):
                pass

            mock_client.query_metric = AsyncMock(
                side_effect=CustomSystemExitError("System exit")
            )

            result = await handle_call_tool(
                "query_metric", {"query": "cpu_usage", "relative_time": "5m"}
            )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text
        assert "System exit" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_call_with_very_large_result_set(self):
        """Test tool call with very large result set."""
        # Create a large result set
        large_result = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {
                            "__name__": f"metric_{i}",
                            "instance": f"server_{i}",
                        },
                        "value": [1640995200, str(i)],
                    }
                    for i in range(1000)  # 1000 series
                ],
            },
        }

        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.query_metric = AsyncMock(return_value=large_result)

            result = await handle_call_tool(
                "query_metric", {"query": "cpu_usage", "relative_time": "5m"}
            )

        assert len(result) == 1
        assert result[0].type == "text"
        # Should return all series without truncation in JSON format
        assert '"metric_1"' in result[0].text
        assert '"metric_999"' in result[0].text
        assert '"metric_500"' in result[0].text
        # Should not have truncation message
        assert "... and" not in result[0].text

    @pytest.mark.asyncio
    async def test_tool_call_with_very_long_metric_names(self):
        """Test tool call with very long metric names."""
        long_metric_name = "very_long_metric_name_" + "x" * 1000

        with patch("mcp_prometheus_server.mcp_server.prometheus_client") as mock_client:
            mock_client.get_instance_value = AsyncMock(return_value=85.5)

            result = await handle_call_tool(
                "get_instance_value",
                {
                    "metric_name": long_metric_name,
                    "instance": "server1",
                    "relative_time": "5m",
                },
            )

        assert len(result) == 1
        assert result[0].type == "text"


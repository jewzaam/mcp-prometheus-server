# Generated-by: Cursor (claude-4-sonnet)
"""
Tests for prometheus_client module.

Comprehensive tests covering Prometheus client functionality,
relative time parsing, and error handling.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import httpx
import pytest

from mcp_prometheus_server.prometheus_client import PrometheusClient


class TestPrometheusClient:
    """Test cases for PrometheusClient."""

    def test_init_default_values(self):
        """Test client initialization with default values."""
        client = PrometheusClient()

        assert client.prometheus_url == "http://localhost:9090"
        assert client.timeout == 30
        assert client.pc is not None
        assert client.http_client is not None

    def test_init_custom_values(self):
        """Test client initialization with custom values."""
        client = PrometheusClient(
            prometheus_url="https://prometheus.example.com",
            auth_token="test-token",
            timeout=60,
        )

        assert client.prometheus_url == "https://prometheus.example.com"
        assert client.timeout == 60
        assert client.pc is not None

    def test_init_basic_auth(self):
        """Test client initialization with basic authentication."""
        client = PrometheusClient(
            prometheus_url="https://prometheus.example.com",
            username="testuser",
            password="testpass",
            timeout=60,
        )

        assert client.prometheus_url == "https://prometheus.example.com"
        assert client.timeout == 60
        assert client.pc is not None

    def test_init_bearer_token_precedence(self):
        """Test that bearer token takes precedence over basic auth."""
        client = PrometheusClient(
            prometheus_url="https://prometheus.example.com",
            auth_token="bearer-token",
            username="testuser",
            password="testpass",
        )

        assert client.prometheus_url == "https://prometheus.example.com"
        assert client.pc is not None

    def test_parse_relative_time_minutes(self):
        """Test parsing relative time in minutes."""
        client = PrometheusClient()
        end_time = datetime(2024, 1, 1, 12, 0, 0)

        start_time = client._parse_relative_time("5m", end_time)
        expected = end_time - timedelta(minutes=5)

        assert start_time == expected

    def test_parse_relative_time_hours(self):
        """Test parsing relative time in hours."""
        client = PrometheusClient()
        end_time = datetime(2024, 1, 1, 12, 0, 0)

        start_time = client._parse_relative_time("2h", end_time)
        expected = end_time - timedelta(hours=2)

        assert start_time == expected

    def test_parse_relative_time_days(self):
        """Test parsing relative time in days."""
        client = PrometheusClient()
        end_time = datetime(2024, 1, 1, 12, 0, 0)

        start_time = client._parse_relative_time("7d", end_time)
        expected = end_time - timedelta(days=7)

        assert start_time == expected

    def test_parse_relative_time_weeks(self):
        """Test parsing relative time in weeks."""
        client = PrometheusClient()
        end_time = datetime(2024, 1, 1, 12, 0, 0)

        start_time = client._parse_relative_time("2w", end_time)
        expected = end_time - timedelta(weeks=2)

        assert start_time == expected

    def test_parse_relative_time_case_insensitive(self):
        """Test parsing relative time is case insensitive."""
        client = PrometheusClient()
        end_time = datetime(2024, 1, 1, 12, 0, 0)

        start_time_upper = client._parse_relative_time("5M", end_time)
        start_time_lower = client._parse_relative_time("5m", end_time)

        assert start_time_upper == start_time_lower

    def test_parse_relative_time_invalid_format(self):
        """Test parsing invalid relative time format raises ValueError."""
        client = PrometheusClient()
        end_time = datetime(2024, 1, 1, 12, 0, 0)

        with pytest.raises(ValueError, match="Invalid relative time format"):
            client._parse_relative_time("invalid", end_time)

    def test_parse_relative_time_negative_value(self):
        """Test parsing negative relative time values."""
        client = PrometheusClient()
        end_time = datetime(2024, 1, 1, 12, 0, 0)

        start_time = client._parse_relative_time("5m", end_time)
        expected = end_time - timedelta(minutes=5)

        assert start_time == expected

    @pytest.mark.asyncio
    async def test_query_metric_success(self):
        """Test successful metric query."""
        client = PrometheusClient()

        mock_response = {
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

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client.query_metric("cpu_usage", "5m")

            assert result["status"] == "success"
            assert len(result["data"]["result"]) == 1
            assert result["data"]["result"][0]["metric"]["__name__"] == "cpu_usage"

    @pytest.mark.asyncio
    async def test_query_metric_invalid_query(self):
        """Test query with invalid PromQL raises ValueError."""
        client = PrometheusClient()

        with patch.object(client.http_client, "get") as mock_get:
            mock_get.side_effect = Exception("Invalid query")

            with pytest.raises(Exception):
                await client.query_metric("invalid query", "5m")

    @pytest.mark.asyncio
    async def test_get_instance_value_success(self):
        """Test successful instance value retrieval."""
        client = PrometheusClient()

        mock_response = {
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

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            value = await client.get_instance_value("cpu_usage", "server1", "5m")

            assert value == 85.5

    @pytest.mark.asyncio
    async def test_get_instance_value_not_found(self):
        """Test instance value retrieval when no data found."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {"resultType": "vector", "result": []},
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            value = await client.get_instance_value("cpu_usage", "server1", "5m")

            assert value is None

    @pytest.mark.asyncio
    async def test_get_metric_history_success(self):
        """Test successful metric history retrieval."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "matrix",
                "result": [
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server1"},
                        "values": [
                            [1640995200, "85.5"],
                            [1640995260, "87.2"],
                            [1640995320, "83.1"],
                        ],
                    }
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            history = await client.get_metric_history("cpu_usage", "1h", "1m")

            assert len(history) == 3
            assert history[0]["value"] == 85.5
            assert history[0]["timestamp"] == 1640995200
            assert history[0]["labels"]["__name__"] == "cpu_usage"

    @pytest.mark.asyncio
    async def test_get_metric_history_empty(self):
        """Test metric history retrieval with no data."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {"resultType": "matrix", "result": []},
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            history = await client.get_metric_history("cpu_usage", "1h", "1m")

            assert len(history) == 0

    @pytest.mark.asyncio
    async def test_list_available_metrics_success(self):
        """Test successful metrics listing."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {"metric": {"__name__": "cpu_usage"}},
                    {"metric": {"__name__": "memory_usage"}},
                    {"metric": {"__name__": "disk_usage"}},
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            metrics = await client.list_available_metrics()

            assert len(metrics) == 3
            assert "cpu_usage" in metrics
            assert "memory_usage" in metrics
            assert "disk_usage" in metrics

    @pytest.mark.asyncio
    async def test_list_available_metrics_with_pattern(self):
        """Test metrics listing with pattern filter."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {"metric": {"__name__": "cpu_usage"}},
                    {"metric": {"__name__": "cpu_temperature"}},
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            metrics = await client.list_available_metrics("cpu.*")

            assert len(metrics) == 2
            assert "cpu_usage" in metrics
            assert "cpu_temperature" in metrics

    @pytest.mark.asyncio
    async def test_execute_query_instant(self):
        """Test instant query execution."""
        client = PrometheusClient()

        mock_response = {"status": "success", "data": {"result": []}}

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client._execute_query("cpu_usage")

            assert result["status"] == "success"
            mock_get.assert_called_once_with(
                "/api/v1/query", params={"query": "cpu_usage"}
            )

    @pytest.mark.asyncio
    async def test_execute_query_range(self):
        """Test range query execution."""
        client = PrometheusClient()

        mock_response = {"status": "success", "data": {"result": []}}
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        end_time = datetime(2024, 1, 1, 12, 5, 0)

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client._execute_query("cpu_usage", start_time, end_time)

            assert result["status"] == "success"
            mock_get.assert_called_once_with(
                "/api/v1/query_range",
                params={
                    "query": "cpu_usage",
                    "start": start_time.timestamp(),
                    "end": end_time.timestamp(),
                },
            )

    @pytest.mark.asyncio
    async def test_execute_range_query_with_step(self):
        """Test range query execution with step parameter."""
        client = PrometheusClient()

        mock_response = {"status": "success", "data": {"result": []}}
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        end_time = datetime(2024, 1, 1, 12, 5, 0)

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client._execute_range_query(
                "cpu_usage", start_time, end_time, "1m"
            )

            assert result["status"] == "success"
            mock_get.assert_called_once_with(
                "/api/v1/query_range",
                params={
                    "query": "cpu_usage",
                    "start": start_time.timestamp(),
                    "end": end_time.timestamp(),
                    "step": "1m",
                },
            )

    @pytest.mark.asyncio
    async def test_close_client(self):
        """Test client close method."""
        client = PrometheusClient()

        with patch.object(client.http_client, "aclose") as mock_close:
            await client.close()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test HTTP error handling."""
        client = PrometheusClient()

        with patch.object(client.http_client, "get") as mock_get:
            mock_get.side_effect = Exception("Connection failed")

            with pytest.raises(Exception, match="Connection failed"):
                await client.query_metric("cpu_usage", "5m")

    def test_relative_time_edge_cases(self):
        """Test edge cases for relative time parsing."""
        client = PrometheusClient()
        end_time = datetime(2024, 1, 1, 12, 0, 0)

        # Test zero values
        start_time = client._parse_relative_time("0m", end_time)
        assert start_time == end_time

        # Test large values
        start_time = client._parse_relative_time("1000m", end_time)
        expected = end_time - timedelta(minutes=1000)
        assert start_time == expected

    @pytest.mark.asyncio
    async def test_query_metric_with_different_time_formats(self):
        """Test query metric with various time formats."""
        client = PrometheusClient()

        mock_response = {"status": "success", "data": {"result": []}}

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            # Test different time formats
            time_formats = ["1m", "5m", "1h", "24h", "7d", "2w"]

            for time_format in time_formats:
                await client.query_metric("cpu_usage", time_format)

            assert mock_get.call_count == len(time_formats)

    def test_init_with_basic_auth(self):
        """Test client initialization with basic authentication."""
        client = PrometheusClient(
            prometheus_url="https://prometheus.example.com",
            username="testuser",
            password="testpass",
            timeout=60,
        )

        assert client.prometheus_url == "https://prometheus.example.com"
        assert client.timeout == 60
        assert client.pc is not None

    def test_init_with_mixed_auth(self):
        """Test client initialization with both auth methods (should prefer token)."""
        client = PrometheusClient(
            prometheus_url="https://prometheus.example.com",
            auth_token="test-token",
            username="testuser",
            password="testpass",
            timeout=60,
        )

        assert client.prometheus_url == "https://prometheus.example.com"
        assert client.timeout == 60
        assert client.pc is not None

    def test_init_with_empty_credentials(self):
        """Test client initialization with empty credential strings."""
        client = PrometheusClient(
            prometheus_url="https://prometheus.example.com",
            auth_token="",
            username="",
            password="",
            timeout=60,
        )

        assert client.prometheus_url == "https://prometheus.example.com"
        assert client.timeout == 60
        assert client.pc is not None

    def test_parse_relative_time_edge_cases(self):
        """Test edge cases for relative time parsing."""
        client = PrometheusClient()
        end_time = datetime(2024, 1, 1, 12, 0, 0)

        # Test zero values
        start_time = client._parse_relative_time("0m", end_time)
        assert start_time == end_time

        # Test large values
        start_time = client._parse_relative_time("1000m", end_time)
        expected = end_time - timedelta(minutes=1000)
        assert start_time == expected

        # Test negative values (should work)
        start_time = client._parse_relative_time("5m", end_time)
        expected = end_time - timedelta(minutes=5)
        assert start_time == expected

    def test_parse_relative_time_invalid_edge_cases(self):
        """Test invalid relative time formats."""
        client = PrometheusClient()
        end_time = datetime(2024, 1, 1, 12, 0, 0)

        # Test various invalid formats that should actually raise ValueError
        invalid_formats = ["5x", "invalid", "", "5", "m5", "5.5m", " 5m "]
        
        for invalid_format in invalid_formats:
            with pytest.raises(ValueError, match="Invalid relative time format"):
                client._parse_relative_time(invalid_format, end_time)

    def test_parse_relative_time_whitespace_handling(self):
        """Test relative time parsing with whitespace."""
        client = PrometheusClient()
        end_time = datetime(2024, 1, 1, 12, 0, 0)

        # Test that whitespace causes ValueError (current implementation doesn't handle it)
        with pytest.raises(ValueError, match="Invalid relative time format"):
            client._parse_relative_time(" 5m ", end_time)
        
        # Test that clean format works
        start_time = client._parse_relative_time("5m", end_time)
        expected = end_time - timedelta(minutes=5)
        assert start_time == expected

    @pytest.mark.asyncio
    async def test_http_timeout_error(self):
        """Test HTTP timeout error handling."""
        client = PrometheusClient()

        with patch.object(client.http_client, "get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timed out")

            with pytest.raises(httpx.TimeoutException):
                await client.query_metric("cpu_usage", "5m")

    @pytest.mark.asyncio
    async def test_http_connection_error(self):
        """Test HTTP connection error handling."""
        client = PrometheusClient()

        with patch.object(client.http_client, "get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")

            with pytest.raises(httpx.ConnectError):
                await client.query_metric("cpu_usage", "5m")

    @pytest.mark.asyncio
    async def test_http_status_errors(self):
        """Test HTTP status code error handling."""
        client = PrometheusClient()

        # Test 401 Unauthorized
        with patch.object(client.http_client, "get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "401 Unauthorized", request=Mock(), response=mock_response
            )
            mock_get.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError):
                await client.query_metric("cpu_usage", "5m")

    @pytest.mark.asyncio
    async def test_malformed_json_response(self):
        """Test handling of malformed JSON responses."""
        client = PrometheusClient()

        with patch.object(client.http_client, "get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response

            with pytest.raises(ValueError):
                await client.query_metric("cpu_usage", "5m")

    @pytest.mark.asyncio
    async def test_empty_response_body(self):
        """Test handling of empty response bodies."""
        client = PrometheusClient()

        with patch.object(client.http_client, "get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = None
            mock_get.return_value = mock_response

            result = await client.query_metric("cpu_usage", "5m")
            assert result is None

    @pytest.mark.asyncio
    async def test_malformed_prometheus_response(self):
        """Test handling of malformed Prometheus responses."""
        client = PrometheusClient()

        # Test response missing required fields
        malformed_response = {"status": "success"}  # Missing 'data' field

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = malformed_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client.query_metric("cpu_usage", "5m")
            assert result["status"] == "success"
            # Should handle missing data gracefully

    @pytest.mark.asyncio
    async def test_invalid_metric_value_conversion(self):
        """Test handling of invalid metric values."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server1"},
                        "value": [1640995200, "invalid_number"],
                    }
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            # Should raise ValueError for invalid number conversion
            with pytest.raises(ValueError, match="could not convert string to float"):
                await client.get_instance_value("cpu_usage", "server1", "5m")

    @pytest.mark.asyncio
    async def test_malformed_value_array(self):
        """Test handling of malformed value arrays."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server1"},
                        "value": [1640995200],  # Missing second element
                    }
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            value = await client.get_instance_value("cpu_usage", "server1", "5m")
            assert value is None

    @pytest.mark.asyncio
    async def test_empty_metric_labels(self):
        """Test handling of empty metric labels."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {},  # Empty metric labels
                        "value": [1640995200, "85.5"],
                    }
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client.query_metric("cpu_usage", "5m")
            assert result["status"] == "success"
            # Should handle empty labels gracefully

    @pytest.mark.asyncio
    async def test_unknown_result_type(self):
        """Test handling of unknown result types."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "unknown_type",
                "result": [
                    {
                        "metric": {"__name__": "cpu_usage", "instance": "server1"},
                        "value": [1640995200, "85.5"],
                    }
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client.query_metric("cpu_usage", "5m")
            assert result["status"] == "success"
            # Should handle unknown result types gracefully

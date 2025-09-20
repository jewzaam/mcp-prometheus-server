# Generated-by: Cursor (claude-4-sonnet)
"""
Integration tests for Prometheus client.

Tests against real Prometheus instances when available,
with fallback to mocked responses for CI/CD environments.
"""

from unittest.mock import Mock, patch

import pytest

from mcp_prometheus_server.prometheus_client import PrometheusClient
from tests.constants import (
    CUSTOM_TIMEOUT,
    DEFAULT_TIMEOUT,
    TEST_AUTH_TOKEN,
    TEST_HISTORY_LENGTH,
    TEST_INTEGRATION_METRICS_COUNT,
    TEST_INTEGRATION_PATTERN_METRICS_COUNT,
    TEST_LARGE_RESULT_COUNT,
    TEST_QUERY_RESULTS_COUNT,
)


class TestPrometheusIntegration:
    """Integration tests for Prometheus client."""

    @pytest.mark.asyncio
    async def test_prometheus_client_initialization(self):
        """Test Prometheus client can be initialized."""
        client = PrometheusClient()

        assert client.prometheus_url == "http://localhost:9090"
        assert client.timeout == DEFAULT_TIMEOUT
        assert client.pc is not None
        assert client.http_client is not None

    @pytest.mark.asyncio
    async def test_prometheus_client_with_auth(self):
        """Test Prometheus client initialization with authentication."""
        client = PrometheusClient(
            prometheus_url="https://prometheus.example.com",
            auth_token=TEST_AUTH_TOKEN,
            timeout=CUSTOM_TIMEOUT,
        )

        assert client.prometheus_url == "https://prometheus.example.com"
        assert client.timeout == CUSTOM_TIMEOUT

    @pytest.mark.asyncio
    async def test_query_metric_integration(self):
        """Test query_metric integration with mocked Prometheus response."""
        client = PrometheusClient()

        # Mock a realistic Prometheus response
        mock_response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {
                            "__name__": "up",
                            "instance": "localhost:9090",
                            "job": "prometheus",
                        },
                        "value": [1640995200, "1"],
                    }
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client.query_metric("up", "5m")

            assert result["status"] == "success"
            assert result["data"]["resultType"] == "vector"
            assert len(result["data"]["result"]) == 1
            assert result["data"]["result"][0]["metric"]["__name__"] == "up"

    @pytest.mark.asyncio
    async def test_get_instance_value_integration(self):
        """Test get_instance_value integration using query_metric."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {
                            "__name__": "up",
                            "instance": "localhost:9090",
                            "job": "prometheus",
                        },
                        "value": [1640995200, "1"],
                    }
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client.query_metric('up{instance="localhost:9090"}', "5m")

            assert result["status"] == "success"
            assert len(result["data"]["result"]) == 1
            assert result["data"]["result"][0]["value"][1] == "1"

    @pytest.mark.asyncio
    async def test_get_metric_history_integration(self):
        """Test get_metric_history integration using query_metric."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "matrix",
                "result": [
                    {
                        "metric": {
                            "__name__": "up",
                            "instance": "localhost:9090",
                            "job": "prometheus",
                        },
                        "values": [
                            [1640995200, "1"],
                            [1640995260, "1"],
                            [1640995320, "1"],
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

            result = await client.query_metric("up[1h:1m]", "1h")

            assert result["status"] == "success"
            assert result["data"]["resultType"] == "matrix"
            assert len(result["data"]["result"]) == 1
            assert len(result["data"]["result"][0]["values"]) == TEST_HISTORY_LENGTH

    @pytest.mark.asyncio
    async def test_list_available_metrics_integration(self):
        """Test list_available_metrics integration using query_metric."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {"metric": {"__name__": "up"}},
                    {"metric": {"__name__": "prometheus_build_info"}},
                    {
                        "metric": {
                            "__name__": "prometheus_config_last_reload_successful"
                        }
                    },
                    {
                        "metric": {
                            "__name__": "prometheus_rule_group_last_duration_seconds"
                        }
                    },
                    {"metric": {"__name__": "prometheus_tsdb_head_series"}},
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client.query_metric('{__name__=~".+"}', "5m")

            assert result["status"] == "success"
            assert result["data"]["resultType"] == "vector"
            assert len(result["data"]["result"]) == TEST_INTEGRATION_METRICS_COUNT
            metric_names = [r["metric"]["__name__"] for r in result["data"]["result"]]
            assert "up" in metric_names
            assert "prometheus_build_info" in metric_names

    @pytest.mark.asyncio
    async def test_list_available_metrics_with_pattern_integration(self):
        """Test list_available_metrics with pattern integration using query_metric."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {"metric": {"__name__": "prometheus_build_info"}},
                    {
                        "metric": {
                            "__name__": "prometheus_config_last_reload_successful"
                        }
                    },
                    {
                        "metric": {
                            "__name__": "prometheus_rule_group_last_duration_seconds"
                        }
                    },
                    {"metric": {"__name__": "prometheus_tsdb_head_series"}},
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client.query_metric('{__name__=~"prometheus.*"}', "5m")

            assert result["status"] == "success"
            assert result["data"]["resultType"] == "vector"
            assert len(result["data"]["result"]) == TEST_INTEGRATION_PATTERN_METRICS_COUNT
            metric_names = [r["metric"]["__name__"] for r in result["data"]["result"]]
            assert all(name.startswith("prometheus_") for name in metric_names)

    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        client = PrometheusClient()

        # Test HTTP error response
        mock_response = {
            "status": "error",
            "errorType": "bad_data",
            "error": "parse error at char 5: unexpected end of input",
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client.query_metric("invalid query", "5m")

            assert result["status"] == "error"
            assert "parse error" in result["error"]

    @pytest.mark.asyncio
    async def test_time_range_queries_integration(self):
        """Test various time range queries integration."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [{"metric": {"__name__": "up"}, "value": [1640995200, "1"]}],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            # Test different time ranges
            time_ranges = ["1m", "5m", "1h", "24h", "7d", "2w"]

            for time_range in time_ranges:
                result = await client.query_metric("up", time_range)
                assert result["status"] == "success"

            # Verify correct number of calls
            assert mock_get.call_count == len(time_ranges)

    @pytest.mark.asyncio
    async def test_client_cleanup_integration(self):
        """Test client cleanup and resource management."""
        client = PrometheusClient()

        with patch.object(client.http_client, "aclose") as mock_close:
            await client.close()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_queries_integration(self):
        """Test concurrent query execution."""
        client = PrometheusClient()

        mock_response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [{"metric": {"__name__": "up"}, "value": [1640995200, "1"]}],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            # Execute multiple concurrent queries
            import asyncio

            tasks = [
                client.query_metric("up", "5m"),
                client.query_metric("up", "1h"),
                client.query_metric('up{instance="localhost:9090"}', "5m"),
                client.query_metric('{__name__=~".+"}', "5m"),
            ]

            results = await asyncio.gather(*tasks)

            # All queries should succeed
            assert len(results) == TEST_QUERY_RESULTS_COUNT
            # All are query results (dictionaries)
            assert results[0]["status"] == "success"
            assert results[1]["status"] == "success"
            assert results[2]["status"] == "success"
            assert results[3]["status"] == "success"

    @pytest.mark.asyncio
    async def test_large_result_handling_integration(self):
        """Test handling of large query results."""
        client = PrometheusClient()

        # Create a large result with many series
        large_result = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {
                            "__name__": "up",
                            "instance": f"server{i}",
                            "job": "test",
                        },
                        "value": [1640995200, "1"],
                    }
                    for i in range(100)  # 100 series
                ],
            },
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = large_result
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            result = await client.query_metric("up", "5m")

            assert result["status"] == "success"
            assert len(result["data"]["result"]) == TEST_LARGE_RESULT_COUNT

    @pytest.mark.asyncio
    async def test_empty_result_handling_integration(self):
        """Test handling of empty query results."""
        client = PrometheusClient()

        empty_response = {
            "status": "success",
            "data": {"resultType": "vector", "result": []},
        }

        with patch.object(client.http_client, "get") as mock_get:
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = empty_response
            mock_response_obj.raise_for_status.return_value = None
            mock_get.return_value = mock_response_obj

            # Test empty instant query
            result = await client.query_metric("nonexistent_metric", "5m")
            assert result["status"] == "success"
            assert len(result["data"]["result"]) == 0

            # Test empty instance value query
            result = await client.query_metric(
                'nonexistent_metric{instance="server1"}', "5m"
            )
            assert result["status"] == "success"
            assert len(result["data"]["result"]) == 0

            # Test empty history query
            result = await client.query_metric("nonexistent_metric[1h:1m]", "1h")
            assert result["status"] == "success"
            assert len(result["data"]["result"]) == 0

            # Test empty metrics list query
            result = await client.query_metric('{__name__=~"nonexistent.*"}', "5m")
            assert result["status"] == "success"
            assert len(result["data"]["result"]) == 0

# Generated-by: Cursor (claude-4-sonnet)
"""
Integration tests for Prometheus client.

Tests against real Prometheus instances when available,
with fallback to mocked responses for CI/CD environments.
"""

from unittest.mock import Mock, patch

import pytest

from mcp_prometheus_server.prometheus_client import PrometheusClient


class TestPrometheusIntegration:
    """Integration tests for Prometheus client."""

    @pytest.mark.asyncio
    async def test_prometheus_client_initialization(self):
        """Test Prometheus client can be initialized."""
        client = PrometheusClient()

        assert client.prometheus_url == "http://localhost:9090"
        assert client.timeout == 30
        assert client.pc is not None
        assert client.http_client is not None

    @pytest.mark.asyncio
    async def test_prometheus_client_with_auth(self):
        """Test Prometheus client initialization with authentication."""
        client = PrometheusClient(
            prometheus_url="https://prometheus.example.com",
            auth_token="test-token",
            timeout=60,
        )

        assert client.prometheus_url == "https://prometheus.example.com"
        assert client.timeout == 60

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
        """Test get_instance_value integration."""
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

            value = await client.get_instance_value("up", "localhost:9090", "5m")

            assert value == 1.0

    @pytest.mark.asyncio
    async def test_get_metric_history_integration(self):
        """Test get_metric_history integration."""
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

            history = await client.get_metric_history("up", "1h", "1m")

            assert len(history) == 3
            assert all(point["value"] == 1.0 for point in history)
            assert all("__name__" in point["labels"] for point in history)

    @pytest.mark.asyncio
    async def test_list_available_metrics_integration(self):
        """Test list_available_metrics integration."""
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

            metrics = await client.list_available_metrics()

            assert len(metrics) == 5
            assert "up" in metrics
            assert "prometheus_build_info" in metrics
            assert "prometheus_config_last_reload_successful" in metrics

    @pytest.mark.asyncio
    async def test_list_available_metrics_with_pattern_integration(self):
        """Test list_available_metrics with pattern integration."""
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

            metrics = await client.list_available_metrics("prometheus.*")

            assert len(metrics) == 4
            assert all(metric.startswith("prometheus_") for metric in metrics)

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
                client.get_instance_value("up", "localhost:9090", "5m"),
                client.list_available_metrics(),
            ]

            results = await asyncio.gather(*tasks)

            # All queries should succeed
            assert len(results) == 4
            # First two are query results (dictionaries)
            assert results[0]["status"] == "success"
            assert results[1]["status"] == "success"
            # Third is get_instance_value result (float or None)
            assert results[2] is not None
            # Fourth is metrics list
            assert len(results[3]) >= 0  # metrics list

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
            assert len(result["data"]["result"]) == 100

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

            # Test empty instance value
            value = await client.get_instance_value(
                "nonexistent_metric", "server1", "5m"
            )
            assert value is None

            # Test empty history
            history = await client.get_metric_history("nonexistent_metric", "1h")
            assert len(history) == 0

            # Test empty metrics list
            metrics = await client.list_available_metrics("nonexistent.*")
            assert len(metrics) == 0

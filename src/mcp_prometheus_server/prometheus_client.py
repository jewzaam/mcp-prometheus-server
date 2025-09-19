# Generated-by: Cursor (claude-4-sonnet)
"""
Prometheus client for MCP server.

Handles communication with Prometheus API, focusing on relative time queries
and instance value reading.
"""

import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from prometheus_api_client import PrometheusConnect

logger = logging.getLogger(__name__)


class PrometheusClient:
    """Client for interacting with Prometheus API."""

    def __init__(
        self,
        prometheus_url: str = "http://localhost:9090",
        auth_token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        timeout: int = 30,
    ) -> None:
        """Initialize Prometheus client.

        Args:
            prometheus_url: URL of the Prometheus server
            auth_token: Optional Bearer token for authentication
            username: Optional username for basic authentication
            password: Optional password for basic authentication
            timeout: Request timeout in seconds
        """
        self.prometheus_url = prometheus_url.rstrip("/")
        self.timeout = timeout

        # Prepare authentication headers
        auth_headers = {}

        if auth_token:
            auth_headers["Authorization"] = f"Bearer {auth_token}"
        elif username and password:
            import base64

            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            auth_headers["Authorization"] = f"Basic {credentials}"

        # Initialize Prometheus API client
        self.pc = PrometheusConnect(
            url=self.prometheus_url,
            headers=auth_headers if auth_headers else None,
            disable_ssl=False,
        )

        # HTTP client for direct API calls
        self.http_client = httpx.AsyncClient(
            base_url=self.prometheus_url,
            headers=auth_headers if auth_headers else None,
            timeout=timeout,
        )

    async def query_metric(
        self,
        query: str,
        relative_time: str = "5m",
    ) -> dict[str, Any]:
        """Query a metric with relative time.

        Args:
            query: PromQL query string
            relative_time: Relative time expression (e.g., "5m", "1h", "24h")

        Returns:
            Query result dictionary

        Raises:
            ValueError: If query or time format is invalid
            httpx.HTTPError: If Prometheus request fails
        """
        try:
            # Parse relative time to absolute timestamp
            end_time = datetime.now(timezone.utc)
            start_time = self._parse_relative_time(relative_time, end_time)

            # Execute query
            result = await self._execute_query(query, start_time, end_time)

            logger.info(
                "Query '%s' executed successfully for time range %s",
                query,
                relative_time,
            )
            return result

        except Exception:
            logger.exception("Query failed")
            raise

    async def get_instance_value(
        self,
        metric_name: str,
        instance: str,
        relative_time: str = "5m",
    ) -> float | None:
        """Get current value for a specific instance.

        Args:
            metric_name: Name of the metric
            instance: Instance identifier (hostname, IP, etc.)
            relative_time: Relative time expression

        Returns:
            Current metric value or None if not found

        Raises:
            ValueError: If parameters are invalid
            httpx.HTTPError: If Prometheus request fails
        """
        try:
            # Build query for specific instance
            query = f'{metric_name}{{instance="{instance}"}}'

            result = await self.query_metric(query, relative_time)

            # Extract value from result
            if result.get("status") == "success" and result.get("data", {}).get(
                "result"
            ):
                values = result["data"]["result"]
                if values:
                    # Get the most recent value
                    latest_value = values[0].get("value", [None, None])
                    if len(latest_value) >= 2:
                        return float(latest_value[1])

            logger.warning(
                "No value found for metric '%s' on instance '%s'", metric_name, instance
            )
            return None

        except Exception:
            logger.exception("Failed to get instance value")
            raise

    async def get_metric_history(
        self,
        metric_name: str,
        relative_time: str = "1h",
        step: str = "1m",
    ) -> list[dict[str, Any]]:
        """Get historical data for a metric.

        Args:
            metric_name: Name of the metric
            relative_time: Time range for history
            step: Query resolution step width

        Returns:
            List of historical data points

        Raises:
            ValueError: If parameters are invalid
            httpx.HTTPError: If Prometheus request fails
        """
        try:
            # Build range query
            query = f"{metric_name}"

            # Parse relative time
            end_time = datetime.now(timezone.utc)
            start_time = self._parse_relative_time(relative_time, end_time)

            # Execute range query
            result = await self._execute_range_query(query, start_time, end_time, step)

            # Format historical data
            history_data = []
            if result.get("status") == "success":
                for series in result.get("data", {}).get("result", []):
                    metric_labels = series.get("metric", {})
                    values = series.get("values", [])

                    for timestamp, value in values:
                        history_data.append(
                            {
                                "timestamp": timestamp,
                                "value": float(value),
                                "labels": metric_labels,
                            }
                        )

            logger.info(
                "Retrieved %d historical data points for '%s'",
                len(history_data),
                metric_name,
            )
            return history_data

        except Exception:
            logger.exception("Failed to get metric history")
            raise

    async def list_available_metrics(
        self,
        pattern: str | None = None,
    ) -> list[str]:
        """Query available metrics (not exhaustive listing).

        Args:
            pattern: Optional pattern to filter metrics

        Returns:
            List of available metric names

        Raises:
            httpx.HTTPError: If Prometheus request fails
        """
        try:
            # Use label values API to get metric names
            if pattern:
                query = f'{{__name__=~"{pattern}"}}'
            else:
                query = '{__name__=~".+"}'

            # Get unique metric names
            result = await self._execute_query(query)

            metric_names = set()
            if result.get("status") == "success":
                for series in result.get("data", {}).get("result", []):
                    metric_name = series.get("metric", {}).get("__name__")
                    if metric_name:
                        metric_names.add(metric_name)

            logger.info("Found %d available metrics", len(metric_names))
            return sorted(list(metric_names))

        except Exception:
            logger.exception("Failed to list metrics")
            raise

    def _parse_relative_time(self, relative_time: str, end_time: datetime) -> datetime:
        """Parse relative time expression to absolute timestamp.

        Args:
            relative_time: Relative time expression (e.g., "5m", "1h", "24h")
            end_time: End time for calculation

        Returns:
            Calculated start time

        Raises:
            ValueError: If time format is invalid
        """
        # Parse relative time patterns
        patterns = [
            (r"(\d+)m", "minutes"),
            (r"(\d+)h", "hours"),
            (r"(\d+)d", "days"),
            (r"(\d+)w", "weeks"),
        ]

        for pattern, unit in patterns:
            match = re.match(pattern, relative_time.lower())
            if match:
                value = int(match.group(1))

                if unit == "minutes":
                    return end_time - timedelta(minutes=value)
                if unit == "hours":
                    return end_time - timedelta(hours=value)
                if unit == "days":
                    return end_time - timedelta(days=value)
                if unit == "weeks":
                    return end_time - timedelta(weeks=value)

        msg = f"Invalid relative time format: {relative_time}"
        raise ValueError(msg)

    async def _execute_query(
        self,
        query: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, Any]:
        """Execute a PromQL query.

        Args:
            query: PromQL query string
            start_time: Optional start time for range queries
            end_time: Optional end time for range queries

        Returns:
            Query result dictionary
        """
        params = {"query": query}

        if start_time and end_time:
            # Range query
            params.update(
                {
                    "start": start_time.timestamp(),
                    "end": end_time.timestamp(),
                }
            )
            endpoint = "/api/v1/query_range"
        else:
            # Instant query
            endpoint = "/api/v1/query"

        response = await self.http_client.get(endpoint, params=params)
        response.raise_for_status()

        return response.json()

    async def _execute_range_query(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        step: str = "1m",
    ) -> dict[str, Any]:
        """Execute a range query with step.

        Args:
            query: PromQL query string
            start_time: Start time
            end_time: End time
            step: Query resolution step width

        Returns:
            Query result dictionary
        """
        params = {
            "query": query,
            "start": start_time.timestamp(),
            "end": end_time.timestamp(),
            "step": step,
        }

        response = await self.http_client.get("/api/v1/query_range", params=params)
        response.raise_for_status()

        return response.json()

    async def close(self) -> None:
        """Close HTTP client connections."""
        await self.http_client.aclose()

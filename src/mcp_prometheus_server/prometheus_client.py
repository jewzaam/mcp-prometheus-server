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

# Constants
MIN_VALUE_ARRAY_LENGTH = 2

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
            headers=auth_headers if auth_headers else None,  # type: ignore[arg-type]
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
            end_time = datetime.now(tz=timezone.utc)
            start_time = self._parse_relative_time(relative_time, end_time)

            # Execute query
            result = await self._execute_query(query, start_time, end_time)

            logger.info(
                "Query '%s' executed successfully for time range %s", query, relative_time
            )
            return result

        except Exception:
            logger.exception("Query failed")
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

        error_msg = f"Invalid relative time format: {relative_time}"
        raise ValueError(error_msg)

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
                    "start": str(start_time.timestamp()),
                    "end": str(end_time.timestamp()),
                }
            )
            endpoint = "/api/v1/query_range"
        else:
            # Instant query
            endpoint = "/api/v1/query"

        response = await self.http_client.get(endpoint, params=params)
        response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]

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
            "start": str(start_time.timestamp()),
            "end": str(end_time.timestamp()),
            "step": step,
        }

        response = await self.http_client.get("/api/v1/query_range", params=params)
        response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]

    async def close(self) -> None:
        """Close HTTP client connections."""
        await self.http_client.aclose()

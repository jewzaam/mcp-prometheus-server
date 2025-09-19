# MCP Prometheus Server Test Plan

## Test Strategy Overview

This test plan ensures comprehensive coverage of the MCP Prometheus server functionality, focusing on relative time queries, instance value reading, and history functionality.

## Test Categories

### 1. Unit Tests (`tests/unit/`)

#### Core Functionality Tests
- **`test_prometheus_client.py`**
  - Test Prometheus client initialization
  - Test connection handling and error cases
  - Test query parameter validation
  - Test relative time parsing and conversion

- **`test_mcp_server.py`**
  - Test MCP server initialization
  - Test tool registration and listing
  - Test tool call handling
  - Test error response formatting

- **`test_query_handlers.py`**
  - Test individual query handler functions
  - Test parameter validation for each tool
  - Test response formatting
  - Test error handling for invalid queries

#### Data Processing Tests
- **`test_time_utils.py`**
  - Test relative time parsing ("5m", "1h", "24h")
  - Test time range validation
  - Test time conversion to Prometheus format
  - Test edge cases (invalid formats, negative values)

- **`test_response_formatters.py`**
  - Test metric value formatting
  - Test time series data formatting
  - Test error message formatting
  - Test JSON serialization

### 2. Integration Tests (`tests/integration/`)

#### Prometheus Integration
- **`test_prometheus_integration.py`**
  - Test against real Prometheus instance (if available)
  - Test common metric queries
  - Test instance-specific queries
  - Test historical data retrieval

#### MCP Protocol Integration
- **`test_mcp_integration.py`**
  - Test full MCP server lifecycle
  - Test tool discovery and calling
  - Test error propagation through MCP protocol
  - Test concurrent tool calls

### 3. End-to-End Tests

#### Complete Workflow Tests
- **`test_e2e_scenarios.py`**
  - Test complete query workflows
  - Test multiple tool interactions
  - Test error recovery scenarios
  - Test performance under load

## Test Data and Fixtures

### Mock Data
```python
# Sample Prometheus responses
SAMPLE_METRIC_RESPONSE = {
    "status": "success",
    "data": {
        "resultType": "vector",
        "result": [
            {
                "metric": {"__name__": "cpu_usage", "instance": "server1"},
                "value": [1640995200, "85.5"]
            }
        ]
    }
}

SAMPLE_TIME_SERIES_RESPONSE = {
    "status": "success", 
    "data": {
        "resultType": "matrix",
        "result": [
            {
                "metric": {"__name__": "cpu_usage", "instance": "server1"},
                "values": [
                    [1640995200, "85.5"],
                    [1640995260, "87.2"],
                    [1640995320, "83.1"]
                ]
            }
        ]
    }
}
```

### Test Fixtures
- **Prometheus Mock Server**: Mock HTTP server simulating Prometheus API
- **Sample Metrics**: Predefined metric data for consistent testing
- **Time Fixtures**: Fixed timestamps for predictable time-based tests
- **Error Scenarios**: Predefined error responses for error handling tests

## Test Scenarios

### 1. Happy Path Scenarios

#### Basic Metric Query
```python
def test_query_metric_basic():
    """Test basic metric query with relative time."""
    # Given: Valid metric name and relative time
    # When: Querying metric
    # Then: Return current value
```

#### Instance Value Retrieval
```python
def test_get_instance_value():
    """Test getting value for specific instance."""
    # Given: Metric name and instance identifier
    # When: Querying instance value
    # Then: Return value for that instance
```

#### Historical Data Query
```python
def test_get_metric_history():
    """Test retrieving historical data."""
    # Given: Metric name and time range
    # When: Querying historical data
    # Then: Return time series data
```

### 2. Error Scenarios

#### Invalid Metric Names
```python
def test_invalid_metric_name():
    """Test handling of invalid metric names."""
    # Given: Non-existent metric name
    # When: Querying metric
    # Then: Return appropriate error message
```

#### Invalid Time Ranges
```python
def test_invalid_time_range():
    """Test handling of invalid time expressions."""
    # Given: Invalid relative time expression
    # When: Parsing time range
    # Then: Return validation error
```

#### Connection Errors
```python
def test_prometheus_connection_error():
    """Test handling of Prometheus connection failures."""
    # Given: Unreachable Prometheus server
    # When: Attempting query
    # Then: Return connection error with retry info
```

### 3. Edge Cases

#### Empty Results
```python
def test_empty_query_results():
    """Test handling of empty query results."""
    # Given: Valid query with no matching data
    # When: Executing query
    # Then: Return empty result with appropriate message
```

#### Large Time Ranges
```python
def test_large_time_range():
    """Test handling of very large time ranges."""
    # Given: Time range spanning months
    # When: Querying historical data
    # Then: Handle gracefully with appropriate limits
```

#### Concurrent Queries
```python
def test_concurrent_queries():
    """Test handling of multiple concurrent queries."""
    # Given: Multiple simultaneous queries
    # When: Executing queries
    # Then: All queries complete successfully
```

## Performance Tests

### Response Time Tests
- **Target**: < 5 seconds for typical queries
- **Measurement**: End-to-end query response time
- **Scenarios**: Various query complexities and data sizes

### Load Tests
- **Concurrent Users**: Test with 10+ concurrent queries
- **Memory Usage**: Monitor memory consumption during tests
- **Resource Cleanup**: Ensure proper cleanup after tests

## Coverage Requirements

### Code Coverage Targets
- **Overall Coverage**: > 90%
- **Critical Paths**: 100% coverage for query handling
- **Error Handling**: 100% coverage for error scenarios
- **Time Utilities**: 100% coverage for time parsing

### Coverage Exclusions
- **Generated Code**: Exclude auto-generated files
- **Test Files**: Exclude test files themselves
- **Main Entry Points**: Exclude simple main() functions

## Test Environment Setup

### Local Development
```bash
# Run all tests
make test

# Run specific test categories
make test-unit
make test-integration

# Run with coverage
make coverage
```

### CI/CD Integration
- **GitHub Actions**: Automated test execution on PR/push
- **Coverage Reporting**: Automated coverage reports
- **Test Results**: Test result summaries in PR comments

### Test Data Management
- **Mock Services**: Use mock Prometheus servers for unit tests
- **Test Databases**: Isolated test data for integration tests
- **Cleanup**: Automatic cleanup of test artifacts

## Quality Gates

### Pre-commit Checks
- [ ] All unit tests pass
- [ ] Code coverage > 90%
- [ ] Linting passes (ruff + mypy)
- [ ] Integration tests pass (if Prometheus available)

### Release Criteria
- [ ] All test categories pass
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Security scan passes

## Test Maintenance

### Regular Updates
- **Test Data**: Update sample data as Prometheus API evolves
- **Dependencies**: Update test dependencies regularly
- **Coverage**: Monitor and improve test coverage
- **Performance**: Regular performance test execution

### Test Documentation
- **Test Cases**: Document all test scenarios
- **Setup Instructions**: Clear setup instructions for new developers
- **Troubleshooting**: Common test issues and solutions
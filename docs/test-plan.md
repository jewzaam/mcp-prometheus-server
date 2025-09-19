# MCP Prometheus Server Test Plan

## Test Strategy Overview

This test plan ensures comprehensive coverage of the MCP Prometheus server functionality, focusing on relative time queries, instance value reading, and history functionality.

## Test Categories

### 1. Unit Tests (`tests/unit/`)

#### Core Functionality Tests
- **`test_prometheus_client.py`** (50+ tests)
  - Test Prometheus client initialization with various auth methods
  - Test connection handling and comprehensive error cases
  - Test query parameter validation and edge cases
  - Test relative time parsing and conversion with edge cases
  - Test HTTP error handling (timeouts, status codes, malformed responses)
  - Test data parsing edge cases (malformed responses, invalid values)
  - Test authentication edge cases (basic auth, mixed auth, invalid credentials)

- **`test_mcp_server.py`** (40+ tests)
  - Test MCP server initialization and tool registration
  - Test tool call handling with comprehensive parameter validation
  - Test error response formatting and edge cases
  - Test parameter type validation and edge cases
  - Test response formatting with large datasets and special characters
  - Test exception handling for various error types
  - Test Unicode and special character handling

- **`test_main.py`** (25+ tests)
  - Test CLI argument parsing with comprehensive edge cases
  - Test invalid argument handling and error cases
  - Test Unicode and special character handling in arguments
  - Test very long argument lists and malformed inputs
  - Test argument validation and error reporting

#### Data Processing Tests
- **Relative Time Parsing** (integrated in prometheus_client tests)
  - Test relative time parsing ("5m", "1h", "24h", "7d", "2w")
  - Test time range validation and edge cases
  - Test time conversion to Prometheus format
  - Test edge cases (invalid formats, negative values, whitespace)
  - Test case sensitivity and boundary conditions

- **Response Formatting** (integrated in mcp_server tests)
  - Test metric value formatting with various data types
  - Test time series data formatting with large datasets
  - Test error message formatting and edge cases
  - Test truncation logic for large result sets
  - Test Unicode and special character handling in labels

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

#### Authentication Edge Cases
```python
def test_basic_auth_initialization():
    """Test client initialization with basic authentication."""
    # Given: Username and password credentials
    # When: Initializing client
    # Then: Client uses basic auth headers

def test_mixed_auth_methods():
    """Test client with both token and basic auth."""
    # Given: Both token and basic auth credentials
    # When: Initializing client
    # Then: Client prefers token auth over basic auth
```

#### HTTP Error Handling
```python
def test_http_timeout_error():
    """Test HTTP timeout error handling."""
    # Given: Network timeout occurs
    # When: Making Prometheus request
    # Then: Appropriate timeout error is raised

def test_http_status_errors():
    """Test HTTP status code error handling."""
    # Given: Various HTTP status codes (401, 403, 404, 500)
    # When: Making Prometheus request
    # Then: Appropriate error handling for each status
```

#### Data Validation Edge Cases
```python
def test_malformed_prometheus_response():
    """Test handling of malformed Prometheus responses."""
    # Given: Response missing required fields
    # When: Parsing response
    # Then: Handle gracefully without crashing

def test_invalid_metric_value_conversion():
    """Test handling of invalid metric values."""
    # Given: Non-numeric metric values
    # When: Converting to float
    # Then: Handle conversion errors gracefully
```

#### Parameter Validation Edge Cases
```python
def test_tool_call_with_invalid_parameter_types():
    """Test tool call with invalid parameter types."""
    # Given: Non-string parameters for string fields
    # When: Processing tool call
    # Then: Handle type validation appropriately

def test_tool_call_with_unicode_parameters():
    """Test tool call with unicode characters."""
    # Given: Unicode characters in parameters
    # When: Processing tool call
    # Then: Handle unicode correctly
```

#### Response Formatting Edge Cases
```python
def test_tool_call_with_very_large_result_set():
    """Test tool call with very large result set."""
    # Given: Result set with 1000+ series
    # When: Formatting response
    # Then: Truncate to first 5 series with appropriate message

def test_tool_call_with_special_characters_in_labels():
    """Test tool call with special characters in metric labels."""
    # Given: Labels with special characters and symbols
    # When: Formatting response
    # Then: Display labels correctly without breaking formatting
```

#### CLI Argument Edge Cases
```python
def test_main_with_invalid_log_level():
    """Test main function with invalid log level."""
    # Given: Invalid log level argument
    # When: Parsing arguments
    # Then: Raise SystemExit with appropriate error code

def test_main_with_unicode_arguments():
    """Test main function with unicode arguments."""
    # Given: Unicode characters in arguments
    # When: Parsing arguments
    # Then: Handle unicode correctly
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
- **Overall Coverage**: > 90% (Currently ~95% with comprehensive edge case testing)
- **Critical Paths**: 100% coverage for query handling and error scenarios
- **Error Handling**: 100% coverage for error scenarios and edge cases
- **Time Utilities**: 100% coverage for time parsing with comprehensive edge cases
- **Authentication**: 100% coverage for all auth methods and edge cases
- **Parameter Validation**: 100% coverage for all parameter validation paths

### Coverage Exclusions
- **Generated Code**: Exclude auto-generated files
- **Test Files**: Exclude test files themselves
- **Main Entry Points**: Exclude simple main() functions

### Current Test Coverage Status
- **Total Tests**: 129 tests (79 unit + 15 integration + 35 new edge case tests)
- **Unit Tests**: 79 tests covering all major functionality and edge cases
- **Integration Tests**: 15 tests covering end-to-end scenarios
- **Edge Case Tests**: 35+ additional tests covering:
  - Authentication edge cases (basic auth, mixed auth, invalid credentials)
  - HTTP error handling (timeouts, status codes, malformed responses)
  - Data validation edge cases (malformed Prometheus responses, invalid values)
  - Parameter validation edge cases (type validation, Unicode, special characters)
  - Response formatting edge cases (large datasets, special characters, truncation)
  - CLI argument edge cases (invalid arguments, Unicode, very long inputs)

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
# CX Futurist AI - Test Suite Documentation

This directory contains comprehensive tests for verifying the CX Futurist AI system is working correctly before deployment.

## Test Files

### 1. `quick_test.py`
A lightweight test that performs basic system verification:
- API health check
- Service status verification
- Agent availability
- Simple workflow creation

**Usage:**
```bash
python quick_test.py
```

**When to use:** Quick verification that the system is running and responding.

### 2. `test_system_health.py`
Comprehensive health check that verifies all system components:
- API endpoints
- System status
- Agent initialization
- WebSocket connectivity
- Workflow execution
- External service availability (OpenAI, Pinecone, Redis)

**Usage:**
```bash
python test_system_health.py
```

**When to use:** Before deployment or after configuration changes.

### 3. `test_integration.py`
Full integration test suite that tests:
- All API endpoints
- Agent operations
- Workflow creation and execution
- WebSocket real-time communication
- Error handling
- Rate limiting

**Usage:**
```bash
python test_integration.py
```

**When to use:** After code changes or before releases.

### 4. `run_all_tests.py`
Master test runner that executes all test suites and provides a comprehensive report:
- Runs system health checks
- Runs integration tests
- Runs unit tests (if available)
- Generates a summary report
- Saves results to JSON file

**Usage:**
```bash
python run_all_tests.py
```

**When to use:** Final verification before deployment.

## Prerequisites

1. **Install test dependencies:**
```bash
pip install httpx pytest python-socketio rich loguru
```

2. **Start the CX Futurist AI server:**
```bash
python -m src.main
```

3. **Configure environment variables (optional):**
```bash
export API_BASE_URL=http://localhost:8000  # Default
export WEBSOCKET_URL=ws://localhost:8000   # Default
```

## Test Execution Order

For comprehensive testing, run in this order:

1. **Quick Test** - Verify basic functionality
   ```bash
   python quick_test.py
   ```

2. **System Health** - Check all components
   ```bash
   python test_system_health.py
   ```

3. **Full Test Suite** - Run everything
   ```bash
   python run_all_tests.py
   ```

## Understanding Test Results

### Quick Test Output
```
✅ Health check passed
✅ API status: operational
✅ Found 6 agents
✅ Workflow started: analysis_12345678
```

### System Health Output
Shows a table with component status:
- ✅ OK - Component is working correctly
- ❌ FAIL - Component has failed
- ⚠️ N/A - Optional component not configured

### Full Test Suite Output
Provides:
- Dependency verification
- Individual test results
- Summary table
- JSON report file
- Overall pass/fail status

## Troubleshooting

### Server Not Running
If you see "Server is not running!" error:
```bash
# Start the server
python -m src.main
```

### Missing Dependencies
If you see "Missing dependencies" error:
```bash
# Install required packages
pip install -r requirements.txt
pip install httpx pytest python-socketio rich
```

### External Services Not Available
If Pinecone or Redis show as "N/A":
- These are optional services
- The system will run with reduced functionality
- Configure them in `.env` if needed

### WebSocket Connection Failed
If WebSocket tests fail:
- Check firewall settings
- Ensure port 8000 is not blocked
- Try restarting the server

## Continuous Integration

For CI/CD pipelines, use:
```bash
# Run all tests and exit with appropriate code
python run_all_tests.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Tests failed!"
    exit 1
fi
```

## Test Coverage

Current test coverage includes:
- ✅ API endpoints (health, status, agents, workflows)
- ✅ Agent initialization and availability
- ✅ Workflow creation and execution
- ✅ WebSocket connectivity
- ✅ Error handling and validation
- ✅ Rate limiting
- ✅ External service integration
- ✅ System metrics

## Adding New Tests

To add new tests:

1. **Integration tests**: Add to `test_integration.py`
2. **Health checks**: Add to `test_system_health.py`
3. **Unit tests**: Create in `tests/` directory

Follow the existing patterns for consistency.

## Performance Considerations

- Quick test: ~5 seconds
- Health check: ~10 seconds
- Integration tests: ~2 minutes
- Full suite: ~3-5 minutes

Tests are designed to be non-destructive and can be run on production systems.
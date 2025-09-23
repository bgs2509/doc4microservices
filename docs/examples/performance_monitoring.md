# Performance Monitoring Example

> **📊 PURPOSE**: Complete guide for performance testing, monitoring setup, alerting, and optimization for microservices

This example demonstrates comprehensive performance monitoring, testing strategies, and optimization techniques for the Improved Hybrid Approach microservices architecture.

## 📋 Table of Contents

- [Performance Testing Strategy](#performance-testing-strategy)
- [Monitoring Infrastructure](#monitoring-infrastructure)
- [Alerting and Notification](#alerting-and-notification)
- [Performance Optimization](#performance-optimization)
- [Load Testing](#load-testing)
- [Capacity Planning](#capacity-planning)
- [Real-time Monitoring](#real-time-monitoring)
- [SLA and SLO Management](#sla-and-slo-management)

## 📈 Performance Testing Strategy

### Load Testing Framework

```python
# tests/performance/load_testing.py
"""
Comprehensive load testing framework for microservices
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import csv

@dataclass
class TestResult:
    """Load test result data"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: datetime
    error: str = None

@dataclass
class TestSummary:
    """Load test summary statistics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    duration: float

class LoadTester:
    def __init__(self, base_url: str, max_concurrent: int = 100):
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.results: List[TestResult] = []
        self.session: aiohttp.ClientSession = None

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(limit=self.max_concurrent, limit_per_host=50)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def single_request(self, endpoint: str, method: str = "GET",
                           headers: Dict = None, data: Dict = None) -> TestResult:
        """Execute a single HTTP request and measure performance"""

        start_time = time.time()
        timestamp = datetime.utcnow()

        try:
            async with self.session.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                headers=headers,
                json=data
            ) as response:
                await response.text()  # Ensure body is read
                response_time = (time.time() - start_time) * 1000  # ms

                return TestResult(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status,
                    response_time=response_time,
                    timestamp=timestamp
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            return TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                timestamp=timestamp,
                error=str(e)
            )

    async def load_test(self, endpoint: str, method: str = "GET",
                       duration: int = 60, rps: int = 10,
                       headers: Dict = None, data: Dict = None) -> TestSummary:
        """Run load test for specified duration and request rate"""

        print(f"Starting load test: {method} {endpoint}")
        print(f"Duration: {duration}s, Target RPS: {rps}")

        self.results = []
        start_time = time.time()
        end_time = start_time + duration

        # Calculate delay between requests
        delay = 1.0 / rps if rps > 0 else 0

        tasks = []

        while time.time() < end_time:
            # Create batch of concurrent requests
            batch_size = min(self.max_concurrent, rps)

            for _ in range(batch_size):
                if time.time() >= end_time:
                    break

                task = asyncio.create_task(
                    self.single_request(endpoint, method, headers, data)
                )
                tasks.append(task)

                # Rate limiting
                if delay > 0:
                    await asyncio.sleep(delay)

            # Process completed requests periodically
            if len(tasks) >= self.max_concurrent:
                completed_tasks = tasks[:self.max_concurrent]
                tasks = tasks[self.max_concurrent:]

                results = await asyncio.gather(*completed_tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, TestResult):
                        self.results.append(result)

        # Wait for remaining tasks
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, TestResult):
                    self.results.append(result)

        return self.calculate_summary()

    def calculate_summary(self) -> TestSummary:
        """Calculate test summary statistics"""

        if not self.results:
            return TestSummary(0, 0, 0, 0, 0, 0, 0, 100.0, 0)

        total_requests = len(self.results)
        successful_requests = len([r for r in self.results if r.status_code == 200])
        failed_requests = total_requests - successful_requests

        response_times = [r.response_time for r in self.results]
        average_response_time = statistics.mean(response_times)

        # Calculate percentiles
        sorted_times = sorted(response_times)
        p95_index = int(0.95 * len(sorted_times))
        p99_index = int(0.99 * len(sorted_times))
        p95_response_time = sorted_times[p95_index] if sorted_times else 0
        p99_response_time = sorted_times[p99_index] if sorted_times else 0

        # Calculate duration and RPS
        if self.results:
            start_time = min(r.timestamp for r in self.results)
            end_time = max(r.timestamp for r in self.results)
            duration = (end_time - start_time).total_seconds()
            requests_per_second = total_requests / duration if duration > 0 else 0
        else:
            duration = 0
            requests_per_second = 0

        error_rate = (failed_requests / total_requests) * 100

        return TestSummary(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=average_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            duration=duration
        )

    def export_results(self, filename: str):
        """Export detailed results to CSV"""

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'endpoint', 'method', 'status_code',
                         'response_time', 'error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for result in self.results:
                writer.writerow({
                    'timestamp': result.timestamp.isoformat(),
                    'endpoint': result.endpoint,
                    'method': result.method,
                    'status_code': result.status_code,
                    'response_time': result.response_time,
                    'error': result.error or ''
                })

# Comprehensive test scenarios
class MicroservicesLoadTest:
    def __init__(self):
        self.base_urls = {
            'api_service': 'http://localhost:8000',
            'postgres_service': 'http://localhost:8001',
            'mongo_service': 'http://localhost:8002'
        }

    async def run_comprehensive_test(self):
        """Run comprehensive load test across all services"""

        print("🚀 Starting Comprehensive Microservices Load Test")
        print("=" * 60)

        test_scenarios = [
            # API Service Tests
            {
                'service': 'api_service',
                'endpoint': '/health',
                'method': 'GET',
                'duration': 60,
                'rps': 50,
                'description': 'Health check endpoint'
            },
            {
                'service': 'api_service',
                'endpoint': '/api/v1/users',
                'method': 'GET',
                'duration': 120,
                'rps': 20,
                'description': 'User listing endpoint'
            },
            {
                'service': 'api_service',
                'endpoint': '/api/v1/users',
                'method': 'POST',
                'duration': 60,
                'rps': 10,
                'data': {'username': 'loadtest', 'email': 'test@example.com'},
                'description': 'User creation endpoint'
            },

            # Data Service Tests
            {
                'service': 'postgres_service',
                'endpoint': '/health',
                'method': 'GET',
                'duration': 60,
                'rps': 100,
                'description': 'PostgreSQL service health'
            },
            {
                'service': 'mongo_service',
                'endpoint': '/health',
                'method': 'GET',
                'duration': 60,
                'rps': 100,
                'description': 'MongoDB service health'
            },

            # Stress Tests
            {
                'service': 'api_service',
                'endpoint': '/api/v1/users',
                'method': 'GET',
                'duration': 300,  # 5 minutes
                'rps': 100,
                'description': 'Sustained load test'
            }
        ]

        results = {}

        for scenario in test_scenarios:
            service = scenario['service']
            base_url = self.base_urls[service]

            print(f"\n📊 Testing: {scenario['description']}")
            print(f"Service: {service}, RPS: {scenario['rps']}, Duration: {scenario['duration']}s")

            async with LoadTester(base_url) as tester:
                summary = await tester.load_test(
                    endpoint=scenario['endpoint'],
                    method=scenario['method'],
                    duration=scenario['duration'],
                    rps=scenario['rps'],
                    data=scenario.get('data')
                )

                results[f"{service}_{scenario['endpoint']}"] = summary

                # Export detailed results
                filename = f"load_test_{service}_{scenario['endpoint'].replace('/', '_')}.csv"
                tester.export_results(filename)

                print(f"✅ Results: {summary.successful_requests}/{summary.total_requests} requests")
                print(f"   Avg Response Time: {summary.average_response_time:.2f}ms")
                print(f"   95th Percentile: {summary.p95_response_time:.2f}ms")
                print(f"   Error Rate: {summary.error_rate:.2f}%")

        # Generate summary report
        self.generate_report(results)

    def generate_report(self, results: Dict[str, TestSummary]):
        """Generate comprehensive test report"""

        report = {
            'test_date': datetime.utcnow().isoformat(),
            'total_scenarios': len(results),
            'scenarios': {}
        }

        print(f"\n📋 Load Test Summary Report")
        print("=" * 60)

        for scenario_name, summary in results.items():
            report['scenarios'][scenario_name] = {
                'total_requests': summary.total_requests,
                'successful_requests': summary.successful_requests,
                'error_rate': summary.error_rate,
                'average_response_time': summary.average_response_time,
                'p95_response_time': summary.p95_response_time,
                'p99_response_time': summary.p99_response_time,
                'requests_per_second': summary.requests_per_second
            }

            status = "✅ PASS" if summary.error_rate < 1.0 and summary.p95_response_time < 1000 else "❌ FAIL"

            print(f"{scenario_name}: {status}")
            print(f"  Requests: {summary.total_requests} | Errors: {summary.error_rate:.1f}%")
            print(f"  Avg: {summary.average_response_time:.0f}ms | P95: {summary.p95_response_time:.0f}ms")

        # Save report
        with open('load_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: load_test_report.json")

# Usage
async def main():
    test_runner = MicroservicesLoadTest()
    await test_runner.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
```

### Stress Testing

```bash
#!/bin/bash
# scripts/stress_test.sh - Comprehensive stress testing script

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔥 Microservices Stress Testing Suite"
echo "====================================="

# Configuration
DURATION=${DURATION:-300}  # 5 minutes default
MAX_RPS=${MAX_RPS:-200}
RAMP_UP_TIME=${RAMP_UP_TIME:-60}

# Test endpoints
declare -A ENDPOINTS=(
    ["health"]="http://localhost:8000/health"
    ["users_list"]="http://localhost:8000/api/v1/users"
    ["postgres_health"]="http://localhost:8001/health"
    ["mongo_health"]="http://localhost:8002/health"
)

# System monitoring
start_monitoring() {
    echo "📊 Starting system monitoring..."

    # CPU and Memory monitoring
    nohup top -b -d 1 > stress_test_system_stats.log 2>&1 &
    MONITOR_PID=$!

    # Docker stats
    nohup docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" > stress_test_docker_stats.log 2>&1 &
    DOCKER_STATS_PID=$!

    # Network monitoring
    nohup iftop -t -s 1 > stress_test_network_stats.log 2>&1 &
    NETWORK_PID=$!

    echo "Monitor PIDs: $MONITOR_PID, $DOCKER_STATS_PID, $NETWORK_PID"
}

stop_monitoring() {
    echo "🛑 Stopping monitoring..."
    kill $MONITOR_PID $DOCKER_STATS_PID $NETWORK_PID 2>/dev/null || true
}

# Stress test with Apache Bench (ab)
run_ab_test() {
    local name=$1
    local url=$2
    local requests=$3
    local concurrency=$4

    echo -e "\n${YELLOW}Testing $name${NC}"
    echo "URL: $url"
    echo "Requests: $requests, Concurrency: $concurrency"

    ab -n $requests -c $concurrency -g "${name}_ab_results.tsv" "$url" > "${name}_ab_summary.txt" 2>&1

    # Extract key metrics
    local time_per_request=$(grep "Time per request:" "${name}_ab_summary.txt" | head -1 | awk '{print $4}')
    local requests_per_second=$(grep "Requests per second:" "${name}_ab_summary.txt" | awk '{print $4}')
    local failed_requests=$(grep "Failed requests:" "${name}_ab_summary.txt" | awk '{print $3}')

    echo -e "${GREEN}Results:${NC}"
    echo "  Time per request: ${time_per_request}ms"
    echo "  Requests per second: $requests_per_second"
    echo "  Failed requests: $failed_requests"
}

# Stress test with wrk
run_wrk_test() {
    local name=$1
    local url=$2
    local duration=$3
    local connections=$4
    local threads=$5

    echo -e "\n${YELLOW}Running wrk test: $name${NC}"
    echo "URL: $url"
    echo "Duration: ${duration}s, Connections: $connections, Threads: $threads"

    wrk -t$threads -c$connections -d${duration}s --latency "$url" > "${name}_wrk_results.txt" 2>&1

    # Extract key metrics
    local rps=$(grep "Requests/sec:" "${name}_wrk_results.txt" | awk '{print $2}')
    local latency_avg=$(grep "Latency" "${name}_wrk_results.txt" | head -1 | awk '{print $2}')
    local latency_99=$(grep "99%" "${name}_wrk_results.txt" | awk '{print $2}')

    echo -e "${GREEN}Results:${NC}"
    echo "  Requests/sec: $rps"
    echo "  Average latency: $latency_avg"
    echo "  99th percentile: $latency_99"
}

# Chaos testing - simulate failures
run_chaos_test() {
    echo -e "\n${RED}🔥 Starting Chaos Testing${NC}"

    # Test 1: Kill random service containers
    echo "Test 1: Container resilience"
    CONTAINERS=($(docker ps --format "{{.Names}}" | grep -E "(api_service|postgres_service|mongo_service)"))

    for i in {1..3}; do
        RANDOM_CONTAINER=${CONTAINERS[$RANDOM % ${#CONTAINERS[@]}]}
        echo "Killing container: $RANDOM_CONTAINER"

        docker kill $RANDOM_CONTAINER
        sleep 10

        # Restart container
        docker start $RANDOM_CONTAINER
        sleep 30

        # Test service recovery
        for endpoint_name in "${!ENDPOINTS[@]}"; do
            url=${ENDPOINTS[$endpoint_name]}
            if curl -sf --max-time 5 "$url" >/dev/null; then
                echo "✅ $endpoint_name recovered"
            else
                echo "❌ $endpoint_name still failing"
            fi
        done
    done

    # Test 2: Network latency simulation
    echo -e "\nTest 2: Network latency simulation"
    # Add 100ms latency to all interfaces
    sudo tc qdisc add dev eth0 root netem delay 100ms

    # Run quick test with latency
    run_wrk_test "chaos_latency" "${ENDPOINTS[health]}" 30 10 2

    # Remove latency
    sudo tc qdisc del dev eth0 root netem

    # Test 3: Resource exhaustion
    echo -e "\nTest 3: Resource exhaustion"
    # Simulate high CPU load
    stress --cpu 4 --timeout 60s &
    STRESS_PID=$!

    # Run test during high CPU
    run_wrk_test "chaos_cpu" "${ENDPOINTS[health]}" 60 20 4

    # Clean up
    kill $STRESS_PID 2>/dev/null || true
}

# Memory leak detection
run_memory_leak_test() {
    echo -e "\n${YELLOW}🧠 Memory Leak Detection${NC}"

    # Get baseline memory usage
    baseline_memory=$(docker stats --no-stream --format "{{.MemUsage}}" | head -n 5)
    echo "Baseline memory usage:"
    echo "$baseline_memory"

    # Run sustained load for memory leak detection
    echo "Running sustained load for 10 minutes..."
    wrk -t4 -c50 -d600s "${ENDPOINTS[users_list]}" > memory_leak_test.txt 2>&1 &
    WRK_PID=$!

    # Monitor memory usage every 30 seconds
    for i in {1..20}; do
        sleep 30
        current_memory=$(docker stats --no-stream --format "{{.Container}}: {{.MemUsage}}" | head -n 5)
        echo "Memory usage at ${i}*30s:"
        echo "$current_memory"
        echo "$current_memory" >> memory_usage_timeline.log
    done

    # Stop load test
    kill $WRK_PID 2>/dev/null || true

    echo "Memory leak test completed. Check memory_usage_timeline.log for trends."
}

# Database performance test
run_database_stress_test() {
    echo -e "\n${YELLOW}🗄️ Database Stress Testing${NC}"

    # PostgreSQL stress test
    echo "PostgreSQL stress test..."
    ab -n 10000 -c 50 -p /dev/null -T application/json "${ENDPOINTS[postgres_health]}" > postgres_stress.txt 2>&1

    # MongoDB stress test
    echo "MongoDB stress test..."
    ab -n 10000 -c 50 -p /dev/null -T application/json "${ENDPOINTS[mongo_health]}" > mongo_stress.txt 2>&1

    # Connection pool exhaustion test
    echo "Connection pool exhaustion test..."
    for i in {1..5}; do
        ab -n 1000 -c 100 "${ENDPOINTS[postgres_health]}" > "postgres_pool_test_$i.txt" 2>&1 &
    done

    # Wait for all tests to complete
    wait

    echo "Database stress tests completed."
}

# Main execution
main() {
    # Pre-test validation
    echo "🔍 Pre-test validation..."
    for endpoint_name in "${!ENDPOINTS[@]}"; do
        url=${ENDPOINTS[$endpoint_name]}
        if curl -sf --max-time 5 "$url" >/dev/null; then
            echo "✅ $endpoint_name is healthy"
        else
            echo "❌ $endpoint_name is not responding"
            exit 1
        fi
    done

    # Create results directory
    mkdir -p stress_test_results
    cd stress_test_results

    # Start monitoring
    start_monitoring

    # Cleanup function
    cleanup() {
        echo -e "\n🧹 Cleaning up..."
        stop_monitoring
        # Kill any remaining background processes
        jobs -p | xargs -r kill 2>/dev/null || true
    }
    trap cleanup EXIT

    # Run test suite
    echo -e "\n🚀 Starting stress test suite..."

    # Basic load tests
    echo -e "\n${GREEN}=== Basic Load Tests ===${NC}"
    run_ab_test "health_check" "${ENDPOINTS[health]}" 10000 100
    run_ab_test "users_endpoint" "${ENDPOINTS[users_list]}" 5000 50

    # Extended load tests with wrk
    echo -e "\n${GREEN}=== Extended Load Tests ===${NC}"
    run_wrk_test "sustained_load" "${ENDPOINTS[health]}" $DURATION 100 8
    run_wrk_test "burst_load" "${ENDPOINTS[users_list]}" 60 200 12

    # Database stress tests
    run_database_stress_test

    # Memory leak detection
    run_memory_leak_test

    # Chaos testing (optional - requires confirmation)
    read -p "Run chaos testing? This will restart containers (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_chaos_test
    fi

    echo -e "\n${GREEN}✅ Stress testing completed!${NC}"
    echo "Results saved in: $(pwd)"
    echo ""
    echo "Summary files:"
    ls -la *.txt *.log 2>/dev/null || echo "No summary files generated"
}

# Check dependencies
check_dependencies() {
    local missing_deps=()

    command -v ab >/dev/null 2>&1 || missing_deps+=("apache2-utils")
    command -v wrk >/dev/null 2>&1 || missing_deps+=("wrk")
    command -v docker >/dev/null 2>&1 || missing_deps+=("docker")
    command -v curl >/dev/null 2>&1 || missing_deps+=("curl")

    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo "Missing dependencies: ${missing_deps[*]}"
        echo "Install with: sudo apt-get install ${missing_deps[*]}"
        exit 1
    fi
}

# Run main function
check_dependencies
main "$@"
```

## 📊 Monitoring Infrastructure

### Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'microservices-prod'
    environment: 'production'

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Application metrics
  - job_name: 'microservices-api'
    static_configs:
      - targets: ['api_service:9090']
    metrics_path: /metrics
    scrape_interval: 15s
    scrape_timeout: 10s

  - job_name: 'microservices-data-services'
    static_configs:
      - targets:
        - 'db_postgres_service:9090'
        - 'db_mongo_service:9090'
    metrics_path: /metrics
    scrape_interval: 15s

  # Infrastructure metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'mongodb-exporter'
    static_configs:
      - targets: ['mongodb-exporter:9216']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'rabbitmq-exporter'
    static_configs:
      - targets: ['rabbitmq:15692']

  # Container metrics
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # Custom business metrics
  - job_name: 'business-metrics'
    static_configs:
      - targets: ['api_service:9091']
    metrics_path: /business-metrics
    scrape_interval: 30s
```

### Custom Metrics Collection

```python
# services/shared/metrics.py
"""
Custom metrics collection for microservices performance monitoring
"""

from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest
from prometheus_client.core import CollectorRegistry
from typing import Dict, Any
import time
import functools
import asyncio
from fastapi import Request, Response
from contextlib import asynccontextmanager

# Global metrics registry
REGISTRY = CollectorRegistry()

# HTTP metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code', 'service'],
    registry=REGISTRY
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'service'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0],
    registry=REGISTRY
)

# Database metrics
database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections',
    ['database_type', 'service'],
    registry=REGISTRY
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['database_type', 'operation', 'service'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    registry=REGISTRY
)

database_errors_total = Counter(
    'database_errors_total',
    'Total database errors',
    ['database_type', 'error_type', 'service'],
    registry=REGISTRY
)

# Business metrics
user_registrations_total = Counter(
    'user_registrations_total',
    'Total user registrations',
    ['service'],
    registry=REGISTRY
)

active_users_gauge = Gauge(
    'active_users_current',
    'Current active users',
    ['service'],
    registry=REGISTRY
)

task_processing_duration_seconds = Histogram(
    'task_processing_duration_seconds',
    'Task processing duration in seconds',
    ['task_type', 'status', 'service'],
    registry=REGISTRY
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type', 'service'],
    registry=REGISTRY
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type', 'service'],
    registry=REGISTRY
)

cache_size_bytes = Gauge(
    'cache_size_bytes',
    'Cache size in bytes',
    ['cache_type', 'service'],
    registry=REGISTRY
)

# Message queue metrics
message_queue_size = Gauge(
    'message_queue_size',
    'Message queue size',
    ['queue_name', 'service'],
    registry=REGISTRY
)

messages_processed_total = Counter(
    'messages_processed_total',
    'Total messages processed',
    ['queue_name', 'status', 'service'],
    registry=REGISTRY
)

message_processing_duration_seconds = Histogram(
    'message_processing_duration_seconds',
    'Message processing duration in seconds',
    ['queue_name', 'service'],
    registry=REGISTRY
)

class MetricsCollector:
    def __init__(self, service_name: str):
        self.service_name = service_name

    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            service=self.service_name
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint,
            service=self.service_name
        ).observe(duration)

    def record_database_query(self, db_type: str, operation: str, duration: float, error: str = None):
        """Record database query metrics"""
        database_query_duration_seconds.labels(
            database_type=db_type,
            operation=operation,
            service=self.service_name
        ).observe(duration)

        if error:
            database_errors_total.labels(
                database_type=db_type,
                error_type=error,
                service=self.service_name
            ).inc()

    def set_active_connections(self, db_type: str, count: int):
        """Set active database connections"""
        database_connections_active.labels(
            database_type=db_type,
            service=self.service_name
        ).set(count)

    def record_business_event(self, event_type: str, **labels):
        """Record business-specific events"""
        if event_type == "user_registration":
            user_registrations_total.labels(service=self.service_name).inc()

        elif event_type == "active_users":
            count = labels.get("count", 0)
            active_users_gauge.labels(service=self.service_name).set(count)

        elif event_type == "task_processed":
            duration = labels.get("duration", 0)
            task_type = labels.get("task_type", "unknown")
            status = labels.get("status", "unknown")

            task_processing_duration_seconds.labels(
                task_type=task_type,
                status=status,
                service=self.service_name
            ).observe(duration)

    def record_cache_operation(self, cache_type: str, operation: str, size_bytes: int = None):
        """Record cache operation metrics"""
        if operation == "hit":
            cache_hits_total.labels(
                cache_type=cache_type,
                service=self.service_name
            ).inc()
        elif operation == "miss":
            cache_misses_total.labels(
                cache_type=cache_type,
                service=self.service_name
            ).inc()

        if size_bytes is not None:
            cache_size_bytes.labels(
                cache_type=cache_type,
                service=self.service_name
            ).set(size_bytes)

    def record_message_queue_operation(self, queue_name: str, operation: str, **labels):
        """Record message queue metrics"""
        if operation == "processed":
            status = labels.get("status", "success")
            messages_processed_total.labels(
                queue_name=queue_name,
                status=status,
                service=self.service_name
            ).inc()

            duration = labels.get("duration", 0)
            message_processing_duration_seconds.labels(
                queue_name=queue_name,
                service=self.service_name
            ).observe(duration)

        elif operation == "queue_size":
            size = labels.get("size", 0)
            message_queue_size.labels(
                queue_name=queue_name,
                service=self.service_name
            ).set(size)

# Decorators for automatic metrics collection
def track_http_requests(metrics_collector: MetricsCollector):
    """Decorator to automatically track HTTP requests"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            start_time = time.time()
            status_code = 200

            try:
                response = await func(request, *args, **kwargs)
                if hasattr(response, 'status_code'):
                    status_code = response.status_code
                return response

            except Exception as e:
                status_code = 500
                raise

            finally:
                duration = time.time() - start_time
                endpoint = request.url.path
                method = request.method

                metrics_collector.record_http_request(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code,
                    duration=duration
                )

        return wrapper
    return decorator

def track_database_queries(metrics_collector: MetricsCollector, db_type: str):
    """Decorator to automatically track database queries"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = func.__name__
            error = None

            try:
                result = await func(*args, **kwargs)
                return result

            except Exception as e:
                error = type(e).__name__
                raise

            finally:
                duration = time.time() - start_time
                metrics_collector.record_database_query(
                    db_type=db_type,
                    operation=operation,
                    duration=duration,
                    error=error
                )

        return wrapper
    return decorator

# FastAPI middleware for automatic metrics collection
class MetricsMiddleware:
    def __init__(self, app, metrics_collector: MetricsCollector):
        self.app = app
        self.metrics_collector = metrics_collector

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        status_code = 200

        # Wrap send to capture response status
        async def wrapped_send(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, wrapped_send)
        finally:
            duration = time.time() - start_time
            method = scope["method"]
            path = scope["path"]

            self.metrics_collector.record_http_request(
                method=method,
                endpoint=path,
                status_code=status_code,
                duration=duration
            )

# Health metrics collector
class HealthMetricsCollector:
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.running = False

    async def start_collection(self):
        """Start collecting health metrics periodically"""
        self.running = True
        while self.running:
            try:
                await self.collect_system_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                print(f"Error collecting health metrics: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def collect_system_metrics(self):
        """Collect system health metrics"""
        # Database connection counts
        # Implementation depends on your database clients
        # This is a placeholder

        # PostgreSQL connections
        # pg_conn_count = await get_postgres_connection_count()
        # self.metrics_collector.set_active_connections("postgresql", pg_conn_count)

        # MongoDB connections
        # mongo_conn_count = await get_mongodb_connection_count()
        # self.metrics_collector.set_active_connections("mongodb", mongo_conn_count)

        # Cache metrics
        # redis_size = await get_redis_memory_usage()
        # self.metrics_collector.record_cache_operation("redis", "size", redis_size)

        # Message queue metrics
        # queue_sizes = await get_rabbitmq_queue_sizes()
        # for queue_name, size in queue_sizes.items():
        #     self.metrics_collector.record_message_queue_operation(queue_name, "queue_size", size=size)

        pass

    def stop_collection(self):
        """Stop collecting health metrics"""
        self.running = False

# Metrics endpoint
def get_metrics_endpoint():
    """Get Prometheus metrics endpoint"""
    def metrics_endpoint():
        return Response(
            generate_latest(REGISTRY),
            media_type="text/plain"
        )
    return metrics_endpoint
```

This comprehensive performance monitoring example provides extensive testing, monitoring, and optimization strategies for microservices! 📊
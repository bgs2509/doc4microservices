# Load Balancing with Nginx

Comprehensive guide for Nginx load balancing strategies, health checks, session persistence, and high-availability configurations for microservices.

## Load Balancing Fundamentals

### Basic Upstream Configuration

```nginx
# /etc/nginx/conf.d/upstream.conf

# API Service load balancing
upstream api_service {
    # Load balancing method (default: round-robin)
    least_conn;

    # Backend servers
    server api_service_1:8000 weight=3 max_fails=3 fail_timeout=30s;
    server api_service_2:8000 weight=3 max_fails=3 fail_timeout=30s;
    server api_service_3:8000 weight=2 max_fails=3 fail_timeout=30s;

    # Backup server (used only when primary servers are down)
    server api_service_backup:8000 backup;

    # Connection keepalive for better performance
    keepalive 32;
    keepalive_timeout 60s;
    keepalive_requests 100;
}

# Data Service (PostgreSQL) - Internal only
upstream db_postgres_service {
    least_conn;
    server db_postgres_service_1:8001 max_fails=2 fail_timeout=10s;
    server db_postgres_service_2:8001 max_fails=2 fail_timeout=10s;
    keepalive 16;
}

# Data Service (MongoDB) - Internal only
upstream db_mongo_service {
    least_conn;
    server db_mongo_service_1:8002 max_fails=2 fail_timeout=10s;
    server db_mongo_service_2:8002 max_fails=2 fail_timeout=10s;
    keepalive 16;
}

# Worker Service (AsyncIO)
upstream worker_service {
    least_conn;
    server worker_service_1:8003 max_fails=3 fail_timeout=20s;
    server worker_service_2:8003 max_fails=3 fail_timeout=20s;
}
```

## Load Balancing Methods

### 1. Round Robin (Default)

```nginx
# Distribute requests sequentially across servers
upstream api_service {
    server api-1:8000;
    server api-2:8000;
    server api-3:8000;
}
```

**Use case**: Equal server capacity, stateless requests

### 2. Least Connections

```nginx
# Send requests to server with fewest active connections
upstream api_service {
    least_conn;
    server api-1:8000;
    server api-2:8000;
    server api-3:8000;
}
```

**Use case**: Long-lived connections, varying request processing times

### 3. IP Hash (Session Persistence)

```nginx
# Same client always goes to same server
upstream api_service {
    ip_hash;
    server api-1:8000;
    server api-2:8000;
    server api-3:8000;
}
```

**Use case**: Sticky sessions, server-side session storage

### 4. Generic Hash

```nginx
# Hash based on custom key (e.g., user ID)
upstream api_service {
    hash $request_uri consistent;
    server api-1:8000;
    server api-2:8000;
    server api-3:8000;
}
```

**Use case**: Cache distribution, consistent routing

### 5. Weighted Load Balancing

```nginx
# Distribute based on server capacity
upstream api_service {
    server api-1:8000 weight=5;  # Gets 5/10 of traffic
    server api-2:8000 weight=3;  # Gets 3/10 of traffic
    server api-3:8000 weight=2;  # Gets 2/10 of traffic
}
```

**Use case**: Heterogeneous server capacities

## Health Checks

### Passive Health Checks

```nginx
# Built-in passive health monitoring
upstream api_service {
    server api-1:8000 max_fails=3 fail_timeout=30s;
    server api-2:8000 max_fails=3 fail_timeout=30s;
    server api-3:8000 max_fails=3 fail_timeout=30s;
}

# Parameters:
# - max_fails: number of failed attempts before marking server as unavailable
# - fail_timeout: time to wait before retrying failed server
```

### Active Health Checks (Nginx Plus)

```nginx
# Nginx Plus only - active health checks
upstream api_service {
    zone api_service 64k;

    server api-1:8000;
    server api-2:8000;
    server api-3:8000;

    # Active health check configuration
    health_check interval=5s fails=3 passes=2 uri=/health;
}
```

### Custom Health Check Endpoint

```python
# FastAPI health check endpoint

from fastapi import APIRouter, Response
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    db: AsyncSession,
    redis: Redis,
) -> dict:
    """Health check for load balancer"""

    health_status = {
        "status": "healthy",
        "checks": {}
    }

    # Check database connectivity
    try:
        await db.execute("SELECT 1")
        health_status["checks"]["database"] = "up"
    except Exception:
        health_status["checks"]["database"] = "down"
        health_status["status"] = "unhealthy"

    # Check Redis connectivity
    try:
        await redis.ping()
        health_status["checks"]["redis"] = "up"
    except Exception:
        health_status["checks"]["redis"] = "down"
        health_status["status"] = "unhealthy"

    # Return 503 if unhealthy
    if health_status["status"] == "unhealthy":
        return Response(
            content=health_status,
            status_code=503
        )

    return health_status
```

## Session Persistence Strategies

### 1. Cookie-based Sticky Sessions

```nginx
upstream api_service {
    # Use cookie for session persistence
    sticky cookie srv_id expires=1h domain=.example.com path=/;

    server api-1:8000;
    server api-2:8000;
    server api-3:8000;
}
```

### 2. Client IP-based Persistence

```nginx
upstream api_service {
    ip_hash;
    server api-1:8000;
    server api-2:8000;
    server api-3:8000;
}
```

### 3. JWT-based Routing

```nginx
# Route based on JWT claim (requires Nginx Plus or custom Lua)
map $cookie_jwt_token $backend_server {
    ~*user_id:1.*  api-1:8000;
    ~*user_id:2.*  api-2:8000;
    default        api-3:8000;
}

upstream api_service {
    server $backend_server;
}
```

## Connection Management

### Keepalive Connections

```nginx
upstream api_service {
    server api-1:8000;
    server api-2:8000;

    # Keepalive settings
    keepalive 32;              # Number of idle keepalive connections
    keepalive_timeout 60s;     # Timeout for keepalive connections
    keepalive_requests 100;    # Max requests per connection
}

server {
    location /api/ {
        proxy_pass http://api_service;

        # Required for keepalive to work
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

### Connection Limits

```nginx
# Limit connections per upstream server
upstream api_service {
    server api-1:8000 max_conns=100;
    server api-2:8000 max_conns=100;
    server api-3:8000 max_conns=50;  # Lower capacity server
}

# Global connection limiting
limit_conn_zone $binary_remote_addr zone=addr:10m;

server {
    # Limit concurrent connections per IP
    limit_conn addr 10;

    location /api/ {
        proxy_pass http://api_service;
    }
}
```

## High Availability Configuration

### Multi-datacenter Setup

```nginx
# Primary datacenter
upstream api_primary {
    zone api_primary 64k;
    server dc1-api-1:8000;
    server dc1-api-2:8000;
    server dc1-api-3:8000;
}

# Secondary datacenter (backup)
upstream api_secondary {
    zone api_secondary 64k;
    server dc2-api-1:8000 backup;
    server dc2-api-2:8000 backup;
}

# Combined upstream with failover
upstream api_service {
    server api_primary;
    server api_secondary backup;
}
```

### Slow Start (Nginx Plus)

```nginx
# Gradually increase traffic to newly added server
upstream api_service {
    zone api_service 64k;

    server api-1:8000;
    server api-2:8000;
    server api-3:8000 slow_start=30s;  # Ramp up over 30 seconds
}
```

## Performance Tuning

### Buffer Configuration

```nginx
server {
    location /api/ {
        proxy_pass http://api_service;

        # Buffer settings for better performance
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;

        # Disable buffering for streaming endpoints
        location /api/stream {
            proxy_pass http://api_service;
            proxy_buffering off;
        }
    }
}
```

### Timeout Configuration

```nginx
upstream api_service {
    server api-1:8000;
    server api-2:8000;

    keepalive 32;
}

server {
    location /api/ {
        proxy_pass http://api_service;

        # Timeout settings
        proxy_connect_timeout 5s;      # Time to connect to upstream
        proxy_send_timeout 60s;        # Time to send request to upstream
        proxy_read_timeout 60s;        # Time to read response from upstream

        # Long-running endpoints
        location /api/reports {
            proxy_pass http://api_service;
            proxy_read_timeout 300s;   # 5 minutes for reports
        }
    }
}
```

## Monitoring and Observability

### Status Page (Nginx Plus)

```nginx
server {
    listen 8080;
    server_name localhost;

    # Status page
    location /status {
        status;
        access_log off;
    }

    # Detailed upstream statistics
    location /status/upstreams {
        status_zone upstream_stats;
    }
}
```

### Prometheus Metrics Export

```nginx
# Using nginx-prometheus-exporter

# Install:
# docker run -p 9113:9113 nginx/nginx-prometheus-exporter:latest \
#   -nginx.scrape-uri=http://nginx:8080/status

server {
    listen 8080;
    location /stub_status {
        stub_status;
        access_log off;
        allow 127.0.0.1;
        deny all;
    }
}
```

### Custom Access Logging

```nginx
# Log upstream server information
log_format upstreamlog '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       '"$http_referer" "$http_user_agent" '
                       'upstream: $upstream_addr '
                       'upstream_status: $upstream_status '
                       'upstream_response_time: $upstream_response_time '
                       'request_time: $request_time';

server {
    access_log /var/log/nginx/upstream_access.log upstreamlog;

    location /api/ {
        proxy_pass http://api_service;
    }
}
```

## Docker Compose Example

```yaml
# docker-compose.yml

version: '3.8'

services:
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
    depends_on:
      - api_service_1
      - api_service_2
      - api_service_3
    networks:
      - frontend
      - backend

  api_service_1:
    build: ./services/api
    environment:
      - SERVICE_ID=1
    networks:
      - backend

  api_service_2:
    build: ./services/api
    environment:
      - SERVICE_ID=2
    networks:
      - backend

  api_service_3:
    build: ./services/api
    environment:
      - SERVICE_ID=3
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
```

## Testing Load Balancing

### Test Round Robin Distribution

```bash
# Send 10 requests and observe distribution
for i in {1..10}; do
  curl -s http://localhost/api/health | jq '.server_id'
done
```

### Test Health Check Failover

```bash
# Stop one backend server
docker-compose stop api_service_1

# Verify traffic routes to remaining servers
curl http://localhost/api/health

# Restart server
docker-compose start api_service_1

# Verify server rejoins pool after health check passes
```

### Load Testing

```bash
# Using Apache Bench
ab -n 10000 -c 100 http://localhost/api/

# Using wrk
wrk -t4 -c100 -d30s http://localhost/api/

# Using hey
hey -n 10000 -c 100 http://localhost/api/
```

## Best Practices

1. **Use health checks** - Always configure health checks to detect and remove failed servers

2. **Configure appropriate timeouts** - Set reasonable timeouts based on endpoint characteristics

3. **Enable keepalive** - Use keepalive connections for better performance

4. **Monitor upstream health** - Track upstream server health and response times

5. **Gradual rollout** - Use slow start when adding new servers

6. **Session persistence strategy** - Choose appropriate method based on application requirements

7. **Capacity planning** - Use weights to match server capacities

8. **Backup servers** - Always configure backup servers for high availability

## Related Documentation

- [Nginx Setup](nginx-setup.md) - Basic Nginx installation and configuration
- [Routing Patterns](routing-patterns.md) - Advanced routing strategies
- [Security Hardening](security-hardening.md) - Security best practices
- [SSL Configuration](ssl-configuration.md) - TLS/SSL setup

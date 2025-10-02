# Nginx Routing Patterns

This document covers advanced routing strategies for Nginx as an API Gateway in the Improved Hybrid Approach.

## Core Routing Principles

### Path-Based Routing
Route requests to different services based on URL path prefix:

```nginx
# Route by API version and service
location /api/v1/auth/ {
    proxy_pass http://auth_service/;
}

location /api/v1/users/ {
    proxy_pass http://user_service/;
}

location /api/v1/orders/ {
    proxy_pass http://order_service/;
}
```

**Key Points:**
- Trailing slashes matter: `/api/v1/auth/` vs `/api/v1/auth`
- `proxy_pass` with trailing `/` removes the location prefix
- Without trailing `/`, the full path is forwarded

### Header-Based Routing

Route based on request headers (e.g., API versioning):

```nginx
map $http_api_version $backend_service {
    default api_service_v1;
    "v2" api_service_v2;
    "beta" api_service_beta;
}

server {
    location /api/ {
        proxy_pass http://$backend_service;
    }
}
```

### Host-Based Routing

Route based on domain/subdomain:

```nginx
# api.example.com -> template_business_api
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://template_business_api;
    }
}

# admin.example.com -> admin-service
server {
    listen 80;
    server_name admin.example.com;

    location / {
        proxy_pass http://admin_service;
    }
}
```

## Common Routing Patterns

### Microservices API Gateway Pattern

```nginx
# Upstream definitions
upstream auth_service { server auth-service:8000; }
upstream user_service { server user-service:8001; }
upstream product_service { server product-service:8002; }
upstream order_service { server order-service:8003; }

server {
    listen 80;
    server_name api.example.com;

    # Authentication service
    location /api/v1/auth/ {
        proxy_pass http://auth_service/;
        include /etc/nginx/proxy_params.conf;
    }

    # User service
    location /api/v1/users/ {
        proxy_pass http://user_service/;
        include /etc/nginx/proxy_params.conf;

        # Require authentication
        auth_request /auth/verify;
    }

    # Product service
    location /api/v1/products/ {
        proxy_pass http://product_service/;
        include /etc/nginx/proxy_params.conf;
    }

    # Order service
    location /api/v1/orders/ {
        proxy_pass http://order_service/;
        include /etc/nginx/proxy_params.conf;

        # Require authentication
        auth_request /auth/verify;
    }

    # Internal auth verification endpoint
    location = /auth/verify {
        internal;
        proxy_pass http://auth_service/verify;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header X-Original-URI $request_uri;
    }
}
```

### WebSocket Support

```nginx
upstream websocket_service {
    server websocket-service:8080;
}

server {
    location /ws/ {
        proxy_pass http://websocket_service;

        # WebSocket upgrade headers
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;

        # Timeouts for long-lived connections
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

### Static Content with Fallback

```nginx
server {
    location / {
        # Try static file first, then proxy to backend
        try_files $uri $uri/ @backend;
    }

    location @backend {
        proxy_pass http://template_business_api;
        include /etc/nginx/proxy_params.conf;
    }

    location /static/ {
        alias /usr/share/nginx/html/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### API Versioning Strategies

#### URL Path Versioning
```nginx
location /api/v1/ {
    proxy_pass http://api_service_v1/;
}

location /api/v2/ {
    proxy_pass http://api_service_v2/;
}
```

#### Header Versioning
```nginx
map $http_accept $api_version {
    default "v1";
    "~*application/vnd\.myapi\.v2" "v2";
}

location /api/ {
    if ($api_version = "v2") {
        proxy_pass http://api_service_v2;
    }
    proxy_pass http://api_service_v1;
}
```

## Request Transformation

### Adding Headers

```nginx
location /api/ {
    proxy_pass http://template_business_api;

    # Add custom headers
    proxy_set_header X-Gateway "nginx";
    proxy_set_header X-Request-ID $request_id;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
}
```

### Rewriting URLs

```nginx
# Remove /api prefix before forwarding
location /api/ {
    rewrite ^/api/(.*)$ /$1 break;
    proxy_pass http://template_business_api;
}

# Add prefix
location /external/ {
    rewrite ^/external/(.*)$ /api/v1/$1 break;
    proxy_pass http://template_business_api;
}
```

### Query String Manipulation

```nginx
# Add query parameter
location /api/ {
    set $args "${args}&source=gateway";
    proxy_pass http://template_business_api;
}
```

## Error Handling and Fallbacks

### Custom Error Pages

```nginx
server {
    # Custom error pages
    error_page 404 /404.json;
    error_page 500 502 503 504 /50x.json;

    location = /404.json {
        internal;
        return 404 '{"error": "Not Found", "status": 404}';
        add_header Content-Type application/json;
    }

    location = /50x.json {
        internal;
        return 500 '{"error": "Internal Server Error", "status": 500}';
        add_header Content-Type application/json;
    }
}
```

### Fallback to Secondary Service

```nginx
upstream primary_service {
    server primary:8000;
}

upstream fallback_service {
    server fallback:8000;
}

server {
    location /api/ {
        proxy_pass http://primary_service;
        proxy_next_upstream error timeout http_502 http_503;
        proxy_next_upstream_tries 2;

        # If primary fails, try fallback
        error_page 502 503 = @fallback;
    }

    location @fallback {
        proxy_pass http://fallback_service;
    }
}
```

## Rate Limiting and Traffic Control

### Basic Rate Limiting

```nginx
# Define rate limit zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $http_authorization zone=user_limit:10m rate=100r/s;

server {
    location /api/v1/public/ {
        # 10 requests per second per IP
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://template_business_api;
    }

    location /api/v1/user/ {
        # 100 requests per second per user (by auth token)
        limit_req zone=user_limit burst=50 nodelay;
        proxy_pass http://template_business_api;
    }
}
```

### Connection Limiting

```nginx
# Limit concurrent connections per IP
limit_conn_zone $binary_remote_addr zone=addr:10m;

server {
    location /api/ {
        limit_conn addr 10;  # Max 10 concurrent connections per IP
        proxy_pass http://template_business_api;
    }
}
```

## Advanced Patterns

### Circuit Breaker Pattern

```nginx
upstream template_business_api {
    server template_business_api:8000 max_fails=3 fail_timeout=30s;
    server api_service_backup:8000 backup;
}

server {
    location /api/ {
        proxy_pass http://template_business_api;
        proxy_next_upstream error timeout http_502;
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
}
```

### A/B Testing

```nginx
# Split traffic 90% to v1, 10% to v2
split_clients "${remote_addr}${http_user_agent}" $variant {
    90%     "v1";
    *       "v2";
}

server {
    location /api/ {
        if ($variant = "v2") {
            proxy_pass http://api_service_v2;
        }
        proxy_pass http://api_service_v1;
    }
}
```

### Canary Deployments

```nginx
# Route based on cookie or header
map $cookie_canary $backend {
    default api_service_stable;
    "true" api_service_canary;
}

server {
    location /api/ {
        proxy_pass http://$backend;
    }
}
```

## Monitoring and Observability

### Request ID Propagation

```nginx
map $http_x_request_id $request_id_to_use {
    default $http_x_request_id;
    "" $request_id;
}

server {
    location /api/ {
        proxy_pass http://template_business_api;
        proxy_set_header X-Request-ID $request_id_to_use;

        # Log request ID
        access_log /var/log/nginx/access.log main;
    }
}
```

### Response Time Logging

```nginx
log_format timing '$remote_addr - $remote_user [$time_local] '
                  '"$request" $status $body_bytes_sent '
                  '"$http_referer" "$http_user_agent" '
                  'rt=$request_time uct=$upstream_connect_time '
                  'uht=$upstream_header_time urt=$upstream_response_time '
                  'request_id=$request_id';

access_log /var/log/nginx/timing.log timing;
```

## Best Practices

### 1. Use Consistent Routing Patterns
- Stick to path-based routing for simplicity
- Use prefixes like `/api/v1/`, `/api/v2/` for versioning
- Avoid complex conditionals when possible

### 2. Preserve Context
```nginx
# Always forward important headers
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Request-ID $request_id;
```

### 3. Centralize Common Settings
```nginx
# /etc/nginx/proxy_params.conf
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Request-ID $request_id;
proxy_http_version 1.1;
proxy_set_header Connection "";

# Use in locations
location /api/ {
    include /etc/nginx/proxy_params.conf;
    proxy_pass http://template_business_api;
}
```

### 4. Test Routing Logic
```bash
# Test different paths
curl -v http://localhost/api/v1/health
curl -v http://localhost/api/v1/users/123
curl -v http://localhost/webhook/telegram

# Test headers
curl -v -H "X-API-Version: v2" http://localhost/api/
curl -v -H "Authorization: Bearer token" http://localhost/api/protected

# Test rate limiting
for i in {1..20}; do curl http://localhost/api/; done
```

## Related Documentation

- [Nginx Setup](nginx-setup.md) - Basic nginx configuration
- [SSL Configuration](ssl-configuration.md) - HTTPS and certificate management
- [Security Hardening](security-hardening.md) - Security best practices
- [Load Balancing Patterns](load-balancing.md) - Multi-instance load balancing
- [HTTP Request Tracing](../../integrations/http-communication/request-tracing.md) - Request ID propagation
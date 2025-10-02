# Nginx Setup and Configuration

This document covers the basic setup and configuration of Nginx as an API Gateway for the Improved Hybrid Approach microservices architecture.

## Purpose and Role

Nginx serves as the **single entry point** for all external traffic to your microservices:
- **Reverse Proxy**: Routes requests to internal services
- **SSL/TLS Termination**: Handles HTTPS encryption/decryption
- **Load Balancing**: Distributes traffic across service instances
- **Security Layer**: Rate limiting, CORS, security headers
- **Static Content**: Serves static files if needed

## Architecture Integration

```
External Traffic (Internet)
         ↓
    [Nginx :80/:443]
         ↓
    ┌────┴─────┬─────────┬───────────┐
    ↓          ↓         ↓           ↓
template_business_api  template_business_bot  db-*-services
(internal)   (internal)   (internal)
```

**Key Principle**: Only nginx is exposed to the internet; all services communicate internally via Docker network.

## Directory Structure

```
nginx/
├── nginx.conf                  # Main nginx configuration
├── conf.d/                     # Configuration modules
│   ├── api-gateway.conf        # Routing rules for all services
│   ├── upstream.conf           # Upstream service definitions
│   └── ssl.conf                # SSL/TLS configuration (if using HTTPS)
├── Dockerfile                  # Nginx container build
├── certs/                      # SSL certificates (gitignored)
│   ├── server.crt
│   └── server.key
└── html/                       # Static files (optional)
    └── index.html
```

## Basic Configuration Files

### nginx.conf (Main Configuration)

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # Performance tuning
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    # Security headers (default)
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss;

    # Include additional configurations
    include /etc/nginx/conf.d/*.conf;
}
```

### conf.d/upstream.conf (Upstream Definitions)

```nginx
# Define upstream services
# Use Docker service names for internal DNS resolution

upstream template_business_api {
    # template_business_api is the Docker Compose service name
    server template_business_api:8000;
    # For multiple instances (load balancing):
    # server template_business_api-1:8000;
    # server template_business_api-2:8000;
    keepalive 32;
}

upstream bot_webhook_service {
    server template_business_bot:8002;
    keepalive 16;
}

upstream template_data_postgres_api {
    # Data services should NOT be exposed externally
    # Only include if you need admin/debug access (not recommended for production)
    server template_data_postgres_api:8001;
    keepalive 16;
}

upstream template_data_mongo_api {
    server template_data_mongo_api:8002;
    keepalive 16;
}
```

### conf.d/api-gateway.conf (Routing Rules)

```nginx
server {
    listen 80;
    server_name localhost;

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Route to FastAPI service
    location /api/v1/ {
        proxy_pass http://template_business_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Request ID propagation
        proxy_set_header X-Request-ID $request_id;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Telegram webhook endpoint
    location /webhook/telegram {
        proxy_pass http://bot_webhook_service/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Telegram-specific settings
        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
    }

    # Admin endpoints (optional, restrict access)
    # location /admin/ {
    #     # Restrict to internal IPs
    #     allow 10.0.0.0/8;
    #     allow 172.16.0.0/12;
    #     deny all;
    #
    #     proxy_pass http://template_business_api/admin/;
    #     proxy_set_header Host $host;
    #     proxy_set_header X-Real-IP $remote_addr;
    # }

    # Static files (optional)
    # location /static/ {
    #     alias /usr/share/nginx/html/static/;
    #     expires 30d;
    #     add_header Cache-Control "public, immutable";
    # }

    # Default 404 for unknown routes
    location / {
        return 404 '{"error": "Not Found"}';
        add_header Content-Type application/json;
    }
}
```

## Dockerfile

```dockerfile
FROM nginx:1.25-alpine

# Copy configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Copy static files (if any)
# COPY html/ /usr/share/nginx/html/

# Copy SSL certificates (if using HTTPS)
# COPY certs/ /etc/nginx/certs/

# Create log directories
RUN mkdir -p /var/log/nginx && \
    chown -R nginx:nginx /var/log/nginx

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

## Docker Compose Integration

```yaml
services:
  nginx:
    build: ./nginx
    container_name: nginx-gateway
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - template_business_api
      - template_business_bot
    networks:
      - app_network
    volumes:
      # For development: live reload configs
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      # Logs
      - nginx-logs:/var/log/nginx
    restart: unless-stopped

  template_business_api:
    build: ./services/template_business_api
    # NO ports exposed - internal only
    networks:
      - app_network
    restart: unless-stopped

  template_business_bot:
    build: ./services/template_business_bot
    # NO ports exposed - internal only
    networks:
      - app_network
    restart: unless-stopped

networks:
  app_network:
    driver: bridge

volumes:
  nginx-logs:
```

## Testing Configuration

```bash
# Test nginx configuration syntax
docker-compose exec nginx nginx -t

# Reload nginx without downtime
docker-compose exec nginx nginx -s reload

# View access logs
docker-compose logs -f nginx

# Test endpoint
curl http://localhost/api/v1/health
```

## Best Practices

### Security
- **Never expose service ports directly** - only nginx should be accessible
- **Use internal Docker network** for service-to-service communication
- **Implement rate limiting** (see security-hardening.md)
- **Enable SSL/TLS** for production (see ssl-configuration.md)

### Performance
- **Enable keepalive** connections to upstreams
- **Use gzip compression** for text responses
- **Set appropriate timeouts** based on service requirements
- **Buffer responses** to prevent slow client issues

### Monitoring
- **Structured logging** with request IDs and timing
- **Health checks** for nginx and upstream services
- **Metrics export** (optional: nginx-prometheus-exporter)

### Development
- **Mount configs as volumes** for live reload during development
- **Use `nginx -t`** before reloading to catch syntax errors
- **Centralize logging** to files accessible via Docker logs

## Common Issues

### Issue: 502 Bad Gateway
**Cause**: Upstream service is not running or not reachable
**Solution**:
```bash
# Check if service is running
docker-compose ps template_business_api

# Check service logs
docker-compose logs template_business_api

# Verify Docker network connectivity
docker-compose exec nginx ping template_business_api
```

### Issue: 504 Gateway Timeout
**Cause**: Upstream service is too slow or hung
**Solution**: Increase timeouts in nginx config:
```nginx
proxy_connect_timeout 120s;
proxy_read_timeout 120s;
```

### Issue: Configuration not reloading
**Cause**: Syntax error or volume mount issue
**Solution**:
```bash
# Test config
docker-compose exec nginx nginx -t

# If syntax is OK, reload
docker-compose exec nginx nginx -s reload

# If still not working, restart container
docker-compose restart nginx
```

## Related Documentation

- [Routing Patterns](routing-patterns.md) - Advanced routing strategies
- [SSL Configuration](ssl-configuration.md) - HTTPS setup and certificate management
- [Security Hardening](security-hardening.md) - Rate limiting, CORS, and security headers
- [Container Networking](../containerization/container-networking.md) - Docker network setup
- [Load Balancing Patterns](load-balancing.md) - Multi-instance service load balancing
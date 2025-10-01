# Nginx Security Hardening

This document covers security best practices for Nginx as an API Gateway in microservices architecture.

## Core Security Principles

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimal permissions and exposure
3. **Fail Secure**: Default deny, explicit allow
4. **Security by Default**: Secure defaults in all configurations

## Essential Security Headers

### Basic Security Headers

```nginx
# Add security headers to all responses
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Content Security Policy (adjust based on your needs)
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';" always;

# HSTS (HTTP Strict Transport Security) - HTTPS only
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

### Complete Security Header Configuration

```nginx
# /etc/nginx/conf.d/security-headers.conf

# Prevent MIME type sniffing
add_header X-Content-Type-Options "nosniff" always;

# Prevent clickjacking
add_header X-Frame-Options "DENY" always;

# Enable XSS filter
add_header X-XSS-Protection "1; mode=block" always;

# Control referer information
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# HSTS - Force HTTPS for 1 year
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Permissions Policy (formerly Feature-Policy)
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;

# Don't expose nginx version
server_tokens off;
more_clear_headers 'Server';  # Requires headers-more-nginx-module
```

## Rate Limiting

### IP-Based Rate Limiting

```nginx
# Define rate limit zones in http block
http {
    # General API rate limit: 10 requests per second per IP
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    # Strict limit for auth endpoints: 5 requests per second per IP
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;

    # Generous limit for static content: 100 requests per second
    limit_req_zone $binary_remote_addr zone=static_limit:10m rate=100r/s;

    server {
        # Apply to API endpoints
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            limit_req_status 429;
            proxy_pass http://api_service;
        }

        # Stricter limit for authentication
        location /api/v1/auth/login {
            limit_req zone=auth_limit burst=3 nodelay;
            limit_req_status 429;
            proxy_pass http://auth_service;
        }

        # Generous for static content
        location /static/ {
            limit_req zone=static_limit burst=50 nodelay;
            root /usr/share/nginx/html;
        }
    }
}
```

### User/Token-Based Rate Limiting

```nginx
# Rate limit by authorization token
limit_req_zone $http_authorization zone=user_limit:10m rate=100r/s;

server {
    location /api/v1/user/ {
        # Limit by auth token (100 req/s per user)
        limit_req zone=user_limit burst=50 nodelay;

        # Fallback to IP-based limit if no auth token
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://api_service;
    }
}
```

### Connection Limiting

```nginx
# Limit concurrent connections per IP
limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;

# Limit concurrent connections to a location
limit_conn_zone $server_name zone=conn_limit_per_server:10m;

server {
    # Max 10 concurrent connections per IP
    limit_conn conn_limit_per_ip 10;

    # Max 1000 concurrent connections to server
    limit_conn conn_limit_per_server 1000;

    location /api/ {
        proxy_pass http://api_service;
    }
}
```

## Request Size Limits

```nginx
server {
    # Limit request body size (default 1M)
    client_body_buffer_size 128k;
    client_max_body_size 10M;  # Max upload size

    # Limit header size
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;

    # Endpoints with larger uploads
    location /api/v1/upload {
        client_max_body_size 50M;
        proxy_pass http://api_service;
    }
}
```

## IP Whitelisting and Blacklisting

### Allow/Deny Specific IPs

```nginx
server {
    # Block specific IPs
    deny 192.168.1.100;
    deny 10.0.0.0/8;

    # Allow specific IPs
    allow 192.168.1.0/24;
    allow 10.1.1.1;

    # Block all others
    deny all;

    location /api/ {
        proxy_pass http://api_service;
    }
}
```

### Protect Admin Endpoints

```nginx
server {
    # Public endpoints
    location /api/v1/public/ {
        proxy_pass http://api_service;
    }

    # Admin endpoints - restrict to internal IPs
    location /api/v1/admin/ {
        # Allow internal networks
        allow 10.0.0.0/8;
        allow 172.16.0.0/12;
        allow 192.168.0.0/16;

        # Allow specific admin IPs
        allow 203.0.113.0/24;

        # Deny everyone else
        deny all;

        proxy_pass http://api_service;
    }
}
```

### GeoIP Blocking

```nginx
# Requires ngx_http_geoip_module
http {
    geoip_country /usr/share/GeoIP/GeoIP.dat;

    map $geoip_country_code $allowed_country {
        default no;
        US yes;
        CA yes;
        GB yes;
    }

    server {
        location /api/ {
            if ($allowed_country = no) {
                return 403 '{"error": "Access denied from your country"}';
            }
            proxy_pass http://api_service;
        }
    }
}
```

## CORS Configuration

### Basic CORS Setup

```nginx
# Simple CORS for public API
location /api/v1/public/ {
    # Allow all origins (not recommended for production)
    add_header Access-Control-Allow-Origin * always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;

    # Handle preflight
    if ($request_method = OPTIONS) {
        return 204;
    }

    proxy_pass http://api_service;
}
```

### Strict CORS with Allowed Origins

```nginx
# Define allowed origins
map $http_origin $cors_origin {
    default "";
    "~^https://app\.example\.com$" $http_origin;
    "~^https://admin\.example\.com$" $http_origin;
}

server {
    location /api/ {
        # Only set CORS headers if origin is allowed
        add_header Access-Control-Allow-Origin $cors_origin always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Request-ID" always;
        add_header Access-Control-Max-Age "3600" always;
        add_header Access-Control-Allow-Credentials "true" always;

        # Handle preflight
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin $cors_origin always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Request-ID" always;
            add_header Access-Control-Max-Age "3600" always;
            add_header Access-Control-Allow-Credentials "true" always;
            return 204;
        }

        proxy_pass http://api_service;
    }
}
```

## DDoS Protection

### SYN Flood Protection

```nginx
# In nginx.conf
http {
    # Connection limits
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

    # Rate limits
    limit_req_zone $binary_remote_addr zone=ddos_limit:10m rate=20r/s;

    server {
        limit_conn conn_limit 10;
        limit_req zone=ddos_limit burst=50 nodelay;

        location / {
            proxy_pass http://api_service;
        }
    }
}
```

### Slow HTTP Attack Protection

```nginx
server {
    # Timeout settings
    client_body_timeout 10s;
    client_header_timeout 10s;
    send_timeout 10s;

    # Keep-alive settings
    keepalive_timeout 65s;
    keepalive_requests 100;

    location /api/ {
        proxy_pass http://api_service;
    }
}
```

## SSL/TLS Hardening

See [SSL Configuration](ssl-configuration.md) for complete TLS setup.

```nginx
server {
    listen 443 ssl http2;

    # Strong SSL protocols
    ssl_protocols TLSv1.2 TLSv1.3;

    # Strong ciphers
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;

    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    location / {
        proxy_pass http://api_service;
    }
}
```

## Request Validation

### Block Common Attack Patterns

```nginx
# Block requests with suspicious patterns
location / {
    # Block SQL injection attempts
    if ($args ~* "(union|select|insert|cast|set|declare|drop|update|md5|benchmark)") {
        return 403;
    }

    # Block XSS attempts
    if ($args ~* "(<script|<iframe|<object|javascript:|onerror=|onload=)") {
        return 403;
    }

    # Block path traversal
    if ($uri ~* "(\.\.\/|\.\.\\)") {
        return 403;
    }

    # Block suspicious user agents
    if ($http_user_agent ~* (nmap|nikto|wikto|sf|sqlmap|bsqlbf|w3af|acunetix|havij|appscan)) {
        return 403;
    }

    proxy_pass http://api_service;
}
```

### Validate Required Headers

```nginx
location /api/ {
    # Require User-Agent header
    if ($http_user_agent = "") {
        return 403 '{"error": "User-Agent header required"}';
    }

    # Require Content-Type for POST/PUT
    if ($request_method ~ ^(POST|PUT)$) {
        set $has_content_type 0;
        if ($http_content_type ~ "application/json") {
            set $has_content_type 1;
        }
        if ($has_content_type = 0) {
            return 415 '{"error": "Content-Type must be application/json"}';
        }
    }

    proxy_pass http://api_service;
}
```

## Logging and Monitoring

### Security-Focused Logging

```nginx
log_format security '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    'request_id=$request_id '
                    'limit_req_status=$limit_req_status '
                    'upstream_addr=$upstream_addr '
                    'upstream_status=$upstream_status';

access_log /var/log/nginx/security.log security;

# Log rate limit violations separately
error_log /var/log/nginx/rate_limit.log warn;
```

### Failed Request Logging

```nginx
map $status $loggable {
    ~^[23] 0;    # Don't log success
    default 1;   # Log errors and rate limits
}

access_log /var/log/nginx/failed_requests.log combined if=$loggable;
```

## ModSecurity WAF Integration (Optional)

```nginx
# Install: apt-get install libnginx-mod-security
# Load module in nginx.conf
load_module modules/ngx_http_modsecurity_module.so;

http {
    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsec/main.conf;

    server {
        location /api/ {
            modsecurity_rules '
                SecRule ARGS "@rx select.*from" "id:1,deny,status:403,msg:SQL Injection Detected"
            ';
            proxy_pass http://api_service;
        }
    }
}
```

## Security Checklist

### Essential
- [ ] Remove `server_tokens` (hide nginx version)
- [ ] Set all security headers (X-Frame-Options, CSP, etc.)
- [ ] Enable HTTPS with strong TLS configuration
- [ ] Implement rate limiting on all public endpoints
- [ ] Set request size limits
- [ ] Configure CORS properly (don't use `*` in production)
- [ ] Restrict admin endpoints to internal IPs

### Recommended
- [ ] Enable HSTS with long max-age
- [ ] Implement connection limiting
- [ ] Configure timeout settings to prevent slow attacks
- [ ] Block suspicious user agents and patterns
- [ ] Set up security-focused logging
- [ ] Use GeoIP blocking if applicable
- [ ] Implement request validation

### Advanced
- [ ] Deploy ModSecurity WAF
- [ ] Set up fail2ban for automated IP blocking
- [ ] Implement certificate pinning (HPKP)
- [ ] Use OCSP stapling
- [ ] Deploy DDoS mitigation (Cloudflare, AWS Shield, etc.)
- [ ] Implement API key validation at gateway level
- [ ] Set up intrusion detection system (IDS)

## Testing Security Configuration

```bash
# Test security headers
curl -I https://api.example.com

# Test rate limiting
for i in {1..100}; do curl https://api.example.com/api/; done

# Test blocked patterns
curl "https://api.example.com/api/?id=1' OR '1'='1"

# Test SSL configuration
nmap --script ssl-enum-ciphers -p 443 api.example.com

# Or use online tools:
# - https://securityheaders.com
# - https://www.ssllabs.com/ssltest/
```

## Common Security Pitfalls

### ❌ Don't Use `if` for Security
```nginx
# BAD - if is evil in location context
location /api/ {
    if ($http_user_agent ~* bot) {
        return 403;
    }
    proxy_pass http://api_service;
}
```

### ✅ Use `map` Instead
```nginx
# GOOD - use map directive
map $http_user_agent $is_bot {
    default 0;
    ~*bot 1;
}

server {
    location /api/ {
        if ($is_bot) {
            return 403;
        }
        proxy_pass http://api_service;
    }
}
```

### ❌ Don't Trust X-Forwarded-For
```nginx
# BAD - easily spoofed
limit_req_zone $http_x_forwarded_for zone=bad:10m rate=10r/s;
```

### ✅ Use $binary_remote_addr
```nginx
# GOOD - uses actual client IP
limit_req_zone $binary_remote_addr zone=good:10m rate=10r/s;
```

## Related Documentation

- [Nginx Setup](nginx-setup.md) - Basic nginx configuration
- [SSL Configuration](ssl-configuration.md) - HTTPS and TLS setup
- [Routing Patterns](routing-patterns.md) - Request routing strategies
- [Security Testing Guide](../../security/security-testing-guide.md) - Testing security controls
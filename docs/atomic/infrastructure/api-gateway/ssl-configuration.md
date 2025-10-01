# SSL/TLS Configuration for Nginx

This document covers HTTPS setup, certificate management, and TLS best practices for Nginx as an API Gateway.

## SSL/TLS Basics

### Why HTTPS is Mandatory

1. **Data Encryption**: Protects data in transit from eavesdropping
2. **Authentication**: Verifies server identity
3. **Data Integrity**: Prevents tampering with requests/responses
4. **SEO and Trust**: Required by browsers, improves search rankings
5. **Compliance**: Required by PCI-DSS, GDPR, and other regulations

## Certificate Options

### 1. Let's Encrypt (Free, Automated)

**Pros**: Free, automated renewal, trusted by all browsers
**Cons**: 90-day validity, requires public domain

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.example.com -d www.example.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

### 2. Self-Signed Certificates (Development Only)

```bash
# Generate self-signed certificate (valid for 365 days)
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout /etc/nginx/certs/selfsigned.key \
  -out /etc/nginx/certs/selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Generate Diffie-Hellman parameters
openssl dhparam -out /etc/nginx/certs/dhparam.pem 2048
```

### 3. Commercial Certificates

Purchase from trusted CA (DigiCert, Sectigo, etc.) and install:

```bash
# Place certificate and key
/etc/nginx/certs/
├── example.com.crt       # SSL certificate
├── example.com.key       # Private key
├── ca-bundle.crt         # CA intermediate certificates
└── dhparam.pem           # DH parameters
```

## Basic HTTPS Configuration

### Minimal HTTPS Setup

```nginx
server {
    listen 80;
    server_name api.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL certificate
    ssl_certificate /etc/nginx/certs/example.com.crt;
    ssl_certificate_key /etc/nginx/certs/example.com.key;

    # Basic SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://api_service;
    }
}
```

## Production-Grade SSL Configuration

### Complete Secure Configuration

```nginx
# SSL configuration in separate file: /etc/nginx/conf.d/ssl.conf

# SSL session cache and timeout
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# DH parameters for perfect forward secrecy
ssl_dhparam /etc/nginx/certs/dhparam.pem;

# Modern TLS protocols only
ssl_protocols TLSv1.2 TLSv1.3;

# Strong cipher suite (Mozilla Intermediate profile)
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';

# Server prefers its cipher order
ssl_prefer_server_ciphers on;

# OCSP stapling for faster SSL handshakes
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/nginx/certs/ca-bundle.crt;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# Security headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;

server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL certificate
    ssl_certificate /etc/nginx/certs/example.com.crt;
    ssl_certificate_key /etc/nginx/certs/example.com.key;

    location / {
        proxy_pass http://api_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Mozilla SSL Configuration Generator

Use [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) for up-to-date cipher suites:

**Modern** (TLS 1.3 only, newer browsers)
**Intermediate** (TLS 1.2+, recommended)
**Old** (TLS 1.0+, legacy compatibility)

## Docker Integration

### Dockerfile with SSL Support

```dockerfile
FROM nginx:1.25-alpine

# Install certbot (for Let's Encrypt)
RUN apk add --no-cache certbot certbot-nginx

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Create directories for certificates
RUN mkdir -p /etc/nginx/certs /var/www/certbot

# Copy certificates (if not using Let's Encrypt)
# COPY certs/ /etc/nginx/certs/

# Generate DH parameters if not provided
RUN if [ ! -f /etc/nginx/certs/dhparam.pem ]; then \
        openssl dhparam -out /etc/nginx/certs/dhparam.pem 2048; \
    fi

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose with Let's Encrypt

```yaml
services:
  nginx:
    build: ./nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      # Nginx config (read-only)
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro

      # Let's Encrypt certificates
      - certbot-etc:/etc/letsencrypt
      - certbot-var:/var/lib/letsencrypt

      # Challenge directory
      - ./nginx/html:/var/www/certbot:ro

    networks:
      - app_network
    restart: unless-stopped

  certbot:
    image: certbot/certbot:latest
    volumes:
      - certbot-etc:/etc/letsencrypt
      - certbot-var:/var/lib/letsencrypt
      - ./nginx/html:/var/www/certbot
    command: >
      certonly --webroot --webroot-path=/var/www/certbot
      --email admin@example.com
      --agree-tos
      --no-eff-email
      -d api.example.com
    depends_on:
      - nginx

volumes:
  certbot-etc:
  certbot-var:

networks:
  app_network:
    driver: bridge
```

### Nginx Config for Let's Encrypt Challenge

```nginx
server {
    listen 80;
    server_name api.example.com;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect everything else to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # Let's Encrypt certificates
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    # Include SSL configuration
    include /etc/nginx/conf.d/ssl-params.conf;

    location / {
        proxy_pass http://api_service;
    }
}
```

## Certificate Renewal

### Let's Encrypt Auto-Renewal

```bash
# Add to crontab (runs twice daily)
0 0,12 * * * docker-compose exec certbot renew --quiet && docker-compose exec nginx nginx -s reload
```

Or use docker-compose:

```yaml
services:
  certbot-renew:
    image: certbot/certbot:latest
    volumes:
      - certbot-etc:/etc/letsencrypt
      - certbot-var:/var/lib/letsencrypt
      - ./nginx/html:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    depends_on:
      - nginx
```

### Manual Certificate Renewal

```bash
# Renew Let's Encrypt certificate
docker-compose exec certbot certbot renew

# Reload nginx
docker-compose exec nginx nginx -s reload

# Or restart nginx
docker-compose restart nginx
```

## Multi-Domain and Wildcard Certificates

### Multiple Domains

```bash
# Single certificate for multiple domains
sudo certbot --nginx \
  -d api.example.com \
  -d www.example.com \
  -d admin.example.com
```

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com www.example.com admin.example.com;

    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    # Route based on hostname
    if ($host = api.example.com) {
        proxy_pass http://api_service;
    }

    if ($host = admin.example.com) {
        proxy_pass http://admin_service;
    }
}
```

### Wildcard Certificates

```bash
# Wildcard certificate (requires DNS validation)
sudo certbot certonly \
  --manual \
  --preferred-challenges dns \
  -d '*.example.com' \
  -d example.com
```

```nginx
server {
    listen 443 ssl http2;
    server_name ~^(?<subdomain>.+)\.example\.com$;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Route based on subdomain
    location / {
        proxy_pass http://$subdomain-service;
    }
}
```

## Client Certificate Authentication (mTLS)

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;

    # Server certificates
    ssl_certificate /etc/nginx/certs/server.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;

    # Client certificate verification
    ssl_client_certificate /etc/nginx/certs/ca.crt;
    ssl_verify_client on;
    ssl_verify_depth 2;

    location / {
        # Pass client cert info to backend
        proxy_set_header X-SSL-Client-Cert $ssl_client_cert;
        proxy_set_header X-SSL-Client-DN $ssl_client_s_dn;
        proxy_pass http://api_service;
    }
}
```

## Monitoring SSL/TLS

### Certificate Expiry Monitoring

```bash
# Check certificate expiration
echo | openssl s_client -connect api.example.com:443 2>/dev/null | openssl x509 -noout -dates

# Get days until expiry
echo | openssl s_client -connect api.example.com:443 2>/dev/null | openssl x509 -noout -checkend $((86400*30)) && echo "Certificate valid for 30+ days" || echo "Certificate expires soon"
```

### SSL/TLS Metrics for Prometheus

```nginx
# nginx-prometheus-exporter can track SSL metrics
# Install: https://github.com/nginxinc/nginx-prometheus-exporter

server {
    listen 9113;
    location /metrics {
        stub_status;
    }
}
```

## Testing SSL Configuration

### Command-Line Testing

```bash
# Test SSL connection
openssl s_client -connect api.example.com:443

# Test specific TLS version
openssl s_client -connect api.example.com:443 -tls1_2
openssl s_client -connect api.example.com:443 -tls1_3

# Check certificate chain
openssl s_client -connect api.example.com:443 -showcerts

# Verify certificate
echo | openssl s_client -connect api.example.com:443 2>/dev/null | openssl x509 -noout -text
```

### Online SSL Testing Tools

1. **SSL Labs**: https://www.ssllabs.com/ssltest/
   - Comprehensive SSL/TLS analysis
   - Grade your configuration (aim for A+)

2. **Security Headers**: https://securityheaders.com/
   - Check security headers (HSTS, CSP, etc.)

3. **SSL Checker**: https://www.sslshopper.com/ssl-checker.html
   - Verify certificate installation

## Common SSL Issues

### Issue: ERR_CERT_COMMON_NAME_INVALID
**Cause**: Certificate doesn't match domain name
**Solution**: Ensure certificate CN/SAN matches your domain

### Issue: ERR_CERT_AUTHORITY_INVALID
**Cause**: Self-signed certificate or untrusted CA
**Solution**: Use trusted CA (Let's Encrypt) or import CA to client

### Issue: Mixed Content Warnings
**Cause**: HTTPS page loading HTTP resources
**Solution**: Use relative URLs or HTTPS for all resources

### Issue: Certificate Expired
**Cause**: Forgot to renew certificate
**Solution**: Set up auto-renewal (cron job or certbot-renew container)

## SSL/TLS Best Practices

### Security
- ✅ Use TLS 1.2 and 1.3 only (disable TLS 1.0/1.1)
- ✅ Use strong cipher suites (ECDHE, AES-GCM, ChaCha20)
- ✅ Enable HSTS with long max-age (31536000 = 1 year)
- ✅ Enable OCSP stapling for faster handshakes
- ✅ Generate strong DH parameters (2048-bit minimum)
- ✅ Use certificate from trusted CA (not self-signed)
- ❌ Don't use SHA-1 certificates
- ❌ Don't allow SSL compression (CRIME attack)

### Performance
- ✅ Enable SSL session caching
- ✅ Use HTTP/2 for better performance
- ✅ Enable keep-alive connections
- ✅ Use CDN for static content with HTTPS

### Operations
- ✅ Automate certificate renewal
- ✅ Monitor certificate expiry (alert 30 days before)
- ✅ Keep private keys secure (600 permissions, never commit to git)
- ✅ Use separate certificates per environment (dev/staging/prod)
- ✅ Test SSL configuration after changes

## Quick SSL Setup Script

```bash
#!/bin/bash
# setup-ssl.sh - Quick SSL setup for development

DOMAIN=${1:-localhost}
CERT_DIR="/etc/nginx/certs"

mkdir -p "$CERT_DIR"

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout "$CERT_DIR/$DOMAIN.key" \
  -out "$CERT_DIR/$DOMAIN.crt" \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"

# Generate DH parameters
openssl dhparam -out "$CERT_DIR/dhparam.pem" 2048

# Set permissions
chmod 600 "$CERT_DIR/$DOMAIN.key"
chmod 644 "$CERT_DIR/$DOMAIN.crt"
chmod 644 "$CERT_DIR/dhparam.pem"

echo "SSL certificates generated for $DOMAIN"
echo "Certificate: $CERT_DIR/$DOMAIN.crt"
echo "Private key: $CERT_DIR/$DOMAIN.key"
echo "DH params: $CERT_DIR/dhparam.pem"
```

## Related Documentation

- [Nginx Setup](nginx-setup.md) - Basic nginx configuration
- [Security Hardening](security-hardening.md) - Additional security measures
- [Routing Patterns](routing-patterns.md) - Request routing with HTTPS
- [Container Networking](../containerization/container-networking.md) - Docker networking with SSL
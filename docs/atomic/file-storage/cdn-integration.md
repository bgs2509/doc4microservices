# CDN Integration Guide

Comprehensive guidance for integrating Content Delivery Networks (CDNs) with microservices, covering asset versioning, cache strategy, invalidation workflows, and security hardening.

## CDN Integration Strategy

### Asset Classification

- **Static immutable assets**: Versioned bundles (JS/CSS), hashed filenames, long-lived cache headers.
- **Semi-static assets**: Marketing images, generated PDFs with periodic updates, cache control tuned per TTL requirements.
- **Dynamic assets**: User-specific downloads sent through signed URLs with short-term caching at the edge.

### CDN Selection Criteria

| Capability | Considerations |
|------------|----------------|
| Global POP coverage | Evaluate latency benchmarks for target regions. |
| Programmable edge | Support for Workers/Lambda@Edge for auth, headers, dynamic redirects. |
| HTTP/3 + TLS 1.3 | Required for modern browsers and latency-sensitive workloads. |
| Purge APIs | REST/GraphQL purge endpoints, bulk purges, invalidation speed guarantees. |
| Metrics & logging | Real-time analytics, log streaming to SIEM, request sampling. |

## Asset Deployment Workflow

### Build Pipeline Integration (CI/CD)

```yaml
# CI step example for versioning and uploading static assets
dependencies:
  predeploy:
    - name: Install dependencies
      run: npm ci
    - name: Build static bundle
      run: npm run build
    - name: Upload assets to storage
      run: >
        aws s3 sync dist/ s3://my-bucket/static/
        --cache-control "public, max-age=31536000, immutable"
        --content-encoding gzip
    - name: Invalidate CDN cache
      run: >
        aws cloudfront create-invalidation
        --distribution-id $CLOUDFRONT_DIST
        --paths "/static/*"
```

### Versioning Rules

1. Compute content hashes for every bundle.
2. Embed hash in file name and release manifest.
3. Maintain backward compatibility manifest for rollback.
4. Align backend references via environment-specific config service.

## Dynamic Asset Delivery

### Signed URLs with CDN

```python
from datetime import datetime, timedelta
from urllib.parse import urljoin
from botocore.signers import CloudFrontSigner
import rsa

with open("cloudfront_private_key.pem", "rb") as fh:
    private_key = rsa.PrivateKey.load_pkcs1(fh.read())

signer = CloudFrontSigner(key_id="K123456789", private_key=private_key)

def generate_signed_url(path: str, expires_minutes: int = 10) -> str:
    expire_at = datetime.utcnow() + timedelta(minutes=expires_minutes)

    def rsa_signer(message: bytes) -> bytes:
        return rsa.sign(message, private_key, "SHA-1")

    signed_url = signer.generate_presigned_url(
        urljoin("https://d123.cloudfront.net", path),
        date_less_than=expire_at,
        rsa_signer=rsa_signer
    )
    return signed_url
```

### Edge Authorization Checks

Configure edge function (Cloudflare Worker, Lambda@Edge) to verify JWT scopes or tenant metadata before serving sensitive objects.

```javascript
export default {
  async fetch(request, env, ctx) {
    const token = request.headers.get("Authorization");
    if (!token) {
      return new Response("Unauthorized", { status: 401 });
    }

    const claims = await env.AUTH_SERVICE.validate(token);
    if (!claims || !claims.scopes.includes("asset:read")) {
      return new Response("Forbidden", { status: 403 });
    }

    const response = await fetch(request);
    return new Response(response.body, {
      ...response,
      headers: {
        ...response.headers,
        "Cache-Control": "public, max-age=60"
      }
    });
  }
};
```

## Cache Invalidation Patterns

### Event-Driven Invalidation

1. Emit `asset.updated` event from content service.
2. Fan-out to CDN invalidation worker via queue.
3. Batch purge requests to stay within rate limits.
4. Log invalidation results and retry failures with exponential backoff.

### Stale-While-Revalidate (SWR)

- Serve stale content while background refresh runs at the edge.
- Use origin response headers: `Cache-Control: public, max-age=60, stale-while-revalidate=300`.
- Combine with ETag/If-None-Match to reduce origin load.

## Monitoring & Alerting

- Track cache hit ratio, origin latency, error rate, bandwidth usage.
- Set alerts for sudden cache miss spikes (>15% delta) indicating purge issues.
- Stream CDN logs to SIEM with enriched headers (request ID, user agent).
- Monitor TLS certificate expiry and automate rotation.

## Security Best Practices

- Enforce HTTPS with HSTS (`Strict-Transport-Security`).
- Strip sensitive headers at the edge (cookies, Authorization) for public assets.
- Implement signed cookies for batch downloads.
- Enable WAF rules for bot mitigation and rate limiting.
- Audit CDN access keys; rotate at least every 90 days.

## Operational Checklist

- [ ] Automated asset hashing and manifest generation.
- [ ] Environment-specific CDN distribution mappings.
- [ ] Multi-region failover via secondary origins.
- [ ] Synthetic monitoring from customer regions.
- [ ] Runbooks for purge failures and degradation triage.

# Container Networking

Reliable networking ensures services communicate securely across environments.

## Docker Compose / Local

- Use named networks to segment traffic (`backend`, `frontend`).
- Reference services by Compose service name (DNS) instead of localhost ports.
- Expose only public-facing ports to the host; keep internal dependencies private.

## Kubernetes / Production

- Map services to ClusterIP or headless services depending on discovery needs.
- Apply network policies to restrict ingress/egress between namespaces.
- Use service meshes (Istio, Linkerd) when advanced routing, mTLS, or traffic shifting is required.

## Observability

- Capture connection metrics (error counts, latency) via service mesh or sidecar instrumentation.
- Log source and destination identifiers for troubleshooting cross-service calls.

## Security

- Enforce TLS in transit (service mesh or sidecar proxies).
- Use mutual TLS or API gateways for external ingress.

## Related Documents

- `docs/atomic/integrations/http-communication/business-to-data-calls.md`
- `docs/atomic/infrastructure/deployment/production-deployment.md`

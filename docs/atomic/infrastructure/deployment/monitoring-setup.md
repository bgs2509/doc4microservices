# Deployment Monitoring Setup

Monitor services and infrastructure to detect regressions quickly.

## Metrics

- Deploy Prometheus/Grafana stack (or cloud equivalent) to scrape service metrics.
- Instrument applications with request latency, error counts, and saturation metrics.
- Set SLOs for critical services and create alerting rules for breaches.

## Logging

- Centralise logs via ELK stack, Loki, or cloud logging services.
- Enrich logs with request IDs, service name, environment, and deployment version.
- Configure retention policies and access controls to meet compliance requirements.

## Tracing

- Export traces via OpenTelemetry collectors to Jaeger or Tempo.
- Correlate traces with logs/metrics using consistent identifiers.

## Dashboards & Alerts

- Maintain dashboards per service (overview, dependencies, infrastructure).
- Alert on deployment anomalies (error spikes, saturation, failing health checks).
- Route alerts to on-call rotations with runbooks for remediation.

## Related Documents

- `docs/atomic/observability/*`
- `docs/atomic/infrastructure/deployment/production-deployment.md`

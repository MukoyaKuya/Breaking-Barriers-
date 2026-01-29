# Production Monitoring & Health Checks

## Health check endpoint

Use for load balancers, Cloud Run, Kubernetes, and orchestration:

- **URL:** `GET /health/`
- **200:** `{"status": "healthy", "database": "ok"}` — app and DB are reachable.
- **503:** `{"status": "unhealthy", "database": "<error>"}` — DB connection failed.

Configure your platform to call `/health/` on an interval and replace/restart instances that return 503.

## Logging

- **Development (`DEBUG=True`):** Logs go to console; `django.db.backends` at DEBUG.
- **Production (`DEBUG=False`):** Logs go to console and to `logs/django.log`. `django.request` and `church` loggers also write to file for errors and app activity.

Ensure the `logs/` directory is writable in production (it is created at startup if missing).

## Optional: external monitoring

- **Sentry:** Add `sentry-sdk` and configure `DSN` for error tracking and performance.
- **APM (e.g. New Relic, Datadog):** Use their Django middleware and agent for traces and metrics.
- **Uptime checks:** Use the `/health/` endpoint from an external service (e.g. UptimeRobot, Pingdom).

# Infrastructure: Load Balancing & Read Replicas

## Load balancing

- Use the **health check** endpoint for your load balancer or orchestrator:
  - **URL:** `GET /health/`
  - **200:** healthy (app + DB reachable)
  - **503:** unhealthy (e.g. DB down)
- Run multiple app instances behind a load balancer; point the health check at `/health/` and remove unhealthy instances from the pool.

## Read replicas

When you have a primary database and one or more read replicas, you can send reads to the replica and writes to the primary.

### Setup.

1. Set **`DATABASE_URL`** to your primary (read/write) database URL.
2. Set **`REPLICA_DATABASE_URL`** to your read replica database URL (same format as `DATABASE_URL`).

When both are set, Django will:

- Use **`default`** for all writes and migrations.
- Use **`replica`** for all reads (queries, etc.).

The router is in `church_app.db_router.ReplicaRouter` and is only enabled when `REPLICA_DATABASE_URL` is present.

### Notes

- Replication lag: replicas can be slightly behind the primary. For strongly consistent reads (e.g. right after a write), use `.using('default')` on the queryset or run critical reads on the primary.
- Migrations always run on `default` only.
- If you have multiple replicas, you can add more entries to `DATABASES` and extend the router to choose among them (e.g. round-robin or random).

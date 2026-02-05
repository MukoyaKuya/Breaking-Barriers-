"""
Database router for read replicas.
When REPLICA_DATABASE_URL is set, read operations use the 'replica' database
and write operations use the 'default' database.
"""


class ReplicaRouter:
    """Route reads to replica, writes to default."""

    def db_for_read(self, model, **hints):
        return 'replica'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'

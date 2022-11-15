import random

from django.conf import settings

class ReplicaRouter:
    read_replica_app_labels = {'sensors', }
    read_replicas = list(settings.DATABASES.keys() - {'default', })

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.read_replica_app_labels:
            return random.choice(self.read_replicas)
        return 'default'
    
    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the primary/replica pool.
        """
        db_set = {'default', 'read_replica'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

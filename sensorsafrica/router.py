import random

from django.conf import settings

class ReplicaRouter:
    read_replicas = list(settings.DATABASES.keys() - {'default', })

    def db_for_read(self, model, **hints):
        # return random.choice(self.read_replicas)
        return "default"
        
    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relation not applicable for our use case
        """
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Restrict migration operations to the master db i.e. default
        """
        return True



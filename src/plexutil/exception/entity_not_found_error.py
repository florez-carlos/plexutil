from peewee import Model


class EntityNotFoundError(Exception):
    def __init__(self, instance: Model):
            if not isinstance(instance, Model):
                raise TypeError("cls must be a subclass of Exception")
            
            self.instance = instance
            
            self.message = f"{self.instance}: Not Found\nProperties: {self.instance.__dict__}"
            
            super().__init__(self.message)


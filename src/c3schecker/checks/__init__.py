from c3schecker.utils import Singleton


class ChecksRegistry(metaclass=Singleton):
    __registry = {}

    def register(self, check_name, check_implementation):
        try:
            self.update({check_name: check_implementation})
        except KeyError:
            self.__registry = {check_name: check_implementation}

    def update(self, checks):
        self.__registry.update(checks)

    def __getitem__(self):
        return self.__registry

    def __contains__(self):
        return self.__registry


def register(check_name):
    """Alias to ChecksRegistry().register to be used as a decorator"""

    def decorator(func):
        ChecksRegistry().register(check_name, func)
        return func

    return decorator

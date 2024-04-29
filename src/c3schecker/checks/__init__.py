from c3schecker.utils import Singleton


class ChecksRegistry(metaclass=Singleton):
    __registry = {}

    def register(self, check_name, check_implementation):
        """Register a function to be used as a check under the check_name.
        Note, if a function was already registered for check_name, it will be
        overridden by subsequent registrations"""
        self.update({check_name: check_implementation})

    def update(self, checks):
        self.__registry.update(checks)

    def items(self):
        return self.__registry.items()

    def __getitem__(self, check_name):
        return self.__registry[check_name]

    def __contains__(self, check_name):
        return check_name in self.__registry


def register(check_name):
    """Alias to ChecksRegistry().register to be used as a decorator"""

    def decorator(func):
        ChecksRegistry().register(check_name, func)
        return func

    return decorator

from c3schecker.utils import Singleton 


class ChecksRegistry(metaclass=Singleton):
    __registry = {"C3S-0.1": {}, "C3S-0.3": {}}
    #__registry = {"C3S-0.3": {}}
    #__registry = {"C3S-0.3": {}, "CF-1.6":{}}
    
    def register(self, convention, check_name, check_implementation):
        try:
            self.update(convention, {check_name: check_implementation})
        except KeyError:
            self.__registry[convention] = {check_name: check_implementation}

    def update(self, convention, checks):
        self.__registry[convention].update(checks)

    def __getitem__(self, convention):
        return self.__registry[convention]

    def __contains__(self, convention):
        return convention in self.__registry
    
    #def __getconvention__(self, convention):
    #    print(convention)

def register(convention, check_name):
    """Alias to ChecksRegistry().register to be used as a decorator"""

    def decorator(func):
        ChecksRegistry().register(convention, check_name, func)
        return func

    return decorator



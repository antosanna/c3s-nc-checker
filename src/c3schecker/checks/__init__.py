from c3schecker.utils import Singleton 


# class ChecksRegistry(metaclass=Singleton):
#     __registry = {"C3S-0.1": {}, "C3S-0.3": {}, "C3S-0.3": {}}
#     #__registry = {"C3S-0.3": {}}
#     #__registry = {"C3S-0.3": {}, "CF-1.6":{}}
    
#     def register(self, convention, check_name, check_implementation):
#         try:
#             self.update(convention, {check_name: check_implementation})
#         except KeyError:
#             self.__registry[convention] = {check_name: check_implementation}

#     def update(self, convention, checks):
#         self.__registry[convention].update(checks)

#     def __getitem__(self, convention):
#         return self.__registry[convention]

#     def __contains__(self, convention):
#         return convention in self.__registry
    
#     #def __getconvention__(self, convention):
#     #    print(convention)

# def register(convention, check_name):
#     """Alias to ChecksRegistry().register to be used as a decorator"""

#     def decorator(func):
#         ChecksRegistry().register(convention, check_name, func)
#         return func

#     return decorator


class ChecksRegistry(metaclass=Singleton):
    #__registry = {"C3S-0.1": {}, "C3S-0.2": {}, "C3S-0.3": {}}
    __registry = {}
    #__registry = {"C3S-0.3": {}}
    #__registry = {"C3S-0.3": {}, "CF-1.6":{}}

    def register(self, check_name, check_implementation):
        try:
            self.update({check_name: check_implementation})
        except KeyError:
            self.__registry = {check_name: check_implementation}
        #print(f"Tests inside the pool: {self.__registry}")

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



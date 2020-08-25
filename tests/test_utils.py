from c3schecker.utils import Singleton


def test_singleton_class():
    class UnWrappedClass:
        pass

    # First, check that the class, if unwrapped, create many instances
    instance1 = UnWrappedClass()
    instance2 = UnWrappedClass()
    assert instance1 is not instance2

    # Now test the Singleton wrapper does it job
    @Singleton
    class WrappedClass:
        pass

    instance1 = WrappedClass()
    instance2 = WrappedClass()
    assert instance1 is instance2

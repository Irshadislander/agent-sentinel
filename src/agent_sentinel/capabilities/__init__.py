from .registry import CapabilityRegistry

registry = CapabilityRegistry()


def register(capability_cls):
    """
    Decorator for auto-registering capabilities.
    """
    registry.register(capability_cls)
    return capability_cls

"""
Stage registry for the Engineering Brain.

Allows registering and retrieving stages by name with explicit execution ordering.
"""

from brain.stages.base import Stage

_REGISTRY: dict[str, tuple[type[Stage], int]] = {}


def register_stage(stage_class: type[Stage], order: int | None = None) -> type[Stage]:
    """
    Decorator to register a stage class with optional explicit execution order.
    
    Args:
        stage_class: The stage class to register
        order: Optional explicit execution order (lower numbers execute first).
               If None, order is determined by registration sequence (legacy behavior).
    
    Returns:
        The stage class (for decorator usage)
    """
    stage_name = stage_class().name
    instance = stage_class()
    stage_name = instance.name
    
    if stage_name in _REGISTRY:
        raise ValueError(f"Stage '{stage_name}' is already registered.")
    
    # If order not specified, use next available integer (preserves import order)
    if order is None:
        order = len(_REGISTRY)
    
    _REGISTRY[stage_name] = (stage_class, order)
    return stage_class


def get_stage_class(name: str) -> type[Stage]:
    """Retrieve a stage class by name."""
    if name not in _REGISTRY:
        raise ValueError(f"Stage '{name}' not found in registry.")
    stage_class, _ = _REGISTRY[name]
    return stage_class


def list_stages() -> list[str]:
    """List all registered stage names."""
    return list(_REGISTRY.keys())

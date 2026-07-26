"""
Stage registry for the Engineering Brain.

Allows registering and retrieving stages by name.
"""

from typing import Dict, Type
from brain.stages.base import Stage

_REGISTRY: Dict[str, Type[Stage]] = {}


def register_stage(stage_class: Type[Stage]) -> Type[Stage]:
    """Decorator to register a stage class."""
    # We need an instance to get the name if it's a property, 
    # but since it's a class we'll just instantiate it once to get the name
    # or assume we can get it from the class.
    # For now, let's just use the class name or a manual mapping.
    
    # Actually, let's just use a simple function for now.
    instance = stage_class()
    _REGISTRY[instance.name] = stage_class
    return stage_class


def get_stage_class(name: str) -> Type[Stage]:
    """Retrieve a stage class by name."""
    if name not in _REGISTRY:
        raise ValueError(f"Stage '{name}' not found in registry.")
    return _REGISTRY[name]


def list_stages() -> list[str]:
    """List all registered stage names."""
    return list(_REGISTRY.keys())

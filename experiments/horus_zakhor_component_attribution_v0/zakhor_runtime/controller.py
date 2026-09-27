"""Public controller entrypoint (architecture-agnostic living-memory hooks).

``LivingMemoryController`` is implemented in ``hooks.py``; this module re-exports
it alongside layer-discovery helpers so callers can::

    from living_memory.controller import LivingMemoryController, get_model_layers
"""

from __future__ import annotations

from .hooks import LivingMemoryController
from .layers import (
    describe_layer_stack,
    get_attn_module,
    get_model_layers,
    iter_attn_modules,
    layer_path,
)

__all__ = [
    "LivingMemoryController",
    "get_model_layers",
    "get_attn_module",
    "describe_layer_stack",
    "iter_attn_modules",
    "layer_path",
]

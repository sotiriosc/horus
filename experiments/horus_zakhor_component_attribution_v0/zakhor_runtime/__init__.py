"""Living-memory activation control (zakhor / Horus scale-keeper lineage).

Application state is owned by ``LivingMemoryRoot`` (path namespaces). Low-level
hooks remain available for ``train.py``; inference should enter via the root.
"""

from .config import MemoryConfig
from .tracker import LivingMemoryTracker
from .bfp import bfp_quantize, localmax_quantize, trimmed_quantize
from .switch import LayerThresholdBank, switch_quantize_row
from .interfaces import ActionFailed, ActionResult, require_true
from .epistemic import BeliefReport, FeelingReport, KnowingReport, validate_epistemic
# torch_keeper imported lazily via LivingMemoryController(training=True)

__all__ = [
    "MemoryConfig",
    "LivingMemoryTracker",
    "bfp_quantize",
    "localmax_quantize",
    "trimmed_quantize",
    "LayerThresholdBank",
    "switch_quantize_row",
    "LivingMemoryController",
    "calibrate_layer_thresholds",
    "get_model_layers",
    "get_attn_module",
    "describe_layer_stack",
    "LivingMemoryRoot",
    "LivingMemoryMap",
    "ActionResult",
    "ActionFailed",
    "require_true",
    "FeelingReport",
    "BeliefReport",
    "KnowingReport",
    "validate_epistemic",
]


def __getattr__(name: str):
    if name == "LivingMemoryController":
        from .controller import LivingMemoryController
        return LivingMemoryController
    if name == "calibrate_layer_thresholds":
        from .switch import calibrate_layer_thresholds
        return calibrate_layer_thresholds
    if name in ("get_model_layers", "get_attn_module", "describe_layer_stack"):
        from . import layers as _layers

        return getattr(_layers, name)
    if name in ("LivingMemoryRoot", "LivingMemoryMap"):
        from .root import LivingMemoryMap, LivingMemoryRoot

        return LivingMemoryRoot if name == "LivingMemoryRoot" else LivingMemoryMap
    raise AttributeError(name)

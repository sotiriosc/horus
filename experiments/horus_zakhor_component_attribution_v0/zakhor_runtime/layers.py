"""Architecture-agnostic transformer layer / attention discovery.

Supports:
  - GPT-2 style: ``model.transformer.h`` + ``block.attn``
  - Llama / Qwen style: ``model.model.layers`` + ``block.self_attn``
  - Pythia / NeoX style: ``model.gpt_neox.layers`` + ``block.attention``
"""

from __future__ import annotations

from typing import Any, List, Sequence, Tuple


def get_model_layers(model) -> List[Any]:
    """Return the ordered list of transformer blocks for ``model``.

    Raises:
        AttributeError: if no known layer container is present.
    """
    # GPT-2 / GPT-J-like
    transformer = getattr(model, "transformer", None)
    if transformer is not None:
        h = getattr(transformer, "h", None)
        if h is not None:
            return list(h)

    # Llama / Qwen / Mistral / Phi (HF CausalLM)
    inner = getattr(model, "model", None)
    if inner is not None:
        layers = getattr(inner, "layers", None)
        if layers is not None:
            return list(layers)

    # GPT-NeoX / Pythia
    neox = getattr(model, "gpt_neox", None)
    if neox is not None:
        layers = getattr(neox, "layers", None)
        if layers is not None:
            return list(layers)

    raise AttributeError(
        "Unsupported model architecture for living-memory hooks: expected "
        "model.transformer.h (GPT-2), model.model.layers (Llama/Qwen), "
        f"or model.gpt_neox.layers (NeoX/Pythia). Got type={type(model).__name__}."
    )


def get_attn_module(block: Any) -> Any:
    """Return the attention submodule on a transformer block."""
    for name in ("attn", "self_attn", "attention"):
        mod = getattr(block, name, None)
        if mod is not None:
            return mod
    raise AttributeError(
        f"Block {type(block).__name__} has no attn/self_attn/attention module"
    )


def describe_layer_stack(model) -> Tuple[str, int]:
    """Return (architecture_tag, n_layers) for telemetry."""
    transformer = getattr(model, "transformer", None)
    if transformer is not None and getattr(transformer, "h", None) is not None:
        layers = list(transformer.h)
        return "gpt2", len(layers)

    inner = getattr(model, "model", None)
    if inner is not None and getattr(inner, "layers", None) is not None:
        layers = list(inner.layers)
        return "llama_qwen", len(layers)

    neox = getattr(model, "gpt_neox", None)
    if neox is not None and getattr(neox, "layers", None) is not None:
        layers = list(neox.layers)
        return "gpt_neox", len(layers)

    # Fall through to raise the same clear error
    get_model_layers(model)
    return "unknown", 0


def layer_path(arch: str, layer_id: int, *, attn: bool = True) -> str:
    """Human-readable module path for logs (architecture-aware)."""
    if arch == "gpt2":
        base = f"transformer.h.{layer_id}"
        return f"{base}.attn" if attn else base
    if arch == "llama_qwen":
        base = f"model.layers.{layer_id}"
        return f"{base}.self_attn" if attn else base
    if arch == "gpt_neox":
        base = f"gpt_neox.layers.{layer_id}"
        return f"{base}.attention" if attn else base
    return f"layers.{layer_id}.attn" if attn else f"layers.{layer_id}"


def iter_attn_modules(model) -> Sequence[Tuple[int, Any, Any]]:
    """Yield ``(layer_id, block, attn_module)`` for hook registration."""
    arch, _ = describe_layer_stack(model)
    out = []
    for li, blk in enumerate(get_model_layers(model)):
        out.append((li, blk, get_attn_module(blk)))
    return out

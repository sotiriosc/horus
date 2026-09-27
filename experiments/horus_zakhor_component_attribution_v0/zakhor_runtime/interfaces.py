"""Structure vs forming — models talk only through ports, never each other's guts.

A *structure* is a named path interface. A *forming* is a concrete adapter that
implements the port. Objects relate through these contracts; they do not reach
into peer internals.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Protocol, runtime_checkable


class ActionFailed(RuntimeError):
    """Raised when an action does not evaluate strictly to True."""

    def __init__(self, path: str, detail: str = ""):
        self.path = path
        self.detail = detail
        msg = f"action failed at {path!r}"
        if detail:
            msg = f"{msg}: {detail}"
        super().__init__(msg)


@dataclass
class ActionResult:
    """Every state transition reports through this envelope.

    Only ``ok is True`` counts as success. ``False``, ``None``, missing fields,
    or any other truthy junk is a failure under strict boolean verification.
    """

    ok: bool
    path: str
    body: Any = None
    error: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        # Explicit: only the boolean True on ok is success.
        return self.ok is True

    @classmethod
    def success(cls, path: str, body: Any = None, **meta: Any) -> "ActionResult":
        return cls(ok=True, path=path, body=body, meta=meta)

    @classmethod
    def failure(cls, path: str, error: str, body: Any = None, **meta: Any) -> "ActionResult":
        return cls(ok=False, path=path, body=body, error=error, meta=meta)


def require_true(result: Any, *, path: str = "") -> ActionResult:
    """Accept only strict True / ActionResult(ok=True). Anything else fails."""
    if result is True:
        return ActionResult.success(path or "/action/true")
    if isinstance(result, ActionResult):
        if result.ok is True:
            return result
        raise ActionFailed(result.path or path, result.error or "ok is not True")
    if result is False:
        raise ActionFailed(path, "returned False")
    if result is None:
        raise ActionFailed(path, "returned None")
    raise ActionFailed(path, f"non-boolean result: {type(result).__name__}")


def body_matches_leaf(path: str, body: Optional[Mapping[str, Any]]) -> bool:
    """Payload must carry a key equal to the path's final segment (leaf name)."""
    leaf = path.rstrip("/").rsplit("/", 1)[-1]
    if not leaf:
        return False
    if body is None:
        return False
    return leaf in body


@runtime_checkable
class ModelPort(Protocol):
    """Forming of the language model — load and expose handles via the port only."""

    @property
    def loaded(self) -> bool: ...

    def load(self, model_id: str, device: Optional[str] = None) -> ActionResult: ...

    def handles(self) -> ActionResult:
        """Body: {model, tokenizer, device} — never borrow peer internals."""
        ...


@runtime_checkable
class SessionPort(Protocol):
    """Forming of conversational transcript memory (not activation-scale)."""

    def wrap(self, question: str, *, raw: bool = False) -> ActionResult: ...

    def extract(self, full_text: str, prompt: str) -> ActionResult: ...

    def add_turn(self, user: str, assistant: str) -> ActionResult: ...


@runtime_checkable
class ControllerPort(Protocol):
    """Forming of living-memory activation hooks."""

    def attach(self) -> ActionResult: ...

    def detach(self) -> ActionResult: ...

    def reset(self) -> ActionResult: ...


@runtime_checkable
class GeneratePort(Protocol):
    """Forming of autoregressive generation under the root's controller."""

    def generate(self, prompt: str, **kwargs: Any) -> ActionResult: ...


class PortAdapter(ABC):
    """Base for concrete formings registered into the root path space."""

    name: str = "port"

    @abstractmethod
    def as_body(self) -> Dict[str, Any]:
        """Snapshot for /state/<name> reads."""
        ...

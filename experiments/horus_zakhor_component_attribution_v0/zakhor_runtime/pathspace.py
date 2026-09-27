"""Path-based namespaces — query state and run actions by URI, not method chase.

Example::

    /state/config
    /state/mode
    /action/generate   body={"generate": {"prompt": "..."}}
    /a/n/d/generate    alias namespace (same leaf contract)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Mapping, Optional, Union

from .interfaces import ActionFailed, ActionResult, body_matches_leaf, require_true

Handler = Callable[[Optional[Mapping[str, Any]]], Union[ActionResult, bool, Any]]


class PathSpace:
    """Hierarchical namespace map: path → handler or stored value."""

    def __init__(self) -> None:
        self._handlers: Dict[str, Handler] = {}
        self._values: Dict[str, Any] = {}

    @staticmethod
    def norm(path: str) -> str:
        p = "/" + "/".join(x for x in path.strip().split("/") if x)
        return p if p != "/" else "/"

    def register(self, path: str, handler: Handler) -> ActionResult:
        key = self.norm(path)
        self._handlers[key] = handler
        return ActionResult.success("/action/register", body={"path": key})

    def put(self, path: str, value: Any) -> ActionResult:
        key = self.norm(path)
        self._values[key] = value
        return ActionResult.success(key, body=value)

    def get(self, path: str) -> ActionResult:
        key = self.norm(path)
        if key in self._values:
            return ActionResult.success(key, body=self._values[key])
        if key in self._handlers:
            # GET on an action path without body → describe registration
            return ActionResult.success(
                key, body={"callable": True, "leaf": key.rsplit("/", 1)[-1]}
            )
        # Prefix listing
        prefix = key if key.endswith("/") else key + "/"
        children = sorted(
            {
                p[len(key) :].lstrip("/").split("/", 1)[0]
                for p in list(self._values) + list(self._handlers)
                if p == key or p.startswith(prefix)
            }
        )
        children = [c for c in children if c]
        if children:
            return ActionResult.success(key, body={"children": children})
        return ActionResult.failure(key, "path not found")

    def call(
        self,
        path: str,
        body: Optional[Mapping[str, Any]] = None,
        *,
        require_leaf_key: bool = True,
    ) -> ActionResult:
        """Invoke a registered action. Leaf name must appear in body when required."""
        key = self.norm(path)
        if key not in self._handlers:
            return ActionResult.failure(key, "no handler registered")

        if require_leaf_key and key.startswith("/action"):
            if not body_matches_leaf(key, body):
                leaf = key.rsplit("/", 1)[-1]
                return ActionResult.failure(
                    key,
                    f"body must include key matching leaf {leaf!r}",
                )

        try:
            raw = self._handlers[key](body)
            return require_true(raw, path=key)
        except ActionFailed as e:
            return ActionResult.failure(e.path or key, e.detail)
        except Exception as e:  # noqa: BLE001 — surface as failed action
            return ActionResult.failure(key, f"{type(e).__name__}: {e}")

    def map(self) -> Dict[str, str]:
        """Full namespace inventory for /state/map."""
        out: Dict[str, str] = {}
        for p in self._values:
            out[p] = "value"
        for p in self._handlers:
            out[p] = "action"
        return dict(sorted(out.items()))

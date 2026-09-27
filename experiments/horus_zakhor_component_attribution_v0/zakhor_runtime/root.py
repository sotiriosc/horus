"""LivingMemoryRoot — the root wrapper that owns application state.

Nothing in the environment is a peer helper. Model, session, controller, and
generate formings live *inside* this map and are reached by path namespaces::

    root("/action/load", {"load": {"model_id": "./checkpoint"}})
    root("/action/generate", {"generate": {"prompt": "What color is the sky?"}})

Direct ``agent.get_memory()``-style chase is replaced by path calls. Actions
must evaluate to True (``ActionResult.ok is True``) or they are failures.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Union

from .config import MemoryConfig
from .interfaces import ActionResult
from .pathspace import PathSpace
from .ports import ControllerForming, GenerateForming, Gpt2ModelPort, SessionForming


class LivingMemoryRoot:
    """Root ``instanceof`` map: config + path space + all formings."""

    def __init__(
        self,
        cfg: Optional[MemoryConfig] = None,
        *,
        mode: str = "keeper",
        policy: str = "soft",
    ) -> None:
        self.cfg = cfg or MemoryConfig()
        self.mode = mode
        self.policy = policy
        self.paths = PathSpace()

        self.model = Gpt2ModelPort()
        self.session = SessionForming()
        self.controller: Optional[ControllerForming] = None
        self.generate_port = GenerateForming(self.model)
        self._bank = None
        self._last_epistemic: Optional[Dict[str, Any]] = None

        self._register_paths()
        # Seed state nodes
        self.paths.put("/state/config", self.cfg)
        self.paths.put("/state/mode", self.mode)
        self.paths.put("/state/policy", self.policy)
        self.paths.put("/state/feeling", {"note": "no generation yet — feeling ≠ knowing"})
        self.paths.put("/state/knowing", {"note": "no generation yet"})

    # -- construction -------------------------------------------------------

    @classmethod
    def open(
        cls,
        model_id: str = "gpt2",
        *,
        mode: str = "keeper",
        policy: str = "soft",
        cfg: Optional[MemoryConfig] = None,
        device: Optional[str] = None,
        calibrate: bool = True,
    ) -> "LivingMemoryRoot":
        """Create root, load model, optionally calibrate + attach controller."""
        root = cls(cfg=cfg, mode=mode, policy=policy)
        loaded = root("/action/load", {"load": {"model_id": model_id, "device": device}})
        if loaded.ok is not True:
            raise RuntimeError(loaded.error)
        if mode in ("switch", "compose", "simulate") and calibrate:
            cal = root(
                "/action/calibrate",
                {"calibrate": {"text": None}},
            )
            if cal.ok is not True:
                raise RuntimeError(cal.error)
        if mode != "none":
            att = root("/action/attach", {"attach": True})
            if att.ok is not True:
                raise RuntimeError(att.error)
        return root

    # -- path entry points --------------------------------------------------

    def __call__(
        self,
        path: str,
        body: Optional[Mapping[str, Any]] = None,
    ) -> ActionResult:
        """Primary API: path + body → ActionResult (strict True)."""
        key = self.paths.norm(path)
        # /a/n/d/<leaf> aliases /action/<leaf>
        if key.startswith("/a/n/d/"):
            key = "/action/" + key[len("/a/n/d/") :]
        if key.startswith("/action/"):
            return self.paths.call(key, body, require_leaf_key=True)
        if key in self.paths._handlers:
            # State readers registered as handlers — no leaf-key body rule
            return self.paths.call(key, body, require_leaf_key=False)
        return self.paths.get(key)

    def __enter__(self) -> "LivingMemoryRoot":
        return self

    def __exit__(self, *exc: Any) -> None:
        self("/action/detach", {"detach": True})

    # -- registration -------------------------------------------------------

    def _register_paths(self) -> None:
        p = self.paths

        p.put("/state/map", None)  # refreshed by handler

        def state_map(_body):
            return ActionResult.success("/state/map", body={"map": p.map()})

        # Re-bind map as action-like read via call without leaf rule:
        p.register("/state/map", state_map)

        p.register("/action/load", self._act_load)
        p.register("/action/calibrate", self._act_calibrate)
        p.register("/action/attach", self._act_attach)
        p.register("/action/detach", self._act_detach)
        p.register("/action/reset", self._act_reset)
        p.register("/action/generate", self._act_generate)
        p.register("/action/wrap", self._act_wrap)
        p.register("/action/set_mode", self._act_set_mode)
        p.register("/action/validate", self._act_validate)

        # Alias namespace /a/n/d/* → same handlers
        for leaf in (
            "load",
            "calibrate",
            "attach",
            "detach",
            "reset",
            "generate",
            "wrap",
            "set_mode",
            "validate",
        ):
            p.register(f"/a/n/d/{leaf}", getattr(self, f"_act_{leaf}"))

        p.register("/state/model", lambda _b: self._state_model())
        p.register("/state/session", lambda _b: self._state_session())
        p.register("/state/controller", lambda _b: self._state_controller())
        p.register("/state/feeling", lambda _b: self._state_feeling())
        p.register("/state/knowing", lambda _b: self._state_knowing())
        p.register("/state/layer_flow", lambda _b: self._state_layer_flow())
        p.register("/state/graphics", lambda _b: self._state_graphics())

    # -- state reads --------------------------------------------------------

    def _state_model(self) -> ActionResult:
        return ActionResult.success("/state/model", body=self.model.as_body())

    def _state_session(self) -> ActionResult:
        return ActionResult.success("/state/session", body=self.session.as_body())

    def _state_controller(self) -> ActionResult:
        if self.controller is None:
            return ActionResult.success(
                "/state/controller", body={"attached": False, "mode": self.mode}
            )
        body = self.controller.as_body()
        # Direct observation — tracker snapshots, not text feedback
        if self.controller._attached:
            from living_memory.epistemic import observe_controller

            body["direct_observation"] = observe_controller(self.controller.raw)
        return ActionResult.success("/state/controller", body=body)

    def _state_feeling(self) -> ActionResult:
        epi = self._last_epistemic or {}
        return ActionResult.success(
            "/state/feeling",
            body=epi.get("feeling")
            or {"note": "no generation yet — feeling = logits, not facts"},
        )

    def _state_knowing(self) -> ActionResult:
        epi = self._last_epistemic or {}
        return ActionResult.success(
            "/state/knowing",
            body=epi.get("knowing")
            or {"note": "no generation yet — text ≠ ground truth"},
        )

    def _state_layer_flow(self) -> ActionResult:
        epi = self._last_epistemic or {}
        return ActionResult.success(
            "/state/layer_flow",
            body=epi.get("layer_flow")
            or {"order": list("ABCDEF"), "note": "run /action/generate first"},
        )

    def _state_graphics(self) -> ActionResult:
        epi = self._last_epistemic or {}
        return ActionResult.success(
            "/state/graphics",
            body=epi.get("graphics") or {"ascii": "(no render yet)"},
        )

    # -- actions (body leaf key required) -----------------------------------

    def _act_load(self, body: Optional[Mapping[str, Any]]) -> ActionResult:
        spec = (body or {}).get("load") or {}
        if isinstance(spec, str):
            spec = {"model_id": spec}
        model_id = spec.get("model_id") or spec.get("model") or "gpt2"
        device = spec.get("device")
        result = self.model.load(model_id, device=device)
        if result.ok is True:
            handles = self.model.handles()
            if handles.ok is True:
                self.session.bind_tokenizer(handles.body["tokenizer"])
            self.paths.put("/state/model", self.model.as_body())
        return result

    def _act_calibrate(self, body: Optional[Mapping[str, Any]]) -> ActionResult:
        from living_memory.switch import calibrate_layer_thresholds

        spec = (body or {}).get("calibrate") or {}
        text = spec.get("text") or (
            "The scale of a signal can drift slowly over time. "
            "A living memory tracks that scale with a leaky update."
        ) * 40
        handles = self.model.handles()
        if handles.ok is not True:
            return ActionResult.failure("/action/calibrate", handles.error)
        h = handles.body
        try:
            self._bank = calibrate_layer_thresholds(
                h["model"], h["tokenizer"], text, cfg=self.cfg, device=h["device"]
            )
        except Exception as e:  # noqa: BLE001
            return ActionResult.failure(
                "/action/calibrate", f"{type(e).__name__}: {e}"
            )
        self.paths.put("/state/thresholds", {"layers": len(self._bank.thresholds)})
        return ActionResult.success(
            "/action/calibrate",
            body={"calibrate": {"layers": len(self._bank.thresholds)}},
        )

    def _act_attach(self, body: Optional[Mapping[str, Any]]) -> ActionResult:
        _ = body
        handles = self.model.handles()
        if handles.ok is not True:
            return ActionResult.failure("/action/attach", handles.error)
        if self.mode == "none":
            return ActionResult.success(
                "/action/attach", body={"attach": True, "mode": "none"}
            )
        if self.controller is not None:
            return self.controller.attach()
        self.controller = ControllerForming(
            handles.body["model"],
            self.cfg,
            mode=self.mode,
            policy=self.policy,
            bank=self._bank,
        )
        self.generate_port.bind_controller(self.controller)
        result = self.controller.attach()
        self.paths.put("/state/controller", self.controller.as_body())
        return result

    def _act_detach(self, body: Optional[Mapping[str, Any]]) -> ActionResult:
        _ = body
        if self.controller is None:
            return ActionResult.success("/action/detach", body={"detach": True})
        result = self.controller.detach()
        self.paths.put("/state/controller", self.controller.as_body())
        return result

    def _act_reset(self, body: Optional[Mapping[str, Any]]) -> ActionResult:
        _ = body
        if self.controller is None:
            return ActionResult.failure("/action/reset", "no controller")
        return self.controller.reset()

    def _act_set_mode(self, body: Optional[Mapping[str, Any]]) -> ActionResult:
        spec = (body or {}).get("set_mode") or {}
        if isinstance(spec, str):
            mode = spec
            policy = self.policy
        else:
            mode = spec.get("mode", self.mode)
            policy = spec.get("policy", self.policy)
        # Re-attach under new mode
        self("/action/detach", {"detach": True})
        self.mode = mode
        self.policy = policy
        self.controller = None
        self.paths.put("/state/mode", mode)
        self.paths.put("/state/policy", policy)
        if mode != "none":
            att = self("/action/attach", {"attach": True})
            if att.ok is not True:
                return att
        return ActionResult.success(
            "/action/set_mode", body={"set_mode": {"mode": mode, "policy": policy}}
        )

    def _act_wrap(self, body: Optional[Mapping[str, Any]]) -> ActionResult:
        spec = (body or {}).get("wrap") or {}
        if isinstance(spec, str):
            spec = {"question": spec}
        q = spec.get("question") or spec.get("prompt") or ""
        raw = bool(spec.get("raw", False))
        return self.session.wrap(q, raw=raw)

    def _act_generate(self, body: Optional[Mapping[str, Any]]) -> ActionResult:
        spec = (body or {}).get("generate") or {}
        if isinstance(spec, str):
            spec = {"prompt": spec}
        prompt = spec.get("prompt")
        question = spec.get("question")
        raw = bool(spec.get("raw", False))
        if prompt is None and question is not None:
            wrapped = self.session.wrap(question, raw=raw)
            if wrapped.ok is not True:
                return wrapped
            prompt = wrapped.body["wrap"]["prompt"]
        if not prompt:
            return ActionResult.failure(
                "/action/generate", "generate.body needs prompt or question"
            )

        kwargs = {
            k: v
            for k, v in spec.items()
            if k
            not in ("prompt", "question", "raw")
        }
        # Prefer long-lived controller; pass mode for one-shot ownership if detached
        if self.controller is None or not self.controller._attached:
            kwargs.setdefault("mode", self.mode)
            kwargs.setdefault("policy", self.policy)
            kwargs.setdefault("cfg", self.cfg)
            if self._bank is not None:
                kwargs.setdefault("threshold_bank", self._bank)
        else:
            kwargs.setdefault("mode", "none")

        # Epistemic manifesto defaults — feeling logged; text ≠ forced certainty
        kwargs.setdefault("return_epistemic", True)
        kwargs.setdefault("no_repeat_ngram_size", 3)
        kwargs.setdefault("repetition_penalty", 1.25)
        kwargs.setdefault("temperature", 0.7)
        kwargs.setdefault("top_p", 0.9)
        kwargs.setdefault("max_new_tokens", 150)
        kwargs.setdefault("dynamic_decode", True)
        kwargs.setdefault("abort_on_sink", True)

        result = self.generate_port.generate(prompt, **kwargs)
        if result.ok is True:
            payload = result.body.get("generate") or {}
            epi = payload.get("epistemic")
            if epi:
                self._last_epistemic = epi
                self.paths.put("/state/feeling", epi.get("feeling"))
                self.paths.put("/state/knowing", epi.get("knowing"))
                self.paths.put("/state/layer_flow", epi.get("layer_flow"))
                self.paths.put("/state/graphics", epi.get("graphics"))
            self.paths.put("/state/last_generate", result.body)
        return result

    def _act_validate(self, body: Optional[Mapping[str, Any]]) -> ActionResult:
        """Run ≠ filter on arbitrary text without regenerating."""
        from living_memory.epistemic import FeelingReport, validate_epistemic

        spec = (body or {}).get("validate") or {}
        if isinstance(spec, str):
            spec = {"text": spec}
        text = spec.get("text") or ""
        if not text:
            return ActionResult.failure("/action/validate", "validate.body needs text")
        feeling = None
        if self._last_epistemic and "feeling" in self._last_epistemic:
            feeling = FeelingReport(**{
                k: v
                for k, v in self._last_epistemic["feeling"].items()
                if k in FeelingReport.__dataclass_fields__
            })
        knowing = validate_epistemic(text, feeling)
        return ActionResult.success(
            "/action/validate", body={"validate": knowing.to_dict()}
        )


# isinstance / map alias the user asked for
LivingMemoryMap = LivingMemoryRoot

"""Concrete formings (adapters) that implement ports without peer reach-ins."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .interfaces import ActionResult, ControllerPort, GeneratePort, ModelPort, SessionPort


class Gpt2ModelPort:
    """ModelPort forming — architecture-aware load (GPT-2 / Qwen / Llama)."""

    def __init__(self) -> None:
        self._model = None
        self._tokenizer = None
        self._device: Optional[str] = None
        self._model_id: Optional[str] = None
        self._model_type: Optional[str] = None

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def load(self, model_id: str, device: Optional[str] = None) -> ActionResult:
        from agent.model import detect_model_type, load_causal_lm
        from living_memory.layers import describe_layer_stack

        try:
            model_type = detect_model_type(model_id)
            model, tok, dev = load_causal_lm(model_id, device=device)
            arch, n_layers = describe_layer_stack(model)
        except Exception as e:  # noqa: BLE001
            return ActionResult.failure(
                "/action/load", f"{type(e).__name__}: {e}"
            )
        self._model = model
        self._tokenizer = tok
        self._device = dev
        self._model_id = model_id
        self._model_type = model_type or arch
        return ActionResult.success(
            "/action/load",
            body={
                "load": {
                    "model_id": model_id,
                    "device": dev,
                    "model_type": self._model_type,
                    "architecture": arch,
                    "n_layers": n_layers,
                }
            },
        )

    def handles(self) -> ActionResult:
        if not self.loaded:
            return ActionResult.failure("/state/model", "model not loaded")
        return ActionResult.success(
            "/state/model",
            body={
                "model": self._model,
                "tokenizer": self._tokenizer,
                "device": self._device,
                "model_id": self._model_id,
                "model_type": self._model_type,
            },
        )

    def as_body(self) -> Dict[str, Any]:
        return {
            "loaded": self.loaded,
            "model_id": self._model_id,
            "model_type": self._model_type,
            "device": self._device,
        }


class SessionForming:
    """SessionPort forming — transcript only; no activation-scale fields."""

    def __init__(self, tokenizer=None, *, history_tokens: int = 768) -> None:
        self._tokenizer = tokenizer
        self._history_tokens = history_tokens
        self._session = None

    def bind_tokenizer(self, tokenizer) -> ActionResult:
        self._tokenizer = tokenizer
        self._session = None
        return ActionResult.success("/action/bind_session", body={"bind_session": True})

    def _ensure(self):
        if self._session is None:
            if self._tokenizer is None:
                raise RuntimeError("session has no tokenizer")
            from agent.session import ConversationSession

            self._session = ConversationSession(
                self._tokenizer, max_history_tokens=self._history_tokens
            )
        return self._session

    def wrap(self, question: str, *, raw: bool = False) -> ActionResult:
        from agent.session import wrap_log_entry

        prompt = wrap_log_entry(question, raw=raw)
        return ActionResult.success(
            "/action/wrap", body={"wrap": {"prompt": prompt}}
        )

    def extract(self, full_text: str, prompt: str) -> ActionResult:
        from agent.session import extract_reply

        reply = extract_reply(full_text, prompt)
        return ActionResult.success(
            "/action/extract", body={"extract": {"reply": reply}}
        )

    def add_turn(self, user: str, assistant: str) -> ActionResult:
        sess = self._ensure()
        sess.add_turn(user, assistant)
        return ActionResult.success(
            "/action/add_turn", body={"add_turn": {"user": user}}
        )

    def build_prompt(self, user_text: str, *, raw: bool = False) -> ActionResult:
        sess = self._ensure()
        if raw:
            sess.raw = True
        prompt = sess.build_prompt(user_text)
        return ActionResult.success(
            "/action/build_prompt", body={"build_prompt": {"prompt": prompt}}
        )

    def as_body(self) -> Dict[str, Any]:
        n = 0
        if self._session is not None:
            n = len(getattr(self._session, "turns", []) or [])
        return {"turns": n, "history_tokens": self._history_tokens}


class ControllerForming:
    """ControllerPort forming — owns LivingMemoryController lifecycle."""

    def __init__(self, model, cfg, *, mode: str = "keeper", policy: str = "soft", bank=None):
        from living_memory.hooks import LivingMemoryController

        self._controller = LivingMemoryController(
            model, mode=mode, cfg=cfg, policy=policy, threshold_bank=bank
        )
        self.mode = mode
        self.policy = policy
        self._attached = False

    def attach(self) -> ActionResult:
        if self._attached:
            return ActionResult.success("/action/attach", body={"attach": True})
        self._controller.attach()
        self._attached = True
        return ActionResult.success("/action/attach", body={"attach": True})

    def detach(self) -> ActionResult:
        if self._attached:
            self._controller.detach()
            self._attached = False
        return ActionResult.success("/action/detach", body={"detach": True})

    def reset(self) -> ActionResult:
        self._controller.reset_trackers()
        return ActionResult.success("/action/reset", body={"reset": True})

    @property
    def raw(self):
        return self._controller

    def as_body(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "policy": self.policy,
            "attached": self._attached,
        }


class GenerateForming:
    """GeneratePort forming — calls generate_text with injected controller only."""

    def __init__(self, model_port: ModelPort, controller: Optional[ControllerPort] = None):
        self._model_port = model_port
        self._controller = controller

    def bind_controller(self, controller: ControllerPort) -> ActionResult:
        self._controller = controller
        return ActionResult.success(
            "/action/bind_generate", body={"bind_generate": True}
        )

    def generate(self, prompt: str, **kwargs: Any) -> ActionResult:
        from agent.generate import generate_text

        handles = self._model_port.handles()
        if handles.ok is not True:
            return ActionResult.failure("/action/generate", handles.error)
        h = handles.body
        mode = kwargs.pop("mode", "none")
        # When a long-lived controller is attached, force mode none so hooks
        # are not double-attached (same pattern as scripts/chat.py).
        controller = None
        if self._controller is not None and getattr(self._controller, "_attached", False):
            mode = "none"
            controller = getattr(self._controller, "raw", None)

        try:
            text = generate_text(
                h["model"],
                h["tokenizer"],
                prompt,
                mode=mode,
                controller=controller,
                device=h["device"],
                **kwargs,
            )
        except Exception as e:  # noqa: BLE001
            return ActionResult.failure(
                "/action/generate", f"{type(e).__name__}: {e}"
            )

        if isinstance(text, dict):
            out = text
        else:
            out = {"text": text}
        return ActionResult.success(
            "/action/generate", body={"generate": out}
        )

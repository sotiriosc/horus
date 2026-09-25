"""Independent option/evidence ordering at the finite Explorer proposal boundary."""

from dataclasses import asdict
import json
from experiments.model_explorer_integration_v0.adapter import (
    ACTIONS, MODEL, OPTIONS, ModelExplorerAdapter, visible_state,
)
from experiments.model_explorer_semantic_prior_study_v0.adapter import SYSTEM, LocalModel

def render(state, records, descriptor):
    mapping = descriptor["surface_to_underlying"]
    inverse = {action: label for label, action in mapping.items()}
    order = descriptor["underlying_option_order"]
    values = {a: [r.consequence for r in records if r.pre_state == state and r.action == a]
              for a in order}
    if not all(values.values()):
        raise ValueError("an offered action lacks authorized experience")
    return dict(state=state, available_actions=[inverse[a] for a in order],
        VERIFIED_PRIOR_OUTCOMES=[dict(surface_action=inverse[a], observed_consequences=values[a]) for a in descriptor["underlying_evidence_order"]])


def parse_surface(raw, descriptor):
    token = raw.strip() if isinstance(raw, str) else None
    if token in descriptor["surface_option_order"]:
        return token, descriptor["surface_to_underlying"][token], None
    if token in descriptor["surface_to_underlying"]:
        return None, None, "out_of_pair"
    return None, None, "malformed_or_unknown_label"


class SurfaceAdapter(ModelExplorerAdapter):
    def __init__(self, *args, descriptor, **kwargs):
        super().__init__(*args, **kwargs)
        self.descriptor = descriptor

    def choose(self, state, audited_records):
        records = list(audited_records)
        canonical = visible_state(state, records, self.coordinates)
        shown = render(state, records, self.descriptor)
        prompt = json.dumps(shown, sort_keys=True, separators=(",", ":"))
        assert shown == self.descriptor["payload"] and prompt == self.descriptor["exact_prompt"]
        raw, metadata = self.transport.generate(prompt, self.seed)
        surface, action, failure = parse_surface(raw, self.descriptor)
        self.observation = dict(model=MODEL, system=SYSTEM, options={**OPTIONS,"seed":self.seed},
            input=canonical, model_visible_input=shown, exact_prompt=prompt,
            surface_to_underlying=self.descriptor["surface_to_underlying"],
            authorized_relevant_records=[asdict(r) for r in records if r.pre_state==state],
            raw_output=raw, parsed_surface_proposal=surface, parsed_action=action,
            parse_failure=failure, response_metadata=metadata)
        return action if action is not None else "INVALID_MODEL_PROPOSAL"


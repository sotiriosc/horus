from itertools import permutations
from experiments.model_map_proposal_v0.adapter import SYSTEM as MAP_SYSTEM, MODEL, OPTIONS as JSON_OPTIONS
from experiments.model_recovery_proposal_v1.adapter import SYSTEM as RECOVERY_SYSTEM

EXPLORER_SYSTEM = 'Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. When evidence is insufficient, you may choose an UNTRIED action to gather information. Reply with exactly one allowed action and no explanation.'
SYSTEMS = dict(Explorer=EXPLORER_SYSTEM, Map=MAP_SYSTEM, Recovery=RECOVERY_SYSTEM)
OPTIONS = {r:{**JSON_OPTIONS,'num_predict':16 if r=='Explorer' else 32} for r in SYSTEMS}
ACTIONS = ('ADVANCE','HOLD','RETREAT')


def schedule():
    return [dict(episode=family*6+j,family=f'O{family+1}',mapping_index=j,
                 mapping=dict(zip(tokens,actions)),base_seed=80001+j)
            for family,tokens in enumerate((('K1','K2','K3'),('Q7','M4','Z2')))
            for j,actions in enumerate(permutations(ACTIONS))]


def seed(descriptor,decision,role):
    return descriptor['base_seed']+100*decision+dict(Explorer=1,Map=2,Recovery=3)[role]

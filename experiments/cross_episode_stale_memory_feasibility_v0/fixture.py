"""External target-only consequence intervention; all authority is inherited."""
from dataclasses import replace
from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeWorld,EpisodeController


def target_law(actual,consequence):
    if type(consequence) is not int or consequence not in (-1,1):raise ValueError('registered consequence required')
    return replace(actual,consequence=consequence) if (actual.pre_state,actual.action)==(0,'ADVANCE') else actual


class TargetWorld(EpisodeWorld):
    def __init__(self,state):
        super().__init__(state);self.target_consequence=1;self.intervention_count=0
    def change_target(self):
        # Harness-only operation on the published external fixture, after reset.
        if self.execution_count!=3 or self.state!=0 or self.intervention_count:
            raise ValueError('registered post-initialization intervention required')
        self.target_consequence=-1;self.intervention_count+=1
    def execute(self,epoch,transaction_id,action):
        actual=super().execute(epoch,transaction_id,action)
        self.fixture.last_actual=target_law(actual,self.target_consequence)
        return self.fixture.last_actual


class Controller(EpisodeController):
    def _make_world(self,state):return TargetWorld(state)

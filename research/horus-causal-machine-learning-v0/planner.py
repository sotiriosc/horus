"""Pure depth-one beam planner: no simulator, hidden state, or oracle access."""
BEAM_WIDTH=4
DEPTH=1
ACTION_BUDGET=4
MATERIAL_ACTION_REGRESSION=0.5

def choose(visible,target,predictions):
 assert set(visible)=={'actuators','sensors','history','candidate_action'}
 assert set(target)==set(visible['sensors']) and len(predictions)==len(visible['actuators'])==BEAM_WIDTH
 # Invalid schemas have infinite predicted distance. Ties use the prospectively
 # provided actuator order. No retries, repairs, oracle, or learned planner.
 candidates=[]
 for i,prediction in enumerate(predictions):
  distance=sum(prediction[s]!=target[s] for s in visible['sensors']) if prediction is not None else float('inf')
  candidates.append((distance,i))
 return visible['actuators'][min(candidates)[1]]

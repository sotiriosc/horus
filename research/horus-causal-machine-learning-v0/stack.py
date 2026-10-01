"""Reuse the published HF/NF4 inference/training implementation unchanged."""
import importlib.util,sys
from functools import lru_cache
from common import *
spec=importlib.util.spec_from_file_location('published_qlora_runtime',OLD/'runtime.py');runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
sys.path.insert(0,str(OLD))
import data as temporal_data
import analysis as temporal_analysis
sys.path.remove(str(OLD))
from safetensors.torch import load_file
from peft import set_peft_model_state_dict

@lru_cache(maxsize=None)
def artifact(arm):
 return json.loads(((OLD/'M1-artifact-freeze.json') if arm=='C0' else P/(arm+'-artifact-freeze.json')).read_bytes())
def path(arm):return C0_FILE if arm=='C0' else ADAPTERS/arm/'adapter_model.safetensors'
def identity(arm):return C0_SHA if arm=='C0' else artifact(arm)['adapter_files']['adapter_model.safetensors']['sha256']
def attach(model,arm):
 assert filehash(path(arm))==identity(arm);set_peft_model_state_dict(model,load_file(str(path(arm))));assert runtime.fingerprints(model,True)==artifact(arm)['adapter_parameter_fingerprints']
def load(arm):
 model,tok=runtime.load();assert runtime.fingerprints(model,False)==json.loads((OLD/'M0-base-fingerprints.json').read_bytes());attach(model,arm);return model,tok

"""Static import closure and legacy-reference inventory; no experiment execution."""
import argparse,ast,hashlib,json,subprocess
from pathlib import Path

def build(root):
    files={str(p.relative_to(root)).removesuffix('.py').replace('/','.'):p for p in (root/'experiments').rglob('*.py')}
    # Package initialization participates in ordinary Python imports too.
    def resolve(m):
        return m if m in files else m+'.__init__' if m+'.__init__' in files else None
    edges={};sites=[]
    for name,p in files.items():
        tree=ast.parse(p.read_text());links=set()
        for n in ast.walk(tree):
            if not isinstance(n,(ast.Import,ast.ImportFrom)):continue
            modules=[]
            if isinstance(n,ast.Import):modules=[a.name for a in n.names]
            else:
                parent=name.split('.')[:-1]
                if n.level:prefix='.'.join(parent[:len(parent)-n.level+1]);base=prefix+('.'+n.module if n.module else '')
                else:base=n.module or ''
                modules=[base]+[base+'.'+a.name for a in n.names]
            resolved={resolve(m) for m in modules};resolved.discard(None)
            for m in list(resolved):
                parts=m.split('.')
                for i in range(1,len(parts)):
                    init='.'.join(parts[:i])+'.__init__'
                    if init in files:resolved.add(init)
            links.update(resolved)
            sites.append(dict(file=str(p.relative_to(root)),line=n.lineno,statement=ast.get_source_segment(p.read_text(),n),resolved=sorted(resolved)))
        edges[name]=sorted(links)
    def closure(starts):
        seen=set();todo=list(starts)
        while todo:
            n=todo.pop()
            if n in seen:continue
            seen.add(n);todo.extend(edges.get(n,[]))
        return sorted(seen)
    def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
    core=closure(['experiments.state_recovery_authorizer_status_binding_v1.framework'])
    binding=closure(['experiments.composition_input_bindings_v1.adapters','experiments.model_recovery_proposal_v1.adapter'])
    excluded={'experiments.base_framework_v1.source_a','experiments.base_framework_v1.source_b','experiments.base_framework_v2.witness_c','experiments.base_framework_v2.campaign','experiments.base_framework_v2.framework'}
    assert not set(core+binding)&excluded
    def metadata(n):
        p=files[n];path=str(p.relative_to(root));return dict(module=n,path=path,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),last_change_commit=git('log','-1','--format=%H','--',path),imports=edges[n],package_initializer=n.endswith('.__init__'))
    manifest=dict(baseline_parent=git('rev-parse','f44bd60'),entry_point='experiments.state_recovery_authorizer_status_binding_v1.framework.StatusBoundFramework',
        core_files=[metadata(n) for n in core],finite_proposal_and_unknown_projection_files=[metadata(n) for n in binding if n not in core],
        forbidden_reality_authorities=sorted(excluded),
        constructor_contract='Caller supplies a registered ExternalExecutionBoundary.reader() from the trusted actual execution emitter. Constructor state and epoch are trusted finite driver values. Models receive serialized values only; no core/source/registry handles.',
        optional_profiles={'cross_episode_initialization':closure(['experiments.cross_episode_initialization_boundary_v1.boundary']),
                          'three_role_R1_driver':closure(['experiments.model_proposal_role_composition_v2.runtime']),
                          'read_only_Map_guided_proposals':closure(['experiments.map_guided_explorer_interface_v0.interface'])})
    manifest['optional_profile_files']={k:[metadata(n) for n in v] for k,v in manifest['optional_profiles'].items()}
    old=json.loads((root/'research/horus-end-to-end-leakage-and-hardcoding-audit-v0/inventory.json').read_text());idx=next(i for i,x in enumerate(old) if x['study']=='realized_event_grounding_v0');studies={x['study'] for x in old[idx:]};post=[]
    for x in old[idx:]:
        starts=[n for n in files if n.startswith('experiments.'+x['study']+'.')];deps=closure(starts)
        relevant=[s for s in sites if s['file'].split('/')[1]==x['study'] and any(t in s['statement'] for t in ('base_framework_v1','base_framework_v2','source_a','source_b','witness_c','make_evidence','model_explorer_integration_v0.campaign','contradiction_revision_v0.preflight','StateRecoveryFramework','RealizedEventFramework','StatusBoundFramework'))]
        # One shortest static import path per forbidden module; runtime meaning is separately reviewed.
        def import_path(target):
            queue=[(n,[n]) for n in starts];visited=set()
            while queue:
                n,path=queue.pop(0)
                if n==target:return path
                if n in visited:continue
                visited.add(n);queue.extend((m,path+[m]) for m in edges.get(n,[]))
            return None
        post.append(dict(study=x['study'],all_python_import_closure=deps,direct_relevant_imports=relevant,legacy_authority_modules_in_static_closure=sorted(set(deps)&excluded),static_paths_to_legacy_modules={n:import_path(n) for n in sorted(set(deps)&excluded)}))
    # Enumerate textual use sites too: aliases/observer references may not be imports.
    refs=[]
    needles=('source_a.observe','source_b.observe','witness_c.observe','make_evidence','submit_receipt','CrossSourceStateAuthorizer','StateRecoveryFramework','CrossSourceFramework')
    for n,p in files.items():
        if p.parent.name not in studies:continue
        for i,line in enumerate(p.read_text().splitlines(),1):
            if any(t in line for t in needles):refs.append(dict(file=str(p.relative_to(root)),line=i,text=line.strip()))
    return manifest,dict(post_grounding_checkpoints=post,use_sites=refs,scope='Static import reachability is not runtime authority. All-python closure includes tests, regression helpers and dormant constants. Report assigns actual active-path meaning separately.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root,uses=build(a.repository);a.output.mkdir(exist_ok=True)
    (a.output/'clean-root-manifest.json').write_text(json.dumps(root,indent=2,sort_keys=True)+'\n');(a.output/'legacy-import-inventory.json').write_text(json.dumps(uses,indent=2,sort_keys=True)+'\n')
    print('Core implementation files',sum(not x['package_initializer'] for x in root['core_files']),'additional finite binding implementation files',sum(not x['package_initializer'] for x in root['finite_proposal_and_unknown_projection_files']))
    for x in root['core_files']+root['finite_proposal_and_unknown_projection_files']:
        if not x['package_initializer']:print(x['path'],x['last_change_commit'][:7])
if __name__=='__main__':main()

"""Read actual native mate entities, rather than infer connections from names."""
from real_limit_mates import *
robot=sys.argv[1];s,d,a,m,build,path=connect_robot(robot);byname={r['name2']:r['id'] for r in build['components']};instances={i['id']:i for i in m['instances']};suffix='_Encoder_L1' if robot=='leader' else '_MG996R_R3';rows=[]
for name,f in mate_features(d).items():
    mate=typed(f.GetSpecificFeature2(),'IMate2');actual=[byname[typed(typed(mate.MateEntity(k),'IMateEntity2').ReferenceComponent,'IComponent2').Name2] for k in range(mate.GetMateEntityCount())]
    if name.startswith('Rigid_'):
        hardware=name.removeprefix('Rigid_');item=instances[hardware];owner=next(i for i in m['instances'] if i['node']==item['node'] and i['part'].endswith(suffix));expected=[owner['id'],hardware]
    else:
        assert name.startswith('J'),name;j=int(name[1:name.index('_')])-1;n=next(n for n in m['nodes'] if n['joint']==j);dat=next(x for x in m['nodes'] if x['id']==n['parent']);p=next(i for i in m['instances'] if i['node']==dat['parent'] and i['part'].endswith(suffix));c=next(i for i in m['instances'] if i['node']==n['id'] and i['part'].endswith(suffix));expected=[p['id'],c['id']]
    row={'feature':name,'actual_component_entities':actual,'source_expected_components':expected,'pass':set(actual)==set(expected) and len(actual) in ([2,3] if name.startswith('J') else [2]),'native_error':f.GetErrorCode2()};rows.append(row);assert row['pass'] and row['native_error'][0]==0,row
(ROOT/f'verification/{robot}_native_mate_connections.json').write_text(json.dumps({'classification':'CAD MEASURED native mate entity components, compared with source rigid groups and joint adjacency','mates':rows,'pass':all(r['pass'] for r in rows)},indent=2));print(robot,len(rows),'native mate connection pairs passed.')

import bpy,json
from pathlib import Path
from mathutils import Vector
sc=bpy.context.scene
result={'lights':[], 'objects':[], 'materials':[m.name for m in bpy.data.materials], 'world':[]}
for o in bpy.data.objects:
 if o.type=='LIGHT': result['lights'].append(dict(name=o.name,energy=o.data.energy,color=list(o.data.color),type=o.data.type,position=list(o.location)))
 if o.name.startswith(('Bench','Reference','Woven','Linen sofa','Soft low sofa','Folded','Freestanding','Bath','Stone vanity','Vanity','Handmade wash','Compact','Concealed','Sunward','Forest courtyard','Deck / dark')):
  b=[o.matrix_world@Vector(v) for v in o.bound_box]
  result['objects'].append(dict(name=o.name,loc=list(o.location),size=list(o.dimensions),bounds=[[min(v[i] for v in b) for i in range(3)],[max(v[i] for v in b) for i in range(3)]],materials=[m.name for m in o.data.materials] if hasattr(o.data,'materials') else []))
for n in sc.world.node_tree.nodes:
 result['world'].append(dict(type=n.type,name=n.name,inputs={i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value') and i.type!='SHADER'}))
Path(__file__).resolve().parent.parent.joinpath('review/base_inspection.json').write_text(json.dumps(result,indent=2))
print('INSPECTED',len(result['objects']))

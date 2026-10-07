"""Read saved geometric and material evidence without rebuilding or saving the scene."""
import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector

OUT=Path(__file__).resolve().parent.parent


def bounds(obj):
    points=[obj.matrix_world@Vector(v) for v in obj.bound_box]
    return [[min(p[k] for p in points) for k in range(3)],
            [max(p[k] for p in points) for k in range(3)]]


def main():
    prefixes=('V4 / separate sofa seat','V4 / tactile handwoven rug yarns',
              'V4 / floating oak vanity','Bath mirror','V4 / solid oak bath bridge',
              'V4 / bath linen over bridge','V4 / open bronze rain gutter',
              'V4 / deck subframe','V4 / grounded side garden retaining edge',
              'V4 / rolled terry towel','V4 / towel spiral woven hem')
    selected=[]
    for ob in bpy.data.objects:
        if ob.name.startswith(prefixes):
            selected.append(dict(name=ob.name,type=ob.type,bounds=bounds(ob),
                vertices=len(ob.data.vertices) if ob.type=='MESH' else None,
                splines=len(ob.data.splines) if ob.type=='CURVE' else None,
                materials=[m.name for m in ob.data.materials],
                modifiers=[dict(type=m.type,render=m.show_render) for m in ob.modifiers]))
    textures={}
    for name in ('Retreat / weathered cedar grain','Retreat / silvered teak decking'):
        mat=bpy.data.materials[name]
        textures[name]=[dict(image=n.image.name,packed=bool(n.image.packed_file),projection=n.projection,
                             vector_source=n.inputs['Vector'].links[0].from_node.type)
                        for n in mat.node_tree.nodes if n.type=='TEX_IMAGE']
    trunk_meshes={ob.data.name:dict(vertices=len(ob.data.vertices),polygons=len(ob.data.polygons))
                  for ob in bpy.data.objects if ob.type=='MESH' and 'complete trunk and branching' in ob.name}
    dynamics=[]
    for ob in bpy.data.objects:
        if ob.type=='MESH' and ob.data.shape_keys and ob.name.startswith(('Bedroom / full length','Forest / fine','Porch / individual')):
            keys=ob.data.shape_keys
            dynamics.append(dict(object=ob.name,keys=[k.name for k in keys.key_blocks],
                expressions=[f.driver.expression for f in keys.animation_data.drivers] if keys.animation_data else []))
    report=dict(scene_sha256=hashlib.file_digest(Path(bpy.data.filepath).open('rb'),'sha256').hexdigest(),
                selected_geometry=selected,timber_mapping=textures,trunk_meshes=trunk_meshes,
                cloth_and_plant_animation=dynamics,
                replaced_objects_still_present=[o.name for o in bpy.data.objects if o.name.startswith(
                    ('Stone vanity unit','Folded bath towel','Low courtyard garden wall','Deck / dark substructure'))],
                scope='Saved editable data and dimensions; visual quality is reviewed in rendered images separately.')
    (OUT/'review/model_inspection.json').write_text(json.dumps(report,indent=2))
    print('MODEL_INSPECTED',len(selected),'selected geometry objects;',len(trunk_meshes),'shared trunk meshes',flush=True)


if __name__=='__main__':
    main()

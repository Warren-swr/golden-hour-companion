"""Rechoreograph the preserved v6 model and bind its extended water cache."""
import hashlib
import json
import sys
from pathlib import Path

import bpy

HERE=Path(__file__).resolve().parent;OUT=HERE.parent
sys.path.insert(0,str(HERE))
import story
from film import FRAMES,FPS,SHOT_COUNT,DURATION


def model_fingerprint():
    rows=[]
    for ob in sorted(bpy.data.objects,key=lambda x:x.name):
        if ob.type=='CAMERA':continue
        rows.append((ob.name,ob.type,ob.data.name if ob.data else None,
                     [round(v,7) for row in ob.matrix_world for v in row],
                     len(ob.data.vertices) if ob.type=='MESH' else None,
                     len(ob.data.polygons) if ob.type=='MESH' else None))
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()


def main():
    source=OUT/'source/v6_scene.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source))
    sc=bpy.context.scene
    sc.frame_set(1);bpy.context.view_layer.update()
    before=model_fingerprint()
    story.build()
    sc.frame_set(1);bpy.context.view_layer.update()
    after=model_fingerprint()
    assert before==after,'Camera revision unexpectedly changed model data or transforms'
    sc['production_revision']='forest_retreat_v7 / faster movement and three continuous long takes'
    sc['render_contract']=f'{FRAMES} native Cycles frames, 2160 square, {FPS} fps, {DURATION:g} seconds, {SHOT_COUNT} shots'
    for ob in bpy.data.objects:
        for mod in ob.modifiers:
            if mod.type=='MESH_CACHE':
                mod.filepath='//cache/'+Path(mod.filepath).name
                mod.name=f'Physical basin waves / baked {DURATION:g} seconds'
                ob['cache_frame_count']=FRAMES
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Golden_Hour_Forest_Retreat.blend'),compress=True,relative_remap=False)
    result=dict(blender=bpy.app.version_string,source_scene_sha256=hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),
                model_fingerprint_before=before,model_fingerprint_after=after,
                objects=len(bpy.data.objects),vertices=sum(len(m.vertices) for m in bpy.data.meshes),
                polygons=sum(len(m.polygons) for m in bpy.data.meshes),
                cameras=[m.camera.name for m in sc.timeline_markers],frames=FRAMES,fps=FPS,shots=SHOT_COUNT)
    (OUT/'review/scene_inventory.json').write_text(json.dumps(result,indent=2))
    print('V7_BUILD_COMPLETE',flush=True)


if __name__=='__main__':main()

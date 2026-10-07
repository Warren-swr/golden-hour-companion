"""Final foliage refinement on the preserved v4 scene; all nine cameras retained."""
import json
import sys
from pathlib import Path

import bpy

HERE=Path(__file__).resolve().parent;OUT=HERE.parent
sys.path.insert(0,str(HERE))
import polish_foliage
import story


def main():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'source/v4_scene.blend'))
    report=polish_foliage.build()
    story.build()
    sc=bpy.context.scene
    sc['production_revision']='forest_retreat_v5 / final botanical surface and geometry refinement'
    sc['render_contract']='1008 native Cycles frames, 2160 square, 24 fps, 42 seconds, 9 shots'
    sc.frame_set(1)
    for obj in bpy.data.objects:
        for mod in obj.modifiers:
            if mod.type=='MESH_CACHE':mod.filepath='//cache/'+Path(mod.filepath).name
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Golden_Hour_Forest_Retreat.blend'),compress=True,relative_remap=False)
    result=dict(blender=bpy.app.version_string,refinement=report,objects=len(bpy.data.objects),
                vertices=sum(len(m.vertices) for m in bpy.data.meshes),
                polygons=sum(len(m.polygons) for m in bpy.data.meshes),
                cameras=[m.camera.name for m in sc.timeline_markers],frames=sc.frame_end,fps=sc.render.fps)
    (OUT/'review/scene_inventory.json').write_text(json.dumps(result,indent=2))
    print('V5_BUILD_COMPLETE',flush=True)


if __name__=='__main__':main()

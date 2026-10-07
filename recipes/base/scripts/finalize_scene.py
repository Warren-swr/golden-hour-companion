"""Set portable opening state and production defaults without altering geometry."""
import bpy
from pathlib import Path
OUT=Path(__file__).resolve().parent.parent
scene=bpy.context.scene
scene.frame_set(1)
# Normalize joinery clearances for scene files from the pre-final v08 build.
for obj in bpy.data.objects:
    if 'opal bulb' in obj.name:
        # The lamp's point emitter sits inside this visible opal bulb surface.
        obj.visible_shadow=False
    if obj.name.startswith('Cabinet drawer with shadow reveal'):
        for old_z,new_z,height in ((.77,.78,.27),(.49,.486,.30),(.20,.194,.272)):
            if abs(obj.location.z-old_z)<.001:
                old_height=max(v.co.z for v in obj.data.vertices)-min(v.co.z for v in obj.data.vertices)
                for vertex in obj.data.vertices:
                    vertex.co.z*=height/old_height
                obj.location.z=new_z
    if obj.name.startswith('Inset bronze pull'):
        for old_z,new_z in ((.817,.827),(.537,.533),(.247,.241)):
            if abs(obj.location.z-old_z)<.001:
                obj.location.z=new_z
scene.cycles.samples=192
scene.cycles.adaptive_threshold=.015
scene['production_revision']='v12 / dense forest, unified low sunset, kitchen interlude and wide forest finale'
scene['fiber_geometry']='170000 cinnamon loops, 18000 saffron loops, 42000 fine wool flyaways'
scene['render_contract']='Native square 2160 x 2160 / 24 fps / 864 source frames / fixed AgX exposure'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.shading.type='SOLID'
        area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'golden_hour_companion.blend'),compress=True)

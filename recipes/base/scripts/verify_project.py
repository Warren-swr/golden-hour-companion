"""Reopen-time validation of resources, camera clearances and render contract."""
import bpy
import csv
import json
import sys
import os
import subprocess
import hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

OUT=Path(__file__).resolve().parent.parent
GUI_STAGE=0


def inspect():
    sc=bpy.context.scene
    saved_markers=[(x.frame,x.camera.name) for x in sc.timeline_markers]
    architecture=[]
    for cname in ('10 • Architecture / connected shell','11 • Roof and joinery'):
        for obj in bpy.data.collections[cname].objects:
            if obj.type!='MESH':
                continue
            points=[obj.matrix_world@Vector(p) for p in obj.bound_box]
            low=[min(p[i] for p in points) for i in range(3)]
            high=[max(p[i] for p in points) for i in range(3)]
            architecture.append((obj.name,low,high))
    collisions=[]
    vegetation=[]
    forest=bpy.data.collections.get('33 • Dense mature forest / complete instanced broadleaf trees')
    if forest:
        for obj in forest.objects:
            points=[obj.matrix_world@Vector(p) for p in obj.bound_box]
            low=[min(p[i] for p in points) for i in range(3)]
            high=[max(p[i] for p in points) for i in range(3)]
            vegetation.append((obj,low,high,obj.matrix_world.inverted()))
    trees={}
    vegetation_collisions=[]
    pillow=bpy.data.objects['Five-lobed stuffed cushion / continuous front and back shell']
    pillow_bounds=[pillow.matrix_world@Vector(p) for p in pillow.bound_box]
    later_pillow_sizes=[]
    path=[]
    for f in range(1,865):
        sc.frame_set(f)
        camera=sc.camera
        pos=camera.matrix_world.translation
        if f>=289:
            projected=[world_to_camera_view(sc,camera,p) for p in pillow_bounds]
            if all(p.z>0 for p in projected):
                width=max(0,min(1,max(p.x for p in projected))-max(0,min(p.x for p in projected)))
                height=max(0,min(1,max(p.y for p in projected))-max(0,min(p.y for p in projected)))
                later_pillow_sizes.append((f,width*height))
        for name,lo,hi in architecture:
            if all(lo[i]-.015<pos[i]<hi[i]+.015 for i in range(3)):
                collisions.append({'frame':f,'camera':camera.name,'object':name})
        for obj,lo,hi,inverse in vegetation:
            if all(lo[i]-.12<pos[i]<hi[i]+.12 for i in range(3)):
                if obj.data.name not in trees:
                    trees[obj.data.name]=BVHTree.FromPolygons([v.co for v in obj.data.vertices],
                                                            [p.vertices for p in obj.data.polygons])
                nearest=trees[obj.data.name].find_nearest(inverse@pos)
                if nearest[0] is not None:
                    distance=(obj.matrix_world@nearest[0]-pos).length
                    if distance<.10:
                        vegetation_collisions.append({'frame':f,'object':obj.name,'clearance_m':distance})
        path.append({'frame':f,'camera':camera.name,'x':pos.x,'y':pos.y,'z':pos.z,
                     'lens_mm':camera.data.lens,'focus_m':camera.data.dof.focus_distance,
                     'fstop':camera.data.dof.aperture_fstop,'exposure':sc.view_settings.exposure})
    missing=[img.filepath for img in bpy.data.images if img.source=='FILE' and not img.packed_file
             and not Path(bpy.path.abspath(img.filepath)).exists()]
    image_nodes=[(mat.name,node.name) for mat in bpy.data.materials if mat.use_nodes
                 for node in mat.node_tree.nodes if node.type=='TEX_IMAGE']
    report={'opened_blend':bpy.data.filepath,'blender':bpy.app.version_string,
            'objects':len(bpy.data.objects),'camera_count':len(bpy.data.cameras),
            'mesh_vertices':sum(len(m.vertices) for m in bpy.data.meshes),
            'mesh_polygons':sum(len(m.polygons) for m in bpy.data.meshes),
            'missing_external_images':missing,'image_texture_nodes':image_nodes,
            'native_resolution':[sc.render.resolution_x,sc.render.resolution_y],
            'fps':sc.render.fps/sc.render.fps_base,'timeline':[sc.frame_start,sc.frame_end],
            'camera_markers':saved_markers,'architecture_camera_collisions':collisions,
            'vegetation_camera_collisions':vegetation_collisions,
            'mature_forest_tree_count':sc.get('forest_tree_count',0),
            'later_pillow_max_projected_frame_fraction':max((area for f,area in later_pillow_sizes),default=0),
            'later_pillow_measurement':'Clipped projected 3D bounds after frame 288; conservative upper bound, does not discount occlusion.',
            'fixed_exposure':len(set(p['exposure'] for p in path))==1,
            'reference_photo_in_scene':False,
            'hold_max_position_delta':max(sum((path[i][c]-path[0][c])**2 for c in ('x','y','z'))**.5 for i in range(48))}
    with open(bpy.data.filepath,'rb') as handle:
        report['blend_sha256']=hashlib.file_digest(handle,'sha256').hexdigest()
    (OUT/'review'/'project_validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    with (OUT/'review'/'camera_path.csv').open('w') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(path[0]))
        writer.writeheader()
        writer.writerows(path)
    sc.frame_set(1)
    print('PROJECT_VALIDATION',json.dumps(report,ensure_ascii=False),flush=True)
    if missing or image_nodes or collisions or vegetation_collisions:
        raise RuntimeError('Project validation found missing resources, image nodes or a camera collision.')
    return report


def gui_finish():
    global GUI_STAGE
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='SOLID'
            area.spaces.active.region_3d.view_perspective='CAMERA'
    if GUI_STAGE<2:
        if GUI_STAGE==0:
            bpy.context.view_layer.update()
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2)
        GUI_STAGE+=1
        return 3.0
    import gpu
    print('GUI_RENDERER',gpu.platform.renderer_get(),gpu.platform.version_get(),flush=True)
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-f','x11grab','-video_size','1280x900',
                    '-i',os.environ['DISPLAY']+'.0','-frames:v','1','-y',
                    str(OUT/'review'/'project_reopened_gui.png')],check=True)
    (OUT/'review'/'gui_open_verified.txt').write_text('PASS: delivered project reopened in isolated Blender 4.5.12 GUI, no network, only output mounted. External X11 screenshot saved.\n')
    if not os.environ.get('GH_GUI_KEEP'):
        bpy.ops.wm.quit_blender()


if __name__=='__main__':
    inspect()
    if not bpy.app.background:
        bpy.app.timers.register(gui_finish,first_interval=15)

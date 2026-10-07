"""Open a relocated bundle and evaluate packed images and cached water animation."""
import hashlib
import json
import struct
import sys
from pathlib import Path

import bpy

OUT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(OUT/'scripts'))
from film import FRAMES,SHOT_COUNT


def main():
    scene_file=Path(bpy.data.filepath).resolve()
    root=scene_file.parent
    missing=[];images=[];caches=[]
    for image in bpy.data.images:
        if image.source!='FILE':continue
        if not image.packed_file and not Path(bpy.path.abspath(image.filepath)).exists():
            missing.append(image.name)
        images.append(dict(name=image.name,packed=bool(image.packed_file),size=list(image.size),
                           first_pixel=float(image.pixels[0]) if len(image.pixels) else None))
    water=None
    for ob in bpy.data.objects:
        for mod in ob.modifiers:
            if mod.type!='MESH_CACHE':continue
            path=Path(bpy.path.abspath(mod.filepath)).resolve()
            with path.open('rb') as handle:
                frames,vertices=struct.unpack('>ii',handle.read(8))
            caches.append(dict(path=str(path),inside_bundle=path.is_relative_to(root),frames=frames,vertices=vertices))
            water=ob
    positions=[]
    sample_frames=(1,600,FRAMES-1,FRAMES)
    for frame in sample_frames:
        bpy.context.scene.frame_set(frame)
        evaluated=water.evaluated_get(bpy.context.evaluated_depsgraph_get())
        verts=evaluated.data.vertices
        indices=[int((len(verts)-1)*i/16) for i in range(17)]
        positions.append([tuple(verts[i].co) for i in indices])
    delta=max(abs(a-b) for va,vb in zip(positions[0],positions[1]) for a,b in zip(va,vb))
    tail_delta=max(abs(a-b) for va,vb in zip(positions[-2],positions[-1]) for a,b in zip(va,vb))
    result=dict(scene_sha256=hashlib.file_digest(scene_file.open('rb'),'sha256').hexdigest(),
                opened_from=str(root),missing_images=missing,images=images,caches=caches,
                camera_markers=len(bpy.context.scene.timeline_markers),
                sampled_water_vertex_change_metres=delta,
                sample_frames=sample_frames,final_frame_water_change_metres=tail_delta,
                scope='Relocated extracted bundle opened in Blender; packed pixels loaded; cached water evaluated through the final frame.')
    (OUT/'review/portable_scene_validation.json').write_text(json.dumps(result,indent=2))
    assert not missing and all(im['packed'] and im['first_pixel'] is not None for im in images)
    assert caches and all(c['inside_bundle'] and c['frames']>=FRAMES for c in caches)
    assert delta>1e-5 and tail_delta>1e-5 and result['camera_markers']==SHOT_COUNT
    print('PORTABLE_SCENE_VALIDATED',flush=True)


if __name__=='__main__':
    main()

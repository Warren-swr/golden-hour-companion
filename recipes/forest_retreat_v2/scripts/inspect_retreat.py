"""Reopen the actual blend: validate assets, all camera frames and moving water."""
import csv
import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = Path(__file__).resolve().parent.parent


def main():
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    geometry = []
    prefixes = ('10 ', '11 ', '20 ', '21 ', '22 ', '50 ', '51 ', '52 ', '53 ', '54 ', '57 ', '58 ')
    for obj in bpy.data.objects:
        if obj.type != 'MESH' or not any(c.name.startswith(prefixes) for c in obj.users_collection):
            continue
        pts = [obj.matrix_world @ Vector(p) for p in obj.bound_box]
        geometry.append((obj, [min(v[i] for v in pts) for i in range(3)], [max(v[i] for v in pts) for i in range(3)]))
    collisions, path = [], []
    trees = {}
    for frame in range(1, 1057):
        scene.frame_set(frame)
        camera = scene.camera
        pos = camera.matrix_world.translation.copy()
        for obj, lo, hi in geometry:
            if all(lo[i] - .045 <= pos[i] <= hi[i] + .045 for i in range(3)):
                if obj.name not in trees:
                    trees[obj.name] = BVHTree.FromObject(obj, depsgraph)
                local = obj.matrix_world.inverted() @ pos
                nearest, normal, index, distance = trees[obj.name].find_nearest(local)
                if nearest is not None:
                    clearance = (obj.matrix_world @ nearest - pos).length
                    if clearance < .045:
                        collisions.append(dict(frame=frame, object=obj.name, clearance_m=clearance))
        direction = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        path.append(dict(frame=frame, camera=camera.name, x=pos.x, y=pos.y, z=pos.z,
                         dx=direction.x, dy=direction.y, dz=direction.z,
                         lens_mm=camera.data.lens, fstop=camera.data.dof.aperture_fstop,
                         focus_m=camera.data.dof.focus_distance, exposure=scene.view_settings.exposure))
    water = bpy.data.objects['Pool / baked gravity-capillary water volume']
    cache = Path(bpy.path.abspath(water.modifiers[0].filepath))
    water_checks = []
    heights = []
    for frame in (1, 625, 680, 744, 1056):
        scene.frame_set(frame)
        evaluated = water.evaluated_get(bpy.context.evaluated_depsgraph_get())
        zz = [evaluated.data.vertices[i].co.z for i in range(0, 37837, 79)]
        heights.append(zz)
        water_checks.append(dict(frame=frame, min_z=min(zz), max_z=max(zz)))
    missing = [image.filepath for image in bpy.data.images if image.source == 'FILE' and
               not image.packed_file and not Path(bpy.path.abspath(image.filepath)).exists()]
    report = dict(blend=bpy.data.filepath, blender=bpy.app.version_string,
                  blend_sha256=hashlib.file_digest(open(bpy.data.filepath, 'rb'), 'sha256').hexdigest(),
                  resolution=[scene.render.resolution_x, scene.render.resolution_y], fps=scene.render.fps,
                  timeline=[scene.frame_start, scene.frame_end], camera_frames_checked=len(path),
                  camera_clearance_threshold_m=.045, geometry_clearance_violations=collisions,
                  missing_images=missing, packed_images=sum(bool(i.packed_file) for i in bpy.data.images),
                  water_cache_exists=cache.is_file(), water_cache=str(cache), water_sample_frames=water_checks,
                  water_changes_over_time=max(abs(a-b) for a,b in zip(heights[1], heights[2])) > .0001,
                  fixed_exposure=len(set(p['exposure'] for p in path)) == 1,
                  exact_opening_hold=max(sum((path[i][k]-path[0][k])**2 for k in ('x','y','z'))**.5 for i in range(48)) < 1e-7,
                  structural_check_scope='Minimum mesh distance for candidate camera positions; visual shot review separately checks framing and occlusion.')
    (OUT/'review/project_validation.json').write_text(json.dumps(report, indent=2))
    with (OUT/'review/camera_path.csv').open('w') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(path[0]))
        writer.writeheader()
        writer.writerows(path)
    scene.frame_set(1)
    print('PROJECT_INSPECTION', json.dumps(report), flush=True)
    if missing or not cache.is_file() or not report['water_changes_over_time'] or collisions:
        raise RuntimeError('Project inspection requires attention; see review/project_validation.json')


if __name__ == '__main__':
    main()

"""Capture the delivered model after actually opening it in Blender's GUI."""
import hashlib
import json
import os
import subprocess
import shutil
from pathlib import Path

import bpy

OUT = Path(__file__).resolve().parent.parent
STAGE = 0
FFMPEG = shutil.which('ffmpeg') or 'ffmpeg'
print('BLENDER_GUI_LOADED',bpy.data.filepath,flush=True)


def step():
    global STAGE
    bpy.context.preferences.view.show_splash = False
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.light = 'STUDIO'
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.overlay.show_overlays = False
    if STAGE == 0:
        bpy.context.scene.frame_set(1)
        STAGE = 1
        return 8
    name = 'gui_opening.png' if STAGE == 1 else 'gui_exterior.png'
    subprocess.run([FFMPEG,'-hide_banner','-v','error','-y',
                    '-f','x11grab','-video_size','1280x900','-i',os.environ['DISPLAY'],
                    '-frames:v','1',str(OUT/'review'/name)], check=True, timeout=20)
    if STAGE == 1:
        bpy.context.scene.frame_set(816)
        STAGE = 2
        return 8
    import gpu
    report = dict(blender=bpy.app.version_string, opened=bpy.data.filepath,
                  blend_sha256=hashlib.file_digest(open(bpy.data.filepath,'rb'),'sha256').hexdigest(),
                  gui_renderer=gpu.platform.renderer_get(), screenshots=['gui_opening.png','gui_exterior.png'],
                  saved_scene_modified=False)
    (OUT/'review/gui_validation.json').write_text(json.dumps(report,indent=2))
    bpy.ops.wm.quit_blender()


bpy.app.timers.register(step,first_interval=8)

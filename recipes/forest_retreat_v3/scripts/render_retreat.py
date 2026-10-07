"""Deterministic Cycles jobs on one explicitly selected OptiX GPU."""
import argparse
import json
import sys
import time
import fcntl
from pathlib import Path

import bpy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs', required=True)
    parser.add_argument('--gpu', type=int, default=0)
    parser.add_argument('--samples', type=int, default=192)
    parser.add_argument('--resolution', type=int, default=2160)
    parser.add_argument('--threshold', type=float, default=.013)
    parser.add_argument('--skip-existing', action='store_true')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--no-motion-blur', action='store_true')
    parser.add_argument('--queue-state')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    devices = [d for d in prefs.devices if d.type == 'OPTIX']
    selected = devices[args.gpu]
    for d in prefs.devices:
        d.use = d == selected
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = args.samples
    scene.cycles.adaptive_threshold = args.threshold
    scene.cycles.denoising_use_gpu = True
    scene.cycles.denoising_quality = 'HIGH'
    scene.cycles.use_auto_tile = False
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 8
    scene.render.resolution_x = args.resolution
    scene.render.resolution_y = args.resolution
    scene.render.resolution_percentage = 100
    scene.render.use_motion_blur = not (args.preview or args.no_motion_blur)
    scene.render.use_persistent_data = True
    markers = sorted([(m.frame, m.camera) for m in scene.timeline_markers])
    # Render's internal frame update otherwise rebinds the timeline camera and
    # silently overrides a requested architectural still camera.
    scene.timeline_markers.clear()
    jobs = json.loads(Path(args.jobs).read_text())
    def pending_jobs():
        if not args.queue_state:
            yield from jobs
            return
        while True:
            with open(args.queue_state, 'r+') as state:
                fcntl.flock(state, fcntl.LOCK_EX)
                index = int(state.read().strip() or '0')
                if index >= len(jobs):
                    return
                state.seek(0)
                state.write(str(index + 1))
                state.truncate()
                fcntl.flock(state, fcntl.LOCK_UN)
            yield jobs[index]

    for job in pending_jobs():
        dest = Path(job['file'])
        dest.parent.mkdir(parents=True, exist_ok=True)
        if args.skip_existing and dest.exists():
            continue
        scene.frame_set(job['frame'])
        scene.camera = (bpy.data.objects[job['camera']] if job.get('camera') else
                        [cam for frame, cam in markers if frame <= job['frame']][-1])
        scene.render.resolution_x = job.get('resolution', args.resolution)
        scene.render.resolution_y = job.get('resolution', args.resolution)
        scene.cycles.samples = job.get('samples', args.samples)
        scene.render.use_motion_blur = job.get('motion_blur', not (args.preview or args.no_motion_blur))
        scene.render.filepath = str(dest)
        start = time.monotonic()
        bpy.ops.render.render(write_still=True)
        record = dict(frame=job['frame'], camera=scene.camera.name, file=str(dest),
                      seconds=round(time.monotonic()-start, 3), samples=scene.cycles.samples,
                      resolution=scene.render.resolution_x, gpu=args.gpu, device_id=selected.id,
                      engine='CYCLES', denoiser='OPENIMAGEDENOISE',
                      motion_blur=scene.render.use_motion_blur, bytes=dest.stat().st_size)
        with (dest.parent / ('render_gpu_%d.jsonl' % args.gpu)).open('a') as handle:
            handle.write(json.dumps(record)+'\n')
        print('RENDER_COMPLETE', json.dumps(record), flush=True)


if __name__ == '__main__':
    main()

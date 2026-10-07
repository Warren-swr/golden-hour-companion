"""Bounded resumable multidevice rendering of a fixed scene revision."""
import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import threading
from collections import deque
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs', required=True)
    parser.add_argument('--gpus', default='0,1,2,3,4,5,6,7')
    parser.add_argument('--samples', type=int, default=192)
    parser.add_argument('--resolution', type=int, default=2160)
    parser.add_argument('--threshold', type=float, default=.013)
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--no-motion-blur', action='store_true')
    parser.add_argument('--dynamic', action='store_true')
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    jobs = json.loads(Path(args.jobs).read_text())
    gpus = [int(x) for x in args.gpus.split(',')]
    run_dir = OUT/'review'/args.tag
    run_dir.mkdir(exist_ok=True)
    blend = OUT/'Golden_Hour_Forest_Retreat.blend'
    scene_hash = hashlib.file_digest(blend.open('rb'), 'sha256').hexdigest()
    specification = dict(blend_sha256=scene_hash, jobs=jobs,
                         render_script_sha256=hashlib.sha256((OUT/'scripts/render_retreat.py').read_bytes()).hexdigest(),
                         samples=args.samples, resolution=args.resolution, threshold=args.threshold,
                         preview=args.preview, no_motion_blur=args.no_motion_blur)
    specification['source_scripts_sha256']={name:hashlib.sha256((OUT/'scripts'/name).read_bytes()).hexdigest()
        for name in ('build_v7.py','film.py','story.py','cinematography.py','common.py','retreat_helpers.py','materials.py',
                     'extend_water_cache.py','water_simulation.py')}
    with (OUT/'cache/pool_gravity_capillary.mdd').open('rb') as handle:
        specification['water_cache_sha256']=hashlib.file_digest(handle,'sha256').hexdigest()
    lock_manifest = run_dir/'input.json'
    if lock_manifest.exists():
        previous = json.loads(lock_manifest.read_text())
        if previous != specification:
            raise RuntimeError('Render inputs changed. Use a new render tag and frame directory.')
    lock_manifest.write_text(json.dumps(specification, indent=2))
    queue_jobs = run_dir/'queue_jobs.json'
    queue_state = run_dir/'queue_state.txt'
    if args.dynamic:
        queue_jobs.write_text(json.dumps([job for job in jobs if not Path(job['file']).exists()], indent=2))
        queue_state.write_text('0')

    def worker(gpu, group):
        jobfile = queue_jobs if args.dynamic else run_dir/('jobs_gpu_%d.json' % gpu)
        if not args.dynamic:
            jobfile.write_text(json.dumps(group, indent=2))
        log = OUT/'logs'/('%s_gpu_%d.log' % (args.tag, gpu))
        cmd = ['blender', '-b', str(blend), '-t', '8', '--python-exit-code', '1', '--python', str(OUT/'scripts/render_retreat.py'),
               '--', '--jobs', str(jobfile), '--gpu', str(gpu), '--samples', str(args.samples),
               '--resolution', str(args.resolution), '--threshold', str(args.threshold), '--skip-existing']
        if args.preview:
            cmd.append('--preview')
        if args.no_motion_blur:
            cmd.append('--no-motion-blur')
        if args.dynamic:
            cmd += ['--queue-state', str(queue_state)]
        env = dict(os.environ, OMP_NUM_THREADS='8', OPENBLAS_NUM_THREADS='2')
        completed=0
        with log.open('w') as handle:
            process=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,text=True,bufsize=1)
            tail=deque(maxlen=100)
            def capture():
                nonlocal completed
                for line in process.stdout:
                    tail.append(line)
                    if line.startswith('RENDER_COMPLETE'):
                        completed+=1
                    if not line.startswith('Fra:'):
                        handle.write(line)
                        handle.flush()
            reader=threading.Thread(target=capture,daemon=True)
            reader.start()
            try:
                code=process.wait(timeout=21600)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    process.kill();process.wait()
                reader.join()
                handle.writelines(tail)
                raise
            reader.join()
            if code:
                handle.writelines(tail)
        if code:
            raise RuntimeError('Render failed; inspect ' + str(log))
        return dict(gpu=gpu, completed_this_attempt=completed, log=str(log), exit_code=code)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(gpus)) as executor:
        futures = [executor.submit(worker, gpu, jobs[i::len(gpus)]) for i, gpu in enumerate(gpus)
                   if jobs[i::len(gpus)]]
        results = [future.result() for future in futures]
    (run_dir/'completion.json').write_text(json.dumps(results, indent=2))
    print('ALL_RENDER_WORKERS_COMPLETE', args.tag, flush=True)


if __name__ == '__main__':
    main()

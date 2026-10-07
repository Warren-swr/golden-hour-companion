"""Bounded resumable multidevice rendering of a fixed scene revision."""
import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
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
    lock_manifest = run_dir/'input.json'
    if lock_manifest.exists():
        previous = json.loads(lock_manifest.read_text())
        if previous != specification:
            raise RuntimeError('Render inputs changed. Use a new render tag and frame directory.')
    lock_manifest.write_text(json.dumps(specification, indent=2))
    queue_jobs = run_dir/'queue_jobs.json'
    queue_state = run_dir/'queue_state.txt'
    if args.dynamic:
        queue_jobs.write_text(json.dumps(jobs, indent=2))
        queue_state.write_text('0')

    def worker(gpu, group):
        jobfile = queue_jobs if args.dynamic else run_dir/('jobs_gpu_%d.json' % gpu)
        if not args.dynamic:
            jobfile.write_text(json.dumps(group, indent=2))
        log = OUT/'logs'/('%s_gpu_%d.log' % (args.tag, gpu))
        cmd = ['blender', '-b', str(blend), '-t', '8', '--python', str(OUT/'scripts/render_retreat.py'),
               '--', '--jobs', str(jobfile), '--gpu', str(gpu), '--samples', str(args.samples),
               '--resolution', str(args.resolution), '--threshold', str(args.threshold), '--skip-existing']
        if args.preview:
            cmd.append('--preview')
        if args.no_motion_blur:
            cmd.append('--no-motion-blur')
        if args.dynamic:
            cmd += ['--queue-state', str(queue_state)]
        env = dict(os.environ, OMP_NUM_THREADS='8', OPENBLAS_NUM_THREADS='2')
        with log.open('w') as handle:
            result = subprocess.run(cmd, stdout=handle, stderr=subprocess.STDOUT, env=env, timeout=21600)
        if result.returncode:
            raise RuntimeError('Render failed; inspect ' + str(log))
        return dict(gpu=gpu, jobs=len(group), log=str(log), exit_code=result.returncode)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(gpus)) as executor:
        futures = [executor.submit(worker, gpu, jobs[i::len(gpus)]) for i, gpu in enumerate(gpus)
                   if jobs[i::len(gpus)]]
        results = [future.result() for future in futures]
    (run_dir/'completion.json').write_text(json.dumps(results, indent=2))
    print('ALL_RENDER_WORKERS_COMPLETE', args.tag, flush=True)


if __name__ == '__main__':
    main()

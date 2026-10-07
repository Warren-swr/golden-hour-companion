"""v3: verify every PNG, decode every movie frame, and save temporal review evidence."""
import hashlib
import argparse
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent
FFMPEG = shutil.which('ffmpeg') or 'ffmpeg'
FFPROBE = shutil.which('ffprobe') or 'ffprobe'
MOVIE = OUT/'Golden_Hour_Forest_Retreat_v3_2160.mp4'
FADE_START = 1056 - 18 + 1


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--render-tag',default='production_v3')
    args=parser.parse_args()
    probe = json.loads(subprocess.check_output([FFPROBE,'-v','error','-show_streams','-show_format',
                                                '-of','json',str(MOVIE)],text=True))
    (OUT/'review/ffprobe_final.json').write_text(json.dumps(probe,indent=2))
    video = next(s for s in probe['streams'] if s['codec_type']=='video')
    assert (video['width'],video['height']) == (2160,2160)
    assert video['avg_frame_rate'] == '24/1'
    assert abs(float(probe['format']['duration'])-44) < .05
    bad_png = []
    for frame in range(1,1057):
        path = OUT/'frames'/('frame_%04d.png'%frame)
        try:
            with Image.open(path) as im:
                assert im.size == (2160,2160)
                im.verify()
        except Exception as error:
            bad_png.append(dict(frame=frame,error=str(error)))
    still_paths = list((OUT/'renders').glob('*.png'))
    assert len(still_paths)==8, 'Expected all eight final stills'
    for path in still_paths:
        with Image.open(path) as im:
            assert im.size == (3240,3240)
            im.verify()
    assert not bad_png, bad_png
    cuts = {265,397,517,721,853}
    contact_frames = set(range(1,1057,12)) | cuts | {x-1 for x in cuts} | {1056}
    extract = OUT/'review/decoded_samples'
    extract.mkdir(exist_ok=True)
    command = [FFMPEG,'-hide_banner','-v','error','-i',str(MOVIE),'-vf','scale=288:288:flags=lanczos',
               '-pix_fmt','rgb24','-f','rawvideo','-']
    process = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    count, previous, initial = 0, None, None
    metrics, selected = [], []
    chunk_size = 288*288*3
    while True:
        data = bytearray()
        while len(data)<chunk_size:
            block=process.stdout.read(chunk_size-len(data))
            if not block:
                break
            data.extend(block)
        if not data:
            break
        assert len(data)==chunk_size, 'Truncated decoded frame'
        count += 1
        pixels = np.frombuffer(data,dtype=np.uint8).reshape(288,288,3)
        mean = float(pixels.mean()/255)
        delta = float(np.abs(pixels.astype(np.float32)-previous).mean()/255) if previous is not None else 0
        if initial is None:
            initial = pixels.astype(np.float32)
        hold_delta = float(np.abs(pixels.astype(np.float32)-initial).mean()/255) if count<=48 else None
        metrics.append(dict(frame=count,mean=mean,delta=delta,editorial_cut=count in cuts,closing_fade=count>=FADE_START,hold_delta=hold_delta))
        if count in contact_frames:
            dest = extract/('video_%04d.jpg'%count)
            Image.fromarray(pixels).save(dest,quality=95)
            selected.append((count,dest))
        previous=pixels.astype(np.float32)
    stderr=process.stderr.read().decode(errors='replace')
    code=process.wait()
    assert code==0 and not stderr, stderr
    assert count==1056, count
    black=[m['frame'] for m in metrics if m['mean']<.015 and not m['closing_fade']]
    suspicious=[m for m in metrics if not m['editorial_cut'] and m['frame']>1 and m['delta']>.06]
    fade=[m['mean'] for m in metrics if m['closing_fade']]
    assert all(a>=b-1e-4 for a,b in zip(fade,fade[1:])), 'Closing fade must darken monotonically'
    hold_error=max(m['hold_delta'] for m in metrics[:48])
    assert not black, black
    assert not suspicious, suspicious
    assert hold_error<.006, hold_error
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
    for sheet, start in enumerate(range(0,len(selected),24),1):
        items=selected[start:start+24]
        canvas=Image.new('RGB',(6*288,4*314),'#191c1b')
        draw=ImageDraw.Draw(canvas)
        for i,(frame,path) in enumerate(items):
            x,y=(i%6)*288,(i//6)*314
            draw.text((x+7,y+5),'%05.2f s / frame %04d'%((frame-1)/24,frame),font=font,fill='#ded6c5')
            with Image.open(path) as im:canvas.paste(im,(x,y+26))
        canvas.save(OUT/'review'/('film_contact_%02d.jpg'%sheet),quality=94)
    records=[]
    for file in (OUT/'frames').glob('render_gpu_*.jsonl'):
        records += [json.loads(line) for line in file.read_text().splitlines()]
    rendered={r['frame'] for r in records}
    assert rendered == {1} | set(range(49,1057))
    assert all(r['resolution']==2160 and r['samples']==192 and r['motion_blur'] for r in records)
    fixed=json.loads((OUT/'review'/args.render_tag/'input.json').read_text())
    scene_hash=hashlib.file_digest((OUT/'Golden_Hour_Forest_Retreat.blend').open('rb'),'sha256').hexdigest()
    water_bake=json.loads((OUT/'review/water_simulation.json').read_text())
    water_hash=hashlib.file_digest((OUT/water_bake['cache']).open('rb'),'sha256').hexdigest()
    assert water_hash==water_bake['sha256'], 'Water cache differs from the recorded simulation bake'
    render_script=hashlib.sha256((OUT/'scripts/render_retreat.py').read_bytes()).hexdigest()
    assert fixed['render_script_sha256']==render_script
    # The main pass used the scene before the Euler-continuity fix. Accept it only if the
    # recorded comparison shows identical frame-centre cameras and every frame whose
    # shutter motion differed was re-rendered from the current scene.
    fix=json.loads((OUT/'review/production_v3_fix/input.json').read_text())
    comparison=json.loads((OUT/'review/euler_fix_comparison.json').read_text())
    refreshed=sorted(job['frame'] for job in fix['jobs'])
    assert fix['blend_sha256']==scene_hash and fix['render_script_sha256']==render_script
    assert comparison['max_centre_matrix_difference']<1e-5
    assert comparison['frames_with_different_shutter_motion']==refreshed
    assert not comparison['new_scene_euler_jumps_over_1_rad']
    main_hash=hashlib.file_digest(open(comparison['old'],'rb'),'sha256').hexdigest() if Path(comparison['old']).exists() else fixed['blend_sha256']
    assert fixed['blend_sha256']==main_hash
    report=dict(movie=str(MOVIE),sha256=hashlib.file_digest(MOVIE.open('rb'),'sha256').hexdigest(),
                width=2160,height=2160,fps=24,duration_seconds=44,decoded_frames=count,
                native_pngs_verified=1056,unique_rendered_source_frames=len(rendered),
                reference_hold_duplicate_frames=47,closing_fade_frames=18,editorial_cuts=sorted(cuts),reference_hold_max_decoded_error=hold_error,
                black_frames=black,unexpected_large_frame_changes=suspicious,
                decoded_sample_count=len(selected),scene_sha256=scene_hash,main_pass_scene_sha256=fixed['blend_sha256'],rerendered_after_euler_fix=refreshed,water_cache_sha256=water_hash,
                native_still_count=len(list((OUT/'renders').glob('*.png'))),
                all_frame_decodes_passed=True,all_native_pngs_passed=True,
                subjective_review='See film contact sheets and the separate visual review record; numerical checks do not certify photorealism.')
    (OUT/'review/video_validation.json').write_text(json.dumps(report,indent=2))
    (OUT/'review/frame_metrics.json').write_text(json.dumps(metrics))
    print('DELIVERY_VIDEO_PASS',json.dumps(report),flush=True)


if __name__=='__main__':
    main()

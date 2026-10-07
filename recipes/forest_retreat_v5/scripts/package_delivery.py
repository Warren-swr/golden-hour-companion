"""Package only a fully rendered and verified v5 delivery; leave raw runs in place."""
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parent.parent


def sha256(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle,'sha256').hexdigest()


def main():
    video=json.loads((OUT/'review/final_video_validation.json').read_text())
    preview=json.loads((OUT/'review/preview_video_validation.json').read_text())
    project=json.loads((OUT/'review/project_validation.json').read_text())
    portable=json.loads((OUT/'review/portable_scene_validation.json').read_text())
    visual=json.loads((OUT/'review/final_visual_review.json').read_text())
    inputs=json.loads((OUT/'review/production_v5/input.json').read_text())
    frame_hashes=json.loads((OUT/'review/final_frame_hashes.json').read_text())
    completion=json.loads((OUT/'review/production_v5/completion.json').read_text())
    scene=OUT/'Golden_Hour_Forest_Retreat.blend'
    assert sha256(scene)==inputs['blend_sha256']==project['scene_sha256']
    assert portable['scene_sha256']==inputs['blend_sha256']
    assert visual['decision']=='accepted' and visual['scene_sha256']==inputs['blend_sha256']
    assert visual['movie_sha256']==video['movie_sha256']
    assert not portable['missing_images'] and portable['sampled_water_vertex_change_metres']>1e-5
    assert all(c['inside_bundle'] for c in portable['caches'])
    assert video['frames']==1008 and video['resolution']==[2160,2160] and video['duration']==42
    assert video['decoded_every_frame'] and not video['duplicates'] and not video['black_frames'] and not video['unexpected_jumps']
    assert sha256(OUT/'Golden_Hour_Forest_Retreat_v5_2160.mp4')==video['movie_sha256']
    assert preview['decoded_frame_count']==1008
    assert sha256(OUT/preview['movie'])==preview['movie_sha256']
    assert len(frame_hashes)==1008 and len(completion)==8
    assert all(r['exit_code']==0 for r in completion)
    for name,digest in inputs['source_scripts_sha256'].items():
        assert sha256(OUT/'scripts'/name)==digest,'Authoring inputs changed after rendering: '+name
    assert sha256(OUT/'scripts/render_retreat.py')==inputs['render_script_sha256']
    receipts={}
    for folder in ('frames','renders'):
        for path in (OUT/folder).glob('render_gpu_*.jsonl'):
            for line in path.read_text().splitlines():
                row=json.loads(line)
                receipts[row['file']]=row
    assert len(receipts)==1017
    for job in inputs['jobs']:
        row=receipts[job['file']]
        assert row['frame']==job['frame']
        assert row['color_depth']=='16' and row['engine']=='CYCLES'
        assert row['resolution']==job.get('resolution',2160)
        assert row['samples']==job.get('samples',256)
        assert row['bytes']==Path(job['file']).stat().st_size
    baseline=json.loads((OUT.parent/'forest_retreat_v3/delivery_manifest.json').read_text())
    cache=next(f for f in baseline['files'] if f['file']=='cache/pool_gravity_capillary.mdd')
    assert sha256(OUT/cache['file'])==cache['sha256']
    # The contact sheet is a viewing derivative of the nine actual final stills.
    images=sorted((OUT/'renders').glob('*_3240.png'))
    assert len(images)==9
    width,height=640,682
    canvas=Image.new('RGB',(width*3,height*3),'#202320')
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
    for i,path in enumerate(images):
        x,y=i%3*width,i//3*height
        title=path.stem.replace('_3240','').replace('_',' ')
        draw.text((x+12,y+11),title,font=font,fill='#ded8ca')
        with Image.open(path) as im:
            assert im.size==(3240,3240)
            canvas.paste(im.convert('RGB').resize((width,width),Image.Resampling.LANCZOS),(x,y+42))
    canvas.save(OUT/'review/final_stills_contact.jpg',quality=95)
    with Image.open(images[1]) as im:
        im.convert('RGB').resize((1600,1600),Image.Resampling.LANCZOS).save(OUT/'renders/film_poster.jpg',quality=96)
    paths=[scene,OUT/'README.md',OUT/'Golden_Hour_Forest_Retreat_v5_scene.zip',OUT/'Golden_Hour_Forest_Retreat_v5_2160.mp4',
           OUT/'Golden_Hour_Forest_Retreat_v5_1080_preview.mp4',OUT/'Golden_Hour_Forest_Retreat_v5_ProRes_HQ.mov',
           OUT/'Golden_Hour_Forest_Retreat_v5_pilot.mp4',OUT/'source/v4_scene.blend',OUT/'source/manifest.json']
    for folder,pattern in (('scripts','*.py'),('renders','*'),('assets','**/*'),('cache','*')):
        paths.extend(p for p in (OUT/folder).glob(pattern) if p.is_file())
    review_names=['project_validation.json','pilot_video_validation.json','final_video_validation.json','preview_video_validation.json',
                  'final_ffprobe.json','final_frame_hashes.json','final_temporal_metrics.json',
                  'runtime.json','production_gate.json','pilot_to_final_motion.json','model_inspection.json','shot_plan.json',
                  'scene_bundle.json','portable_scene_validation.json',
                  'camera_path.csv','iteration_log.md','final_visual_review.json','final_stills_contact.jpg','final_detail_review.jpg',
                  'scene_inventory.json','production_status.json',
                  'production_v5/input.json','production_v5/completion.json',
                  'pilot_v5/input.json','pilot_v5/completion.json']
    paths.extend(OUT/'review'/name for name in review_names)
    paths.extend(sorted((OUT/'review').glob('final_film_contact_*.jpg')))
    paths.extend(sorted((OUT/'review').glob('native_*.jpg')))
    for folder in ('frames','renders'):
        paths.extend(sorted((OUT/folder).glob('render_gpu_*.jsonl')))
    files=[]
    for path in sorted(set(paths)):
        assert path.is_file(),str(path)
        files.append(dict(file=str(path.relative_to(OUT)),bytes=path.stat().st_size,sha256=sha256(path)))
    manifest=dict(project='Golden Hour Companion - A Forest Retreat v5',
                  time_utc=datetime.now(timezone.utc).isoformat(),scene_sha256=inputs['blend_sha256'],
                  native_frames=1008,stills=9,source_frame_hashes='review/final_frame_hashes.json',
                  raw_run=str((OUT/'frames').resolve().parent),files=files)
    (OUT/'delivery_manifest.json').write_text(json.dumps(manifest,indent=2))
    (OUT/'SHA256SUMS.txt').write_text(''.join(row['sha256']+'  '+row['file']+'\n' for row in files))
    print('DELIVERY_MANIFEST_COMPLETE',len(files),'files',flush=True)


if __name__=='__main__':
    main()

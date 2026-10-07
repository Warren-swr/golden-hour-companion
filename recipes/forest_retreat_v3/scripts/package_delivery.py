"""Create a scoped portable project archive after rendering and review pass."""
import hashlib
import json
import zipfile
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent


def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle,'sha256').hexdigest()


def main():
    video=json.loads((OUT/'review/video_validation.json').read_text())
    visual=json.loads((OUT/'review/final_visual_review.json').read_text())
    assert video['all_frame_decodes_passed'] and video['all_native_pngs_passed']
    assert visual['accepted_for_delivery']
    project=json.loads((OUT/'review/project_validation.json').read_text())
    portable=json.loads((OUT/'review/portable_validation.json').read_text())
    gui=json.loads((OUT/'review/gui_validation.json').read_text())
    scene_hash=digest(OUT/'Golden_Hour_Forest_Retreat.blend')
    assert scene_hash==video['scene_sha256']==project['blend_sha256']==portable['blend_sha256']==gui['blend_sha256']
    assert not project['missing_images'] and not project['geometry_clearance_violations']
    core=[OUT/'Golden_Hour_Forest_Retreat.blend', OUT/'README.md', OUT/'requirements.txt']
    for pattern in ('cache/*.mdd','assets/*.json','assets/textures/*.jpg','scripts/*.py','scripts/*.sh',
                    'source/*.blend','source/*.md','source/*.json','source/*.txt','source/*.jpg',
                    'source/scripts/*.py','renders/*.png'):
        core.extend(sorted(OUT.glob(pattern)))
    selected_review=['water_simulation.json','project_validation.json','portable_validation.json',
                     'gui_validation.json','video_validation.json','final_visual_review.json',
                     'shot_plan.json','camera_path.csv','camera_motion_metrics.json',
                     'frozen_production_inputs.json','final_stills_contact.jpg',
                     'runtime_context.json','reference_comparison.jpg','reference_overlay.png',
                     'baseline_preservation.json','ffprobe_final.json',
                     'gui_opening.png','gui_exterior.png']
    core.extend(OUT/'review'/name for name in selected_review if (OUT/'review'/name).exists())
    core.extend(sorted(OUT.glob('review/film_contact_*.jpg')))
    core=sorted(set(core))
    sums=OUT/'PROJECT_SHA256SUMS.txt'
    sums.write_text(''.join(digest(path)+'  '+str(path.relative_to(OUT))+'\n' for path in core))
    core.append(sums)
    archive=OUT/'Golden_Hour_Forest_Retreat_Project.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as handle:
        for path in core:
            handle.write(path,arcname='Golden_Hour_Forest_Retreat/'+str(path.relative_to(OUT)))
    with zipfile.ZipFile(archive) as handle:
        bad=handle.testzip()
        assert bad is None, bad
    entries=[]
    for path in sorted(set(core+[archive,OUT/'Golden_Hour_Forest_Retreat_2160.mp4',
                                 OUT/'Golden_Hour_Forest_Retreat_1080_preview.mp4'])):
        entries.append(dict(file=str(path.relative_to(OUT)),bytes=path.stat().st_size,sha256=digest(path)))
    manifest=dict(project='Golden Hour Companion — A Forest Retreat',revision='forest_retreat_v2',
                  native_video=[2160,2160,24,44],project_archive_crc_passed=True,files=entries)
    (OUT/'delivery_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    (OUT/'SHA256SUMS.txt').write_text(''.join(e['sha256']+'  '+e['file']+'\n' for e in entries))
    print('PORTABLE_ARCHIVE_VERIFIED',archive,archive.stat().st_size,flush=True)


if __name__=='__main__':
    main()

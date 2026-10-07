"""Explicit native-resolution production frame and still manifests."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
frames = [dict(frame=f, file=str(OUT/'frames'/('frame_%04d.png' % f))) for f in [1] + list(range(49, 1057))]
(OUT/'review/production_frame_jobs.json').write_text(json.dumps(frames, indent=2))
stills = [
    (1, None, '01_reference_3240.png', 384),
    (816, 'Still / exterior hero', '02_cabin_and_pool_3240.png', 320),
    (160, 'Still / living room', '03_living_room_3240.png', 320),
    (468, 'Still / bedroom', '04_linen_bedroom_3240.png', 320),
    (360, 'Still / breakfast detail', '05_kitchen_detail_3240.png', 320),
    (684, 'Still / water optics', '06_water_and_caustics_3240.png', 384),
    (816, 'Still / pool at sunset', '07_pool_garden_3240.png', 320),
    (972, 'Still / fire garden', '08_fire_garden_3240.png', 320),
]
jobs = [dict(frame=f, camera=camera, file=str(OUT/'renders'/name), resolution=3240, samples=samples, motion_blur=False)
        for f, camera, name, samples in stills]
(OUT/'review/production_still_jobs.json').write_text(json.dumps(jobs, indent=2))
(OUT/'review/production_all_jobs.json').write_text(json.dumps(jobs + frames, indent=2))
print('PRODUCTION_MANIFESTS', len(frames), 'native moving/first frames and', len(jobs), '3240 square stills')

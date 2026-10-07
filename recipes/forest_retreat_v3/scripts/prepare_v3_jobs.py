"""Production manifests for v3: 8 native stills plus every rendered film frame.

Heavy jobs go first (3240 stills, then the water close-up) so the dynamic
queue finishes evenly across GPUs.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
film = [1] + list(range(49, 1057))
water = [f for f in film if 721 <= f <= 852]
order = water + [f for f in film if f not in water]
frames = [dict(frame=f, file=str(OUT / 'frames' / ('frame_%04d.png' % f))) for f in order]
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
jobs = [dict(frame=f, camera=camera, file=str(OUT / 'renders' / name), resolution=3240, samples=samples,
             motion_blur=False) for f, camera, name, samples in stills]
(OUT / 'review' / 'production_all_jobs.json').write_text(json.dumps(jobs + frames, indent=1))
print('V3_PRODUCTION_JOBS', len(frames), 'film frames and', len(jobs), 'stills')

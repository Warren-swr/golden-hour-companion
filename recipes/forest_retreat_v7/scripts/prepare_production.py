"""Fixed 16-bit native-frame and still-image delivery jobs."""
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent
from film import FRAMES,STILLS


def main():
    jobs=[dict(frame=f,file=str(OUT/'frames'/('frame_%04d.png'%f)),color_depth='16') for f in range(1,FRAMES+1)]
    stills=[dict(frame=f,file=str(OUT/'renders'/(name+'_3240.png')),resolution=3240,samples=384,
                 motion_blur=False,color_depth='16') for f,name in STILLS]
    (OUT/'review/production_jobs.json').write_text(json.dumps(jobs+stills,indent=2))
    print('PRODUCTION_JOBS',len(jobs),'native frames;',len(stills),'architectural stills',flush=True)


if __name__=='__main__':
    main()

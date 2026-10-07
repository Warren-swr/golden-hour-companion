"""Fixed 16-bit native-frame and still-image delivery jobs."""
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent
STILLS=[(1,'01_reference'),(114,'02_house_and_clearing'),(228,'03_living_room'),
        (336,'04_bedroom_and_forest'),(420,'05_stone_bathroom'),(540,'06_open_threshold'),
        (648,'07_reflections'),(756,'08_garden_room'),(960,'09_forest_departure')]


def main():
    jobs=[dict(frame=f,file=str(OUT/'frames'/('frame_%04d.png'%f)),color_depth='16') for f in range(1,1009)]
    stills=[dict(frame=f,file=str(OUT/'renders'/(name+'_3240.png')),resolution=3240,samples=384,
                 motion_blur=False,color_depth='16') for f,name in STILLS]
    (OUT/'review/production_jobs.json').write_text(json.dumps(jobs+stills,indent=2))
    print('PRODUCTION_JOBS',len(jobs),'native frames;',len(stills),'architectural stills',flush=True)


if __name__=='__main__':
    main()

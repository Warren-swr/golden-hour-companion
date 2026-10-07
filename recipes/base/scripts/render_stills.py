"""Render the final still selection and the native first animation frame."""
import concurrent.futures
import argparse
import json
import subprocess
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent
SCRIPT=OUT/'scripts'/'render_scene.py'
GROUPS={
    1:[('first_frame',None,1,2160,192,OUT/'frames'/'frame_0001.png')],
    2:[('reference',None,1,3240,384,OUT/'renders'/'01_reference_3240.png')],
    3:[('living','Still • Living room',1,2160,256,OUT/'renders'/'02_living_room.png'),
       ('forest','Still • Forest',1,2160,256,OUT/'renders'/'07_forest.png')],
    4:[('exterior','Still • Exterior',1,2160,256,OUT/'renders'/'03_house_and_courtyard.png'),
       ('garden','Still • Garden',1,2160,256,OUT/'renders'/'08_garden.png')],
    5:[('bedroom','Still • Bedroom',1,2160,256,OUT/'renders'/'04_bedroom.png')],
    6:[('bathroom','Still • Bathroom',1,2160,256,OUT/'renders'/'05_bathroom.png')],
    7:[('kitchen','Still • Kitchen',1,2160,256,OUT/'renders'/'06_kitchen.png')],
}


def worker(gpu,jobs):
    for name,camera,frame,resolution,samples,target in jobs:
        cmd=['blender','-b',str(OUT/'golden_hour_companion.blend'),'-t','8','--python',str(SCRIPT),'--',
             '--gpu',str(gpu),'--frames',str(frame),'--resolution',str(resolution),
             '--samples',str(samples),'--threshold','.01','--gpu-denoise','--output',str(target)]
        if camera:
            cmd+=['--camera',camera]
        with (OUT/'logs'/f'final_still_{name}.log').open('w') as handle:
            subprocess.run(cmd,stdout=handle,stderr=subprocess.STDOUT,check=True)
        print('FINAL_STILL_DONE',name,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--gpus',default='1,2,3,4,5,6,7')
    chosen=[int(x) for x in parser.parse_args().gpus.split(',')]
    assignments={gpu:[] for gpu in chosen}
    for i,jobs in enumerate(GROUPS.values()):
        assignments[chosen[i%len(chosen)]].extend(jobs)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(chosen)) as executor:
        results=[executor.submit(worker,gpu,jobs) for gpu,jobs in assignments.items()]
        for result in results:
            result.result()
    print('ALL_FINAL_STILLS_COMPLETE',flush=True)

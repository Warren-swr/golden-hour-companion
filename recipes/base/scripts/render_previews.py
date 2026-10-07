"""Concurrent look-development checks of all four moves and the forest."""
import argparse
import concurrent.futures
import subprocess
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser()
parser.add_argument('--revision',default='v09')
parser.add_argument('--resolution',type=int,default=900)
parser.add_argument('--extras',action='store_true')
args=parser.parse_args()
dest=OUT/'review'/args.revision
dest.mkdir(exist_ok=True)
jobs=[('01_reference',1,None),('02_room',288,None),('03_kitchen_start',289,None),
      ('04_kitchen_end',432,None),('05_window',570,None),('06_forest_home',864,None),
      ('07_exterior',1,'Still • Exterior')]
if args.extras:
    jobs=[('08_bedroom',1,'Still • Bedroom'),('09_bathroom',1,'Still • Bathroom'),
          ('10_garden',1,'Still • Garden'),('11_forest',1,'Still • Forest'),
          ('12_departure',625,None),('13_crane_mid',720,None),('14_crane_high',800,None)]


def worker(gpu,job):
    name,frame,camera=job
    command=['blender','-b',str(OUT/'golden_hour_companion.blend'),'-t','8',
             '--python',str(OUT/'scripts'/'render_scene.py'),'--','--gpu',str(gpu),
             '--frames',str(frame),'--resolution',str(args.resolution),'--samples','96',
             '--threshold','.025','--gpu-denoise','--output',str(dest/(name+'.png'))]
    if camera:
        command+=['--camera',camera]
    with (OUT/'logs'/f'{args.revision}_{name}.log').open('w') as handle:
        subprocess.run(command,stdout=handle,stderr=subprocess.STDOUT,check=True)
    print('PREVIEW_COMPLETE',name,flush=True)


with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
    futures=[executor.submit(worker,i+1,job) for i,job in enumerate(jobs)]
    for future in futures:
        future.result()
from review_images import contact_sheet,comparison
contact_sheet(sorted(dest.glob('*.png')),OUT/'review'/f'{args.revision}_contact.jpg')
if (dest/'01_reference.png').exists():
    comparison(OUT/'review'/'reference_original.jpg',dest/'01_reference.png',OUT/'review'/args.revision)

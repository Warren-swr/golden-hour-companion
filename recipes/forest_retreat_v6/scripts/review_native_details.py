"""Make unscaled pixel crops from completed native production frames."""
import json
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parent.parent
CROPS=[
    (1,650,1350,'Upholstery pile and seams'),
    (270,740,1000,'Door casing and bedroom connection'),
    (270,20,1100,'Cabinet grain, joints and tile'),
    (564,160,1160,'Pool coping, water and reflection'),
    (606,1300,1280,'Terrace boards and chair contact'),
    (649,1300,450,'Roof, gutter and eaves'),
]


def main():
    receipts={}
    for path in (OUT/'frames').glob('render_gpu_*.jsonl'):
        for line in path.read_text().splitlines():
            row=json.loads(line)
            receipts[row['frame']]=row
    size,header=600,48
    canvas=Image.new('RGB',(3*size,2*(size+header)),'#202320')
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    for i,(frame,left,top,title) in enumerate(CROPS):
        row=receipts[frame]
        assert row['resolution']==2160 and row['color_depth']=='16'
        x,y=i%3*size,i//3*(size+header)
        with Image.open(row['file']) as im:
            assert im.size==(2160,2160)
            crop=im.convert('RGB').crop((left,top,left+size,top+size))
            canvas.paste(crop,(x,y+header))
        draw.text((x+10,y+5),title,font=font,fill='#ded8ca')
        draw.text((x+10,y+26),f'Frame {frame:04d} / native pixels 1:1',font=font,fill='#aba99f')
    canvas.save(OUT/'review/final_detail_review.jpg',quality=97)


if __name__=='__main__':
    main()

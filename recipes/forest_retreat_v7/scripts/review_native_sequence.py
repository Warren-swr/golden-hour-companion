"""Build labeled review sheets from completed native render receipts."""
import argparse
import json
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parent.parent


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--frames',nargs='+',type=int,required=True)
    parser.add_argument('--name',required=True)
    parser.add_argument('--columns',type=int,default=3)
    args=parser.parse_args()
    assert args.name.startswith('native_') and '/' not in args.name
    assert 1<=args.columns<=3
    receipts={}
    for path in (OUT/'frames').glob('render_gpu_*.jsonl'):
        for line in path.read_text().splitlines():
            row=json.loads(line);receipts[row['frame']]=row
    width,header=864,52
    canvas=Image.new('RGB',(args.columns*width,((len(args.frames)+args.columns-1)//args.columns)*(width+header)),'#202320')
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    for i,frame in enumerate(args.frames):
        row=receipts[frame]
        assert row['resolution']==2160 and row['color_depth']=='16'
        path=Path(row['file'])
        assert path.stat().st_size==row['bytes']
        x,y=i%args.columns*width,i//args.columns*(width+header)
        draw.text((x+12,y+6),f'Frame {frame:04d} / {(frame-1)/24:.2f} s',font=font,fill='#ded8ca')
        draw.text((x+12,y+29),row['camera'],font=font,fill='#aba99f')
        with Image.open(path) as im:
            assert im.size==(2160,2160)
            canvas.paste(im.convert('RGB').resize((width,width),Image.Resampling.LANCZOS),(x,y+header))
    dest=OUT/'review'/(args.name+'.jpg')
    canvas.save(dest,quality=96)
    print(dest)


if __name__=='__main__':main()

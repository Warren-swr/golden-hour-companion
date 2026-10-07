"""Render a vector player UI and animate the original 16-bit film into it."""
import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont

from edit import OUT,OPENING,FPS,INTRO_FRAMES,TITLE,ARTIST,animation

cv2.setNumThreads(4)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
WHITE=(252,247,239,255)
MUTED=(215,190,166,255)


class Drawing:
    def __init__(self,resolution):
        self.scale=resolution/1080*2
        self.image=Image.new('RGBA',(resolution*2,resolution*2))
        self.draw=ImageDraw.Draw(self.image)

    def rect(self,box,fill,radius=0,width=0,outline=None):
        self.draw.rounded_rectangle(tuple(round(v*self.scale) for v in box),
            radius=round(radius*self.scale),fill=fill,outline=outline,width=max(1,round(width*self.scale)))

    def line(self,points,fill,width=1):
        self.draw.line([(round(x*self.scale),round(y*self.scale)) for x,y in points],fill=fill,
            width=max(1,round(width*self.scale)),joint='curve')

    def polygon(self,points,fill):
        self.draw.polygon([(round(x*self.scale),round(y*self.scale)) for x,y in points],fill=fill)

    def circle(self,x,y,r,fill):
        self.draw.ellipse(tuple(round(v*self.scale) for v in (x-r,y-r,x+r,y+r)),fill=fill)

    def text(self,xy,text,size=20,fill=WHITE,bold=False,anchor=None):
        font=ImageFont.truetype(BOLD if bold else FONT,round(size*self.scale))
        self.draw.text(tuple(round(v*self.scale) for v in xy),text,font=font,fill=fill,anchor=anchor)

    def arc(self,box,start,end,fill,width=1):
        self.draw.arc(tuple(round(v*self.scale) for v in box),start,end,fill=fill,
            width=max(1,round(width*self.scale)))

    def result(self,resolution):
        return np.asarray(self.image.resize((resolution,resolution),Image.Resampling.LANCZOS),dtype=np.float32)/255


def speaker(d,x,y,size=12,waves=False):
    d.polygon([(x,y-3),(x+4,y-3),(x+size,y-size*.65),(x+size,y+size*.65),(x+4,y+3),(x,y+3)],MUTED)
    if waves:
        for r in (8,13):d.arc((x+8-r,y-r,x+8+r,y+r),305,55,MUTED,1.8)


def skip(d,x,y,direction):
    for offset in (-9,9):
        cx=x+offset
        d.polygon([(cx-9*direction,y-15),(cx+12*direction,y),(cx-9*direction,y+15)],WHITE)


def static_ui(resolution):
    d=Drawing(resolution)
    d.text((72,33),'15:23',20,bold=True)
    for i,h in enumerate((7,11,15,19)):
        x=910+i*6;d.rect((x,54-h,x+3.6,54),WHITE,1.2)
    for radius in (16,11):d.arc((960-radius,52-radius,960+radius,52+radius),225,315,WHITE,2.8)
    d.circle(960,52,2,WHITE)
    d.rect((987,36,1019,53),None,5,1.5,(250,242,230,180))
    d.rect((990,39,1016,50),WHITE,2.5)
    d.rect((1021,42,1023,47),(250,242,230,150),1)
    d.rect((504,73,576,78),(223,201,177,140),2.5)
    d.text((240,741),TITLE,34,bold=True)
    d.text((240,788),ARTIST,24,fill=MUTED)
    for x in (756,818):d.circle(x,766,24,(211,179,144,39))
    points=[]
    for i in range(11):
        angle=-math.pi/2+i*math.pi/5
        radius=13 if i%2==0 else 5.7
        points.append((756+radius*math.cos(angle),766+radius*math.sin(angle)))
    d.line(points,WHITE,2)
    for x in (810,818,826):d.circle(x,766,2.1,WHITE)
    d.rect((240,852,840,858),(219,190,160,80),3)
    skip(d,408,944,-1);skip(d,672,944,1)
    d.rect((522,920,534,968),WHITE,3)
    d.rect((546,920,558,968),WHITE,3)
    d.rect((320,1010,760,1015),(218,190,160,65),2.5)
    d.rect((320,1010,406,1015),MUTED,2.5)
    speaker(d,289,1012,10);speaker(d,782,1012,10,True)
    d.line([(472,1042),(486,1057),(479,1063),(479,1036),(486,1042),(472,1056)],MUTED,1.7)
    d.text((548,1051),'WH-1000XM5',13,fill=MUTED,anchor='mm')
    return d.result(resolution)


def dynamic_ui(resolution,time):
    d=Drawing(resolution)
    elapsed=78+time
    p=elapsed/146
    d.rect((240,852,240+600*p,858),(239,209,177,255),3)
    d.text((240,867),f'{int(elapsed)//60}:{int(elapsed)%60:02d}',15,fill=(208,180,151,210))
    remaining=146-int(elapsed)
    d.text((840,867),f'−{remaining//60}:{remaining%60:02d}',15,fill=(208,180,151,210),anchor='ra')
    for i in range(4):
        height=5+13*(.5+.5*math.sin(time*(3.8+i*.65)+i*1.7))
        x=329+i*5.5
        d.rect((x,812-height,x+3,812),(230,197,158,230),1.4)
    return d.result(resolution)


def backdrop(resolution):
    yy,xx=np.mgrid[0:resolution,0:resolution].astype(np.float32)/resolution
    glow=np.exp(-((xx-.5)**2/.23+(yy-.36)**2/.30))
    top=np.array([113,79,51],np.float32)/255
    bottom=np.array([57,39,27],np.float32)/255
    rgb=top[None,None,:]*(1-yy[:,:,None])+bottom[None,None,:]*yy[:,:,None]
    rgb=np.broadcast_to(rgb,(resolution,resolution,3)).copy()
    rgb+=glow[:,:,None]*np.array([15,10,5],np.float32)/255
    rng=np.random.default_rng(7138)
    rgb+=rng.normal(0,.27/255,(resolution,resolution,1)).astype(np.float32)
    return np.clip(rgb,0,1)


def blend_rgba(background,layer,opacity):
    alpha=layer[:,:,3:4]*opacity
    return background*(1-alpha)+layer[:,:,:3]*alpha


def rounded_mask(xx,yy,x,y,side,radius):
    qx=np.abs(xx-(x+side/2))-(side/2-radius)
    qy=np.abs(yy-(y+side/2))-(side/2-radius)
    distance=np.sqrt(np.maximum(qx,0)**2+np.maximum(qy,0)**2)+np.minimum(np.maximum(qx,qy),0)-radius
    return np.clip(.5-distance,0,1)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--resolution',type=int,default=2160)
    p.add_argument('--tag',default='native')
    p.add_argument('--samples',help='Comma-separated zero-based frames for layout scouting')
    args=p.parse_args()
    assert args.tag.replace('_','').isalnum()
    resolution=args.resolution
    dest=OUT/'frames'/args.tag
    dest.mkdir(exist_ok=True)
    frames=[int(v) for v in args.samples.split(',')] if args.samples else range(INTRO_FRAMES)
    background=backdrop(resolution)
    static=static_ui(resolution)
    yy,xx=np.mgrid[0:resolution,0:resolution].astype(np.float32)
    scale=resolution/1080
    records=[]
    source_id=None;source=None;native=None
    for frame in frames:
        state=animation(frame)
        path=dest/f'frame_{frame+1:04d}.png'
        assert not path.exists(),f'Render to a new tag: {path}'
        if state['source_frame']!=source_id:
            source_id=state['source_frame']
            source_path=OPENING/f'frame_{source_id:04d}.png'
            native=cv2.imread(str(source_path),cv2.IMREAD_UNCHANGED)
            assert native.shape==(2160,2160,3) and native.dtype==np.uint16
            source=cv2.cvtColor(native,cv2.COLOR_BGR2RGB).astype(np.float32)/65535
        exact=frame==INTRO_FRAMES-1 and resolution==2160
        if exact:
            shutil.copy2(source_path,path)
        else:
            base=blend_rgba(background,static,state['ui_opacity'])
            if state['ui_opacity']>0:
                base=blend_rgba(base,dynamic_ui(resolution,state['time']),state['ui_opacity'])
            x,y,side,radius=[state[k]*scale for k in ('cover_x','cover_y','cover_side','radius')]
            mask=rounded_mask(xx,yy,x,y,side,radius)
            shadow=rounded_mask(xx,yy,x,y+18*scale*(1-state['progress']),side,radius)
            shadow=cv2.GaussianBlur(shadow,(0,0),max(.01,20*scale))
            base*=1-shadow[:,:,None]*.25*(1-state['progress'])
            ratio=side/source.shape[1]
            filtered=source
            if ratio<.99:
                filtered=cv2.GaussianBlur(source,(0,0),.45*(1/ratio-1))
            matrix=np.array([[ratio,0,x],[0,ratio,y]],np.float32)
            cover=cv2.warpAffine(filtered,matrix,(resolution,resolution),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
            result=base*(1-mask[:,:,None])+cover*mask[:,:,None]
            pixels=np.rint(np.clip(result,0,1)*65535).astype(np.uint16)
            cv2.imwrite(str(path),cv2.cvtColor(pixels,cv2.COLOR_RGB2BGR),[cv2.IMWRITE_PNG_COMPRESSION,3])
        state.update(file=str(path),bytes=path.stat().st_size,exact_source_identity=exact)
        records.append(state)
        if frame%12==0 or frame==INTRO_FRAMES-1:print(f'{args.tag}: {frame+1}/{INTRO_FRAMES}',flush=True)
    scripts={}
    for name in ('edit.py','render_intro.py'):
        with (OUT/'scripts'/name).open('rb') as handle:scripts[name]=hashlib.file_digest(handle,'sha256').hexdigest()
    report=dict(tag=args.tag,resolution=resolution,fps=FPS,frames=records,source_scripts_sha256=scripts)
    (OUT/'review'/f'{args.tag}_render.json').write_text(json.dumps(report,indent=2))


if __name__=='__main__':main()

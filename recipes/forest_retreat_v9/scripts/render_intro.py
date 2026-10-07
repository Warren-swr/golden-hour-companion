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
WHITE=(247,234,218,255)
MUTED=(213,186,160,255)
INK=(83,57,39,255)
ICON_STROKE=3.4
BUTTON_RADIUS=32


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
        for x,y in points:self.circle(x,y,width/2,fill)

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


def skip(d,x,y,direction):
    points=[(-9,-10),(3,0),(-9,10),(-9,-10)]
    d.line([(x+px*direction,y+py) for px,py in points],WHITE,ICON_STROKE)
    d.line([(x+9*direction,y-10),(x+9*direction,y+10)],WHITE,ICON_STROKE)


def static_ui(resolution):
    d=Drawing(resolution)
    d.text((540,750),TITLE,33,bold=True,anchor='mm')
    d.text((540,793),ARTIST,21,fill=MUTED,anchor='mm')
    d.rect((260,846,820,850),(219,190,160,65),2)
    for x in (432,648):d.circle(x,957,BUTTON_RADIUS,(239,217,189,24))
    d.circle(540,957,BUTTON_RADIUS,WHITE)
    skip(d,432,957,-1);skip(d,648,957,1)
    for x in (534,546):d.line([(x,946),(x,968)],INK,ICON_STROKE)
    return d.result(resolution)


def dynamic_ui(resolution,time):
    d=Drawing(resolution)
    elapsed=78+time
    p=elapsed/146
    d.rect((260,846,260+560*p,850),WHITE,2)
    d.text((260,863),f'{int(elapsed)//60}:{int(elapsed)%60:02d}',14,fill=MUTED)
    remaining=146-int(elapsed)
    d.text((820,863),f'−{remaining//60}:{remaining%60:02d}',14,fill=MUTED,anchor='ra')
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
            shadow=cv2.GaussianBlur(shadow,(0,0),max(.01,20*scale*(1-.6*state['progress'])))
            base*=1-shadow[:,:,None]*.22*(1-state['progress'])**2
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

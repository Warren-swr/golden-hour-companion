"""A restrained player layout and an asymmetric cover expansion."""
import math
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent
SOURCE=OUT/'source/v7'
OPENING=OUT/'source/decoded_v7_opening'
NATIVE_TAG='native_a'
FPS=24
INTRO_FRAMES=132
PREROLL_FRAMES=72
OVERLAP_FRAMES=INTRO_FRAMES-PREROLL_FRAMES
SOURCE_FRAMES=1344
FINAL_FRAMES=PREROLL_FRAMES+SOURCE_FRAMES
DURATION=FINAL_FRAMES/FPS
PILOT_FRAMES=240
COVER_RECT=(230,82,620)
EXPAND_START=PREROLL_FRAMES/FPS
EXPAND_END=(INTRO_FRAMES-1)/FPS
UI_FADE_START=3.0
UI_FADE_END=3.25
TITLE='time stamps'
ARTIST='Brxvs'


def smootherstep(value):
    value=max(0.0,min(1.0,value))
    return value**3*(value*(value*6-15)+10)


def release(value,tail=7):
    """Asymmetric C2 easing: a short acceleration and a long quiet settle."""
    value=max(0.0,min(1.0,value))
    return 1-(1-value)**tail*(1+tail*value+tail*(tail+1)/2*value**2)


def animation(frame):
    t=frame/FPS
    u=(t-EXPAND_START)/(EXPAND_END-EXPAND_START)
    progress=release(u)
    position=release(u,8)
    x,y,size=COVER_RECT
    side=size*math.exp(math.log(1080/size)*progress)
    center_y=y+size/2+(540-y-size/2)*position
    if frame==INTRO_FRAMES-1:side=1080;center_y=540
    return dict(frame=frame,time=t,progress=progress,position_progress=position,
        cover_x=(1080-side)/2,cover_y=center_y-side/2,cover_side=side,
        radius=24*(1-progress)**1.4,
        ui_opacity=1-smootherstep((t-UI_FADE_START)/(UI_FADE_END-UI_FADE_START)),
        source_frame=max(1,frame-PREROLL_FRAMES+1))

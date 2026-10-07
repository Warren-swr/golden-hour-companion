"""Timing and paths for the player-to-scene opening."""
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent
SOURCE=OUT/'source/v7'
OPENING=OUT/'source/decoded_v7_opening'
NATIVE_TAG='native_b'
FPS=24
INTRO_FRAMES=96
PREROLL_FRAMES=72
OVERLAP_FRAMES=INTRO_FRAMES-PREROLL_FRAMES
SOURCE_FRAMES=1344
FINAL_FRAMES=PREROLL_FRAMES+SOURCE_FRAMES
DURATION=FINAL_FRAMES/FPS
COVER_RECT=(240,112,600)
EXPAND_START=1.0
EXPAND_END=(INTRO_FRAMES-1)/FPS
UI_FADE_START=1.10
UI_FADE_END=1.75
TITLE='time stamps'
ARTIST='Brxvs'


def smootherstep(value):
    value=max(0.0,min(1.0,value))
    return value**3*(value*(value*6-15)+10)


def animation(frame):
    t=frame/FPS
    progress=smootherstep((t-EXPAND_START)/(EXPAND_END-EXPAND_START))
    x,y,size=COVER_RECT
    side=size+(1080-size)*progress
    center_y=y+size/2+(540-y-size/2)*progress
    return dict(frame=frame,time=t,progress=progress,
        cover_x=(1080-side)/2,cover_y=center_y-side/2,cover_side=side,
        radius=24*(1-progress),
        ui_opacity=1-smootherstep((t-UI_FADE_START)/(UI_FADE_END-UI_FADE_START)),
        source_frame=max(1,frame-PREROLL_FRAMES+1))

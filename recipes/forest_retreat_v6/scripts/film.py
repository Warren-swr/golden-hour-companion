"""One timing contract for camera authoring, rendering, encoding and review."""
FPS=24
SIZE=2160
TIMING=[
    ('01','reference_and_room',5.5),
    ('02','living_room',4.0),
    ('03','kitchen_and_room_junction',3.5),
    ('04','bedroom_and_forest',3.5),
    ('05','stone_bathroom',3.0),
    ('06','open_threshold',4.0),
    ('07','terrace_and_clearing',3.5),
    ('08','house_and_clearing',3.5),
    ('09','reflections',3.5),
    ('10','garden_room',3.5),
    ('11','forest_departure',6.5),
]
RANGES={};STILLS=[];cursor=1
for shot,name,duration in TIMING:
    end=cursor+round(duration*FPS)-1
    RANGES[shot]=(cursor,end)
    STILLS.append((1 if shot=='01' else (cursor+end)//2,shot+'_'+name))
    cursor=end+1
FRAMES=cursor-1
DURATION=FRAMES/FPS
CUTS={start for start,end in list(RANGES.values())[1:]}
SHOT_COUNT=len(TIMING)
FADE_SECONDS=.75
assert FRAMES==1056 and DURATION==44

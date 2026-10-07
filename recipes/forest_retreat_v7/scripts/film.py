"""One timing contract for the faster 56-second edit with three long takes."""
FPS=24
SIZE=2160
TIMING=[
    ('01','reference_and_room',6.0),
    ('02','living_to_room_junction',8.0),
    ('03','bedroom_and_forest',4.5),
    ('04','stone_bathroom',3.5),
    ('05','threshold_to_terrace',9.0),
    ('06','house_and_clearing',5.0),
    ('07','reflections',4.5),
    ('08','garden_passage',6.5),
    ('09','forest_departure',9.0),
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
LONG_TAKES={'02','05','09'}
assert FRAMES==1344 and DURATION==56

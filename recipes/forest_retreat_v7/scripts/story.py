"""Faster spatial movement, with room, threshold and departure long takes."""
import cinematography as motion
from film import RANGES,FRAMES

SHOTS=[
    dict(id='01',name='Afternoon begins to unfold',
         position=[(.26,-2.75,1.41),(.40025,-3.13775,1.430625),(.54875,-3.53375,1.45125)],
         target=[(0,0,1.35),(-.066,-.099,1.30875),(-.1485,-.20625,1.2675)],
         lens=[(0,54),(1,54)],fstop=[(0,8),(1,8)],
         v_in=.22,v_out=.55,ramp_in=.20,ramp_out=.17,float=0,exposure=0,
         intent='A six-second opening with more physical travel than v6, retaining the exact reference first pose.'),
    dict(id='02',name='One continuous room reveal',
         position=[(-.70,-3.70,1.55),(-.26,-3.65,1.57),(.14,-3.80,1.60),(.45,-4.10,1.63)],
         target=[(1.80,-.70,1.42),(2.21,-.74,1.44),(2.63,-1.04,1.46),(3.00,-1.42,1.49)],
         lens=[(0,24),(1,24)],fstop=[(0,6.3),(1,6.3)],exposure=.12,
         v_in=.45,v_out=.45,ramp_in=.18,ramp_out=.22,
         intent='An eight-second lateral track unfolds the bench, kitchen and bedroom doorway with restrained turning and gentle cut-in/cut-out speed.'),
    dict(id='03',name='Linen and the forest window',
         position=[(3.74,-2.95,1.48),(4.006,-2.969,1.499),(4.291,-2.969,1.499)],
         target=[(5.39,-1.28,1.41),(5.58,-1.299,1.41),(5.77,-1.318,1.41)],
         lens=[(0,24),(1,24)],fstop=[(0,5.6),(1,5.6)],exposure=.24,
         intent='Increase bedroom lateral travel to keep the window and bed evolving through the 4.5-second view.'),
    dict(id='04',name='Stone and afternoon light',
         position=[(3.56,-4.49,1.45),(3.791,-4.6055,1.45),(4.0385,-4.7045,1.4665)],
         target=[(5.67,-4.12,1.15),(5.835,-4.12,1.15),(6.00,-4.1365,1.15)],
         lens=[(0,24),(1,24)],fstop=[(0,5.6),(1,5.6)],exposure=.20,
         intent='A more purposeful 3.5-second architectural glide, keeping the tub and stone wall in context.'),
    dict(id='05',name='Through the door and onto the terrace',
         position=[(1.88,-4.83,1.60),(1.96,-5.48,1.60),(2.35,-6.05,1.62),(2.78,-6.48,1.65),(3.15,-6.86,1.68)],
         target=[(2.30,-11.50,.95),(2.30,-11.88,.98),(2.22,-12.15,1.02),(2.10,-12.35,1.06),(1.95,-12.55,1.10)],
         lens=[(0,29),(1,29)],fstop=[(0,6.3),(1,6.3)],exposure=.03,
         intent='A nine-second continuous threshold crossing: the doorway clears and a rightward arc beside the table opens the pool without a central column wipe.'),
    dict(id='06',name='The house across the water',
         position=[(9.12,-17.50,2.27),(8.38,-16.66,2.43),(7.64,-15.80,2.57)],
         target=[(1.10,-7.25,1.67),(1.01,-7.07,1.70),(.92,-6.89,1.73)],
         lens=[(0,32),(1,32)],fstop=[(0,8),(1,8)],exposure=0,
         intent='A five-second exterior move with stronger foreground parallax and a fuller reveal of the facade.'),
    dict(id='07',name='Reflections below the eaves',
         position=[(-.45,-15.48,.59),(.0925,-15.36625,.59875),(.6525,-15.2525,.6075)],
         target=[(1.05,-6.94,1.78),(1.2775,-6.94,1.78),(1.5225,-6.94,1.78)],
         lens=[(0,31),(1,31)],fstop=[(0,8),(1,8)],exposure=0,
         intent='A faster 4.5-second low tracking view keeps the house readable above its moving reflection.'),
    dict(id='08',name='Among the garden layers',
         position=[(-9.40,-14.76,1.43),(-8.88,-15.13,1.47),(-8.31,-15.34,1.54),(-7.82,-15.45,1.61)],
         target=[(-3.05,-7.70,1.55),(-2.73,-7.49,1.64),(-2.34,-7.26,1.72),(-1.90,-7.05,1.78)],
         lens=[(0,30),(1,30)],fstop=[(0,6.3),(1,6.3)],exposure=0,
         intent='A 6.5-second garden passage reveals layers of chairs, stones and planting while circling toward the house.'),
    dict(id='09',name='A place within the forest',
         position=[(-7.35,-19.55,3.75),(-8.02,-20.50,4.53),(-8.62,-21.56,5.48),(-9.17,-22.73,6.52),(-9.70,-23.90,7.60)],
         target=[(1.02,-7.15,1.73),(1.07,-6.95,1.78),(1.14,-6.63,1.85),(1.22,-6.33,1.91),(1.30,-6.16,1.96)],
         lens=[(0,34),(1,34)],fstop=[(0,8),(1,8)],
         v_in=.55,v_out=0,ramp_in=.16,ramp_out=.28,float=0,exposure=0,
         intent='A nine-second rising retreat travels farther and faster, then gradually settles over the complete house and garden.'),
]
for shot in SHOTS:
    shot['frames']=RANGES[shot['id']]
    for key,value in dict(v_in=.55,v_out=.55,ramp_in=.16,ramp_out=.16,float=0).items():
        shot.setdefault(key,value)


def build():
    motion.SHOTS=SHOTS
    motion.FRAME_END=FRAMES
    return motion.build()

"""42 seconds in nine connected spaces; authored lenses, movement and edit rhythm."""
import cinematography as motion

SHOTS = [
    dict(id='01', name='A fleeting familiar afternoon', frames=(1,60),
         position=[(.26,-2.75,1.41),(.52,-3.47,1.45),(.90,-4.10,1.50)],
         target=[(0,0,1.35),(-.10,-.16,1.28),(-.27,-.40,1.20)],
         lens=[(0,54),(1,44)],fstop=[(0,8),(1,6.3)],
         v_in=.78,v_out=1,ramp_in=.16,ramp_out=0,float=0,exposure=0,
         intent='The reference exists for one frame, then immediately opens into the room. '
                'A brief 2.5-second memory, without a static hold or a prolonged cushion study.'),
    dict(id='02', name='The house and its clearing', frames=(61,168),
         position=[(9.55,-18.0,2.05),(8.83,-17.08,2.25),(8.10,-16.15,2.47)],
         target=[(1.15,-7.42,1.60),(1.02,-7.16,1.67),(.94,-6.98,1.72)],
         lens=[(0,32),(1,32)],fstop=[(0,8),(1,8)],
         v_in=.9,v_out=.9,ramp_in=.15,ramp_out=.15,float=.25,exposure=0,
         intent='An early environmental reveal. Chairs, moving water, porch, gable and woodland '
                'have separate depth layers; a 32 mm lateral approach produces real parallax.'),
    dict(id='03', name='An inhabited room', frames=(169,288),
         position=[(2.36,-4.66,1.60),(1.99,-4.38,1.62),(1.53,-4.00,1.62)],
         target=[(-.24,-1.23,1.43),(-.56,-1.35,1.43),(-.86,-1.48,1.43)],
         lens=[(0,27),(1,27)],fstop=[(0,5.6),(1,5.6)],
         v_in=.85,v_out=.85,ramp_in=.18,ramp_out=.18,float=.35,exposure=.10,
         intent='A shoulder-height wide interior. The breakfast table, kitchen, reading corner, '
                'sofa and library connect in one room; furniture passes at different depths.'),
    dict(id='04', name='Linen and the forest window', frames=(289,384),
         position=[(3.66,-2.94,1.48),(3.87,-2.96,1.49),(4.10,-2.96,1.49)],
         target=[(5.34,-1.27,1.41),(5.48,-1.29,1.41),(5.60,-1.30,1.41)],
         lens=[(0,24),(1,24)],fstop=[(0,5.6),(1,5.6)],
         v_in=.9,v_out=.9,ramp_in=.2,ramp_out=.2,float=.22,exposure=.32,
         intent='A complete bedroom and its forest window, at eye level. Bed linen supports '
                'the composition; pillows never become a separate close-up.'),
    dict(id='05', name='Stone and quiet water', frames=(385,456),
         position=[(3.51,-4.47,1.45),(3.70,-4.56,1.45),(3.91,-4.64,1.46)],
         target=[(5.63,-4.12,1.15),(5.78,-4.12,1.15),(5.92,-4.13,1.15)],
         lens=[(0,24),(1,24)],fstop=[(0,5.6),(1,5.6)],
         v_in=.9,v_out=.9,ramp_in=.15,ramp_out=.15,float=.18,exposure=.20,
         intent='A compact architectural glimpse of the repaired bathing room: vanity and mirror, '
                'stone, the supported bath bridge and the window. No isolated product close-up.'),
    dict(id='06', name='Through the open house', frames=(457,600),
         position=[(1.54,-3.62,1.59),(1.88,-4.88,1.58),(2.51,-6.00,1.53),
                   (3.37,-7.16,1.45),(4.04,-8.58,1.30)],
         target=[(2.10,-10.5,1.08),(2.40,-11.2,.92),(2.92,-12.0,.72),
                 (3.61,-12.54,.51),(4.11,-12.8,.36)],
         lens=[(0,29),(1,29)],fstop=[(0,6.3),(1,6.3)],
         v_in=.8,v_out=.9,ramp_in=.20,ramp_out=.18,float=.35,exposure=0,
         intent='A continuous doorway traversal proves the real connection of interior, pergola '
                'and pool garden. The eye follows the open doorway rather than a furniture detail.'),
    dict(id='07', name='Reflections below the eaves', frames=(601,696),
         position=[(-.76,-15.55,.58),(-.18,-15.42,.57),(.46,-15.30,.59)],
         target=[(.92,-6.93,1.78),(1.20,-6.94,1.77),(1.48,-6.95,1.78)],
         lens=[(0,31),(1,31)],fstop=[(0,8),(1,8)],
         v_in=.9,v_out=.9,ramp_in=.15,ramp_out=.15,float=.16,exposure=0,
         intent='One low, wide reflection shot, not a macro of the spillway. The entire facade '
                'and its rippling reflection share the frame; water carries the motion.'),
    dict(id='08', name='The garden room', frames=(697,816),
         position=[(-9.35,-14.96,1.32),(-8.70,-15.24,1.41),(-7.94,-15.39,1.48)],
         target=[(-3.20,-7.70,1.53),(-2.74,-7.45,1.56),(-2.22,-7.22,1.60)],
         lens=[(0,30),(1,30)],fstop=[(0,6.3),(1,6.3)],
         v_in=.8,v_out=.9,ramp_in=.20,ramp_out=.15,float=.30,exposure=0,
         intent='The fire bowl and crafted chairs lead to a second outdoor room, with the '
                'tree trunk as a foreground frame and the cabin beyond. A fresh side of the house.'),
    dict(id='09', name='A place within the forest', frames=(817,1008),hold_out=8,
         position=[(-6.85,-18.48,2.65),(-7.45,-19.36,3.69),(-8.09,-20.58,5.18),
                   (-8.70,-22.04,6.68),(-8.93,-23.13,7.30)],
         target=[(.78,-7.88,1.52),(.93,-7.29,1.63),(1.13,-6.67,1.81),
                 (1.35,-6.12,1.97),(1.42,-5.92,2.03)],
         lens=[(0,34),(1,35)],fstop=[(0,8),(1,11)],
         v_in=.85,v_out=0,ramp_in=.12,ramp_out=.40,float=.15,exposure=0,
         intent='A left-side crane departure reveals roof, woodland, fire garden and pool together. '
                'The final image is broader than the first exterior; only the final third-second settles.'),
]


def build():
    motion.SHOTS = SHOTS
    motion.FRAME_END = 1008
    return motion.build()

"""A measured room-to-garden sequence, with longer opening and closing moves."""
import cinematography as motion
from film import RANGES,FRAMES

SHOTS=[
    dict(id='01',name='A measured familiar afternoon',
         position=[(.26,-2.75,1.41),(.43,-3.22,1.435),(.61,-3.70,1.46)],
         target=[(0,0,1.35),(-.08,-.12,1.30),(-.18,-.25,1.25)],
         lens=[(0,54),(1,54)],fstop=[(0,8),(1,8)],
         v_in=.12,v_out=.35,ramp_in=.25,ramp_out=.25,float=0,exposure=0,
         intent='A 5.5-second opening with a gentle physical retreat and fixed focal length. '
                'The reference composition gradually reveals the bench; no compounded dolly and zoom.'),
    dict(id='02',name='The room opens around us',
         position=[(2.17,-4.50,1.60),(1.93,-4.34,1.61),(1.70,-4.16,1.61)],
         target=[(-.38,-1.30,1.43),(-.56,-1.38,1.43),(-.72,-1.43,1.43)],
         lens=[(0,27),(1,27)],fstop=[(0,5.6),(1,5.6)],exposure=.10,
         intent='A wider continuation of the opening room, retaining the sunlit bench as the visual anchor.'),
    dict(id='03',name='At the room junction',
         position=[(1.02,-4.78,1.59),(1.18,-4.74,1.60),(1.35,-4.69,1.60)],
         target=[(3.45,-2.44,1.46),(3.54,-2.37,1.46),(3.64,-2.30,1.46)],
         lens=[(0,26),(1,26)],fstop=[(0,6.3),(1,6.3)],exposure=.16,
         intent='A new contextual view of the breakfast area and room junction motivates the following bedroom cut.'),
    dict(id='04',name='Linen and the forest window',
         position=[(3.74,-2.95,1.48),(3.88,-2.96,1.49),(4.03,-2.96,1.49)],
         target=[(5.39,-1.28,1.41),(5.49,-1.29,1.41),(5.59,-1.30,1.41)],
         lens=[(0,24),(1,24)],fstop=[(0,5.6),(1,5.6)],exposure=.24,
         intent='A 3.5-second spatial bedroom view at a restrained lateral pace; the window carries the eye onward.'),
    dict(id='05',name='Stone and quiet water',
         position=[(3.56,-4.49,1.45),(3.70,-4.56,1.45),(3.85,-4.62,1.46)],
         target=[(5.67,-4.12,1.15),(5.77,-4.12,1.15),(5.87,-4.13,1.15)],
         lens=[(0,24),(1,24)],fstop=[(0,5.6),(1,5.6)],exposure=.20,
         intent='A concise three-second architectural view, with the same calm lateral movement as the bedroom.'),
    dict(id='06',name='Across the open threshold',
         position=[(1.82,-4.65,1.60),(1.94,-5.05,1.59),(2.06,-5.45,1.58)],
         target=[(2.30,-11.5,.95),(2.42,-11.70,.93),(2.55,-11.9,.91)],
         lens=[(0,29),(1,29)],fstop=[(0,6.3),(1,6.3)],exposure=.03,
         intent='A short 0.67-metre threshold move replaces the fast six-second traverse. '
                'The doorway frames the pool before the edit moves onto the terrace.'),
    dict(id='07',name='The terrace and the clearing',
         position=[(6.45,-6.45,1.64),(6.27,-6.60,1.64),(6.08,-6.76,1.64)],
         target=[(.65,-10.9,1.05),(.55,-11.0,1.04),(.45,-11.1,1.03)],
         lens=[(0,28),(1,28)],fstop=[(0,8),(1,8)],exposure=0,
         intent='A new oblique terrace view links the doorway to the garden; furniture remains spatial context.'),
    dict(id='08',name='The house across the water',
         position=[(9.12,-17.50,2.27),(8.75,-17.08,2.35),(8.38,-16.65,2.42)],
         target=[(1.10,-7.25,1.67),(1.055,-7.16,1.685),(1.01,-7.07,1.70)],
         lens=[(0,32),(1,32)],fstop=[(0,8),(1,8)],exposure=0,
         intent='A restrained exterior reveal after the rooms and terrace are established; water links both sides of the cut.'),
    dict(id='09',name='Reflections below the eaves',
         position=[(-.45,-15.48,.59),(-.14,-15.415,.595),(.18,-15.35,.60)],
         target=[(1.05,-6.94,1.78),(1.18,-6.94,1.78),(1.32,-6.94,1.78)],
         lens=[(0,31),(1,31)],fstop=[(0,8),(1,8)],exposure=0,
         intent='Lower the eye to the water while keeping the facade dominant, at a moderated lateral pace.'),
    dict(id='10',name='The garden room',
         position=[(-9.00,-15.10,1.40),(-8.75,-15.20,1.43),(-8.45,-15.30,1.46)],
         target=[(-2.85,-7.53,1.56),(-2.68,-7.44,1.57),(-2.47,-7.36,1.58)],
         lens=[(0,30),(1,30)],fstop=[(0,6.3),(1,6.3)],exposure=0,
         intent='A compact 3.5-second garden view prepares the same side of the house for the final crane.'),
    dict(id='11',name='A place within the forest',
         position=[(-7.35,-19.55,3.75),(-7.93,-20.68,4.72),(-8.52,-21.98,5.85)],
         target=[(1.02,-7.15,1.73),(1.16,-6.63,1.85),(1.30,-6.16,1.96)],
         lens=[(0,34),(1,34)],fstop=[(0,8),(1,8)],
         v_in=.45,v_out=0,ramp_in=.18,ramp_out=.32,float=0,exposure=0,
         intent='A 6.5-second departure with a shorter crane arc and fixed focal length. '
                'The move eases into the final composition instead of accelerating away.'),
]
for shot in SHOTS:
    shot['frames']=RANGES[shot['id']]
    for key,value in dict(v_in=.45,v_out=.45,ramp_in=.20,ramp_out=.20,float=0).items():
        shot.setdefault(key,value)

# Calibrated against the first complete pilot's measured visible motion.
# Keep the reference pose exact and keep the threshold's final position outside.
for index,scale,anchor in ((0,.50,0),(1,.72,0),(5,.80,-1)):
    shot=SHOTS[index]
    for field in ('position','target'):
        origin=shot[field][anchor]
        shot[field]=[tuple(a+scale*(b-a) for a,b in zip(origin,point)) for point in shot[field]]
    shot['travel_scale']=scale


def build():
    motion.SHOTS=SHOTS
    motion.FRAME_END=FRAMES
    return motion.build()

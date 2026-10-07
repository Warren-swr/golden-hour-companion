"""Read-only diagnostic of the physical objects intercepting sunset rays."""
import bpy
from mathutils import Vector
scene=bpy.context.scene
depsgraph=bpy.context.evaluated_depsgraph_get()
direction=Vector((-.35,-1,.165)).normalized()
for label,points in [
    ('wall',[(x,-.15,z) for z in (.9,1.7,2.5) for x in (-.5,0,.5)]),
    ('terrace',[(x,-7.5,.1) for x in (-4,-2,0,2,4,6)]),
    ('roof',[(x,-3.0,3.7) for x in (-2,0,2,4,6)]),
    ('kitchen',[(2,-.4,1.6),(2.6,-.4,1.2)])]:
    for point in points:
        origin=Vector(point)
        hits=[]
        for attempt in range(16):
            hit,loc,normal,index,obj,matrix=scene.ray_cast(depsgraph,origin,direction,distance=180)
            if not hit:
                hits.append('SUN')
                break
            if obj.visible_shadow and 'glass' not in obj.name.lower():
                hits.append([obj.name,[round(v,2) for v in loc]])
                break
            origin=loc+direction*.01
        print(label,point,hits,flush=True)

import bpy
from mathutils import Vector
sc=bpy.context.scene
dg=bpy.context.evaluated_depsgraph_get()
direction=Vector((-.35,-1,.165)).normalized()
def caster(origin):
    for _ in range(16):
        hit,loc,normal,index,obj,matrix=sc.ray_cast(dg,origin,direction,distance=100)
        if not hit:
            return 'SUN'
        if obj.visible_shadow and 'glass' not in obj.name.lower():
            return obj.name
        origin=loc+direction*.01
    return 'TRANSMISSION_LIMIT'
for z in (.68,.83,.90,1.03,1.17,1.28):
    row=[]
    for x in (-.25,-.10,.03,.18,.32):
        row.append((x,caster(Vector((x,-.40,z)))))
    print('LIGHT_PROBE',z,row,flush=True)

"""Four physically plausible camera moves and architectural still cameras."""
from common import *


def camera(name,location,target,lens=50,fstop=8):
    data=bpy.data.cameras.new(name)
    obj=bpy.data.objects.new(name,data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location=location
    aim(obj,target)
    data.lens=lens
    data.sensor_width=36
    data.clip_start=.025
    data.clip_end=250
    data.dof.use_dof=True
    data.dof.aperture_fstop=fstop
    data.dof.aperture_blades=9
    data.dof.focus_distance=(Vector(target)-obj.location).length
    return obj


def key(obj,frame,position,target,lens,fstop):
    obj.location=position
    aim(obj,target)
    obj.data.lens=lens
    obj.data.dof.focus_distance=(Vector(target)-obj.location).length
    obj.data.dof.aperture_fstop=fstop
    obj.keyframe_insert(data_path='location',frame=frame)
    obj.keyframe_insert(data_path='rotation_euler',frame=frame)
    obj.data.keyframe_insert(data_path='lens',frame=frame)
    obj.data.dof.keyframe_insert(data_path='focus_distance',frame=frame)
    obj.data.dof.keyframe_insert(data_path='aperture_fstop',frame=frame)


def lighting():
    collection('40 • Single golden-hour lighting state')
    world=bpy.data.worlds.new('Late afternoon physical sky')
    bpy.context.scene.world=world
    world.use_nodes=True
    n,l=world.node_tree.nodes,world.node_tree.links
    sky=n.new('ShaderNodeTexSky')
    sky.sky_type='NISHITA'
    sky.sun_elevation=math.radians(8.55)
    sky.sun_rotation=math.atan2(-100,-35)
    sky.sun_disc=False
    sky.altitude=.15
    sky.air_density=1.0
    sky.dust_density=2.8
    bg=n.get('Background')
    bg.inputs['Strength'].default_value=.65
    l.new(sky.outputs['Color'],bg.inputs['Color'])
    data=bpy.data.lights.new('Setting sun • 8.55 degrees','SUN')
    sun=bpy.data.objects.new('Setting sun • physical window and plant shadows',data)
    bpy.context.scene.collection.objects.link(sun)
    sun.location=(-35,-100,16.5)
    aim(sun,(0,0,0))
    data.energy=5.3
    data.angle=math.radians(.62)
    data.color=(1.0,.57,.22)
    # Only a very low-energy practical lamp; no invisible orange fill cards.
    data=bpy.data.lights.new('Warm reading lamp practical','POINT')
    obj=bpy.data.objects.new('Warm reading lamp practical',data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location=(-1.40,-.56,1.58)
    data.energy=5
    data.color=(1,.72,.40)
    data.shadow_soft_size=.04
    for x in (3.89,6.17):
        data=bpy.data.lights.new('Bedside warm practical','POINT')
        obj=bpy.data.objects.new('Bedside warm practical',data)
        bpy.context.scene.collection.objects.link(obj)
        obj.location=(x,-.72,1.015)
        data.energy=18
        data.color=(1,.74,.47)
        data.shadow_soft_size=.027


def build(m):
    lighting()
    collection('41 • Cinematography / native square gate')
    a=camera('A • Reference to room',(.26,-2.75,1.41),(0,0,1.35),54,8)
    key(a,1,(.26,-2.75,1.41),(0,0,1.35),54,8)
    key(a,49,(.26,-2.75,1.41),(0,0,1.35),54,8)
    key(a,158,(.71,-3.49,1.62),(-.15,-.32,1.26),44,7.1)
    key(a,288,(1.50,-4.52,1.82),(-.24,-.92,1.23),31,8)
    b=camera('B • A quiet kitchen',(1.05,-3.45,1.66),(2.32,-.33,1.21),40,8)
    key(b,289,(1.05,-3.45,1.66),(2.32,-.33,1.21),40,8)
    key(b,432,(.55,-2.66,1.61),(2.25,-.32,1.10),42,8)
    c=camera('C • The afternoon window',(1.55,-2.80,1.6),(-.55,-5.5,1.2),36,5.6)
    key(c,433,(1.55,-2.80,1.6),(-.55,-5.5,1.2),36,5.6)
    key(c,624,(.80,-4.0,1.30),(-.5,-5.5,1.04),40,6.3)
    d=camera('D • Home in a golden forest',(3.8,-10.90,2.25),(.75,-2.1,1.43),32,9)
    key(d,625,(3.8,-10.90,2.25),(.75,-2.1,1.43),32,9)
    key(d,864,(11.6,-21.0,7.20),(1.4,-2.58,2.35),36,11)
    sc=bpy.context.scene
    for f,obj in [(1,a),(289,b),(433,c),(625,d)]:
        marker=sc.timeline_markers.new(obj.name,frame=f)
        marker.camera=obj
    sc.camera=a
    camera('Still • Living room',(2.62,-4.71,1.82),(-.75,-1.54,1.12),27,9)
    camera('Still • Bedroom',(3.77,-2.99,1.70),(5.16,-1.42,.87),24,9)
    camera('Still • Bathroom',(3.67,-3.80,1.87),(5.53,-4.39,.77),23,9)
    camera('Still • Kitchen',(1.29,-2.67,1.72),(2.34,-.35,1.24),35,8)
    camera('Still • Exterior',(13.40,-21.0,9.20),(1.40,-2.64,2.50),39,11)
    camera('Still • Garden',(-4.6,-10.19,1.72),(.5,-4.1,1.4),31,8)
    camera('Still • Forest',(14.2,-18.3,2.4),(8,0,6.6),38,8)
    sc.frame_set(1)

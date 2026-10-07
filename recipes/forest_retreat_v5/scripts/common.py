"""Deterministic, metre-scale modeling helpers for Golden Hour Companion."""
import bpy
import math
import random
from mathutils import Vector
from math import sin, cos, pi

ROOT = None
COLLECTION = None
RNG = random.Random(251025)


def collection(name):
    global COLLECTION
    COLLECTION = bpy.data.collections.get(name)
    if COLLECTION is None:
        COLLECTION = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(COLLECTION)
    return COLLECTION


def link_object(obj):
    if COLLECTION:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        COLLECTION.objects.link(obj)
    return obj


def material(obj, mat):
    if mat:
        obj.data.materials.append(mat)
    return obj


def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def cube(name, loc, size, mat, bevel=0.0):
    verts=[(x*size[0]/2,y*size[1]/2,z*size[2]/2) for x,y,z in
           [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    faces=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
    obj=mesh(name,verts,faces,mat)
    obj.location=loc
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        mod = obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj


def sphere(name, loc, scale, mat, segments=40, rings=24):
    verts=[(scale[0]*sin(pi*j/rings)*cos(2*pi*i/segments),
            scale[1]*sin(pi*j/rings)*sin(2*pi*i/segments),scale[2]*cos(pi*j/rings))
           for j in range(rings+1) for i in range(segments)]
    faces=[]
    for j in range(rings):
        for i in range(segments):
            a=j*segments+i
            b=j*segments+(i+1)%segments
            faces.append((a,a+segments,b+segments,b))
    obj=mesh(name,verts,faces,mat)
    obj.location=loc
    return smooth(obj)


def cylinder(name, loc, radius, depth, mat, vertices=48):
    verts=[(radius*cos(i*2*pi/vertices),radius*sin(i*2*pi/vertices),z)
           for z in (-depth/2,depth/2) for i in range(vertices)]
    faces=[tuple(reversed(range(vertices))),tuple(range(vertices,vertices*2))]
    faces += [(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
    obj=mesh(name,verts,faces,mat)
    obj.location=loc
    mod = obj.modifiers.new('Edge radius', 'BEVEL')
    mod.width = min(radius * .12, .008)
    mod.segments = 3
    smooth(obj)
    return obj


def beam(name, a, b, radius, mat, r2=None):
    a, b = Vector(a), Vector(b)
    delta = b-a
    rot=delta.to_track_quat('Z','Y')
    verts=[tuple(center+rot@Vector((r*cos(i*2*pi/12),r*sin(i*2*pi/12),0)))
           for center,r in [(a,radius),(b,radius if r2 is None else r2)] for i in range(12)]
    faces=[tuple(reversed(range(12))),tuple(range(12,24))]
    faces += [(i,(i+1)%12,(i+1)%12+12,i+12) for i in range(12)]
    return smooth(mesh(name,verts,faces,mat))


def curve(name, points, radius, mat, cyclic=False):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 2
    data.bevel_depth = radius
    data.bevel_resolution = 2
    spl = data.splines.new('POLY')
    spl.points.add(len(points)-1)
    spl.points.foreach_set('co', [c for p in points for c in (*p, 1)])
    spl.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    (COLLECTION or bpy.context.scene.collection).objects.link(obj)
    return material(obj, mat)


def mesh(name, verts, faces, mat):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    (COLLECTION or bpy.context.scene.collection).objects.link(obj)
    material(obj, mat)
    return obj


def lathe(name, profile, loc, mat, segments=64):
    verts = [(r*cos(i*2*pi/segments), r*sin(i*2*pi/segments), z)
             for r,z in profile for i in range(segments)]
    faces = []
    for j in range(len(profile)-1):
        for i in range(segments):
            a = j*segments+i
            b = j*segments+(i+1)%segments
            faces.append((a,b,b+segments,a+segments))
    obj=smooth(mesh(name, verts, faces, mat))
    obj.location=loc
    return obj


def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def torus(name, loc, major, minor, mat, rotation=(0,0,0)):
    verts=[((major+minor*cos(j*2*pi/12))*cos(i*2*pi/64),
            (major+minor*cos(j*2*pi/12))*sin(i*2*pi/64),minor*sin(j*2*pi/12))
           for i in range(64) for j in range(12)]
    faces=[]
    for i in range(64):
        for j in range(12):
            faces.append((i*12+j,((i+1)%64)*12+j,((i+1)%64)*12+(j+1)%12,i*12+(j+1)%12))
    obj=mesh(name,verts,faces,mat)
    obj.location=loc
    obj.rotation_euler=rotation
    return smooth(obj)

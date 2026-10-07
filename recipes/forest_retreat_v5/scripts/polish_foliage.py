"""Repair per-face color bands and refine the four calibrated broad window leaves."""
import math
from math import sin,cos,pi

import bpy
import bmesh
from mathutils import Vector

from common import collection,mesh,smooth,curve,cylinder
from materials import pbr,rgb

SPECS=[((-1.16,-4.40,1.12),(.05,.4,1),.91,.42),
       ((-.85,-4.30,.94),(.2,.4,1),.68,.30),
       ((-1.20,-4.43,.75),(-.1,-.3,1),.68,.26),
       ((-.92,-4.35,1.31),(.3,.4,.8),.59,.27)]


def blade_material(name,color,underside=False):
    mat=pbr(name,color,.53 if underside else .43,noise=.14,bump=.00009,scale=95)
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    bs=nodes.get('Principled BSDF')
    bs.inputs['IOR'].default_value=1.44
    bs.inputs['Coat Weight'].default_value=.035 if underside else .13
    bs.inputs['Coat Roughness'].default_value=.4
    bs.inputs['Subsurface Weight'].default_value=.025
    translucent=nodes.new('ShaderNodeBsdfTranslucent')
    translucent.inputs['Color'].default_value=rgb(color)
    mix=nodes.new('ShaderNodeMixShader')
    mix.inputs[0].default_value=.12
    links.new(bs.outputs[0],mix.inputs[1]);links.new(translucent.outputs[0],mix.inputs[2])
    links.new(mix.outputs[0],nodes.get('Material Output').inputs['Surface'])
    return mat


def build():
    old=bpy.data.objects['Window fig broad veined leaves']
    before=dict(vertices=len(old.data.vertices),polygons=len(old.data.polygons),
                material_indices=[p.material_index for p in old.data.polygons])
    for obj in list(bpy.data.objects):
        if obj.name.startswith(('Window fig broad veined leaves','Window fig woody stem')):
            bpy.data.objects.remove(obj,do_unlink=True)
    collection('65 • V5 / anatomically detailed window foliage')
    vein=pbr('V5 / raised leaf veins','#728057',.56,noise=.10,bump=.00004,scale=140)
    underside_vein=pbr('V5 / underside vascular relief','#7A875C',.60,noise=.10,bump=.00004,scale=140)
    petiole=pbr('V5 / living olive-green petioles','#59683A',.47,noise=.12,bump=.00015,scale=50)
    back=blade_material('V5 / diffuse leaf undersides','#68734A',True)
    colours=('#42562D','#485E34','#455B30','#3E542C')
    objects=[]
    for index,(position,axis,L,W) in enumerate(SPECS):
        p=Vector(position)+Vector((.52,0,0));n=Vector(axis).normalized()
        across=n.cross(Vector((0,0,1))).normalized()
        def point(t,s):
            envelope=max(0,sin(pi*t))
            width=W*envelope**.75*(1+.008*sin(t*37+index*1.7))
            center=p+n*(L*t)+Vector((0,0,.12*L*envelope))
            rib=.035*L*math.sqrt(envelope)*(1-s*s)**2
            edge=.003*envelope*s**4*sin(t*31+index*1.3)
            fold=.0018*envelope*sin(t*53+abs(s)*11+index)*s*s
            return center+across*(width*s)+Vector((0,0,rib+edge+fold))
        rows,columns=65,17
        verts=[tuple(point(j/(rows-1),-1+2*i/(columns-1))) for j in range(rows) for i in range(columns)]
        faces=[]
        for j in range(rows-1):
            for i in range(columns-1):
                a=j*columns+i
                faces.append((a,a+1,a+1+columns,a+columns))
        front=blade_material('V5 / window leaf %02d chlorophyll'%index,colours[index])
        ob=smooth(mesh('V5 / continuous curved window leaf %02d'%index,verts,faces,front))
        ob.data.materials.append(back)
        # Every face of one blade has the same front material. The inherited code
        # divided polygon indices by 8, although each of these leaves had 40 faces.
        # That assigned the pale material as stripes across individual leaves.
        for polygon in ob.data.polygons:polygon.material_index=0
        uv=ob.data.uv_layers.new(name='Anatomical leaf coordinates')
        for polygon in ob.data.polygons:
            for loop_index in polygon.loop_indices:
                vi=ob.data.loops[loop_index].vertex_index
                uv.data[loop_index].uv=(vi//columns/(rows-1),vi%columns/(columns-1))
        bm=bmesh.new();bm.from_mesh(ob.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        bm.to_mesh(ob.data);bm.free();ob.data.update()
        solid=ob.modifiers.new('Botanical lamina thickness','SOLIDIFY')
        solid.thickness=.00065;solid.material_offset=1;solid.material_offset_rim=1
        ob['construction']='Continuous blade; one front material; separate underside; raised midrib and branching secondary veins.'
        def vascular_point(t,s,underside):
            dt=point(t+.0001,s)-point(t-.0001,s)
            ds=point(t,s+.0001)-point(t,s-.0001)
            normal=ds.cross(dt).normalized()
            return point(t,s)+normal*(-.00095 if underside else .0003)
        for underside in (False,True):
            label='underside' if underside else 'upper surface'
            mat=underside_vein if underside else vein
            curve('V5 / leaf %02d %s central midrib'%(index,label),
                  [vascular_point(.025+.945*j/48,0,underside) for j in range(49)],
                  (.0016 if underside else .0014)*(L/.91),mat)
            for k in range(8):
                root_t=.12+k*.092
                for side in (-1,1):
                    points=[vascular_point(root_t+.075*u,side*.86*u,underside) for u in [j/12 for j in range(13)]]
                    curve('V5 / leaf %02d %s secondary vein'%(index,label),points,.00065*(L/.91),mat)
        origin=Vector((-.62+(index-1.5)*.011,-4.42,.355))
        stem=[]
        for j in range(25):
            t=j/24
            stem.append(origin.lerp(p,t)+Vector((.018*sin(pi*t+index)*sin(pi*t),-.025*sin(pi*t),0)))
        curve('V5 / curved supporting petiole %02d'%index,stem,.0085,petiole)
        objects.append(ob.name)
    soil=bpy.data.materials['Retreat / dark potting humus']
    cylinder('V5 / real potting soil under window plant',(-.62,-4.42,.365),.171,.026,soil,64)
    return dict(old=before,new_leaf_objects=objects,new_blade_vertices=sum(len(bpy.data.objects[name].data.vertices) for name in objects),
                per_blade_material_assignment=True,secondary_veins=128,
                retained='Original four leaf positions, axes and overall dimensions; camera choreography unchanged.')

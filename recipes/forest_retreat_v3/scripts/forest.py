"""Dense, wholly geometric woodland with shared mature broadleaf tree variants."""
from common import *
from materials import pbr, rgb


def woodland_materials(m):
    """Real leaf transmission, bark relief and a subdued forest floor."""
    colors=('#40562B','#526B32','#65783A','#7C8543','#384B27')
    m['forest_leaves']=[]
    for i,color in enumerate(colors):
        mat=pbr('Woodland broadleaf chlorophyll '+str(i),color,.43,noise=.22,bump=.00015,scale=85)
        n,l=mat.node_tree.nodes,mat.node_tree.links
        bs=n.get('Principled BSDF')
        bs.inputs['IOR'].default_value=1.42
        bs.inputs['Coat Weight'].default_value=.12
        bs.inputs['Coat Roughness'].default_value=.35
        transmission=n.new('ShaderNodeBsdfTranslucent')
        transmission.inputs['Color'].default_value=rgb(color)
        mix=n.new('ShaderNodeMixShader')
        mix.inputs[0].default_value=.22
        l.new(bs.outputs[0],mix.inputs[1])
        l.new(transmission.outputs[0],mix.inputs[2])
        l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
        m['forest_leaves'].append(mat)
    m['forest_bark']=pbr('Mature broadleaf bark / longitudinal fissures','#574A36',.94,noise=.48,bump=.017,scale=11)
    n,l=m['forest_bark'].node_tree.nodes,m['forest_bark'].node_tree.links
    noise=next(node for node in n if node.type=='TEX_NOISE')
    coord=n.new('ShaderNodeTexCoord')
    stretch=n.new('ShaderNodeVectorMath')
    stretch.operation='MULTIPLY'
    stretch.inputs[1].default_value=(3.0,3.0,.22)
    l.new(coord.outputs['Object'],stretch.inputs[0])
    l.new(stretch.outputs[0],noise.inputs[0])
    m['forest_floor']=pbr('Moss and fallen leaves / woodland loam','#484735',.97,noise=.65,bump=.035,scale=5)
    m['moss']=pbr('Living forest moss','#4B582D',.96,noise=.40,bump=.007,scale=65)
    m['fallen_leaf']=pbr('Old beech leaf litter','#785533',.88,noise=.40,bump=.001,scale=30)


def branch_mesh(name, segments, mat):
    """Combine tapered branch segments into one efficient mesh."""
    verts,faces=[],[]
    for a,b,r1,r2 in segments:
        a,b=Vector(a),Vector(b)
        rot=(b-a).to_track_quat('Z','Y')
        start=len(verts)
        sides=12 if r1>.05 else 7
        for center,r in ((a,r1),(a.lerp(b,.52),(r1+r2)*.49),(b,r2)):
            for i in range(sides):
                theta=2*pi*i/sides
                radius=r*(1+.045*sin(i*5.7))
                verts.append(tuple(center+rot@Vector((radius*cos(theta),radius*sin(theta),0))))
        faces.append(tuple(start+i for i in reversed(range(sides))))
        for j in range(2):
            for i in range(sides):
                a=start+j*sides+i
                b=start+j*sides+(i+1)%sides
                faces.append((a,b,b+sides,a+sides))
        faces.append(tuple(start+2*sides+i for i in range(sides)))
    return smooth(mesh(name,verts,faces,mat))


def foliage_mesh(name, specs, materials):
    """Individual folded, pointed leaves with several natural green tones."""
    verts,faces,indices=[],[],[]
    for pos,axis,length,width,roll,color in specs:
        p,n=Vector(pos),Vector(axis).normalized()
        u=n.cross(Vector((0,0,1)))
        if u.length<.01:
            u=Vector((1,0,0))
        u.normalize()
        v=n.cross(u).normalized()
        u,v=u*cos(roll)+v*sin(roll),v*cos(roll)-u*sin(roll)
        start=len(verts)
        verts.append(tuple(p))
        for t,w in ((.34,.94),(.72,.80)):
            center=p+n*length*t+v*length*.06*sin(pi*t)
            verts.extend([tuple(center-u*width*w),tuple(center+v*width*.16),tuple(center+u*width*w)])
        verts.append(tuple(p+n*length-v*length*.075))
        local=[(0,1,2),(0,2,3),(1,4,5,2),(2,5,6,3),(4,7,5),(5,7,6)]
        faces.extend(tuple(start+x for x in f) for f in local)
        indices.extend([color]*len(local))
    obj=mesh(name,verts,faces,materials[0])
    for mat in materials[1:]:
        obj.data.materials.append(mat)
    for polygon,index in zip(obj.data.polygons,indices):
        polygon.material_index=index
        polygon.use_smooth=True
    return obj


def tree_variant(index, m):
    """Build one full-size tree in local coordinates for mesh instancing."""
    rng=random.Random(9137+index*211)
    h=rng.uniform(9.3,11.5)
    width=rng.uniform(3.15,4.05)
    joints=[Vector((0,0,0)),Vector((.10,-.06,h*.16)),
            Vector((-.08,.07,h*.34)),Vector((.12,.02,h*.52)),Vector((.05,-.13,h*.73))]
    segments=[]
    for i in range(4):
        segments.append((joints[i],joints[i+1],(.33,.235,.185,.125)[i],(.235,.185,.125,.025)[i]))
    for i in range(7):
        a=i*2*pi/7+.2
        segments.append(((.12*cos(a),.12*sin(a),.45),(.9*cos(a),.9*sin(a),-.01),.13,.026))
    leaves=[]
    for branch in range(22):
        angle=branch*2.399963+rng.uniform(-.2,.2)
        level=(branch+.5)/22
        radius=width*(.64+.36*sin(pi*level))
        crown_z=h*(.51+.37*level)
        root=joints[2].lerp(joints[4],level*.8)
        elbow=Vector((radius*.52*cos(angle-.16),radius*.52*sin(angle-.16),crown_z-.48))
        end=Vector((radius*cos(angle),radius*sin(angle),crown_z))
        segments.extend([(root,elbow,.09*(1-level*.6),.045),(elbow,end,.045,.010)])
        for shoot in range(8):
            t=.27+.73*shoot/7
            start=elbow.lerp(end,t)
            side=angle+(-1 if shoot%2 else 1)*rng.uniform(.55,1.65)
            reach=rng.uniform(.40,.86)
            tip=start+Vector((reach*cos(side),reach*sin(side),rng.uniform(.10,.66)))
            segments.append((start,tip,.014,.0035))
            # Overlapping asymmetric sprays produce a full, porous crown.
            for j in range(185):
                a=rng.uniform(0,2*pi)
                z=rng.uniform(-1,1)
                r=rng.random()**(1/3)
                horizontal=math.sqrt(1-z*z)
                p=tip+Vector((cos(a)*horizontal*.62,sin(a)*horizontal*.62,z*.54))*r
                direction=rng.uniform(0,2*pi)
                axis=(cos(direction),sin(direction),rng.uniform(-.8,.6))
                leaves.append((p,axis,rng.uniform(.105,.185),rng.uniform(.032,.063),
                               rng.uniform(-.9,.9),rng.choices(range(5),weights=(25,32,22,9,12))[0]))
    bark=branch_mesh('Woodland variant %d / complete trunk and branching'%index,segments,m['forest_bark'])
    crown=foliage_mesh('Woodland variant %d / 32560 individual leaves'%index,leaves,m['forest_leaves'])
    return (bark,crown)


def tree_instance(name, prototype, location, scale, angle):
    objects=[]
    for source in prototype:
        obj=bpy.data.objects.new(name+' / '+source.name.split(' / ')[-1],source.data)
        link_object(obj)
        obj.location=location
        obj.scale=scale
        obj.rotation_euler.z=angle
        obj['asset_type']='living broadleaf tree / shared three-dimensional mesh'
        objects.append(obj)
    return objects


def ground_height(x, y):
    distance=math.hypot((x-1)*.9,(y+3)*.85)
    amplitude=min(1.0,max(0,distance-17)/28)
    return -.22+amplitude*(.55*sin(x*.12)+.40*sin(y*.14+x*.06))


def woodland_floor(m, rng):
    collection('32 • Forest floor / moss, ferns and leaf litter')
    count=113
    verts,faces=[],[]
    for j in range(count):
        y=-120+j*240/(count-1)
        for i in range(count):
            x=-120+i*240/(count-1)
            verts.append((x,y,ground_height(x,y)))
    for j in range(count-1):
        for i in range(count-1):
            a=j*count+i
            faces.append((a,a+1,a+1+count,a+count))
    smooth(mesh('Continuous gently undulating woodland earth',verts,faces,m['forest_floor']))
    # Shared fern rosettes: each frond carries paired, tapered pinnate leaves.
    fern_leaves=[]
    stems=[]
    for i in range(9):
        angle=i*2.39996
        length=rng.uniform(.52,.82)
        start=Vector((0,0,0))
        points=[]
        for j in range(14):
            t=j/13
            point=Vector((cos(angle)*length*t,sin(angle)*length*t,.07+.54*sin(t*pi*.71)))
            points.append(point)
            if j:
                stems.append((points[-2],point,.004*(1-t*.7),.0015))
            if 1<j<13:
                for side in (-1,1):
                    a=angle+side*1.12
                    fern_leaves.append((point,(cos(a),sin(a),-.10),.19*sin(pi*t)**.7,.021,0,i%3))
    fern=foliage_mesh('Fern prototype / individually modeled pinnae',fern_leaves,m['forest_leaves'])
    fern_stems=branch_mesh('Fern prototype / curved rachises',stems,m['moss'])
    for i in range(950):
        x,y=rng.uniform(-28,30),rng.uniform(-29,23)
        if -5.9<x<9.5 and -10.9<y<1.5:
            continue
        scale=rng.uniform(.5,1.4)
        tree_instance('Forest fern %04d'%i,(fern,fern_stems),(x,y,ground_height(x,y)),
                      (scale,scale,scale),rng.uniform(0,2*pi))
    bpy.data.objects.remove(fern,do_unlink=True)
    bpy.data.objects.remove(fern_stems,do_unlink=True)
    # Actual low curved grasses around the clearing, with loose fallen leaves.
    verts,faces=[],[]
    litter=[]
    for i in range(12000):
        x,y=rng.uniform(-30,32),rng.uniform(-32,26)
        if -5.9<x<9.5 and -10.9<y<1.5:
            continue
        z=ground_height(x,y)+.01
        a=rng.uniform(0,2*pi)
        litter.append(((x,y,z),(cos(a),sin(a),.015),rng.uniform(.08,.17),.034,.1,0))
        if i%2:
            continue
        for j in range(6):
            angle=rng.uniform(0,2*pi)
            h=rng.uniform(.13,.48)
            dx,dy=cos(angle),sin(angle)
            first=len(verts)
            for k in range(4):
                t=k/3
                px,py=x+dx*.17*t*t,y+dy*.17*t*t
                w=.005*(1-t)
                verts.extend([(px-dy*w,py+dx*w,z+h*t),(px+dy*w,py-dx*w,z+h*t)])
            for k in range(3):
                a=first+k*2
                faces.append((a,a+1,a+3,a+2))
    mesh('Lush clearing grasses / individual arching blades',verts,faces,m['moss'])
    foliage_mesh('Scattered beech leaves on the woodland floor',litter,[m['fallen_leaf']])
    for i in range(70):
        x,y=rng.uniform(-24,26),rng.uniform(-24,19)
        if -6<x<10 and -11<y<2:
            continue
        size=rng.uniform(.18,.6)
        rock=sphere('Mossy rounded forest rock',(x,y,ground_height(x,y)),
                    (size,size*.75,size*.36),m['moss'],16,10)
        rock.rotation_euler.z=rng.uniform(0,2*pi)


def build(m):
    woodland_materials(m)
    rng=random.Random(250925)
    woodland_floor(m,rng)
    collection('33 • Dense mature forest / complete instanced broadleaf trees')
    prototypes=[tree_variant(i,m) for i in range(6)]
    positions=[]
    for j in range(23):
        for i in range(23):
            x=-66+i*6+rng.uniform(-1.7,1.7)
            y=-66+j*6+rng.uniform(-1.7,1.7)
            if math.hypot(x-1,y+3)>78:
                continue
            # The house stands in a natural clearing with a narrow sunlit ride.
            if -8.5<x<12.5 and -19.5<y<4.6:
                continue
            if y<-10 and -10<x-.35*y<16:
                continue
            # Preserve physical room for the final crane move and its foreground.
            a,b=Vector((3.8,-10.9)),Vector((11.6,-21.0))
            p=Vector((x,y))
            t=max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared))
            if (p-a.lerp(b,t)).length<5.5:
                continue
            positions.append((x,y))
    # A lower distant tree line closes the long sunward clearing below the sun rays.
    for row in range(4):
        for column in range(23):
            positions.append((-66+column*6+rng.uniform(-1.5,1.5),-86-row*6+rng.uniform(-1.2,1.2)))
    for i,(x,y) in enumerate(positions):
        scale=rng.uniform(.82,1.38) if y>-80 else rng.uniform(.72,.96)
        tree_instance('Mature forest tree %03d'%i,prototypes[i%6],
                      (x,y,ground_height(x,y)),(scale*rng.uniform(.88,1.1),scale,scale),rng.uniform(0,2*pi))
    # Young, full crowns fill the sunward view while remaining below the low sun.
    # Their natural height progression admits real rays to the house and terrace.
    saplings=0
    for row in range(9):
        y=-27-row*5.8
        for column in range(7):
            x=.35*y-7.8+column*3.6+rng.uniform(-.8,.8)
            sy=y+rng.uniform(-1.3,1.3)
            scale=max(.15,(-.165*sy-2.8)/12.6)*rng.uniform(.85,1.0)
            tree_instance('Sunward young forest %03d'%saplings,prototypes[saplings%6],
                          (x,sy,ground_height(x,sy)),(scale*1.12,scale*1.12,scale),rng.uniform(0,2*pi))
            saplings+=1
    # Deliberately placed near trees frame the house while allowing low sunlight below the crown.
    for i,(x,y,scale) in enumerate([(-6.8,-3.4,.83),(-8.8,-10.1,1.0),
                                   (10.3,-4.2,.88),(11.8,1.6,1.0),
                                   (-4.15,-7.7,.95),(13.5,-10.2,.90),
                                   (-5.0,2.1,.83),(6.8,4.1,.97)]):
        tree_instance('Clearing edge tree %02d'%i,prototypes[(i+2)%6],
                      (x,y,ground_height(x,y)),(scale,scale,scale),rng.uniform(0,2*pi))
    # A second, lower foliage layer closes the gaps between trunks.
    for i in range(190):
        x,y=rng.uniform(-36,37),rng.uniform(-34,31)
        if -6.4<x<10 and -11.3<y<2.3:
            continue
        if y<-10 and abs(x-.35*y)<3:
            continue
        scale=rng.uniform(.12,.24)
        tree_instance('Woodland understory shrub %03d'%i,prototypes[i%6],
                      (x,y,ground_height(x,y)-scale*2.8),
                      (scale*1.35,scale*1.35,scale),rng.uniform(0,2*pi))
    for variant in prototypes:
        for obj in variant:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.scene['forest_tree_count']=len(positions)+8
    bpy.context.scene['forest_sapling_count']=saplings
    bpy.context.scene['forest_asset']='6 shared tree variants; 32560 folded geometric leaves per mature crown; layered shrubs, fern rosettes, grasses and litter'
    print('FOREST_COMPLETE',len(positions)+8,'mature trees; 190 understory planting attempts',flush=True)

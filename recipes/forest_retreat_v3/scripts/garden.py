"""Living indoor shadow casters and a stone courtyard in dense woodland."""
from common import *


def leaves_mesh(name, specs, m, segments=5):
    verts,faces=[],[]
    for pos,axis,length,width in specs:
        n=Vector(axis).normalized()
        u=n.cross(Vector((0,0,1)))
        if u.length<.01:
            u=Vector((1,0,0))
        u.normalize()
        p=Vector(pos)
        start=len(verts)
        for j in range(segments):
            t=j/(segments-1)
            w=width*sin(t*pi)**.75
            center=p+n*(length*t)+Vector((0,0,.12*length*sin(t*pi)))
            verts.extend([tuple(center-u*w),tuple(center+Vector((0,0,.035*length))),tuple(center+u*w)])
        for j in range(segments-1):
            for k in range(2):
                a=start+j*3+k
                faces.append((a,a+1,a+4,a+3))
    obj=smooth(mesh(name,verts,faces,m['leaf']))
    obj.data.materials.append(m['leaflight'])
    for p in obj.data.polygons:
        if (p.index//8)%4==0:
            p.material_index=1
    return obj


def herb(name,loc,m,scale=1):
    x,y,z=loc
    r=.085*scale
    lathe(name+' hollow earthen pot',[(0,0),(r*.8,0),(r,.18*scale),(r*.99,.19*scale),
          (r*.84,.19*scale),(r*.68,.016),(0,.016)],loc,m['terra'])
    cylinder(name+' potting earth',(x,y,z+.167*scale),r*.83,.013,m['earth'])
    rng=random.Random(33+int(x*20))
    specs=[]
    for i in range(15):
        angle=rng.uniform(0,2*pi)
        height=rng.uniform(.17,.42)*scale
        spread=rng.uniform(.018,.14)*scale
        a=Vector((x,y,z+.17*scale))
        b=a+Vector((spread*cos(angle),spread*sin(angle),height))
        beam(name+' fine woody stem',a,b,.0025*scale,m['bark'],.0007*scale)
        for j in range(4,12):
            t=j/12
            p=a.lerp(b,t)
            for side in (-1,1):
                axis=Vector((cos(angle+side*1.2),sin(angle+side*1.2),.38))
                specs.append((p,axis,.051*scale,.014*scale))
    leaves_mesh(name+' individual living leaves',specs,m)


def olive(name,loc,height,m,seed):
    rng=random.Random(seed)
    origin=Vector(loc)
    trunk=origin+Vector((.10,-.07,height*.51))
    beam(name+' mature trunk',origin,trunk,height*.035,m['bark'],height*.019)
    # Multiple swept limb segments avoid lollipop silhouettes.
    tips=[]
    for i in range(8):
        a=i*2*pi/8+rng.uniform(-.25,.25)
        joint=origin+Vector((cos(a)*height*.17,sin(a)*height*.17,height*rng.uniform(.55,.72)))
        end=origin+Vector((cos(a)*height*.37,sin(a)*height*.34,height*rng.uniform(.70,.94)))
        beam(name+' primary gnarled limb',trunk,joint,height*.013,m['bark'],height*.007)
        beam(name+' outer limb',joint,end,height*.007,m['bark'],height*.002)
        for j in range(9):
            t=rng.uniform(.3,1)
            root=joint.lerp(end,t)
            tip=root+Vector((rng.uniform(-.25,.25),rng.uniform(-.25,.25),rng.uniform(.02,.34)))*height*.6
            beam(name+' fine twig',root,tip,height*.0017,m['bark'],height*.0005)
            tips.append((root,tip))
    specs=[]
    for a,b in tips:
        for j in range(55):
            t=rng.random()
            pos=a.lerp(b,t)+Vector((rng.uniform(-.14,.14),rng.uniform(-.14,.14),rng.uniform(-.08,.15)))
            th=rng.uniform(0,2*pi)
            axis=(cos(th),sin(th),rng.uniform(-.7,.6))
            specs.append((pos,axis,rng.uniform(.045,.086),rng.uniform(.009,.015)))
    leaves_mesh(name+' silver green leaf canopy',specs,m)


def landscape(m):
    collection('32 • Rural setting / terrain and distant tree lines')
    cube('Continuous warm earth terrain',(0,0,-.33),(180,180,.20),m['earth'],.05)
    verts,faces=[],[]
    count=75
    for j in range(count):
        y=-90+j*180/(count-1)
        for i in range(count):
            x=-90+i*180/(count-1)
            dist=math.hypot(x-1,y+2)
            height=max(0,dist-16)*.025*(1.5+.8*sin(x*.075)+sin(y*.13+x*.045))
            verts.append((x,y,-.25+height))
    for j in range(count-1):
        for i in range(count-1):
            a=j*count+i
            faces.append((a,a+1,a+1+count,a+count))
    smooth(mesh('Rolling late summer meadow',verts,faces,m['grass']))
    rng=random.Random(736)
    # Long low topographic silhouettes, fully modeled and viewable from above.
    for ridge in range(3):
        verts,faces=[],[]
        for j in range(6):
            y=21+ridge*19+j*5
            for i in range(65):
                x=-110+i*220/64
                h=(3+ridge*2.2)*(sin(i*.073+ridge)**2+.5*sin(i*.21)**2)
                verts.append((x,y,-.28+h*sin(j*pi/5)))
        for j in range(5):
            for i in range(64):
                a=j*65+i
                faces.append((a,a+1,a+66,a+65))
        smooth(mesh('Distant rolling ridge '+str(ridge),verts,faces,m['grass']))
    for i in range(20):
        theta=rng.uniform(0,2*pi)
        radius=rng.uniform(19,40)
        olive('Distant orchard tree %02d'%i,(radius*cos(theta),radius*sin(theta),-.20),rng.uniform(2.1,3.3),m,100+i)
    # Clumps of dry grass; each individual blade is a curved tapered mesh.
    verts,faces=[],[]
    for i in range(2400):
        x,y=rng.uniform(-15,17),rng.uniform(-18,12)
        if -5.8<x<9.6 and -11<y<1.4:
            continue
        z=-.18
        for j in range(5):
            a=rng.uniform(0,2*pi)
            h=rng.uniform(.08,.31)
            dx,dy=cos(a),sin(a)
            start=len(verts)
            for k in range(4):
                t=k/3
                px=x+dx*.09*t*t
                py=y+dy*.09*t*t
                w=.007*(1-t)
                verts.extend([(px-dy*w,py+dx*w,z+h*t),(px+dy*w,py-dx*w,z+h*t)])
            for k in range(3):
                v=start+k*2
                faces.append((v,v+1,v+3,v+2))
    mesh('Thousands of individual meadow grass blades',verts,faces,m['grass'])


def build(m):
    collection('30 • Living plants and reference shadow casters')
    herb('Reference console herb',(-1.48,-2.54,1.038),m,1.0)
    herb('Window sill aromatic',(-2.79,-5.21,.716),m,.74)
    herb('Kitchen basil',(2.88,-.17,1.61),m,.45)
    lathe('Large indoor olive planter',[(0,0),(.22,0),(.31,.54),(.29,.58),(.26,.58),(.20,.04),(0,.04)],(-3.0,-4.68,.04),m['ceramic'])
    olive('Indoor young olive',(-3.0,-4.68,.50),1.65,m,4)
    # Broad real leaves provide the soft organic shadow at the right of the hero.
    lathe('Window fig ceramic planter',[(0,0),(.17,0),(.21,.32),(.20,.35),(.18,.35),(.14,.03),(0,.03)],(-1.14,-4.42,.04),m['ceramic'])
    fig_specs=[]
    for pos,axis,length,width in [((-1.16,-4.40,1.12),(.05,.4,1),.91,.42),
                                  ((-.85,-4.30,.94),(.2,.4,1),.68,.30),
                                  ((-1.20,-4.43,.75),(-.1,-.3,1),.68,.26),
                                  ((-.92,-4.35,1.31),(.3,.4,.8),.59,.27)]:
        beam('Window fig woody stem',(-1.14,-4.42,.34),pos,.008,m['bark'],.003)
        fig_specs.append((pos,axis,length,width))
    fig=leaves_mesh('Window fig broad veined leaves',fig_specs,m,segments=21)
    modifier=fig.modifiers.new('Living leaf thickness','SOLIDIFY')
    modifier.thickness=.0012
    for obj in bpy.data.collections['30 • Living plants and reference shadow casters'].objects:
        if obj.name.startswith('Window fig'):
            obj.location.x+=.52
    collection('31 • Courtyard / stone terrace within the forest')
    cube('Terrace gravel bedding',(1.15,-7.76,-.09),(13.0,5.3,.12),m['earth'],.02)
    for i in range(17):
        for j in range(7):
            cube('Courtyard limestone paver',(-4.86+i*.76,-5.64-j*.69,-.015),(.747,.677,.085),m['stone'],.009)
    for i in range(6):
        cube('Stepping stone approach',(6.3+i*.12,-10.64-i*.80,-.10),(.80,.56,.14),m['stone'],.026)
    # Courtyard boundary: a low textured limestone retaining wall.
    for x in (-5.65,8.0):
        cube('Low courtyard garden wall',(x,-5.4,.24),(.23,10.8,.56),m['exterior'],.025)
        cube('Garden wall stone cap',(x,-5.4,.55),(.29,10.9,.08),m['stone'],.016)
    olive('Reference courtyard understory olive',(-3.35,-7.3,0),3.8,m,12)
    for loc in [(-4.15,-7.7,0),(-3.35,-7.3,0)]:
        for j in range(10):
            a=j*2*pi/10
            sphere('Natural limestone edging',(loc[0]+.59*cos(a),loc[1]+.59*sin(a),.01),(.13,.10,.06),m['stone'],16,8)
    cylinder('Outdoor oak bistro tabletop',(2.1,-7.55,.765),.54,.043,m['oak'],96)
    for a in (0,2*pi/3,4*pi/3):
        beam('Bistro table leg',(2.1+.39*cos(a),-7.55+.39*sin(a),.025),(2.1+.24*cos(a),-7.55+.24*sin(a),.75),.026,m['oak'])
    for x,y,angle in [(1.19,-7.53,-pi/2),(3.01,-7.50,pi/2)]:
        chair=cube('Outdoor woven chair seat',(x,y,.43),(.45,.46,.04),m['linen'],.035)
        for dx in (-.18,.18):
            for dy in (-.18,.18):
                beam('Outdoor chair leg',(x+dx,y+dy,.02),(x+dx,y+dy,.44),.017,m['oak'])
        backx=x-.22 if x<2 else x+.22
        for j in range(7):
            beam('Chair bent back slat',(backx,y-.19+j*.063,.44),(backx,y-.19+j*.063,.84),.010,m['oak'])
        curve('Chair top curved rail',[(backx,y-.23+.46*j/24,.81+.06*sin(j*pi/24)) for j in range(25)],.016,m['oak'])
    from furniture import cup,book
    cup('Courtyard tea',2.24,-7.61,.79,m)
    book('Open afternoon notebook',(1.94,-7.49,.809),(.25,.19,.02),m,'paper',-.25)
    herb('Porch terracotta rosemary',(4.57,-6.03,.02),m,2.0)
    # Dense low aromatic beds soften the terrace edge and give foreground parallax.
    for i in range(16):
        x=-5.08 if i<8 else 7.44
        y=-9.85+(i%8)*.60
        rng=random.Random(800+i)
        specs=[]
        for j in range(160):
            a=rng.uniform(0,2*pi)
            r=rng.uniform(0,.29)
            p=(x+r*cos(a),y+r*sin(a),rng.uniform(.10,.47)*(1-r*.9))
            specs.append((p,(cos(a),sin(a),rng.uniform(-.2,.8)),.09,.016))
        leaves_mesh('Low aromatic garden planting '+str(i),specs,m)
    lathe('Reflecting stone birdbath',[(0,0),(.18,0),(.16,.34),(.38,.40),(.43,.46),(.42,.49),(.37,.47),(.05,.41)],(-3.37,-8.91,.0),m['stone'])
    cylinder('Still water in garden bowl',(-3.37,-8.91,.451),.37,.004,m['glass'])
    import forest
    forest.build(m)

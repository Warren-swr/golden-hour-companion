"""Sewn five-petal cushion with explicitly modeled curled wool pile."""
from common import *
import numpy as np

CZ = .857
CY = -.197


def surface(theta, phi):
    radii=[.18]
    for i in range(5):
        a=theta-(1.37+i*2*pi/5)
        d,rx,rz=.222,.194,.151
        aa=cos(a)**2/rx**2+sin(a)**2/rz**2
        bb=-2*d*cos(a)/rx**2
        cc=d*d/rx**2-1
        disc=bb*bb-4*aa*cc
        if disc>0:
            radii.append(max(0,(-bb+math.sqrt(disc))/(2*aa)))
    r=max(radii)+.006*sin(3*theta+.7)
    s = sin(phi)
    x = 1.025*r*s*cos(theta)-.028
    z = CZ+r*s*sin(theta)
    z = max(.473, z)
    lobes = .5+.5*cos(5*(theta-1.37))
    thickness = .140 + .045*lobes*s*s
    y = CY+.18*(z-CZ)-thickness*cos(phi)
    y += .0025*sin(x*61+z*24)*sin(z*49)*s
    return Vector((x,y,z))


def normal_at(theta, phi):
    dt=surface(theta+.001,phi)-surface(theta-.001,phi)
    dp=surface(theta,phi+.001)-surface(theta,phi-.001)
    n=dt.cross(dp).normalized()
    if n.dot(surface(theta,phi)-Vector((-.028,CY,CZ)))<0:
        n=-n
    return n


def curly_pile(name, count, mats, sampler, seed):
    """Aggregate real, open curled fibre tubes rather than shaded displacement."""
    rng=random.Random(seed)
    points,faces,indices=[],[],[]
    steps,sides=9,3
    for strand in range(count):
        p,n,scale=sampler(rng)
        up=Vector((0,0,1)) if abs(n.z)<.92 else Vector((1,0,0))
        u=n.cross(up).normalized()
        v=n.cross(u).normalized()
        turn=rng.uniform(0,2*pi)
        u,v=u*cos(turn)+v*sin(turn),-u*sin(turn)+v*cos(turn)
        rad=rng.uniform(.0021,.0041)*scale
        high=rng.uniform(.0026,.0061)*scale
        wire=rng.uniform(.00105,.00160)*scale
        start=len(points)
        for j in range(steps):
            t=j/(steps-1)*pi*2.25
            q=p+u*(rad*cos(t))+v*(rad*.68*sin(t))+n*(.0004+high*sin(t/2.25)**2)
            for k in range(sides):
                a=2*pi*k/sides
                points.append(tuple(q+wire*(u*cos(a)+n*sin(a))))
        idx=rng.randrange(len(mats))
        for j in range(steps-1):
            for k in range(sides):
                a=start+j*sides+k
                b=start+j*sides+(k+1)%sides
                faces.append((a,b,b+sides,a+sides))
                indices.append(idx)
    obj=mesh(name,points,faces,None)
    for mat in mats:
        obj.data.materials.append(mat)
    obj.data.polygons.foreach_set('material_index',indices)
    smooth(obj)
    return obj


def main_pile(rng):
    theta=rng.uniform(0,2*pi)
    # Independent front/back surfaces continue around all five silhouettes.
    phi=math.acos(rng.uniform(-1,1))
    p=surface(theta,phi)
    return p,normal_at(theta,phi),1.0


def fine_fuzz(m):
    rng=random.Random(481)
    verts,faces=[],[]
    for i in range(42000):
        p,n,_=main_pile(rng)
        u=n.cross(Vector((0,0,1)))
        if u.length<.01:
            u=Vector((1,0,0))
        u.normalize()
        v=n.cross(u)
        a=rng.random()*2*pi
        bend=(u*cos(a)+v*sin(a))*rng.uniform(.0004,.0021)
        length=rng.uniform(.003,.0065)
        width=rng.uniform(.00010,.00019)
        start=len(verts)
        for j in range(3):
            t=j/2
            pos=p+n*(.001+length*t)+bend*t*t
            for k in range(3):
                angle=k*2*pi/3
                verts.append(tuple(pos+(u*cos(angle)+v*sin(angle))*width*(1-.8*t)))
        for j in range(2):
            for k in range(3):
                a=start+j*3+k
                b=start+j*3+(k+1)%3
                faces.append((a,b,b+3,a+3))
    smooth(mesh('42,000 fine wool flyaway fibres',verts,faces,m['pile3']))


def center_pile(rng):
    th=rng.uniform(0,2*pi)
    ph=math.acos(rng.uniform(.03,1))
    x=.124*sin(ph)*cos(th)
    z=.135*sin(ph)*sin(th)
    p=Vector((-.048+x,-.355-.013*cos(ph),CZ-.015+z))
    n=Vector((x/.124**2,-cos(ph)/.014,z/.135**2)).normalized()
    return p,n,.36


def build(m):
    collection('01 • HERO / sewn boucle flower')
    verts,faces=[],[]
    nt,np_=240,88
    for j in range(np_+1):
        phi=.00001+(pi-.00002)*j/np_
        for i in range(nt):
            verts.append(tuple(surface(i*2*pi/nt,phi)))
    for j in range(np_):
        for i in range(nt):
            a=j*nt+i
            b=j*nt+(i+1)%nt
            faces.append((a,a+nt,b+nt,b))
    smooth(mesh('Five-lobed stuffed cushion / continuous front and back shell',verts,faces,m['boucle']))
    curve('Hand sewn perimeter piping', [surface(i*2*pi/640,pi/2) for i in range(640)], .0018,m['boucle'],True)
    sphere('Saffron inset velvet flower heart',(-.048,-.355,CZ-.015),(.124,.014,.135),m['ochre'],96,48)
    curve('Recessed heart seam',[(-.048+.126*cos(i*2*pi/180),-.355,CZ-.015+.137*sin(i*2*pi/180)) for i in range(180)],.00075,m['ochre'],True)
    curly_pile('170,000 individual curled cinnamon wool loops',170000,[m['pile'+str(i)] for i in range(5)],main_pile,773)
    curly_pile('18,000 short saffron velvet loops',18000,[m['ochre']],center_pile,814)
    fine_fuzz(m)
    for obj in bpy.data.collections['01 • HERO / sewn boucle flower'].objects:
        obj.scale *= .86
        obj.location.x = obj.location.x*.86-.043
        obj.location.y = obj.location.y*.86-.0276
        obj.location.z = obj.location.z*.86+CZ*.14+.05
    collection('02 • Upholstered reading bench')
    cube('Solid oak bench plinth',(0,-.44,.270),(2.48,.94,.24),m['oak'],.045)
    pad=cube('Compressed oatmeal bench cushion',(0,-.49,.496),(2.51,1.00,.205),m['linen'],.085)
    # A distinct upholstery lip catches low sunlight; underside has a shadow gap.
    points=[]
    for i in range(161):
        a=2*pi*i/160
        x=1.215*math.copysign(abs(cos(a))**.2,cos(a))
        y=-.49+.467*math.copysign(abs(sin(a))**.2,sin(a))
        points.append((x,y,.55))
    curve('Continuous linen seat welt',points,.0032,m['linen'],True)
    for x in (-1.00,1.00):
        for y in (-.78,-.18):
            cylinder('Bench turned oak foot',(x,y,.095),.042,.18,m['walnut'])
    # Two correctly dimensioned three-dimensional wall switch assemblies.
    collection('03 • Reference wall fittings')
    for name,x,z,w,h in [('Left switch',-.912,2.044,.096,.185),('Right switch',.584,1.888,.135,.224)]:
        cube(name+' recessed gasket',(x,-.006,z),(w+.005,.008,h+.005),m['frame'],.004)
        cube(name+' ivory cover plate',(x,-.014,z),(w,.016,h),m['switch'],.005)
        cube(name+' rocker recess',(x,-.024,z),(w*.56,.006,h*.67),m['bronze'],.003)
        rock=cube(name+' tactile rocker',(x,-.03,z),(w*.50,.01,h*.62),m['switch'],.005)
        rock.rotation_euler.x=.055
        for dz in (-h*.415,h*.415):
            screw=cylinder(name+' slotted screw',(x,-.024,z+dz),.004,.003,m['switch'],20)
            screw.rotation_euler.x=pi/2
            cube(name+' screw slot',(x,-.026,z+dz),(.0038,.001,.0006),m['frame'],0)

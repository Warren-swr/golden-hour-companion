"""v4 construction, textile and landscape refinements, in real metres."""
from retreat_helpers import *
from materials import pbr, cloth, rgb
from forest import foliage_mesh, branch_mesh, ground_height
import numpy as np


def existing(name):
    return bpy.data.materials[name]


def materials():
    m = dict(oak=existing('Natural quarter-sawn European oak'),
             bronze=existing('Retreat / aged patinated bronze'),
             dark=existing('Blackened metal'), linen=existing('Retreat / washed ivory linen'),
             stone=existing('Retreat / ivory travertine with pores'),
             ceramic=existing('Porcelain enamel'), bark=existing('Retreat / bark fissures and lichens'),
             paper=existing('Uncoated warm paper'), glass=existing('Clear architectural glass'))
    m['seam'] = cloth('V4 / natural flax binding', '#A89B80')
    m['rug'] = cloth('V4 / undyed handwoven wool', '#B8B1A0')
    m['soap'] = pbr('V4 / olive soap', '#A8AC7E', .61, noise=.13, bump=.0003, scale=220)
    m['enamel'] = pbr('V4 / warm satin mineral composite', '#D9D6CA', .29, noise=.018, bump=.00008, scale=120)
    m['seal'] = pbr('V4 / recessed graphite EPDM seal', '#353530', .76)
    m['moss'] = pbr('V4 / fine damp moss', '#465435', .94, noise=.45, bump=.002, scale=170)
    m['linen_stripe'] = cloth('V4 / tobacco rug border', '#776D58')
    # Sample one scanned plank per modeled board. Box projection repeated photographed
    # board joints across each real plank, producing a false brick-like grid.
    for name in ('Retreat / weathered cedar grain', 'Retreat / silvered teak decking'):
        mat = existing(name)
        n, l = mat.node_tree.nodes, mat.node_tree.links
        info = n.new('ShaderNodeObjectInfo')
        coord=n.new('ShaderNodeTexCoord')
        sep=n.new('ShaderNodeSeparateXYZ')
        l.new(coord.outputs['Generated'],sep.inputs[0])
        row=n.new('ShaderNodeMath'); row.operation='MULTIPLY'
        row.inputs[1].default_value=7.99
        l.new(info.outputs['Random'],row.inputs[0])
        floor=n.new('ShaderNodeMath'); floor.operation='FLOOR'
        l.new(row.outputs[0],floor.inputs[0])
        offset=n.new('ShaderNodeMath'); offset.operation='MULTIPLY_ADD'
        offset.inputs[1].default_value=.125; offset.inputs[2].default_value=.017
        l.new(floor.outputs[0],offset.inputs[0])
        u=n.new('ShaderNodeMath'); u.operation='MULTIPLY_ADD'
        u.inputs[1].default_value=.92;u.inputs[2].default_value=.04
        l.new(sep.outputs['Z' if 'cedar' in name else 'X'],u.inputs[0])
        across=n.new('ShaderNodeMath'); across.operation='ADD'
        l.new(sep.outputs['Y'],across.inputs[0])
        if 'cedar' in name:l.new(sep.outputs['X'],across.inputs[1])
        v=n.new('ShaderNodeMath');v.operation='MULTIPLY_ADD'
        v.inputs[1].default_value=.042 if 'cedar' in name else .084
        l.new(across.outputs[0],v.inputs[0]);l.new(offset.outputs[0],v.inputs[2])
        uv=n.new('ShaderNodeCombineXYZ')
        l.new(u.outputs[0],uv.inputs['X']);l.new(v.outputs[0],uv.inputs['Y'])
        texs = [x for x in n if x.type == 'TEX_IMAGE']
        for tex in texs:
            tex.projection='FLAT'
            l.new(uv.outputs[0], tex.inputs['Vector'])
    # Millimetre relief was excessive for indoor honed stone.
    for name in ('Honed cream limestone', 'Honed cream limestone.001'):
        mat = bpy.data.materials.get(name)
        if mat:
            for node in mat.node_tree.nodes:
                if node.type == 'BUMP':
                    node.inputs['Distance'].default_value = .0006
    return m


def rounded_pad(name, center, size, mat, seam_mat, depression=.02, rotation=0):
    """Closed upholstered box: rounded perimeter, crowned panels and piped seams."""
    L, W, H = size
    center = Vector(center)
    vertices, faces = [], []
    rings, segments = 25, 112
    def point(t, a):
        c, s = cos(a), sin(a)
        x = L / 2 * math.copysign(abs(c) ** .23, c)
        y = W / 2 * math.copysign(abs(s) ** .23, s)
        # Rounded side wall and a gently compressed, non-planar top.
        z = H / 2 * cos(pi * t)
        radius = .02 + .98 * sin(pi * t) ** .22
        x, y = x * radius, y * radius
        z += .004 * sin(13 * a + t * 8) * sin(pi * t) ** 4
        if t < .5:
            z -= depression * math.exp(-((x / (L * .28)) ** 2 + ((y + W * .1) / (W * .31)) ** 2))
        return center + Vector((x * cos(rotation) - y * sin(rotation),
                                x * sin(rotation) + y * cos(rotation), z))
    for j in range(rings):
        for i in range(segments):
            vertices.append(tuple(point(j / (rings - 1), 2 * pi * i / segments)))
    for j in range(rings - 1):
        for i in range(segments):
            a, b = j * segments + i, j * segments + (i + 1) % segments
            faces.append((a, a + segments, b + segments, b))
    faces.extend((tuple(reversed(range(segments))), tuple(range((rings - 1) * segments, rings * segments))))
    obj = smooth(mesh(name, vertices, faces, mat))
    for t in (.28, .72):
        curve(name + ' sewn welt', [point(t, i * 2 * pi / segments) for i in range(segments)], .0020, seam_mat, True)
    return obj


def textiles(m):
    collection('60 • V4 / tailored textiles and lived-in surfaces')
    remove_prefix('Linen sofa seat')
    for i, y in enumerate((-2.325, -1.365)):
        rounded_pad('V4 / separate sofa seat %d' % i, (-2.69, y, .432), (.88, .947, .236),
                    existing('Washed natural linen'), m['seam'], .022 + i * .006)
    # Preserve the reference bench geometry and change the supporting room furnishings.
    for ob in list(bpy.data.objects):
        if ob.name.startswith(('Poolside / adjustable teak chaise linen cushion', 'Garden / fireside low chair linen cushion')):
            name, loc, size, rot, mat = ob.name, ob.location.copy(), tuple(ob.dimensions), ob.rotation_euler.z, ob.data.materials[0]
            bpy.data.objects.remove(ob, do_unlink=True)
            rounded_pad('V4 / ' + name, loc, size, mat, m['seam'], .008, rot)
    # Real spiral hems and open central rolls replace featureless capped cylinders.
    for ob in list(bpy.data.objects):
        if not ob.name.startswith('Poolside / rolled linen towel'):
            continue
        transform=ob.matrix_world.copy()
        bpy.data.objects.remove(ob,do_unlink=True)
        roll=lathe('V4 / rolled terry towel hollow cloth',[(.009,-.22),(.078,-.22),(.080,-.217),
                   (.080,.217),(.078,.22),(.009,.22),(.009,-.22)],(0,0,0),m['linen'],80)
        roll.matrix_world=transform
        for end in (-.221,.221):
            points=[]
            for j in range(481):
                t=j/480;r=.011+.066*t;a=2*pi*5.3*t
                points.append(transform@Vector((r*cos(a),r*sin(a),end)))
            curve('V4 / towel spiral woven hem',points,.00135,m['seam'])
    # A real woven relief surface with bound edges; no flat monochrome rug slab.
    for name in ('Woven undyed wool rug', 'Bedroom woven rug'):
        ob = bpy.data.objects.get(name)
        if not ob:
            continue
        cx, cy, _ = ob.location
        L, W, _ = ob.dimensions
        ob.data.materials.clear()
        ob.data.materials.append(m['rug'])
        for side in (-1, 1):
            y = cy + side * (W / 2 - .075)
            cube('V4 / woven rug border', (cx, y, .058), (L - .04, .043, .0015), m['linen_stripe'], .0007)
        strands = bpy.data.curves.new('V4 / warp and weft pile geometry', 'CURVE')
        strands.dimensions, strands.bevel_depth, strands.bevel_resolution = '3D', .00075, 1
        for j in range(int(W / .009)):
            y = cy - W / 2 + .018 + j * .009
            spl = strands.splines.new('POLY')
            count = 33
            spl.points.add(count - 1)
            spl.points.foreach_set('co', [c for i in range(count) for c in
                (cx - L / 2 + .016 + (L - .032) * i / (count - 1), y,
                 .059 + .0008 * sin(i * 1.7 + j * .8), 1)])
        threads = bpy.data.objects.new('V4 / tactile handwoven rug yarns', strands)
        link_object(threads)
        material(threads, m['rug'])
    # Supple irregular folds, concentrated where the blanket turns over the mattress.
    for ob in bpy.data.objects:
        if ob.name.startswith(('Bedroom / relaxed linen duvet', 'Bedroom / sage throw across')):
            for v in ob.data.vertices:
                x, y, z = v.co
                edge = min(1, max(0, (abs(x - 5.02) - .45) / .55))
                v.co.z += (.005 + .012 * edge) * sin(x * 22 + y * 7 + .7 * sin(y * 13))
                v.co.z += .008 * sin(x * 7 - y * 11) * sin(y * 5 + x)
        if ob.name.startswith('Bedroom / full length pleated linen drapery'):
            ob.shape_key_add(name='Basis')
            key = ob.shape_key_add(name='Open-window breathing')
            for v in key.data:
                weight = max(0, min(1, (2.8 - v.co.z) / 2.8))
                v.co.x += .014 * weight ** 1.5 * sin(v.co.y * 4 + v.co.z)
            key.driver_add('value').driver.expression = '.5+.5*sin(frame*.025)'


def bathroom(m):
    collection('61 • V4 / coherent limestone bathroom')
    remove_prefix('Stone vanity unit', 'Vanity limestone slab', 'Handmade wash basin', 'Bath brass faucet',
                  'Folded bath towel', 'Compact porcelain toilet', 'Toilet seat rim', 'Concealed toilet cistern')
    # Vanity is now directly below its mirror, with a usable walkway to the tub.
    cube('V4 / floating oak vanity carcass', (4.06, -3.80, .60), (.97, .49, .44), m['oak'], .011)
    for x in (3.815, 4.305):
        cube('V4 / inset vanity drawer', (x, -4.052, .60), (.469, .022, .404), m['oak'], .004)
        cube('V4 / recessed drawer pull', (x, -4.068, .773), (.28, .016, .012), m['bronze'], .003)
    cube('V4 / honed vanity stone top', (4.06, -3.82, .848), (1.04, .55, .043), m['stone'], .009)
    lathe('V4 / hollow wash basin', [(0, 0), (.13, 0), (.205, .10), (.209, .137), (.198, .143),
          (.181, .103), (.10, .018), (0, .018)], (4.06, -3.88, .872), m['enamel'], 96)
    curve('V4 / curved vanity faucet', [(4.06, -3.64, .87), (4.06, -3.64, 1.15),
          (4.06, -3.67, 1.19), (4.06, -3.79, 1.19), (4.06, -3.82, 1.16)], .012, m['bronze'])
    cylinder('V4 / basin pop-up waste', (4.06, -3.88, .894), .021, .003, m['bronze'], 32)
    for x in (3.73, 4.39):
        cylinder('V4 / faucet cross tap', (x, -3.67, .893), .022, .041, m['bronze'], 32)
    # Large format stone with actual joints and slim corner sealant beads.
    for i in range(9):
        for j in range(3):
            cube('V4 / bathroom honed wall panel', (3.58 + i * .39, -3.52, .27 + j * .39),
                 (.385, .028, .385), m['stone'], .0018)
    for z in (.075, 1.267):
        cube('V4 / bathroom stone edge trim', (5.25, -3.539, z), (3.72, .022, .015), m['bronze'], .002)
    # A compact closed-seat wall-hung toilet with a shaped base and proper flush plate.
    lathe('V4 / wall hung porcelain bowl', [(0, 0), (.13, 0), (.18, .10), (.192, .24), (.185, .27), (0, .27)],
          (5.05, -3.87, .16), m['enamel'], 80).scale.y = 1.43
    lid = sphere('V4 / closed soft toilet lid', (5.05, -3.93, .447), (.204, .302, .029), m['enamel'], 64, 24)
    cube('V4 / concealed flush plate', (5.05, -3.552, 1.04), (.235, .014, .14), m['bronze'], .012)
    for x, r in ((5.012, .031), (5.097, .022)):
        disk = cylinder('V4 / dual flush button', (x, -3.562, 1.04), r, .006, m['dark'], 32)
        disk.rotation_euler.x = pi / 2
    # A bridge physically supports the draped towel, bath book and soap tray.
    cube('V4 / solid oak bath bridge', (6.17, -4.34, .665), (.28, .92, .026), m['oak'], .009)
    cloth_surface('V4 / bath linen over bridge', 6.03, 6.28, -4.94, -3.84,
                  lambda x, y: .684 - .24 * min(1, max(0, abs(y + 4.34) - .42) / .18)
                  + .005 * sin(x * 55 + y * 9), m['linen'], 35, 61, .003)
    lathe('V4 / soap dish', [(0,0),(.061,0),(.070,.014),(.065,.022),(.047,.009),(0,.009)],
          (6.15,-4.08,.686), m['stone'], 40)
    cube('V4 / handmade olive soap', (6.15, -4.08, .720), (.084, .046, .024), m['soap'], .009)
    cylinder('V4 / bathtub waste', (6.06, -4.34, .201), .024, .003, m['bronze'], 32)
    for x in (3.49, 4.56):
        cube('V4 / sconce bronze backplate', (x, -3.55, 1.82), (.055, .026, .21), m['bronze'], .006)
        shade = cylinder('V4 / opal bathroom sconce', (x, -3.61, 1.82), .033, .25, existing('Opal lamp diffuser'), 48)
        light('V4 / bathroom sconce practical', (x, -3.65, 1.83), 9, (1, .84, .64), .035)
    # Linen bath mat, pulled clear of the door swing and the sanitary fixtures.
    cloth_surface('V4 / bathroom textured floor runner', 4.55, 5.71, -4.98, -4.50,
                  lambda x, y: .060 + .0015 * sin(x * 52) * sin(y * 28), m['rug'], 57, 25, .009)


def joinery(m):
    collection('62 • V4 / architectural closures and fittings')
    # Inherited garden walls floated above the woodland soil and obstructed the side garden.
    # Rebuild as low, ground-bearing stone edging with a gate-sized gap to the fire garden.
    walls=[o for o in bpy.data.objects if o.name.startswith('Low courtyard garden wall')]
    wall_x=[o.location.x for o in walls]
    remove_prefix('Low courtyard garden wall','Garden wall stone cap')
    for x in wall_x:
        for ya,yb in ((-9.82,-7.98),(-6.80,-.02)):
            cube('V4 / grounded side garden retaining edge',(x,(ya+yb)/2,-.095),(.24,yb-ya,.31),m['stone'],.012)
            for j in range(max(1,round((yb-ya)/.58))):
                length=(yb-ya)/max(1,round((yb-ya)/.58))
                cube('V4 / individual low wall coping',(x,ya+(j+.5)*length,.075),(.29,length-.006,.038),m['stone'],.006)
    # Replace the solid rain gutters with genuine open channels and end caps.
    remove_prefix('Cabin / half-round bronze gutter')
    for yy in (-5.88, .73):
        verts, faces = [], []
        profile = [(.073 * cos(pi * i / 24), -.066 * sin(pi * i / 24)) for i in range(25)]
        profile += [(.063 * cos(pi * i / 24), -.056 * sin(pi * i / 24)) for i in range(24, -1, -1)]
        for xx in (-4.22, 7.78):
            verts.extend((xx, yy + y, 3.59 + z) for y, z in profile)
        n = len(profile)
        for i in range(n):
            faces.append((i, (i+1)%n, (i+1)%n+n, i+n))
        faces += [tuple(reversed(range(n))), tuple(range(n,2*n))]
        mesh('V4 / open bronze rain gutter', verts, faces, m['bronze'])
        for xx in (-3.55, -1.70, .15, 2.00, 3.85, 5.70, 7.55):
            curve('V4 / gutter support strap', [(xx, yy + .074*cos(pi*i/24), 3.586-.069*sin(pi*i/24))
                  for i in range(25)], .004, m['dark'])
    # The old deck slab filled the tree well despite its cut planks.
    remove_prefix('Deck / dark substructure')
    for xa, xb, ya, yb in ((-5.19,-4.81,-9.815,-5.305),(-3.47,7.83,-9.815,-5.305),
                            (-4.81,-3.47,-9.815,-8.36),(-4.81,-3.47,-7.05,-5.305)):
        cube('V4 / deck subframe around open tree well', ((xa+xb)/2,(ya+yb)/2,-.119),
             (xb-xa,yb-ya,.13), m['dark'], .003)
    # Window gaskets, operable casement handles and floor transition tracks.
    for x, y0, y1, z0, z1 in ((6.973,-2.75,-.85,.70,2.57),(-3.438,-4.30,-1.15,.63,2.67)):
        curve('V4 / continuous recessed window gasket', [(x,y0,z0),(x,y1,z0),(x,y1,z1),(x,y0,z1)], .005, m['seal'], True)
        for yy in (y0+.13,y1-.13):
            cube('V4 / window handle escutcheon', (x,yy,1.40), (.019,.032,.12), m['bronze'], .005)
            curve('V4 / casement lever', [(x-.022,yy,1.43),(x-.057,yy,1.43),(x-.057,yy,1.34)], .007, m['bronze'])
    for yy in (-5.355,-5.275):
        cube('V4 / bronze threshold sliding track', (2.08,yy,.047), (1.89,.019,.015), m['bronze'], .002)
    for xx in (1.18,3.0):
        for zz in (.25,1.45,2.72):
            pin=cylinder('V4 / garden door fixing screw', (xx,-5.433,zz), .0037,.002,m['bronze'],16)
            pin.rotation_euler.x=pi/2
    # Board end grain joints and board-to-stone drainage remain visible in wider shots.
    for i in range(51):
        cube('V4 / linear deck drainage slot', (-2.8+i*.175,-9.848,-.105), (.098,.019,.023),m['dark'],.002)
    for ob in bpy.data.objects:
        if ob.name.startswith(('Cabin / south cedar weatherboard','Cabin / side cedar board')):
            rng=random.Random(ob.name)
            ob.rotation_euler.z += rng.uniform(-.0015,.0015)


def landscape(m):
    collection('63 • V4 / organic ground and gentle breeze')
    rng = random.Random(928040)
    segments, leaves = [], []
    for i in range(330):
        x,y = rng.uniform(-10.5,-4.2),rng.uniform(-16.9,-9.8)
        # Keep the fire garden and its circulation readable.
        if math.hypot(x+6.55,y+12.2)<1.1:
            continue
        z = ground_height(x,y)+.024
        a=rng.uniform(0,2*pi)
        length=rng.uniform(.06,.24)
        segments.append(((x,y,z),(x+length*cos(a),y+length*sin(a),z+.007),.0025,.0009))
        if i%3==0:
            leaves.append(((x,y,z+.01),(cos(a),sin(a),.10),.09,.033,rng.uniform(-.6,.6),i%3))
    branch_mesh('V4 / fallen articulated twigs',segments,m['bark'])
    foliage_mesh('V4 / scattered oak leaves',leaves,[existing('Old beech leaf litter'),existing('Olive leaf upper cuticle'),existing('Olive leaf silver underside')])
    for ob in bpy.data.objects:
        if ob.name.startswith('Garden / individual basalt stepping stone'):
            rng=random.Random(ob.name)
            for v in ob.data.vertices:
                if v.co.z>0:
                    v.co.z += rng.uniform(-.008,.008)
                    v.co.x *= rng.uniform(.94,1.06)
                    v.co.y *= rng.uniform(.94,1.06)
        if ob.type=='MESH' and ob.name.startswith(('Porch / individual jasmine leaves','Forest / fine living grass blades')):
            print('BREEZE_GEOMETRY',ob.name,len(ob.data.vertices),flush=True)
            ob.shape_key_add(name='Basis')
            key=ob.shape_key_add(name='Evening breeze')
            coords=np.empty(len(key.data)*3,dtype=np.float32)
            key.data.foreach_get('co',coords)
            coords=coords.reshape(-1,3)
            x,y,z=coords[:,0].copy(),coords[:,1].copy(),coords[:,2]
            if ob.name.startswith('Forest /'):
                distance=np.hypot((x-1)*.9,(y+3)*.85)
                amplitude=np.clip((distance-17)/28,0,1)
                ground=-.22+amplitude*(.55*np.sin(x*.12)+.40*np.sin(y*.14+x*.06))
                weight=np.clip(z-ground,0,.40)/.40
            else:
                weight=.40
            coords[:,0] += .018*weight*weight*np.sin(x*.9+y*.7)
            coords[:,1] += .012*weight*weight*np.cos(x*.7-y*.5)
            key.data.foreach_set('co',coords.ravel())
            key.driver_add('value').driver.expression='.5+.5*sin(frame*.031)'
    # An additional folded blanket remains subordinate to the landscape composition.
    cloth_surface('V4 / folded fireside linen',-8.08,-7.79,-11.49,-11.04,
                  lambda x,y:.407+.006*sin(x*36+y*18),m['linen'],31,35,.017)


def seamless_trunks(m):
    """Join the four capped trunk sections into one continuous bent radial surface."""
    from cinematography import catmull_rom
    changed=set()
    for ob in list(bpy.data.objects):
        if ob.type!='MESH' or 'complete trunk and branching' not in ob.name or ob.data.name in changed:
            continue
        data=ob.data
        changed.add(data.name)
        # Original branch_mesh wrote three 12-sided rings per thick segment.
        joints=[sum((data.vertices[i+j].co for j in range(12)),Vector())/12 for i in (0,36,72,108,132)]
        radii=[sum((data.vertices[i+j].co-joints[k]).length for j in range(12))/12
               for k,i in enumerate((0,36,72,108,132))]
        verts=[tuple(v.co) for v in list(data.vertices)[144:]]
        faces=[tuple(i-144 for i in p.vertices) for p in data.polygons if min(p.vertices)>=144]
        begin=len(verts); rings=129; sides=40
        for j in range(rings):
            t=j/(rings-1)
            center=catmull_rom(joints,t)
            tangent=(catmull_rom(joints,min(1,t+.001))-catmull_rom(joints,max(0,t-.001))).normalized()
            rot=tangent.to_track_quat('Z','Y')
            k=min(3,int(t*4));u=t*4-k
            radius=radii[k]*(1-u)+radii[k+1]*u
            radius+=.025*math.exp(-t*18)
            for i in range(sides):
                a=i*2*pi/sides
                r=radius*(1+.045*sin(a*5+.4*t)+.018*sin(a*13+t*5))
                verts.append(tuple(center+rot@Vector((r*cos(a),r*sin(a),0))))
        for j in range(rings-1):
            for i in range(sides):
                a=begin+j*sides+i;b=begin+j*sides+(i+1)%sides
                faces.append((a,b,b+sides,a+sides))
        faces.append(tuple(begin+i for i in reversed(range(sides))))
        faces.append(tuple(begin+(rings-1)*sides+i for i in range(sides)))
        data.clear_geometry();data.from_pydata(verts,[],faces);data.update()
        for p in data.polygons:p.use_smooth=True
    print('SEAMLESS_TRUNK_VARIANTS',len(changed),flush=True)


def light_balance():
    collection('64 • V4 / motivated window light')
    # Large soft sources sit outside real apertures, preserving the afternoon sun direction.
    for name,pos,energy,color,target,size in (
            ('V4 / bedroom cool sky through east window',(6.985,-1.75,2.04),72,(.68,.79,1.0),(4.9,-1.3,.85),1.7),
            ('V4 / bathroom sky through clerestory',(6.985,-4.28,2.13),34,(.73,.83,1.0),(5.0,-4.2,.70),.85)):
        lamp=light(name,pos,energy,color,target=target,size=size)
        lamp.data.shape='RECTANGLE'
        lamp.data.size_y=size*.8
        lamp.visible_camera=False
        lamp.visible_glossy=False
        lamp.visible_transmission=False
    # Reduce the blown central lamp diffuser and let window illumination describe the room.
    bpy.data.objects['Living / woven reading pendant practical'].data.energy=34


def build():
    before=len(bpy.data.objects)
    m=materials()
    for fn in (textiles,bathroom,joinery,landscape,seamless_trunks):
        print('REFINE_STAGE',fn.__name__,flush=True)
        fn(m)
    light_balance()
    return dict(objects_before=before,objects_after=len(bpy.data.objects),
                fixes=['vanity aligned below mirror','bath towel supported by bridge',
                       'closed shaped toilet','open gutter channels','deck tree well cut through subframe',
                       'non-repeating timber scan offsets','reduced interior stone bump'],
                additions=['tailored seat panels and piping','woven rug geometry','cloth folds and breeze',
                           'window seals and hardware','stone bathroom and sconces','irregular stepping stones and litter'])

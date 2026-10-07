"""Layered forest floor, native planting, poolside furniture and a garden path."""
from retreat_helpers import *
from forest import foliage_mesh, branch_mesh, tree_instance, ground_height
from materials import pbr
from furniture import cup, book


def reserved(x, y):
    return (-5.5 < x < 8.15 and -10.0 < y < 1.2) or (-3.1 < x < 8.8 and -17.0 < y < -9.7)


def ground(m):
    remove_prefix('Continuous gently undulating woodland earth',
                  'Lush clearing grasses', 'Scattered beech leaves')
    for obj in list(bpy.data.objects):
        if obj.name.startswith(('Forest fern ', 'Woodland understory shrub ', 'Mossy rounded forest rock')):
            if -3.3 < obj.location.x < 9 and -17.5 < obj.location.y < -9.5:
                bpy.data.objects.remove(obj, do_unlink=True)
    collection('55 • Retreat / excavated forest floor')
    # Four terrain patches leave a genuine hole for the 1.3 m deep pool.
    for xa, xb, ya, yb in [(-120, -2.66, -120, 120), (5.66, 120, -120, 120),
                           (-2.66, 5.66, -120, -15.76), (-2.66, 5.66, -10.14, 120)]:
        nx, ny = max(3, int((xb - xa) / 1.1)), max(3, int((yb - ya) / 1.1))
        verts, faces = [], []
        for j in range(ny):
            y = ya + (yb - ya) * j / (ny - 1)
            for i in range(nx):
                x = xa + (xb - xa) * i / (nx - 1)
                z = ground_height(x, y)
                if not reserved(x, y):
                    z += .028 * sin(x * 1.7) * sin(y * 2.3)
                verts.append((x, y, z))
        for j in range(ny - 1):
            for i in range(nx - 1):
                a = j * nx + i
                faces.append((a, a + 1, a + 1 + nx, a + nx))
        smooth(mesh('Forest / continuous soil surrounding excavation', verts, faces, m['ground']))
    # Nearby flora and actual curled leaf litter survive low camera angles.
    rng = random.Random(260926)
    leaves, blades, faces = [], [], []
    for i in range(6600):
        x, y = rng.uniform(-20, 22), rng.uniform(-26, 13)
        if reserved(x, y):
            continue
        z = ground_height(x, y) + .012
        a = rng.uniform(0, 2 * pi)
        leaves.append(((x, y, z), (cos(a), sin(a), .025), rng.uniform(.06, .13), .027, rng.uniform(-.1, .4), 0))
        for k in range(8):
            ang = rng.uniform(0, 2 * pi)
            h = rng.uniform(.09, .34)
            n = len(blades)
            for j in range(5):
                t = j / 4
                px, py = x + .12 * cos(ang) * t ** 2, y + .12 * sin(ang) * t ** 2
                w = .004 * (1 - t)
                blades.extend(((px - w * sin(ang), py + w * cos(ang), z + h * t),
                               (px + w * sin(ang), py - w * cos(ang), z + h * t)))
            for j in range(4):
                b = n + j * 2
                faces.append((b, b + 1, b + 3, b + 2))
    foliage_mesh('Forest / curled fallen leaves', leaves, [bpy.data.materials['Old beech leaf litter']])
    mesh('Forest / fine living grass blades', blades, faces, m['grass'])
    for i in range(36):
        x, y = rng.uniform(-11, 12), rng.uniform(-19, 4)
        if reserved(x, y):
            continue
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=(x, y, -.23))
        ob = link_object(bpy.context.object)
        ob.name = 'Forest / fractured granite with moss seams'
        for v in ob.data.vertices:
            v.co *= 1 + rng.uniform(-.11, .11)
        s = rng.uniform(.23, .71)
        ob.scale = (s, s * .75, s * .40)
        ob.rotation_euler.z = rng.uniform(0, 2 * pi)
        material(ob, m['rock'])
        smooth(ob)


def trees(m):
    collection('56 • Retreat / birch and conifer variation')
    # Replace smooth generic trunk shading on the inherited trees with real bark relief.
    old = bpy.data.materials.get('Mature broadleaf bark / longitudinal fissures')
    if old:
        for me in bpy.data.meshes:
            for i, mat in enumerate(me.materials):
                if mat == old:
                    me.materials[i] = m['bark_scan']
    birch = pbr('Retreat / silver birch parchment bark', '#C2C0AD', .86, noise=.30, bump=.007, scale=13)
    rng = random.Random(9281)
    for obj in bpy.data.objects:
        if obj.name.startswith('Sunward young forest '):
            group = obj.name.split(' / ')[0]
            variant_rng = random.Random(group)
            obj.location.x += variant_rng.uniform(-1.8, 1.8)
            obj.location.y += variant_rng.uniform(-1.3, 1.3)
    leafm = [bpy.data.materials['Woodland broadleaf chlorophyll ' + str(i)] for i in range(5)]
    segments, trunks, specs = [], [], []
    for trunk in range(3):
        dx, dy = (trunk - 1) * .22, trunk * .11
        top = Vector((dx + .30 * (trunk - 1), dy + .10, 8.1 + trunk * .64))
        trunks.append(((dx, dy, 0), top, .09, .017))
        for i in range(24):
            t = .26 + .70 * i / 24
            root = Vector((dx, dy, 0)).lerp(top, t)
            a = i * 2.39996 + trunk
            reach = 1.9 * sin(t * pi) + .25
            end = root + Vector((reach * cos(a), reach * sin(a), .62))
            segments.append((root, end, .027 * (1 - t) + .006, .003))
            for j in range(78):
                p = root.lerp(end, rng.uniform(.37, 1)) + Vector((rng.uniform(-.44, .44), rng.uniform(-.44, .44), rng.uniform(-.1, .48)))
                ang = rng.uniform(0, 2 * pi)
                specs.append((p, (cos(ang), sin(ang), rng.uniform(-.3, .6)), rng.uniform(.062, .115), .024, .3, j % 5))
    trunk = branch_mesh('Birch prototype / pale articulated trunks', trunks, birch)
    limbs = branch_mesh('Birch prototype / fine dark twigs', segments, m['bark_scan'])
    crown = foliage_mesh('Birch prototype / small fluttering leaves', specs, leafm)
    for i, (x, y, scale) in enumerate(((-11.0, -9.0, 1.05), (-11.0, -1.0, .91), (12.0, -3.0, .90), (13.0, -13.0, 1.10), (5.8, 3.7, .95))):
        tree_instance('Retreat birch %02d' % i, (trunk, limbs, crown), (x, y, ground_height(x, y)), (scale, scale, scale), i * .71)
    bpy.data.objects.remove(trunk, do_unlink=True)
    bpy.data.objects.remove(limbs, do_unlink=True)
    bpy.data.objects.remove(crown, do_unlink=True)
    # Tall fir silhouettes break the repetitive spherical broadleaf canopy.
    segments, specs = [((0, 0, 0), (0, 0, 15), .26, .024)], []
    for level in range(19):
        z = 2.4 + level * .63
        reach = 3.2 * (1 - (z - 2.4) / 14)
        for branch in range(8):
            a = branch * 2 * pi / 8 + level * .87
            end = Vector((reach * cos(a), reach * sin(a), z - .28))
            segments.append(((0, 0, z), end, .043 * (1 - level / 22), .004))
            for j in range(135):
                t = rng.uniform(.15, 1)
                p = Vector((0, 0, z)).lerp(end, t) + Vector((rng.uniform(-.28, .28), rng.uniform(-.28, .28), rng.uniform(-.10, .24)))
                aa = a + rng.uniform(-1.5, 1.5)
                specs.append((p, (cos(aa), sin(aa), .3), rng.uniform(.075, .17), .011, 0, j % 3))
    trunk = branch_mesh('Fir prototype / complete branching', segments, m['bark_scan'])
    crown = foliage_mesh('Fir prototype / needle sprays', specs, leafm[:3])
    for i, (x, y) in enumerate(((-12, 7), (-7, 11), (2, 12), (11, 8), (17, 4), (18, -8), (-17, -4), (-20, -15), (15, -23), (-13, 17))):
        scale = .85 + .30 * rng.random()
        tree_instance('Retreat silver fir %02d' % i, (trunk, crown), (x, y, ground_height(x, y)), (scale, scale, scale), i)
    bpy.data.objects.remove(trunk, do_unlink=True)
    bpy.data.objects.remove(crown, do_unlink=True)


def lounge(name, x, y, angle, m, long=True):
    def p(xx, yy, zz):
        return (x + xx * cos(angle) - yy * sin(angle), y + xx * sin(angle) + yy * cos(angle), zz)
    length = 1.7 if long else .66
    for xx in (-.29, .29):
        for yy in (-length * .38, length * .36):
            rectangular_beam(name + ' tapered leg', p(xx, yy, -.15), p(xx * .86, yy, .33), .045, .046, m['teak'])
        rectangular_beam(name + ' longitudinal rail', p(xx, -length / 2, .27), p(xx, length / 2, .29), .054, .075, m['teak'])
    for j in range(21 if long else 9):
        yy = -length / 2 + .08 * j
        rectangular_beam(name + ' individual seat slat', p(-.31, yy, .34), p(.31, yy, .34), .067, .024, m['teak'])
    for i in range(8):
        xx = -.28 + i * .08
        rectangular_beam(name + ' reclining back slat', p(xx, length * .12, .35), p(xx, length * .46 + .23, .91), .059, .027, m['teak'])
    for xx in (-.35, .35):
        rectangular_beam(name + ' arm support', p(xx, -.12, .28), p(xx, -.12, .55), .03, .035, m['teak'])
        rectangular_beam(name + ' sculpted armrest', p(xx, -.38, .55), p(xx, .43, .64), .077, .039, m['teak'])
    ob = cube(name + ' linen cushion', p(0, -.20, .397), (.53, length * .54, .08), m['ivory_cloth'], .035)
    ob.rotation_euler.z = angle
    return p


def garden(m):
    collection('57 • Retreat / garden rooms and poolside furniture')
    # Irregular stepping stones connect the deck to a small fire garden.
    for i in range(16):
        t = i / 15
        x = -4.65 - 1.05 * sin(t * pi) + 2.0 * t * t
        y = -9.95 - 7.10 * t
        ob = cylinder('Garden / individual basalt stepping stone', (x, y, -.135), .37, .09, m['rock'], 7)
        ob.scale = (1.22, .85, 1)
        ob.rotation_euler.z = .3 * sin(i * 2.3)
    # Quiet circular fire bowl and two low crafted chairs.
    lathe('Garden / aged bronze fire bowl', [(0, 0), (.23, 0), (.56, .20), (.62, .32), (.61, .345), (.575, .315), (.50, .19), (.21, .04), (0, .04)], (-6.55, -12.2, -.14), m['copper'], 96)
    for i in range(6):
        a = i * 2.4
        beam('Garden / split logs in fire bowl', (-6.55 - .34 * cos(a), -12.2 - .34 * sin(a), .09), (-6.55 + .32 * cos(a), -12.2 + .32 * sin(a), .13), .06, m['bark_scan'])
    lounge('Garden / fireside low chair', -7.95, -11.2, -.71, m, False)
    lounge('Garden / fireside low chair', -5.55, -11.25, .82, m, False)
    for x, y, ang in ((6.51, -12.09, -.17), (6.63, -14.40, -.15)):
        p = lounge('Poolside / adjustable teak chaise', x, y, ang, m)
        # Rolled white towels with concentric hems.
        towel = cylinder('Poolside / rolled linen towel', p(0, -.52, .54), .080, .44, m['ivory_cloth'], 48)
        towel.rotation_euler = (0, pi / 2, ang)
        for xx in (-.19, .19):
            ob = torus('Poolside / towel hem ring', p(xx, -.52, .54), .071, .003, m['linen'], (0, pi / 2, ang))
    cylinder('Poolside / low carved side table', (6.65, -13.22, .30), .27, .08, m['teak'], 64)
    cylinder('Poolside / carved pedestal', (6.65, -13.22, .06), .08, .41, m['teak'], 48)
    cup('Poolside / afternoon cup', 6.64, -13.23, .35, m, m['ceramic'])
    book('Poolside / weathered paperback', (6.75, -13.11, .354), (.18, .23, .025), m, 'sage', -.18)
    # Small outdoor shower: a working-scale fixture against a privacy screen.
    for i in range(12):
        cube('Garden / shower privacy cedar slat', (8.38, -10.81 - i * .103, .92), (.054, .080, 2.24), m['cedar'], .006)
    curve('Garden / bronze shower riser', [(8.28, -11.39, -.1), (8.28, -11.39, 1.89), (8.20, -11.39, 2.02), (7.99, -11.39, 2.02)], .016, m['copper'])
    head = cylinder('Garden / rain shower rose', (8.0, -11.39, 1.99), .10, .022, m['copper'], 48)
    for i in range(28):
        a = i * 2.399
        r = .085 * math.sqrt((i + 1) / 28)
        cylinder('Garden / shower rose perforation', (8.0 + r * cos(a), -11.39 + r * sin(a), 1.977), .0019, .002, m['dark'], 8)
    # Narrow raised teak path next to the pool, over the prepared soil.
    for j in range(55):
        cube('Poolside / teak walkway plank', (7.08, -10.24 - j * .12, -.12), (2.52, .114, .055), m['deck'], .004)
    for x, y in ((-2.93, -10.68), (-3.04, -15.66), (5.96, -16.3), (7.93, -10.12)):
        lantern('Garden / warm path lantern', (x, y, -.17), m, .8)
    # Re-use the detailed fern prototype around the landscaped edge.
    fern = next(o for o in bpy.data.objects if o.name.startswith('Forest fern ') and 'pinnae' in o.name)
    stems = next(o for o in bpy.data.objects if o.name.startswith('Forest fern ') and 'rachises' in o.name)
    rng = random.Random(2911)
    for i in range(95):
        side = -1 if i % 2 else 1
        x = (-3.3 if side < 0 else 8.9) + rng.uniform(-.55, .55)
        y = rng.uniform(-17.7, -9.5)
        s = rng.uniform(.32, .78)
        tree_instance('Garden / sculpted fern bank %03d' % i, (fern, stems), (x, y, -.21), (s, s, s), rng.uniform(0, 2 * pi))
    # The far edge of the water opens onto a natural fern meadow, not a bare strip.
    for i in range(72):
        x = rng.uniform(-3.5, 7.8)
        y = rng.uniform(-21.8, -17.4)
        s = rng.uniform(.48, 1.02)
        tree_instance('Garden / sunward fern meadow %03d' % i, (fern, stems), (x, y, ground_height(x, y)), (s, s, s), rng.uniform(0, 2*pi))
    verts, faces = [], []
    for clump in range(28):
        x = -3.1 + clump * .405
        y = -17.13 - .40 * sin(clump * 1.8)
        for k in range(74):
            a = rng.uniform(0, 2*pi)
            reach, h = rng.uniform(.12, .38), rng.uniform(.23, .64)
            n = len(verts)
            for j in range(9):
                t = j/8
                px, py = x + reach*cos(a)*t, y + reach*sin(a)*t
                z = -.22 + h*sin(t*pi*.66)
                w = .008*(1-t)
                verts.extend(((px-w*sin(a),py+w*cos(a),z),(px+w*sin(a),py-w*cos(a),z)))
            for j in range(8):
                b = n+j*2
                faces.append((b,b+1,b+3,b+2))
    mesh('Garden / arching ornamental sedges at the pool edge', verts, faces, m['grass'])
    # Fallen branch and mushrooms anchor the close forest floor.
    beam('Forest / fallen birch limb', (-8.1, -16.9, -.16), (-5.75, -17.5, -.03), .12, m['bark_scan'], .085)
    for i in range(8):
        x, y = -5.91 + .09 * cos(i * 2.4), -17.51 + .16 * sin(i * 2.4)
        h = .035 + (i % 3) * .016
        beam('Forest / tiny mushroom stem', (x, y, -.19), (x, y, -.19 + h), .007, m['paper'])
        sphere('Forest / tiny mushroom cap', (x, y, -.19 + h), (.028, .026, .013), m['terra'], 20, 12)


def build(m):
    ground(m)
    trees(m)
    garden(m)
    # Closed branch segments must not interpolate the cap normals onto bark.
    # This removes the artificial dark rings inherited from smooth-shaded caps.
    for data in bpy.data.meshes:
        if any(mat and 'bark' in mat.name.lower() for mat in data.materials):
            for polygon in data.polygons:
                if len(polygon.vertices) > 4:
                    polygon.use_smooth = False

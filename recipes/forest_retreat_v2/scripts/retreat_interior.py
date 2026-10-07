"""A lived-in reading room, breakfast kitchen and layered linen bedroom."""
from retreat_helpers import *
from furniture import book, cup, cushion
from garden import herb, leaves_mesh


def pendant(name, pos, m, radius=.25):
    x, y, z = pos
    beam(name + ' textile cable', (x, y, z + .26), (x, y, 3.25), .003, m['dark'])
    for i in range(44):
        a = i * 2 * pi / 44
        points = []
        for j in range(25):
            t = j / 24
            r = radius * (.36 + .64 * sin(pi * t) ** .65)
            points.append((x + r * cos(a), y + r * sin(a), z + .38 * t))
        curve(name + ' bent rattan rib', points, .0028, m['teak'])
    for j in range(15):
        t = j / 14
        r = radius * (.36 + .64 * sin(pi * t) ** .65)
        torus(name + ' woven binding', (x, y, z + .38 * t), r, .0023, m['teak'])
    lathe(name + ' inner linen diffuser', [(.055, 0), (.11, .10), (.11, .28), (.055, .37)], (x, y, z), m['lamp_linen'])
    bulb = sphere(name + ' frosted bulb', (x, y, z + .17), (.028, .028, .048), m['glow'], 24, 16)
    bulb.visible_shadow = False
    light(name + ' practical', (x, y, z + .15), 45, radius=.035)


def living(m):
    collection('50 • Retreat / library and hearth')
    # A small freestanding stove replaces the generic plant at this corner.
    remove_prefix('Large indoor olive planter', 'Indoor young olive')
    x, y = -2.94, -4.62
    cube('Hearth / dark stone slab', (x, y, .071), (.92, .75, .074), m['rock'], .022)
    cube('Hearth / cast iron stove', (x, y, .47), (.43, .39, .56), m['dark'], .055)
    cube('Hearth / recessed firebox', (x, y - .203, .49), (.34, .009, .38), m['dark'], .025)
    for z in (.32, .37, .43):
        beam('Hearth / ember log', (x - .14, y - .17, z), (x + .13, y - .16, z + .024), .026, m['bark_scan'])
    for i in range(13):
        sphere('Hearth / banked embers', (x - .12 + i * .02, y - .213, .292), (.013, .009, .012), m['ember'], 12, 8)
    cube('Hearth / fireproof glass door', (x, y - .220, .49), (.33, .006, .36), m['glass'], .017)
    beam('Hearth / door latch', (x + .183, y - .25, .44), (x + .183, y - .25, .55), .008, m['copper'])
    for dx in (-.14, .14):
        for dy in (-.13, .13):
            beam('Hearth / cast foot', (x + dx, y + dy, .10), (x + dx, y + dy, .24), .021, m['dark'])
    beam('Hearth / chimney pipe', (x, y, .74), (x, y, 5.14), .070, m['dark'])
    for z in (1.2, 2.3, 3.3, 4.5):
        torus('Hearth / flue collar', (x, y, z), .071, .007, m['dark'])
    cylinder('Hearth / rain cowl', (x, y, 5.17), .12, .04, m['dark'])
    basket('Hearth / kindling basket', (-2.06, -4.74, .06), .20, .24, m)
    for i in range(8):
        dx, dy = RNG.uniform(-.13, .13), RNG.uniform(-.13, .13)
        beam('Hearth / split kindling', (-2.06 + dx, -4.74 + dy, .09), (-2.01 + dx, -4.73 + dy, .39 + i * .008), .022, m['bark_scan'])
    # Real shelving with varied books, bowls, paper and baskets.
    for x in (-3.46, -2.83):
        cube('Library / solid walnut side', (x, -.41, 1.34), (.035, .50, 2.53), m['walnut'], .005)
    for z in (.09, .52, .96, 1.40, 1.84, 2.27, 2.61):
        cube('Library / floating shelf', (-3.145, -.41, z), (.665, .52, .035), m['walnut'], .006)
    for row, z in enumerate((.54, .98, 1.42, 2.29)):
        for i in range(7 if row != 2 else 4):
            xx = -3.39 + i * .066
            hh = .23 + .07 * sin(i * 2.2 + row)
            ob = cube('Library / linen book spine', (xx, -.37, z + hh / 2), (.042, .28, hh), m[('sage', 'paper', 'terra', 'linen')[(i + row) % 4]], .002)
            ob.rotation_euler.y = .03 * sin(i * 2)
            for zz in (z + .025, z + hh - .025):
                cube('Library / embossed spine band', (xx, -.513, zz), (.035, .0015, .004), m['copper'], .0005)
    vessel('Library / ceramic bud vase', (-3.0, -.41, 1.865), .075, .20, m['ceramic'])
    herb('Library / trailing thyme', (-3.25, -.41, 1.862), m, .45)
    basket('Library / small woven storage', (-3.16, -.42, .115), .19, .28, m)
    # Throw tucked over the sofa with a gravity-shaped fall over its front.
    def sofa_throw(x, y):
        fall = max(0, x + 2.32)
        return .561 - min(.33, fall * 1.55) + .018 * sin(y * 33 + x * 9) + .008 * sin(y * 72)
    cloth_surface('Living / casually draped wool throw', -3.12, -2.10, -2.74, -2.11, sofa_throw, m['rust_cloth'])
    for i in range(30):
        yy = -2.74 + i * .021
        curve('Living / throw tasseled edge', [(-2.105, yy, sofa_throw(-2.105, yy)), (-2.09, yy + .004, .19), (-2.08, yy, .14)], .0016, m['rust_cloth'])
    # A real folded letter, reading glasses and a small vase give the table a story.
    cube('Living / folded letter', (-.86, -2.37, .484), (.15, .10, .0016), m['paper'], .001)
    for xx in (-.85, -.807):
        torus('Living / reading glasses lens rim', (xx, -2.36, .491), .022, .0011, m['copper'])
    beam('Living / glasses bridge', (-.827, -2.36, .491), (-.83, -2.36, .491), .0012, m['copper'])
    curve('Living / glasses temples', [(-.875, -2.36, .491), (-.89, -2.30, .493), (-.87, -2.27, .491)], .0012, m['copper'])
    vessel('Living / quiet ceramic vase', (-.35, -2.07, .478), .045, .14, m['ceramic'])
    for i in range(5):
        a = i * 2.4
        beam('Living / dried flower stem', (-.35, -2.07, .55), (-.35 + .04 * cos(a), -2.07 + .04 * sin(a), .81 + .015 * i), .0011, m['bark'])
        sphere('Living / dried seed head', (-.35 + .04 * cos(a), -2.07 + .04 * sin(a), .81 + .015 * i), (.012, .01, .021), m['terra'], 14, 8)
    pendant('Living / woven reading pendant', (-.47, -2.11, 2.43), m, .31)
    bpy.data.objects['Living / woven reading pendant practical'].data.energy = 72
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.name.startswith('Warm reading lamp practical'):
            obj.data.energy = 5
            obj.data.color = (1, .81, .61)
            obj.data.shadow_soft_size = .065


def kitchen(m):
    collection('51 • Retreat / breakfast and pantry details')
    remove_prefix('Stacked handmade stoneware')
    for i in range(17):
        for j in range(5):
            ob = cube('Kitchen / imperfect celadon backsplash tile', (1.39 + i * .102, -.048, 1.037 + j * .099), (.098, .015, .095), m['tile_variants'][(i * 3 + j) % 5], .004)
            ob.rotation_euler.y = .002 * sin(i + j)
    for x, count in ((1.62, 5), (2.08, 3)):
        for j in range(count):
            lathe('Kitchen / stacked shallow handmade plates', [(0, 0), (.056, 0), (.102, .009), (.114, .021), (.108, .026), (.061, .010), (0, .010)], (x, -.19, 1.605 + j * .017), m['ceramic'])
    vessel('Kitchen / utensil crock', (2.48, -.18, 1.605), .052, .13, m['sage'])
    for i in range(5):
        xx = 2.46 + .013 * i
        beam('Kitchen / wooden spoon handle', (xx, -.18, 1.64), (xx + .016 * sin(i), -.18, 1.87 + .008 * i), .003, m['teak'])
        sphere('Kitchen / wooden spoon bowl', (xx + .016 * sin(i), -.18, 1.89 + .008 * i), (.014, .005, .022), m['teak'], 20, 12)
    for x in (2.02, 2.14):
        lathe('Kitchen / olive oil glass bottle', [(0, 0), (.034, 0), (.037, .13), (.02, .17), (.014, .22), (.012, .23), (0, .23)], (x, -.20, 1.0), m['bottle'])
        cylinder('Kitchen / cork stopper', (x, -.20, 1.235), .014, .025, m['oak'], 24)
        cube('Kitchen / cotton paper bottle label', (x, -.236, 1.07), (.044, .001, .065), m['paper'], .002)
    # A cut lemon with separate pith, radial flesh sections and seeds.
    cylinder('Kitchen / lemon half rind', (2.31, -.50, 1.04), .037, .065, m['lemon'])
    cylinder('Kitchen / lemon cut pith', (2.31, -.50, 1.074), .034, .002, m['paper'])
    for i in range(9):
        a = i * 2 * pi / 9
        verts = [(2.31, -.5, 1.076)] + [(2.31 + .030 * cos(a + j * .065), -.5 + .030 * sin(a + j * .065), 1.076) for j in range(10)]
        mesh('Kitchen / lemon translucent segment', verts, [tuple(range(len(verts)))], m['lemon_flesh'])
    cube('Kitchen / chef knife blade', (2.39, -.55, 1.019), (.023, .15, .002), m['steel'], .002)
    cube('Kitchen / chef knife walnut handle', (2.39, -.665, 1.022), (.021, .079, .016), m['walnut'], .006)
    # Linen towel folds over the oven handle; no floating rectangular plane.
    verts, faces = [], []
    for j in range(51):
        t = j / 50
        for i in range(41):
            xx = 1.51 + i * .22 / 40
            yy = -.831 + .025 * sin(t * pi)
            zz = .645 - .34 * t + .009 * sin(i * .9) * sin(t * pi / 2)
            verts.append((xx, yy, zz))
    for j in range(50):
        for i in range(40):
            a = j * 41 + i
            faces.append((a, a + 1, a + 42, a + 41))
    smooth(mesh('Kitchen / hanging flax tea towel', verts, faces, m['ivory_cloth']))
    pendant('Kitchen / hand-woven pendant', (2.22, -1.35, 2.29), m, .24)
    # Breakfast table sits outside the dolly corridor.
    cylinder('Breakfast / round teak table', (2.16, -3.77, .75), .47, .045, m['teak'], 96)
    cylinder('Breakfast / turned pedestal', (2.16, -3.77, .40), .055, .69, m['walnut'])
    cylinder('Breakfast / weighted base', (2.16, -3.77, .073), .29, .055, m['walnut'], 64)
    cloth_surface('Breakfast / soft linen table runner', 1.90, 2.38, -4.05, -3.49,
                  lambda x, y: .779 + .003 * sin(x * 53 + y * 28), m['ivory_cloth'], 31, 31)
    cup('Breakfast / celadon cup', 2.21, -3.94, .784, m, m['sage'])
    lathe('Breakfast / bread plate', [(0, 0), (.12, 0), (.14, .022), (.135, .028), (.10, .011), (0, .011)], (2.03, -3.64, .784), m['ceramic'])
    loaf = sphere('Breakfast / small sourdough loaf', (2.03, -3.64, .843), (.11, .069, .056), m['bread'], 40, 24)
    for i in range(4):
        curve('Breakfast / scored crust', [(1.97 + j * .016, -3.675 + i * .023, .876 + .020 * sin(j * pi / 8)) for j in range(9)], .003, m['paper'])
    for x, y in ((2.83, -3.75), (2.12, -4.52)):
        cylinder('Breakfast / woven stool seat', (x, y, .445), .20, .04, m['linen'], 64)
        for a in (0, 2 * pi / 3, 4 * pi / 3):
            beam('Breakfast / stool splayed leg', (x + .17 * cos(a), y + .17 * sin(a), .055), (x + .12 * cos(a), y + .12 * sin(a), .43), .016, m['walnut'])


def bedroom(m):
    collection('52 • Retreat / linen bedroom and dressing')
    remove_prefix('Soft draped linen duvet', 'Duvet turned foot hem')
    def duvet_z(x, y):
        side = max(0, abs(x - 5.02) - .78) / .23
        foot = max(0, -y - 2.57) / .36
        z = .731 - .28 * min(1, side) ** 1.3 - .31 * min(1, foot) ** 1.3
        z += .006 * sin(x * 11 + y * 7) * sin(y * 9 + x * 3)
        z += (.004 + .009 * min(1, side + foot)) * sin(x * 34 + y * 13)
        z += .067 * math.exp(-((y + 1.10 + .06 * sin(x * 4)) / .095) ** 2)
        for cx, cy, amp, width in ((4.3,-1.42,.020,.31),(5.35,-1.82,.013,.39),(5.75,-1.36,.018,.24)):
            z += amp * math.exp(-((x-cx)**2+(y-cy)**2)/(width*width))
        return z
    cloth_surface('Bedroom / relaxed linen duvet with gravity folds', 3.99, 6.05, -2.96, -1.00, duvet_z, m['ivory_cloth'], 101, 91, .007)
    def throw_z(x, y):
        return duvet_z(x, y) + .020 + .006 * sin(x * 29 + y * 11)
    cloth_surface('Bedroom / sage throw across foot of bed', 3.98, 6.07, -2.69, -2.03, throw_z, m['sage_cloth'], 87, 47, .006)
    for i in range(65):
        xx = 4.00 + i * .0315
        zz = throw_z(xx, -2.69)
        curve('Bedroom / loose throw tassels', [(xx, -2.69, zz), (xx + .004, -2.77, zz - .035), (xx, -2.81, zz - .075)], .0015, m['sage_cloth'])
    for x in (4.52, 5.45):
        p = cushion('Bedroom / relaxed linen pillow', (x, -.93, .82), (.68, .41, .22), {'cream': m['ivory_cloth']})
        p.rotation_euler = (.15, .03, .07 if x < 5 else -.07)
        curve('Bedroom / visible pillow piping', [(x + .31 * cos(a * 2 * pi / 100), -.94 + .185 * sin(a * 2 * pi / 100), .833) for a in range(100)], .002, m['linen'], True)
    # Window curtains are pleated geometry, held to a real bronze rail.
    beam('Bedroom / curtain pole', (6.83, -3.02, 2.99), (6.83, -.53, 2.99), .015, m['copper'])
    for y0 in (-2.98, -1.04):
        vv, ff = [], []
        for j in range(61):
            t = j / 60
            for i in range(49):
                u = i / 48
                xx = 6.84 + .045 * cos(u * pi * 14) * (.65 + .35 * t)
                yy = y0 + .49 * u + .028 * sin(t * pi) * sin(u * pi)
                zz = 2.94 - 2.83 * t + .015 * sin(u * pi * 14) * t ** 8
                vv.append((xx, yy, zz))
        for j in range(60):
            for i in range(48):
                a = j * 49 + i
                ff.append((a, a + 1, a + 50, a + 49))
        ob = smooth(mesh('Bedroom / full length pleated linen drapery', vv, ff, m['lamp_linen']))
        for i in range(8):
            torus('Bedroom / curtain ring', (6.84, y0 + i * .07, 2.98), .025, .003, m['copper'], (pi / 2, 0, 0))
    book('Bedroom / bedside botanical book', (6.14, -.66, .71), (.19, .25, .028), m, 'paper', .12)
    cup('Bedroom / bedside water cup', 3.9, -.88, .705, m, m['ceramic'], .035)
    vessel('Bedroom / bedside dried bouquet vase', (6.22, -.89, .704), .05, .17, m['terra'])
    for i in range(12):
        a = i * 2.4
        end = (6.22 + .085 * cos(a), -.89 + .065 * sin(a), 1.12 + .06 * sin(i))
        beam('Bedroom / dried oat stem', (6.22, -.89, .84), end, .0012, m['bark'])
        sphere('Bedroom / dried oat panicle', end, (.01, .009, .04), m['paper'], 12, 8)
    # Quiet botanical artwork modeled in relief.
    for x in (4.58, 5.40):
        cube('Bedroom / oak botanical frame', (x, -.025, 2.06), (.58, .055, .79), m['walnut'], .012)
        cube('Bedroom / warm cotton picture mount', (x, -.061, 2.06), (.52, .008, .73), m['paper'], .002)
        specs = []
        for i in range(7):
            z = 1.78 + i * .062
            beam('Bedroom / pressed botanical stem', (x, -.071, 1.76), (x + .035, -.071, 2.33), .002, m['bark'])
            for side in (-1, 1):
                leaf = sphere('Bedroom / pressed botanical leaf', (x + side * .052, -.073, z), (.062, .002, .018), m['sage'], 24, 12)
                leaf.rotation_euler.y = side * -.42
    basket('Bedroom / laundry basket', (6.57, -2.65, .07), .25, .38, m)
    cloth_surface('Bedroom / linen in laundry basket', 6.38, 6.80, -2.84, -2.46,
                  lambda x, y: .47 + .06 * sin(x * 18) * sin(y * 23), m['ivory_cloth'], 31, 31)
    pendant('Bedroom / woven soft pendant', (5.12, -1.69, 2.56), m, .34)
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.name.startswith('Bedside warm practical'):
            obj.data.energy = 32


def build(m):
    living(m)
    kitchen(m)
    bedroom(m)

"""A complete excavated pool, optical water volume and gravity-fed spillway."""
from retreat_helpers import *
from materials import pbr, rgb
from water_simulation import topology, NX, NY, FRAMES, OUT


def mosaic(name, plane):
    mat = pbr(name, '#85A399', .28)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bs = nodes.get('Principled BSDF')
    geom = nodes.new('ShaderNodeNewGeometry')
    sep = nodes.new('ShaderNodeSeparateXYZ')
    comb = nodes.new('ShaderNodeCombineXYZ')
    links.new(geom.outputs['Position'], sep.inputs[0])
    links.new(sep.outputs[plane[0]], comb.inputs['X'])
    links.new(sep.outputs[plane[1]], comb.inputs['Y'])
    brick = nodes.new('ShaderNodeTexBrick')
    links.new(comb.outputs[0], brick.inputs['Vector'])
    brick.offset = 0
    brick.inputs['Scale'].default_value = 1
    brick.inputs['Mortar Size'].default_value = .0018
    brick.inputs['Mortar Smooth'].default_value = .0008
    brick.inputs['Brick Width'].default_value = .098
    brick.inputs['Row Height'].default_value = .098
    brick.inputs['Color1'].default_value = rgb('#7E9C93')
    brick.inputs['Color2'].default_value = rgb('#B1BFA8')
    brick.inputs['Mortar'].default_value = rgb('#BCC5B4')
    links.new(brick.outputs['Color'], bs.inputs['Base Color'])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = .002
    bump.inputs['Strength'].default_value = .55
    bump.invert = True
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs[0], bs.inputs['Normal'])
    return mat


def build(m):
    collection('58 • Retreat / pool construction and optical water')
    floor = mosaic('Pool / hand-laid pale celadon mosaic floor', 'XY')
    wallx = mosaic('Pool / hand-laid mosaic end wall', 'YZ')
    wally = mosaic('Pool / hand-laid mosaic long wall', 'XZ')
    basin = cube('Pool / solid tiled floor', (1.50, -12.95, -1.575), (7.64, 4.94, .13), floor, .015)
    basin.cycles.is_caustics_receiver = True
    for x in (-2.40, 5.40):
        wall = cube('Pool / structural tiled end wall', (x, -12.95, -.855), (.20, 5.10, 1.45), wallx, .012)
        wall.cycles.is_caustics_receiver = True
    for y in (-15.50, -10.40):
        wall = cube('Pool / structural tiled long wall', (1.50, y, -.855), (7.62, .20, 1.45), wally, .012)
        wall.cycles.is_caustics_receiver = True
    for y in (-15.59, -10.31):
        for i in range(11):
            cube('Pool / individually mitred travertine coping', (-2.66 + (i + .5) * 8.32 / 11, y, -.058), (8.32 / 11 - .006, .38, .116), m['rim'], .010)
    for x in (-2.49, 5.49):
        for i in range(7):
            cube('Pool / honed side coping stone', (x, -15.39 + (i + .5) * 4.89 / 7, -.058), (.38, 4.89 / 7 - .006, .116), m['rim'], .010)
    # A low perimeter apron makes the pool sit within a constructed garden.
    for x in (-3.02, 6.02):
        for i in range(9):
            cube('Pool / limestone garden apron', (x, -15.99 + i * .755, -.155), (.64, .747, .085), m['stone'], .012)
    for y in (-16.08, -9.93):
        for i in range(11):
            cube('Pool / limestone end apron', (-2.68 + i * .79, y, -.155), (.782, .58, .085), m['stone'], .011)
    for i in range(4):
        ztop = -.42 - i * .255
        step = cube('Pool / submerged entry stair', (-2.13 + i * .35, -11.19, (-1.51 + ztop) / 2), (.35, 1.35, ztop + 1.51), floor, .014)
        step.cycles.is_caustics_receiver = True
        cube('Pool / visible anti-slip step nosing', (-1.966 + i * .35, -11.19, ztop + .004), (.018, 1.32, .009), m['rim'], .002)
    curve('Pool / entry handrail', [(-2.46, -10.76, -.04), (-2.46, -10.76, .46), (-2.32, -10.76, .53),
          (-1.15, -10.76, -.16), (-1.10, -10.76, -.61)], .021, m['steel'])
    for x in (4.24, 4.77):
        curve('Pool / polished ladder handrail', [(x, -15.87, -.10), (x, -15.86, .37), (x, -15.74, .49),
              (x, -15.52, .49), (x, -15.23, .30), (x, -15.18, -.98)], .023, m['steel'])
        torus('Pool / ladder anchored flange', (x, -15.87, -.09), .052, .009, m['steel'])
    for z in (-.35, -.64, -.93):
        cube('Pool / ladder non-slip rung', (4.505, -15.18, z), (.54, .082, .026), m['steel'], .010)
    # Underwater light housings remain restrained in afternoon daylight.
    for x in (-.8, 1.5, 3.8):
        disk = cylinder('Pool / underwater lamp bezel', (x, -10.509, -.69), .067, .014, m['steel'], 48)
        disk.rotation_euler.x = pi / 2
        disk = cylinder('Pool / underwater frosted lens', (x, -10.519, -.69), .052, .016, m['glow'], 48)
        disk.rotation_euler.x = pi / 2
        light('Pool / low wattage submerged luminaire', (x, -10.55, -.69), 4, (1, .90, .73), .035)
    verts, faces = topology()
    water = smooth(mesh('Pool / baked gravity-capillary water volume', verts.tolist(), faces, m['water']))
    water.cycles.is_caustics_caster = True
    water.cycles.use_deform_motion = True
    cache = water.modifiers.new('Physical basin waves / baked 44 seconds', 'MESH_CACHE')
    cache.cache_format = 'MDD'
    cache.filepath = str(OUT / 'cache' / 'pool_gravity_capillary.mdd')
    cache.forward_axis = 'POS_Y'
    cache.up_axis = 'POS_Z'
    cache.interpolation = 'LINEAR'
    cache.frame_start = 1
    cache.frame_scale = 1
    water['physics'] = 'Finite-depth gravity-capillary eigenmodes with reflecting pool walls; see review/water_simulation.json'
    water['ior'] = 1.333
    water['cache_frame_count'] = FRAMES
    # A bronze spillway creates a visible, physically motivated source of ripples.
    cube('Pool / spillway stone pedestal', (5.69, -12.80, .18), (.39, .96, .73), m['rock'], .025)
    cube('Pool / bronze spillway body', (5.39, -12.80, .24), (.47, .67, .075), m['copper'], .015)
    cube('Pool / narrow spillway outlet slot', (5.147, -12.8, .236), (.009, .58, .026), m['dark'], .004)
    verts, faces = [], []
    for j in range(57):
        t = .318 * j / 56
        for i in range(25):
            u = i / 24
            verts.append((5.144 - .85 * t, -13.09 + .58 * u,
                          .229 - 4.905 * t * t + .002 * sin(u * 31 + t * 70)))
    for j in range(56):
        for i in range(24):
            a = j * 25 + i
            faces.append((a, a + 1, a + 26, a + 25))
    sheet = smooth(mesh('Pool / gravity accelerated spillway water sheet', verts, faces, m['water']))
    solid = sheet.modifiers.new('Thin flowing water thickness', 'SOLIDIFY')
    solid.thickness = .0018
    sheet.shape_key_add(name='Basis')
    ripple = sheet.shape_key_add(name='Flow striations')
    for i, v in enumerate(ripple.data):
        v.co.x += .0025 * sin(i * .73)
        u = (i % 25) / 24
        t = (i // 25) / 56
        v.co.y += .013 * sin(t * 23) * abs(2*u-1)**6
    driver = ripple.driver_add('value').driver
    driver.expression = '.5+.5*sin(frame*.31)'
    sheet['physics'] = 'Steady thin-sheet ballistic trajectory: x=x0-v*t, z=z0-g*t^2/2; fine flow ripple shape key.'
    for i in range(18):
        droplet = sphere('Pool / falling spray bead', (0, 0, 0), (.0035, .0035, .006), m['water'], 12, 8)
        phase = i * .019
        tau = '((frame/24+%.5f)%%.32)' % phase
        for axis, expression in ((0, '5.15-.90*' + tau), (1, str(-13.04 + (i % 9) * .060)),
                                 (2, '.23-4.905*' + tau + '**2')):
            droplet.driver_add('location', axis).driver.expression = expression

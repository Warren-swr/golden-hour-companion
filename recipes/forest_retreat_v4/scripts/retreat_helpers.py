"""Small reusable geometry and practical-light helpers, in metres."""
from common import *


def remove_prefix(*prefixes):
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)


def rectangular_beam(name, a, b, width, depth, mat):
    a, b = Vector(a), Vector(b)
    obj = cube(name, (a + b) / 2, (width, depth, (b - a).length), mat, .005)
    obj.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return obj


def light(name, loc, energy, color=(1, .78, .52), radius=.05, target=None, size=.35):
    data = bpy.data.lights.new(name, 'AREA' if target else 'POINT')
    obj = bpy.data.objects.new(name, data)
    link_object(obj)
    obj.location = loc
    data.energy = energy
    data.color = color
    if target:
        data.shape = 'DISK'
        data.size = size
        aim(obj, target)
    else:
        data.shadow_soft_size = radius
    return obj


def cloth_surface(name, x0, x1, y0, y1, height, mat, nx=65, ny=51, thickness=.003):
    vertices = [(x0 + (x1 - x0) * i / (nx - 1), y0 + (y1 - y0) * j / (ny - 1),
                 height(x0 + (x1 - x0) * i / (nx - 1), y0 + (y1 - y0) * j / (ny - 1)))
                for j in range(ny) for i in range(nx)]
    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            faces.append((a, a + 1, a + 1 + nx, a + nx))
    obj = smooth(mesh(name, vertices, faces, mat))
    mod = obj.modifiers.new('Sewn textile thickness', 'SOLIDIFY')
    mod.thickness = thickness
    return obj


def vessel(name, pos, r, h, mat):
    return lathe(name, [(0, 0), (r * .7, 0), (r, h * .15), (r * 1.04, h * .65),
                        (r * .55, h * .89), (r * .52, h), (r * .42, h),
                        (r * .45, h * .9), (r * .9, h * .63), (r * .86, h * .18), (0, .012)], pos, mat)


def basket(name, pos, r, h, m):
    x, y, z = pos
    for j in range(26):
        t = j / 25
        rr = r * (.78 + .22 * t)
        curve(name + ' woven horizontal strand', [(x + rr * cos(a * 2 * pi / 80),
              y + rr * sin(a * 2 * pi / 80), z + t * h) for a in range(80)], .0034, m['teak'], True)
    for i in range(42):
        a = i * 2 * pi / 42
        curve(name + ' vertical wicker', [(x + r * (.78 + .22 * j / 16) * cos(a),
              y + r * (.78 + .22 * j / 16) * sin(a), z + h * j / 16) for j in range(17)], .003, m['teak'])
    torus(name + ' bound rim', (x, y, z + h), r, .008, m['teak'])


def lantern(name, pos, m, scale=1):
    x, y, z = pos
    w, h = .18 * scale, .29 * scale
    cube(name + ' bronze base', (x, y, z + .02 * scale), (w, w, .04 * scale), m['copper'], .007)
    cube(name + ' bronze lid', (x, y, z + h), (w, w, .025 * scale), m['copper'], .005)
    for dx in (-w / 2, w / 2):
        for dy in (-w / 2, w / 2):
            beam(name + ' frame', (x + dx, y + dy, z), (x + dx, y + dy, z + h), .006 * scale, m['copper'])
    cylinder(name + ' wax pillar', (x, y, z + .09 * scale), .038 * scale, .14 * scale, m['wax'])
    flame = sphere(name + ' flame', (x, y, z + .18 * scale), (.007 * scale, .006 * scale, .023 * scale), m['glow'], 16, 12)
    flame.visible_shadow = False
    light(name + ' practical candle', (x, y, z + .18 * scale), 2.5 * scale, radius=.008)
    torus(name + ' ring handle', (x, y, z + h + .036 * scale), .04 * scale, .005 * scale, m['copper'], (pi / 2, 0, 0))

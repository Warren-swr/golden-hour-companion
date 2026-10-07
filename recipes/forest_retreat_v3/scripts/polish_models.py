"""v3 model polish applied on top of the reviewed v2 scene.

Fixes found during the v2 film review: sparse fir crowns that read as bare
masts above the canopy, the black edge of the solid spillway sheet, boxy
bedroom pillows and over-bright bedside shades.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from retreat_helpers import *
from forest import foliage_mesh, branch_mesh, tree_instance, ground_height
from mathutils import Matrix


def remove_objects(prefix):
    meshes = set()
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefix):
            if obj.type == 'MESH':
                meshes.add(obj.data)
            bpy.data.objects.remove(obj, do_unlink=True)
    for data in meshes:
        if data.users == 0:
            bpy.data.meshes.remove(data)


def firs():
    """Dense layered silver firs; the v2 crowns were thin enough to read as masts."""
    old = [o for o in bpy.data.objects if o.name.startswith('Retreat silver fir ') and o.name.endswith('complete branching')]
    placements = [(o.location.copy(), o.scale.copy(), o.rotation_euler.z) for o in old]
    remove_objects('Retreat silver fir ')
    collection('56 • Retreat / birch and conifer variation')
    leafm = [bpy.data.materials['Woodland broadleaf chlorophyll ' + str(i)] for i in range(3)]
    rng = random.Random(260927)
    segments, specs = [((0, 0, 0), (0, 0, 15.1), .27, .02)], []
    levels = 31
    for level in range(levels):
        z = 1.9 + level * .42
        f = (z - 1.9) / 13.2
        reach = 3.05 * (1 - f) ** 1.1 + .22
        count = 9 if f < .8 else 6
        for branch in range(count):
            a = branch * 2 * pi / count + level * 2.39996 + rng.uniform(-.2, .2)
            droop = -.30 - .25 * (1 - f)
            end = Vector((reach * cos(a), reach * sin(a), z + droop))
            root = Vector((0, 0, z))
            segments.append((root, end, .045 * (1 - f) + .006, .004))
            # Flattened sprays on both sides of each limb form the layered fir silhouette.
            side = Vector((-sin(a), cos(a), 0))
            for j in range(int(360 * (reach / 3.3) + 60)):
                t = rng.uniform(.12, 1) ** .8
                p = root.lerp(end, t) + side * rng.uniform(-.34, .34) * (1.1 - .6 * t) + Vector((0, 0, rng.uniform(-.07, .09)))
                aa = a + rng.choice((-1, 1)) * rng.uniform(.5, 1.5)
                specs.append((p, (cos(aa), sin(aa), rng.uniform(-.15, .25)), rng.uniform(.11, .20), .030, rng.uniform(-.3, .3), j % 3))
    for j in range(260):
        z = rng.uniform(13.9, 15.25)
        r = .30 * (15.3 - z)
        a = rng.uniform(0, 2 * pi)
        specs.append(((r * cos(a), r * sin(a), z), (cos(a) * .4, sin(a) * .4, 1), rng.uniform(.10, .18), .028, 0, j % 3))
    trunk = branch_mesh('Fir prototype v3 / layered branching', segments, bpy.data.materials.get('Retreat / bark fissures and lichens') or old_bark())
    crown = foliage_mesh('Fir prototype v3 / dense needle sprays', specs, leafm)
    for i, (loc, scale, angle) in enumerate(placements):
        tree_instance('Retreat silver fir %02d' % i, (trunk, crown), tuple(loc), tuple(scale), angle)
    bpy.data.objects.remove(trunk, do_unlink=True)
    bpy.data.objects.remove(crown, do_unlink=True)
    return len(placements), len(specs)


def old_bark():
    for mat in bpy.data.materials:
        if 'bark' in mat.name.lower() and 'birch' not in mat.name.lower():
            return mat


def thin_water_material():
    """Single refracting surface: visible flow distortion without trapped-ray black rims."""
    mat = bpy.data.materials.new('Pool / thin falling water film')
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    refraction = nt.nodes.new('ShaderNodeBsdfRefraction')
    refraction.inputs['Color'].default_value = (.90, .97, .95, 1)
    refraction.inputs['Roughness'].default_value = .012
    refraction.inputs['IOR'].default_value = 1.16
    glossy = nt.nodes.new('ShaderNodeBsdfGlossy')
    glossy.inputs['Roughness'].default_value = .03
    fresnel = nt.nodes.new('ShaderNodeFresnel')
    fresnel.inputs['IOR'].default_value = 1.333
    coord = nt.nodes.new('ShaderNodeTexCoord')
    mapping = nt.nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1, 5, 1)
    nt.links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    # Striations travel down the sheet at roughly the 1.4 m/s outlet speed.
    mapping.inputs['Location'].driver_add('default_value', 2).driver.expression = 'frame*.058'
    wave = nt.nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Y'
    wave.inputs['Scale'].default_value = 9
    wave.inputs['Distortion'].default_value = 9
    wave.inputs['Detail'].default_value = 4
    wave.inputs['Detail Scale'].default_value = 2.5
    nt.links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .55
    bump.inputs['Distance'].default_value = .004
    nt.links.new(wave.outputs['Fac'], bump.inputs['Height'])
    for node in (glossy, refraction, fresnel):
        nt.links.new(bump.outputs['Normal'], node.inputs['Normal'])
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(fresnel.outputs['Fac'], mix.inputs['Fac'])
    nt.links.new(refraction.outputs['BSDF'], mix.inputs[1])
    nt.links.new(glossy.outputs['BSDF'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return mat


def spillway():
    sheet = bpy.data.objects['Pool / gravity accelerated spillway water sheet']
    for mod in list(sheet.modifiers):
        if mod.type == 'SOLIDIFY':
            sheet.modifiers.remove(mod)
    sheet.data.materials.clear()
    sheet.data.materials.append(thin_water_material())
    sheet.visible_shadow = False
    sheet['physics'] = sheet.get('physics', '') + ' v3: single thin-film surface, Fresnel reflection over clear transmission.'


def pillow(name, center, size, rotation, mat, dent=.0, seed=0):
    """Two sewn halves meeting at a piped seam, with fuller centre and pinched corners."""
    rng = random.Random(seed)
    L, W, H = size
    n = 49
    rot = Matrix.Rotation(rotation[2], 4, 'Z') @ Matrix.Rotation(rotation[1], 4, 'Y') @ Matrix.Rotation(rotation[0], 4, 'X')
    phase = [rng.uniform(0, 2 * pi) for _ in range(4)]

    def local(i, j, side):
        u, v = -1 + 2 * i / (n - 1), -1 + 2 * j / (n - 1)
        edge = max(0, (1 - abs(u) ** 3.2) * (1 - abs(v) ** 3.2))
        corner = abs(u * v) ** 2
        # Corners flare outward slightly as the stuffing pushes into them.
        x = u * L / 2 * (1 + .035 * corner)
        y = v * W / 2 * (1 + .05 * corner)
        h = H / 2 * edge ** .42
        wrinkle = .0045 * sin(9 * math.atan2(v, u) + phase[side]) * (1 - edge) ** .6 * edge ** .25
        if side == 0:
            h -= dent * H * math.exp(-((u + .1) ** 2 / .28 + v * v / .45))
            z = h + wrinkle
        else:
            z = -.72 * h + wrinkle
        return rot @ Vector((x, y, z)) + Vector(center)

    verts, faces, index = [], [], {}
    for side in (0, 1):
        for j in range(n):
            for i in range(n):
                perimeter = i in (0, n - 1) or j in (0, n - 1)
                if side == 1 and perimeter:
                    index[(1, i, j)] = index[(0, i, j)]
                    continue
                index[(side, i, j)] = len(verts)
                verts.append(tuple(local(i, j, side)))
    for j in range(n - 1):
        for i in range(n - 1):
            q = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            faces.append(tuple(index[(0,) + p] for p in q))
            faces.append(tuple(index[(1,) + p] for p in reversed(q)))
    obj = smooth(mesh(name, verts, faces, mat))
    sub = obj.modifiers.new('Soft sewn fill', 'SUBSURF')
    sub.levels = sub.render_levels = 1
    ring = [(i, 0) for i in range(n)] + [(n - 1, j) for j in range(1, n)] + \
           [(i, n - 1) for i in range(n - 2, -1, -1)] + [(0, j) for j in range(n - 2, 0, -1)]
    curve(name + ' piped seam', [verts[index[(0,) + p]] for p in ring[::2]], .0032, mat, True)
    return obj


def bedroom():
    collection('52 • Retreat / linen bedroom and dressing')
    old = [o for o in bpy.data.objects if o.name.startswith('Bedroom / relaxed linen pillow')]
    specs = [(tuple(o.location), tuple(o.rotation_euler), o.data.materials[0]) for o in old]
    for prefix in ('Bedroom / relaxed linen pillow', 'Bedroom / visible pillow piping'):
        remove_objects(prefix)
    for k, (loc, rot, mat) in enumerate(sorted(specs)):
        rx, ry, rz = rot
        # Pillows rest back against the headboard, fuller than the old bevelled boxes.
        pillow('Bedroom / sewn linen pillow', (loc[0], loc[1] + .01, loc[2] + .015), (.70, .47, .21),
               (rx + .22, ry, rz), mat, dent=.10 + .06 * k, seed=31 + k)
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.name.startswith('Bedside warm practical'):
            obj.data.energy = 15
    return len(specs)


def main():
    count, sprays = firs()
    spillway()
    pillows = bedroom()
    report = dict(firs=count, fir_sprays=sprays, pillows=pillows)
    print('POLISH_COMPLETE', report, flush=True)
    return report


if __name__ == '__main__':
    main()

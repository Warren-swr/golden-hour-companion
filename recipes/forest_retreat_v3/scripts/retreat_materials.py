"""Tactile cedar, mineral, woven and optical materials for the revised cabin."""
from pathlib import Path

import bpy

from materials import build as base_materials, cloth, pbr, rgb, wood

OUT = Path(__file__).resolve().parent.parent


def scanned(name, asset, scale=1, relief=.008, tint=None):
    mat = pbr(name, '#FFFFFF', .6)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bs = nodes.get('Principled BSDF')
    coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeVectorMath')
    mapping.operation = 'SCALE'
    mapping.inputs['Scale'].default_value = scale
    links.new(coord.outputs['Object'], mapping.inputs[0])
    for channel, suffix in [('color', 'diff'), ('rough', 'rough'), ('height', 'disp')]:
        tex = nodes.new('ShaderNodeTexImage')
        path = OUT / 'assets' / 'textures' / (asset + '_' + suffix + '_2k.jpg')
        tex.image = bpy.data.images.load(str(path), check_existing=True)
        tex.image.pack()
        tex.projection = 'BOX'
        tex.projection_blend = .28
        links.new(mapping.outputs[0], tex.inputs['Vector'])
        if channel != 'color':
            tex.image.colorspace_settings.name = 'Non-Color'
        if channel == 'color':
            source = tex.outputs['Color']
            if tint:
                mix = nodes.new('ShaderNodeMixRGB')
                mix.blend_type = 'MULTIPLY'
                mix.inputs[0].default_value = 1
                mix.inputs[2].default_value = rgb(tint)
                links.new(source, mix.inputs[1])
                source = mix.outputs[0]
            links.new(source, bs.inputs['Base Color'])
        elif channel == 'rough':
            links.new(tex.outputs['Color'], bs.inputs['Roughness'])
        else:
            bump = nodes.new('ShaderNodeBump')
            bump.inputs['Distance'].default_value = relief
            bump.inputs['Strength'].default_value = .52
            links.new(tex.outputs['Color'], bump.inputs['Height'])
            links.new(bump.outputs[0], bs.inputs['Normal'])
    return mat


def build():
    m = base_materials()
    m['cedar'] = scanned('Retreat / weathered cedar grain', 'wood_planks', .65, .002, '#8B765E')
    m['deck'] = scanned('Retreat / silvered teak decking', 'wood_planks', .44, .0025, '#C1A786')
    m['rock'] = scanned('Retreat / irregular granite and mica', 'rock_boulder_dry', .78, .032)
    m['ground'] = scanned('Retreat / scanned forest duff', 'forest_ground_04', .38, .025, '#767D60')
    nodes, links = m['ground'].node_tree.nodes, m['ground'].node_tree.links
    bs = nodes.get('Principled BSDF')
    base_color = bs.inputs['Base Color'].links[0].from_socket
    coord = nodes.new('ShaderNodeTexCoord')
    patch = nodes.new('ShaderNodeTexNoise')
    patch.inputs['Scale'].default_value = .83
    patch.inputs['Detail'].default_value = 4
    links.new(coord.outputs['Object'], patch.inputs['Vector'])
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .25
    ramp.color_ramp.elements[0].color = (.12, .12, .12, 1)
    ramp.color_ramp.elements[1].position = .68
    ramp.color_ramp.elements[1].color = (.78, .78, .78, 1)
    links.new(patch.outputs['Fac'], ramp.inputs[0])
    mix = nodes.new('ShaderNodeMixRGB')
    links.new(ramp.outputs['Color'], mix.inputs[0])
    links.new(base_color, mix.inputs[1])
    mix.inputs[2].default_value = rgb('#414D28')
    links.new(mix.outputs[0], bs.inputs['Base Color'])
    m['bark_scan'] = scanned('Retreat / bark fissures and lichens', 'bark_brown_02', 1.1, .035)
    m['charred'] = wood('Retreat / charred cedar battens', '#292A25')
    m['teak'] = wood('Retreat / hand-oiled teak', '#987449')
    m['rim'] = pbr('Retreat / ivory travertine with pores', '#C9BDA1', .64, noise=.28, bump=.004, scale=43)
    m['copper'] = pbr('Retreat / aged patinated bronze', '#927957', .3, .85, noise=.38, bump=.0006, scale=47)
    m['steel'] = pbr('Retreat / brushed pool stainless', '#B5C0C1', .22, .96, noise=.07, bump=.00006, scale=140)
    m['sage_cloth'] = cloth('Retreat / softly creased sage linen', '#768071')
    m['ivory_cloth'] = cloth('Retreat / washed ivory linen', '#DAD1BB')
    m['rust_cloth'] = cloth('Retreat / tobacco wool', '#8E6245')
    m['tile'] = pbr('Retreat / celadon glazed pool tesserae', '#7EA39A', .24, noise=.16, bump=.0003, scale=150)
    m['tile_variants'] = [pbr('Retreat / handmade zellige %02d' % i, color, .24 + .035 * i,
                             noise=.10, bump=.0006, scale=80)
                          for i, color in enumerate(('#8E9984', '#A2AB95', '#ABB29D', '#929B87', '#BBC1AC'))]
    m['lemon'] = pbr('Retreat / lemon dimpled peel', '#D4A32E', .42, noise=.20, bump=.0009, scale=210)
    m['lemon_flesh'] = pbr('Retreat / translucent lemon flesh', '#E8C877', .28, noise=.15, bump=.0003, scale=140)
    m['lemon_flesh'].node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value = .14
    m['wax'] = pbr('Retreat / beeswax candle', '#D5BD81', .5)
    m['soil'] = pbr('Retreat / dark potting humus', '#382E20', .97, noise=.7, bump=.008, scale=65)
    m['lavender'] = pbr('Retreat / dried lavender florets', '#887B8E', .82, noise=.3, bump=.0003, scale=90)
    m['bread'] = pbr('Retreat / baked sourdough crust', '#A76F39', .88, noise=.38, bump=.002, scale=85)
    m['water'] = pbr('Retreat / optical pool water IOR 1.333', '#FFFFFF', .025)
    nodes, links = m['water'].node_tree.nodes, m['water'].node_tree.links
    bs = nodes.get('Principled BSDF')
    bs.inputs['Transmission Weight'].default_value = 1
    bs.inputs['IOR'].default_value = 1.333
    absorb = nodes.new('ShaderNodeVolumeAbsorption')
    absorb.inputs['Color'].default_value = (.38, .78, .72, 1)
    absorb.inputs['Density'].default_value = .075
    links.new(absorb.outputs[0], nodes.get('Material Output').inputs['Volume'])
    # Actual geometry supplies the moving gravity waves. This adds only sub-mm capillary roughness.
    tex = nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 145
    tex.inputs['Detail'].default_value = 2
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = .00012
    bump.inputs['Strength'].default_value = .18
    links.new(tex.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs[0], bs.inputs['Normal'])
    m['bottle'] = pbr('Retreat / olive glass bottle', '#87916B', .1)
    bs = m['bottle'].node_tree.nodes.get('Principled BSDF')
    bs.inputs['Transmission Weight'].default_value = .88
    bs.inputs['IOR'].default_value = 1.47
    m['ember'] = pbr('Retreat / stove ember', '#552515', .8)
    bs = m['ember'].node_tree.nodes.get('Principled BSDF')
    bs.inputs['Emission Color'].default_value = rgb('#CF521B')
    bs.inputs['Emission Strength'].default_value = 1.1
    return m

"""Analytic PBR materials; no photographic assets or image-texture nodes."""
import bpy


def rgb(hex_value):
    h = hex_value.lstrip('#')
    c = [int(h[i:i+2], 16)/255 for i in (0,2,4)]
    return tuple(x/12.92 if x <= .04045 else ((x+.055)/1.055)**2.4 for x in c) + (1,)


def pbr(name, color, roughness=.5, metal=0, noise=0, bump=.01, scale=80):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    n, l = mat.node_tree.nodes, mat.node_tree.links
    bs = n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = rgb(color)
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metal
    if noise:
        coord = n.new('ShaderNodeTexCoord')
        tex = n.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = scale
        tex.inputs['Detail'].default_value = 3
        tex.inputs['Roughness'].default_value = .72
        l.new(coord.outputs['Object'], tex.inputs['Vector'])
        ramp = n.new('ShaderNodeValToRGB')
        col = rgb(color)
        ramp.color_ramp.elements[0].position = .1
        ramp.color_ramp.elements[0].color = tuple(x*(1-noise) for x in col[:3])+(1,)
        ramp.color_ramp.elements[1].position = .9
        ramp.color_ramp.elements[1].color = tuple(min(1,x*(1+noise)) for x in col[:3])+(1,)
        l.new(tex.outputs['Fac'], ramp.inputs[0])
        l.new(ramp.outputs['Color'], bs.inputs['Base Color'])
        bn = n.new('ShaderNodeBump')
        bn.inputs['Strength'].default_value = .32
        bn.inputs['Distance'].default_value = bump
        l.new(tex.outputs['Fac'], bn.inputs['Height'])
        l.new(bn.outputs['Normal'], bs.inputs['Normal'])
    return mat


def cloth(name, color, boucle=False):
    mat = pbr(name, color, .86, noise=.18, bump=.0008, scale=420 if boucle else 180)
    n,l = mat.node_tree.nodes,mat.node_tree.links
    bs=n.get('Principled BSDF')
    bs.inputs['Sheen Weight'].default_value=.32
    bs.inputs['Sheen Roughness'].default_value=.65
    coord=n.new('ShaderNodeTexCoord')
    waves=[]
    for direction in ('X','Z'):
        wave=n.new('ShaderNodeTexWave')
        wave.bands_direction=direction
        wave.inputs['Scale'].default_value=520
        wave.inputs['Distortion'].default_value=2.5
        wave.inputs['Detail Scale'].default_value=3
        l.new(coord.outputs['Object'],wave.inputs['Vector'])
        waves.append(wave)
    mix=n.new('ShaderNodeMath')
    mix.operation='MULTIPLY'
    l.new(waves[0].outputs['Fac'],mix.inputs[0])
    l.new(waves[1].outputs['Fac'],mix.inputs[1])
    bump=n.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value=.00025
    bump.inputs['Strength'].default_value=.4
    l.new(bs.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
    l.new(mix.outputs[0],bump.inputs['Height'])
    l.new(bump.outputs[0],bs.inputs['Normal'])
    return mat


def wood(name, color):
    mat=pbr(name,color,.4,noise=.4,bump=.001,scale=4)
    n,l=mat.node_tree.nodes,mat.node_tree.links
    tex=next(n for n in n if n.type=='TEX_NOISE')
    coord=n.new('ShaderNodeTexCoord')
    mapping=n.new('ShaderNodeVectorMath')
    mapping.operation='MULTIPLY'
    mapping.inputs[1].default_value=(3,65,4)
    l.new(coord.outputs['Generated'],mapping.inputs[0])
    l.new(mapping.outputs[0],tex.inputs[0])
    return mat


def build():
    m={
        'wall':pbr('Warm lime plaster / fine mineral grain','#C7C2B4',.89,noise=.065,bump=.0011,scale=135),
        'exterior':pbr('Ivory limewash / trowelled exterior','#DDD1B9',.83,noise=.11,bump=.006,scale=50),
        'stone':pbr('Honed cream limestone','#B6AB92',.61,noise=.19,bump=.003,scale=16),
        'grout':pbr('Warm limestone grout','#8E8676',.9),
        'oak':wood('Natural quarter-sawn European oak','#A37C4D'),
        'walnut':wood('Oiled walnut end grain','#5B3B27'),
        'frame':pbr('Painted window joinery / warm putty','#9D947E',.4,noise=.045,bump=.0003,scale=60),
        'bronze':pbr('Brushed champagne bronze','#96734A',.28,.72,noise=.08,bump=.0003,scale=190),
        'dark':pbr('Blackened metal','#292922',.38,.75),
        'switch':pbr('Ivory bakelite','#CABB9C',.37,noise=.03,bump=.0001,scale=150),
        'linen':cloth('Oatmeal linen / warp and weft','#B5A78F'),
        'cream':cloth('Washed natural linen','#D7C9B0'),
        'boucle':cloth('Cinnamon teddy boucle backing','#976947',True),
        'ochre':cloth('Saffron cotton velvet flower centre','#BE6808',True),
        'terra':pbr('Hand-thrown terracotta','#9B5238',.81,noise=.16,bump=.0018,scale=110),
        'ceramic':pbr('Speckled oatmeal stoneware','#CAC4AC',.3,noise=.08,bump=.0007,scale=240),
        'sage':pbr('Sage celadon glaze','#768271',.24,noise=.09,bump=.0004,scale=120),
        'leaf':pbr('Olive leaf upper cuticle','#566443',.52,noise=.25,bump=.0002,scale=45),
        'leaflight':pbr('Olive leaf silver underside','#8C9167',.6,noise=.17,bump=.0002,scale=90),
        'bark':pbr('Gnarled olive bark','#5D5140',.91,noise=.4,bump=.01,scale=9),
        'earth':pbr('Dry loam','#716149',.94,noise=.5,bump=.035,scale=9),
        'grass':pbr('Late summer grass','#7A8053',.9,noise=.3,bump=.003,scale=18),
        'paper':pbr('Uncoated warm paper','#DDD3B6',.9,noise=.08,bump=.0002,scale=160),
        'coffee':pbr('Dark amber tea','#462918',.16),
        'white':pbr('Porcelain enamel','#E3DDD0',.22),
        'roof':pbr('Aged standing-seam zinc','#585A50',.52,.55,noise=.08,bump=.001,scale=40),
    }
    m['glass']=pbr('Clear architectural glass','#F4F5EC',.035)
    bs=m['glass'].node_tree.nodes.get('Principled BSDF')
    bs.inputs['Transmission Weight'].default_value=1
    bs.inputs['IOR'].default_value=1.45
    for i,color in enumerate(('#936B4C','#A27656','#AD7C58','#B58A66','#896043')):
        mat=pbr('Cinnamon wool strand '+str(i),color,.83,noise=.08,bump=.00007,scale=120)
        mat.node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.30
        m['pile'+str(i)]=mat
    m['sheer']=cloth('Upper window natural linen solar veil','#DDD2B9')
    n,l=m['sheer'].node_tree.nodes,m['sheer'].node_tree.links
    bs=n.get('Principled BSDF')
    transparent=n.new('ShaderNodeBsdfTransparent')
    mix=n.new('ShaderNodeMixShader')
    mix.inputs[0].default_value=.50
    l.new(bs.outputs[0],mix.inputs[1])
    l.new(transparent.outputs[0],mix.inputs[2])
    l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
    m['glow']=pbr('Opal lamp diffuser','#F3D8A0',.42)
    bs=m['glow'].node_tree.nodes.get('Principled BSDF')
    bs.inputs['Emission Color'].default_value=rgb('#FFE1AC')
    bs.inputs['Emission Strength'].default_value=.6
    m['lamp_linen']=cloth('Translucent woven lampshade','#DDD2B9')
    n,l=m['lamp_linen'].node_tree.nodes,m['lamp_linen'].node_tree.links
    bs=n.get('Principled BSDF')
    translucent=n.new('ShaderNodeBsdfTranslucent')
    translucent.inputs['Color'].default_value=rgb('#DDD2B9')
    mix=n.new('ShaderNodeMixShader')
    mix.inputs[0].default_value=.38
    l.new(bs.outputs[0],mix.inputs[1])
    l.new(translucent.outputs[0],mix.inputs[2])
    l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
    return m

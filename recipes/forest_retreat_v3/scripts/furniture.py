"""Living, kitchen, sleeping and bathing furnishings, all editable geometry."""
from common import *


def cup(name, x,y,z, m, mat=None, r=.046):
    mat=mat or m['ceramic']
    profile=[(0,0),(r*.8,0),(r,.015),(r*1.03,.093),(r*.98,.100),
             (r*.84,.097),(r*.79,.018),(0,.014)]
    lathe(name+' hollow ceramic body',profile,(x,y,z),mat)
    handle=torus(name+' open loop handle',(x+r*1.10,y,z+.057),r*.57,.0075,mat,(pi/2,0,0))
    cylinder(name+' tea meniscus',(x,y,z+.079),r*.82,.001,m['coffee'],64)
    lathe(name+' matching saucer',[(0,0),(.054,0),(.074,.009),(.077,.015),(.069,.019),(.04,.006),(0,.006)],(x,y,z-.005),mat)


def book(name,loc,size,m,color='sage',rotation=0):
    cover=cube(name+' cover',loc,size,m[color],.002)
    cover.rotation_euler.z=rotation
    pages=cube(name+' paper block',(loc[0],loc[1],loc[2]+.006),(size[0]-.01,size[1]-.009,size[2]-.013),m['paper'],.001)
    pages.rotation_euler.z=rotation


def cushion(name,loc,size,m,mat='cream'):
    return cube(name,loc,size,m[mat],min(size)*.38)


def duvet(m):
    verts,faces=[],[]
    nx,ny=91,77
    for j in range(ny):
        y=-2.91+j*1.83/(ny-1)
        for i in range(nx):
            x=4.02+i*2.0/(nx-1)
            side=max(0,abs(x-5.02)-.84)/.16
            foot=max(0,-y-2.69)/.22
            z=.695-.24*side**1.3-.20*foot**1.35
            z+=.009*sin(x*18+y*9)+.006*sin(x*37-y*14)
            z+=.014*sin(y*44+cos(x*8))*math.exp(-((y+1.13)/.16)**2)
            verts.append((x,y,z))
    for j in range(ny-1):
        for i in range(nx-1):
            a=j*nx+i
            faces.append((a,a+1,a+1+nx,a+nx))
    obj=smooth(mesh('Soft draped linen duvet / sewn fabric shell',verts,faces,m['linen']))
    mod=obj.modifiers.new('Linen hem thickness','SOLIDIFY')
    mod.thickness=.007
    curve('Duvet turned foot hem',[(4.02+i*2/(nx-1),-2.908,verts[i][2]+.003) for i in range(nx)],.004,m['linen'])


def living(m):
    collection('20 • Living room / linen and oak')
    cube('Woven undyed wool rug',(-.85,-2.27,.047),(2.75,2.90,.02),m['cream'],.015)
    for i in range(110):
        x=-2.20+i*.0245
        curve('Hand knotted rug fringe',[(x,-3.72,.051),(x+.005,-3.79,.048),(x+.006,-3.83,.042)],.0019,m['cream'])
    cube('Walnut sofa underframe',(-2.82,-1.84,.24),(1.08,2.02,.20),m['walnut'],.028)
    cushion('Linen sofa seat',(-2.69,-1.84,.415),(.88,1.90,.24),m)
    cushion('Soft low sofa back',(-3.18,-1.84,.72),(.25,2.12,.65),m)
    for y in (-2.86,-.83):
        cushion('Sofa padded arm',(-2.79,y,.62),(1.02,.20,.47),m)
    p=cushion('Loose flax back pillow',(-2.96,-2.23,.76),(.20,.55,.54),m,'linen')
    p.rotation_euler.y=-.16
    p=cushion('Loose sage cushion',(-2.9,-1.41,.72),(.22,.51,.43),m,'linen')
    p.rotation_euler.x=.14
    for x in (-3.14,-2.42):
        for y in (-2.64,-1.04):
            cylinder('Sofa tapered foot',(x,y,.15),.031,.27,m['walnut'])
    # Low elliptical coffee table with fine edge and offset stacked books.
    top=cylinder('Solid walnut coffee table',(-.60,-2.25,.44),.58,.065,m['walnut'],96)
    top.scale=(1.12,.79,1)
    for a in (0,2*pi/3,4*pi/3):
        beam('Coffee table angled leg',(-.6+.37*cos(a),-2.25+.27*sin(a),.06),
             (-.6+.26*cos(a),-2.25+.22*sin(a),.415),.025,m['walnut'])
    book('Quiet architecture',(-.66,-2.27,.494),(.26,.19,.03),m,'paper',.16)
    book('Botanical notebook',(-.65,-2.26,.525),(.22,.15,.025),m,'sage',.08)
    cup('Small afternoon tea',-.38,-2.38,.478,m,m['sage'])
    # The table, pot and mug are the actual shadow-casting reference objects.
    cube('Window-side oak herb console',(-1.625,-2.53,1.00),(1.20,.37,.067),m['oak'],.014)
    cube('Console shallow storage apron',(-1.625,-2.36,.89),(1.15,.035,.17),m['oak'],.01)
    cylinder('Console stable weighted foot',(-1.625,-2.53,.082),.225,.085,m['dark'])
    beam('Console central pedestal',(-1.625,-2.53,.10),(-1.625,-2.53,.970),.034,m['walnut'])
    cup('Reference silhouette mug',-1.85,-2.56,1.038,m,m['sage'],.060)
    cube('Oak window tea tray',(-.45,-5.13,.727),(.56,.30,.025),m['oak'],.014)
    cup('Window tea cup',-.45,-5.13,.745,m,m['ceramic'],.053)
    book('Window-side poetry',(-.14,-5.16,.75),(.21,.15,.024),m,'sage',-.08)
    # Reading floor lamp, task light kept subtle against the afternoon sun.
    cylinder('Reading lamp weighted foot',(-1.69,-.56,.06),.19,.07,m['dark'])
    beam('Reading lamp upright',(-1.69,-.56,.06),(-1.69,-.56,1.75),.014,m['bronze'])
    beam('Reading lamp swept neck',(-1.69,-.56,1.75),(-1.40,-.56,1.81),.013,m['bronze'])
    lathe('Small linen lamp shade',[(.145,0),(.15,.02),(.10,.24),(.087,.245)],(-1.40,-.56,1.53),m['cream'])
    bulb=sphere('Lamp opal bulb',(-1.40,-.56,1.60),(.042,.042,.06),m['glow'])
    bulb.visible_shadow=False
    # Framed abstract textile study, modeled rather than a texture.
    cube('Oak artwork frame',(-2.48,-.032,2.02),(.62,.046,.73),m['oak'],.008)
    cube('Linen artwork field',(-2.48,-.059,2.02),(.56,.013,.67),m['cream'],.001)
    for i in range(5):
        curve('Embossed woven artwork arc',[(-2.7+.40*j/70,-.073,1.89+i*.049+.13*sin(j*pi/70)) for j in range(71)],.009,m['terra'])


def kitchen(m):
    collection('21 • Kitchen / functioning spatial layout')
    for x in (1.68,2.26,2.84):
        for side in (-1,1):
            cube('Oak cabinet side wall',(x+side*.274,-.39,.49),(.018,.67,.88),m['oak'],.005)
        cube('Oak cabinet back wall',(x,-.064,.49),(.547,.018,.88),m['oak'],.005)
        cube('Oak cabinet bottom shelf',(x,-.39,.061),(.547,.67,.022),m['oak'],.004)
        for z,h in ((.78,.27),(.486,.30),(.194,.272)):
            cube('Cabinet drawer with shadow reveal',(x,-.736,z),(.552,.025,h),m['oak'],.004)
            cube('Inset bronze pull',(x,-.756,z+.047),(.19,.019,.011),m['bronze'],.004)
    # Four real stone sections surround the sink opening; no hidden overlay basin.
    for name,loc,size in [
        ('main',(1.97,-.414,.966),(1.24,.79,.055)),
        ('right',(3.13,-.414,.966),(.08,.79,.055)),
        ('front',(2.84,-.715,.966),(.50,.188,.055)),
        ('back',(2.84,-.115,.966),(.50,.192,.055)),
    ]:
        cube('Limestone kitchen countertop '+name,loc,size,m['stone'],.007)
    cube('Stone backsplash',(2.26,-.021,1.18),(1.82,.034,.39),m['stone'],.006)
    cube('Sink porcelain base',(2.84,-.42,.785),(.486,.384,.022),m['white'],.015)
    for x in (2.598,3.082):
        cube('Sink porcelain side',(x,-.42,.880),(.016,.398,.202),m['white'],.007)
    for y in (-.612,-.228):
        cube('Sink porcelain end',(2.84,y,.880),(.486,.016,.202),m['white'],.007)
    cylinder('Sink stainless drain',(2.84,-.42,.799),.026,.005,m['bronze'])
    cylinder('Sink drain inset',(2.84,-.42,.802),.012,.002,m['dark'])
    torus('Sink drain trim',(2.84,-.42,.804),.022,.0015,m['bronze'])
    points=[(2.84,-.145,1.00),(2.84,-.145,1.25),(2.84,-.18,1.30),(2.84,-.27,1.30),(2.84,-.32,1.25)]
    curve('Gooseneck bronze mixer',points,.014,m['bronze'])
    cube('Black glass induction hob',(1.69,-.43,1.00),(.46,.47,.014),m['dark'],.01)
    for y in (-.32,-.55):
        torus('Induction ring',(1.69,y,1.009),.079,.0015,m['frame'])
    cube('Compact oven bronze surround',(1.68,-.756,.50),(.515,.035,.44),m['bronze'],.01)
    cube('Compact oven dark glazed door',(1.68,-.779,.50),(.465,.022,.38),m['dark'],.012)
    cube('Oven horizontal bronze handle',(1.68,-.811,.651),(.36,.026,.019),m['bronze'],.007)
    for x in (1.57,1.79):
        knob=cylinder('Oven tactile control dial',(x,-.766,.776),.015,.013,m['bronze'],32)
        knob.rotation_euler.x=pi/2
    lathe('Small cooking pot',[(0,0),(.075,0),(.089,.02),(.093,.10),(.085,.105),(.075,.017),(0,.015)],(1.69,-.33,1.012),m['dark'])
    for z in (1.58,2.14):
        cube('Open oak kitchen shelf',(2.23,-.18,z),(1.84,.34,.04),m['oak'],.007)
    for i in range(7):
        x=1.49+i*.17
        lathe('Stacked handmade stoneware',[(0,0),(.051,0),(.088,.04),(.09,.054),(.080,.059),(.044,.014),(0,.014)],(x,-.19,1.61),m['ceramic'])
    for x,sz in [(1.65,.18),(2.12,.25),(2.72,.20)]:
        lathe('Kitchen storage jar',[(0,0),(.077,0),(.083,.03),(.08,sz-.03),(.06,sz),(.054,sz),(.05,.03),(0,.03)],(x,-.18,2.16),m['ceramic'])
        cylinder('Storage jar oak lid',(x,-.18,2.16+sz),.067,.018,m['oak'])
    cube('Oak cutting board',(2.24,-.4,1.002),(.24,.33,.022),m['oak'],.03)
    for i in range(3):
        sphere('Ripe citrus',(2.23+i*.045,-.4+i*.02,1.065),(.042,.042,.043),m['ochre'],24,16)


def suites(m):
    collection('22 • Bedroom / complete private suite')
    cube('Oak bed frame',(5.02,-1.68,.27),(1.87,2.28,.35),m['oak'],.036)
    cushion('Thick linen mattress',(5.02,-1.66,.48),(1.81,2.16,.26),m)
    cube('Upholstered bed headboard',(5.02,-.48,.84),(1.98,.17,1.02),m['linen'],.07)
    for x in (4.58,5.46):
        p=cushion('Soft bedroom pillow',(x,-.83,.68),(.73,.45,.16),m)
        p.rotation_euler.z=.035 if x<5 else -.04
    duvet(m)
    for x in (3.89,6.17):
        cube('Bedside oak chest',(x,-.72,.36),(.45,.48,.66),m['oak'],.018)
        lathe('Bedside ceramic lamp',[(0,0),(.085,0),(.10,.06),(.075,.20),(.04,.23)],(x,-.72,.70),m['ceramic'])
        lathe('Bedside linen shade',[(.14,0),(.15,.025),(.095,.21),(.09,.215)],(x,-.72,.92),m['lamp_linen'])
        bulb=sphere('Bedside opal bulb',(x,-.72,1.015),(.027,.027,.038),m['glow'],24,16)
        bulb.visible_shadow=False
    cube('Bedroom woven rug',(5.0,-1.85,.048),(2.65,2.77,.022),m['cream'],.008)
    for x in (5.96,6.47):
        cube('Full height wardrobe',(x,-3.13,1.37),(.50,.46,2.68),m['oak'],.009)
        cube('Wardrobe recessed handle',(x-.15,-2.892,1.45),(.015,.02,.38),m['bronze'],.005)
    collection('23 • Bathroom / stone and porcelain')
    cube('Stone vanity unit',(4.08,-4.85,.47),(1.05,.50,.86),m['oak'],.014)
    cube('Vanity limestone slab',(4.08,-4.83,.92),(1.12,.60,.05),m['stone'],.012)
    lathe('Handmade wash basin',[(0,0),(.12,0),(.21,.11),(.21,.14),(.20,.147),(.17,.10),(.10,.016),(0,.016)],(4.08,-4.80,.95),m['white'])
    curve('Bath brass faucet',[(4.08,-5.01,.95),(4.08,-5.01,1.22),(4.08,-4.90,1.22)],.013,m['bronze'])
    # Full-volume freestanding tub, modeled with a hollow inner shell.
    tub=lathe('Freestanding stone bathtub',[(.02,0),(.39,0),(.48,.12),(.50,.50),(.485,.57),(.45,.575),(.42,.51),(.33,.14),(.02,.12)],(6.06,-4.34,.07),m['white'],96)
    tub.scale=(1.48,.73,1)
    cube('Folded bath towel',(5.76,-4.34,.69),(.22,.68,.035),m['cream'],.016)
    curve('Floor mounted bath mixer',[(6.89,-4.08,.04),(6.89,-4.08,.91),(6.60,-4.08,.91)],.017,m['bronze'])
    cube('Bath mirror bronze frame',(4.02,-3.52,1.81),(.90,.04,.91),m['bronze'],.16)
    mirror=bpy.data.materials.new('Polished silver bathroom mirror')
    mirror.use_nodes=True
    bs=mirror.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Metallic'].default_value=1
    bs.inputs['Roughness'].default_value=.03
    cube('Bath mirror',(4.02,-3.548,1.81),(.864,.013,.874),mirror,.14)
    sphere('Compact porcelain toilet',(5.16,-3.90,.32),(.21,.30,.28),m['white'])
    torus('Toilet seat rim',(5.16,-3.94,.57),.165,.031,m['white'])
    cube('Concealed toilet cistern',(5.16,-3.58,.58),(.37,.17,.90),m['white'],.04)


def build(m):
    living(m)
    kitchen(m)
    suites(m)

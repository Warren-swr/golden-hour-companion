"""Complete connected single-storey courtyard home."""
from common import *


def partition_with_door(name, x, y0, y1, door0, door1, m):
    for lo,hi in [(y0,door0),(door1,y1)]:
        if hi>lo:
            cube(name+' wall',(x,(lo+hi)/2,1.5),(.16,hi-lo,3),m['wall'],.015)
    cube(name+' lintel',(x,(door0+door1)/2,2.67),(.16,door1-door0,.66),m['wall'],.012)
    for y in (door0,door1):
        cube(name+' oak jamb',(x,y,1.18),(.20,.055,2.36),m['oak'],.006)
    cube(name+' oak head',(x,(door0+door1)/2,2.345),(.20,door1-door0,.07),m['oak'],.006)


def window_x(name,x,y0,y1,z0,z1,m):
    for y in (y0,y1):
        cube(name+' jamb',(x,y,(z0+z1)/2),(.18,.085,z1-z0),m['frame'],.009)
    for z in (z0,z1):
        cube(name+' rail',(x,(y0+y1)/2,z),(.18,y1-y0,.085),m['frame'],.009)
    cube(name+' clear double pane',(x,(y0+y1)/2,(z0+z1)/2),(.009,y1-y0-.08,z1-z0-.08),m['glass'],.001)


def build(m):
    collection('10 • Architecture / connected shell')
    cube('Continuous slab foundation',(1.8,-2.6,-.16),(10.85,5.75,.32),m['stone'],.04)
    cube('Floor grout bed',(1.78,-2.59,-.012),(10.48,5.32,.04),m['grout'])
    # Individual stone flags, with true recessed joints and slight tone variation.
    for ix in range(15):
        for iy in range(8):
            x=-3.43+ix*.715
            y=-5.12+iy*.715
            cube('Limestone flag %02d %02d'%(ix,iy),(x,y,.016),(.711,.711,.038),m['stone'],.004)
    cube('Reference lime plaster wall',(1.75,.12,1.56),(10.9,.24,3.12),m['wall'],.018)
    # West elevation: a picture window opening and solid piers.
    for ya,yb,za,zb in [(-5.3,-4.35,0,3.1),(-1.1,.12,0,3.1),(-4.35,-1.1,0,.58),(-4.35,-1.1,2.72,3.1)]:
        cube('West masonry pier',(-3.55,(ya+yb)/2,(za+zb)/2),(.24,yb-ya,zb-za),m['exterior'],.015)
    window_x('West casement',-3.55,-4.35,-1.1,.58,2.72,m)
    # South window supplies the actual reference grid shadows.
    for xa,xb,za,zb in [(-3.65,-3.10,0,3.1),(.86,1.08,0,3.1),(-3.10,.86,0,.67),(-3.10,.86,2.99,3.14),
                        (3.08,7.20,0,.85),(3.08,7.20,2.62,3.14),(6.95,7.20,.85,2.62)]:
        cube('South plaster opening surround',((xa+xb)/2,-5.30,(za+zb)/2),(xb-xa,.23,zb-za),m['exterior'],.012)
    for x in (-3.10,.86):
        cube('Deep oak window jamb',(x,-5.285,1.835),(.11,.20,2.33),m['frame'],.007)
    for z in (.70,2.98):
        cube('South window perimeter rail',(-1.12,-5.285,z),(4.03,.20,.085),m['frame'],.007)
    cube('Reference broad vertical mullion',(-1.505,-5.285,2.41),(.17,.21,1.18),m['frame'],.006)
    cube('Reference broad transom',(-1.12,-5.285,2.505),(4.02,.21,.235),m['frame'],.007)
    cube('Slender lower glazing bar',(-1.12,-5.285,2.185),(4.02,.095,.045),m['frame'],.004)
    cube('Lower solid oak solar baffle',(-1.12,-5.385,2.015),(4.02,.15,.35),m['oak'],.008)
    cube('Lower casement offset stile',(-1.66,-5.30,1.28),(.095,.16,1.08),m['frame'],.006)
    # Thin solid glass with caustic-free straight-through shadow transport.
    for xa,xb in [(-3.05,-1.595),(-1.415,.81)]:
        for za,zb in [(.745,2.155),(2.215,2.385),(2.625,2.935)]:
            pane=cube('South true glass pane',((xa+xb)/2,-5.30,(za+zb)/2),(xb-xa,.006,zb-za),m['glass'])
            pane.visible_shadow=False
    cube('Deep limestone window sill',(-1.12,-5.30,.674),(4.15,.48,.075),m['stone'],.016)
    # An open, physically traversable 2-metre garden door.
    for x in (1.08,3.08):
        cube('Garden door solid jamb',(x,-5.30,1.49),(.11,.24,2.98),m['oak'],.008)
    cube('Garden door header',(2.08,-5.30,2.98),(2.1,.24,.10),m['oak'],.008)
    cube('Pocket garden door',(3.01,-4.75,1.43),(.075,1.08,2.81),m['oak'],.015)
    cube('Pocket door glazed light',(2.965,-4.75,1.55),(.012,.89,2.2),m['glass'],.003)
    # East suite and independent bathroom, reached through the internal corridor.
    partition_with_door('Bedroom',3.34,-3.43,.0,-2.97,-1.92,m)
    partition_with_door('Bathroom',3.34,-5.18,-3.43,-4.78,-3.8,m)
    cube('Suite dividing wall',(5.23,-3.43,1.52),(3.76,.16,3.04),m['wall'],.015)
    for ya,yb,za,zb in [(-5.3,-4.85,0,3.1),(-3.75,-2.8,0,3.1),(-.8,.12,0,3.1),
                        (-4.85,-3.75,0,1.40),(-4.85,-3.75,2.5,3.1),(-2.8,-.8,0,.65),(-2.8,-.8,2.62,3.1)]:
        cube('East masonry',(7.08,(ya+yb)/2,(za+zb)/2),(.24,yb-ya,zb-za),m['exterior'],.014)
    window_x('Bedroom east window',7.08,-2.8,-.8,.65,2.62,m)
    window_x('Bathroom clerestory',7.08,-4.85,-3.75,1.4,2.5,m)
    cube('South bath clear glazing',(5.02,-5.30,1.74),(3.82,.008,1.70),m['glass'],.002)
    for x in (3.1,4.5,5.9,6.96):
        cube('South bath window frame',(x,-5.30,1.735),(.075,.14,1.78),m['frame'],.006)
    collection('11 • Roof and joinery')
    cube('Plastered ceiling',(1.76,-2.60,3.09),(10.78,5.54,.14),m['wall'],.015)
    cube('Roof insulation fascia',(1.76,-2.58,3.205),(11.02,5.92,.15),m['exterior'],.018)
    cube('Weatherproof zinc roof',(1.76,-2.58,3.296),(11.12,6.02,.04),m['roof'],.01)
    for i in range(26):
        cube('Standing roof seam',(-3.72+i*.44,-2.58,3.322),(.018,5.98,.022),m['roof'],.006)
    for x in (-3.71,7.25):
        cube('Zinc gutter',(x,-2.55,3.18),(.09,6.1,.10),m['roof'],.026)
        for y in (-5.39,.30):
            beam('Rainwater downpipe',(x,y,.06),(x,y,3.18),.035,m['roof'])
    for x in (-3.32,1.10,3.17,6.88):
        cube('Exposed solid oak ceiling beam',(x,-2.56,2.97),(.12,5.28,.16),m['oak'],.014)
    for i in range(47):
        cube('Fine oak ceiling batten',(-3.3+i*.132,-2.57,3.00),(.032,5.24,.045),m['oak'],.005)
    for x0,x1 in [(-3.42,3.25),(3.44,6.94)]:
        cube('Rear oak skirting',((x0+x1)/2,-.018,.073),(x1-x0,.031,.12),m['oak'],.004)
    cube('Bedroom oak skirting',(6.94,-1.68,.073),(.025,3.29,.12),m['oak'],.004)
    # Deep front canopy, with warm timber soffit and honest vertical supports.
    cube('Garden porch canopy',(3.0,-6.05,2.91),(3.95,1.32,.13),m['oak'],.016)
    for x in (1.12,4.86):
        cube('Porch oak post',(x,-6.64,1.46),(.105,.105,2.91),m['oak'],.014)
    # Raise the upper opening and roof without moving the calibrated transom.
    for name in ('10 • Architecture / connected shell','11 • Roof and joinery'):
        for obj in bpy.data.collections[name].objects:
            if obj.type!='MESH':
                continue
            for vert in obj.data.vertices:
                if vert.co.z+obj.location.z>2.70:
                    vert.co.z+=.35
    cube('Upper linen roller veil',(-1.12,-5.16,2.98),(3.93,.001,.70),m['sheer'])
    beam('Linen roller shade lower dowel',(-3.09,-5.15,2.63),(.85,-5.15,2.63),.009,m['oak'])

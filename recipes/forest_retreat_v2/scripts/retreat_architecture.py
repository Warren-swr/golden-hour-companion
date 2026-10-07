"""Cedar gable cabin, precise joinery, timber porch and a planted deck."""
from retreat_helpers import *
from garden import herb


def build(m):
    collection('53 • Retreat / cedar envelope and gabled roof')
    remove_prefix('Roof insulation fascia', 'Weatherproof zinc roof', 'Standing roof seam',
                  'Zinc gutter', 'Rainwater downpipe', 'Garden porch canopy', 'Porch oak post')
    # Keep the connected interior shell and calibrated south window. Clad its exterior.
    for i in range(74):
        x = -3.58 + i * .146
        cube('Cabin / rear vertical cedar board', (x, .262, 1.745), (.140, .038, 3.46), m['cedar'], .004)
        if i % 3 == 0:
            cube('Cabin / rear narrow cover batten', (x + .073, .289, 1.745), (.027, .025, 3.47), m['charred'], .003)
    front_areas = [(-3.62, -3.10, 0, 3.45), (.91, 1.03, 0, 3.45),
                   (-3.10, .89, 0, .615), (-3.10, .89, 3.36, 3.49),
                   (3.16, 7.12, 0, .79), (3.16, 7.12, 3.0, 3.48)]
    for xa, xb, za, zb in front_areas:
        count = max(1, round((xb - xa) / .145))
        for i in range(count):
            w = (xb - xa) / count
            cube('Cabin / south cedar weatherboard', (xa + w * (i + .5), -5.443, (za + zb) / 2),
                 (w - .005, .038, zb - za), m['cedar'], .003)
    for east in (False, True):
        x = 7.223 if east else -3.693
        for i in range(38):
            y = -5.3 + (i + .5) * 5.56 / 38
            if east:
                ranges = [(0, .59), (2.68, 3.48)] if -2.85 < y < -.75 else (
                    [(0, 1.35), (2.56, 3.48)] if -4.88 < y < -3.72 else [(0, 3.48)])
            else:
                ranges = [(0, .52), (3.08, 3.48)] if -4.40 < y < -1.05 else [(0, 3.48)]
            for za, zb in ranges:
                cube('Cabin / side cedar board', (x, y, (za + zb) / 2), (.038, .140, zb - za), m['cedar'], .004)
        # The solid end gable is a real three-dimensional timber skin.
        for i in range(42):
            y = -5.47 + (i + .5) * 5.87 / 42
            ztop = 5.22 - abs(y + 2.58) * (1.70 / 3.22)
            if ztop > 3.48:
                cube('Cabin / tapered gable cedar', (x, y, (ztop + 3.48) / 2), (.056, .135, ztop - 3.48), m['cedar'], .003)
        rectangular_beam('Cabin / gable king post', (x * 1.003, -2.58, 3.48), (x * 1.003, -2.58, 5.19), .10, .12, m['charred'])
        for yy in (-5.67, .51):
            rectangular_beam('Cabin / gable raking fascia', (x, yy, 3.57), (x, -2.58, 5.25), .15, .16, m['charred'])
    # Roof slopes use two closed, bevelled metal shells with real raised seams.
    angle = math.atan2(1.70, 3.22)
    for side in (-1, 1):
        center_y = -2.58 + side * 1.61
        roof = cube('Cabin / pitched zinc roof plane', (1.78, center_y, 4.37), (11.88, math.hypot(3.22, 1.70), .075), m['roof'], .009)
        roof.rotation_euler.x = -side * angle
        for i in range(33):
            xx = -4.09 + i * .367
            rectangular_beam('Cabin / standing-seam roof rib', (xx, -2.58, 5.274), (xx, -2.58 + side * 3.22, 3.572), .014, .025, m['dark'])
        for i in range(11):
            xx = -3.73 + i * 1.095
            rectangular_beam('Cabin / exposed rafter tail', (xx, -2.58 + side * 2.5, 3.84),
                             (xx, -2.58 + side * 3.14, 3.50), .074, .12, m['teak'])
    cube('Cabin / folded ridge cap', (1.78, -2.58, 5.29), (12.0, .15, .065), m['dark'], .025)
    cube('Cabin / closed south eave fascia', (1.78, -5.42, 3.65), (10.85, .16, .36), m['cedar'], .006)
    cube('Cabin / closed rear eave fascia', (1.78, .27, 3.60), (10.85, .16, .27), m['cedar'], .006)
    for yy in (-5.88, .73):
        cube('Cabin / half-round bronze gutter', (1.78, yy, 3.54), (12.0, .13, .12), m['copper'], .048)
    # The chimney flashing meets the pitched metal roof.
    flash = cube('Cabin / sealed stove chimney flashing', (-2.94, -4.62, 4.22), (.40, .43, .043), m['dark'], .018)
    flash.rotation_euler.x = angle
    for x in (-3.6, 7.19):
        cube('Cabin / corner post with shadow reveal', (x, -5.49, 1.74), (.13, .10, 3.48), m['charred'], .008)
    # A shallow cedar porch frames the threshold without enclosing it.
    collection('54 • Retreat / porch joinery and weathered deck')
    for xx in (-3.45, 1.11, 7.02):
        cube('Porch / structural timber post', (xx, -6.83, 1.72), (.145, .145, 3.44), m['charred'], .008)
        cube('Porch / bronze post shoe', (xx, -6.83, .07), (.16, .16, .13), m['copper'], .006)
        for z in (.18, 3.22):
            for side in (-1, 1):
                bolt = cylinder('Porch / exposed structural bolt', (xx, -6.915, z), .011, .009, m['copper'], 12)
                bolt.rotation_euler.x = pi / 2
    cube('Porch / continuous front beam', (1.79, -6.83, 3.36), (10.83, .19, .22), m['charred'], .009)
    for i in range(23):
        xx = -3.48 + i * .482
        rectangular_beam('Porch / spaced cedar pergola rafter', (xx, -5.39, 3.53), (xx, -7.00, 3.40), .065, .115, m['teak'])
    # Sparse, delicate climbers leave most roof light open.
    from forest import foliage_mesh
    specs = []
    for i in range(9):
        x = -3.47 + i * .081
        points = [(x + .065 * sin(j * .6 + i), -6.83 + .07 * cos(j * .7 + i), .15 + j * .11) for j in range(31)]
        curve('Porch / climbing jasmine woody stem', points, .004, m['bark'])
        for j in range(10, 31):
            p = Vector(points[j])
            for side in (-1, 1):
                specs.append((p, (side, -.15, .34), .085, .027, .3, i % 3))
    leafm = [bpy.data.materials.get('Woodland broadleaf chlorophyll ' + str(i)) for i in range(3)]
    foliage_mesh('Porch / individual jasmine leaves', specs, leafm)
    remove_prefix('Courtyard limestone paver', 'Terrace gravel bedding', 'Stepping stone approach')
    cube('Deck / dark substructure', (1.32, -7.56, -.119), (13.02, 4.51, .13), m['charred'], .014)
    for j in range(31):
        yy = -5.41 - j * .142
        for i in range(6):
            xa = -5.16 + i * 2.162
            xb = xa + 2.154
            # An open tree well, cut into the actual boards and substructure.
            intervals = [(xa, xb)]
            if -8.36 < yy < -7.05:
                intervals = [(a, b) for a, b in ((xa, min(xb, -4.81)), (max(xa, -3.47), xb)) if b - a > .02]
            for a, b in intervals:
                cube('Deck / separate weathered timber plank', ((a + b) / 2, yy, -.028), (b - a, .136, .062), m['deck'], .004)
                for xx in (a + .043, b - .043):
                    for dy in (-.043, .043):
                        cylinder('Deck / recessed screw head', (xx, yy + dy, .005), .0027, .0014, m['dark'], 10)
    for yy in (-5.34, -9.79):
        cube('Deck / fine front fascia', (1.31, yy, -.11), (13.05, .065, .24), m['cedar'], .007)
    # Raised herb beds, real potting soil and edge planting.
    for x, y in ((7.57, -7.98), (-5.15, -8.85)):
        cube('Garden / cedar raised planter', (x, y, .23), (.48, 1.45, .50), m['cedar'], .016)
        cube('Garden / deep planter soil', (x, y, .486), (.40, 1.36, .026), m['soil'], .01)
        for j in range(5):
            herb('Garden / planted aromatic', (x, y - .54 + j * .26, .43), m, .82)
    # A rain chain and gravel basin bring the small architectural scale into focus.
    for i in range(35):
        torus('Cabin / copper rain chain link', (7.62, -5.85, 3.41 - i * .087), .041, .0045, m['copper'], (pi / 2, 0, (i % 2) * pi / 2))
    lathe('Cabin / rain-chain catch bowl', [(0, 0), (.26, 0), (.33, .10), (.32, .17), (.30, .18), (.27, .09), (0, .025)], (7.62, -5.85, -.19), m['rock'])
    for x, y, s in ((-4.70, -6.22, 1.1), (3.28, -5.7, .83), (6.7, -9.25, 1.25)):
        lantern('Porch / bronze evening lantern', (x, y, .02), m, s)
    # Under-eave log store: bark, visible cut ends and honest stacking.
    cube('Cabin / log store back', (7.41, -1.65, .53), (.07, 1.59, 1.14), m['charred'], .006)
    for y in (-2.45, -.84):
        cube('Cabin / log store frame', (7.67, y, .55), (.62, .06, 1.12), m['charred'], .006)
    for j in range(5):
        for i in range(9):
            yy = -2.36 + i * .166 + (j % 2) * .04
            zz = .04 + j * .148
            beam('Cabin / stacked split firewood bark', (7.4, yy, zz), (7.99, yy + .013, zz + .01), .073, m['bark_scan'])
            beam('Cabin / pale sawn end grain', (7.989, yy + .013, zz + .01), (8.00, yy + .013, zz + .01), .066, m['oak'])

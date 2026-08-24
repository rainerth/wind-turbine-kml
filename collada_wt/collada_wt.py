## Collada WT
# This script creates a wonderful 3D wind turbine
# that can be displayed in Google Earth Pro

import collada
import numpy as np


def rotation_matrix(x_degrees=0,y_degrees=0,z_degrees=0):

    theta_x = np.radians(x_degrees)
    rx = np.array([[1,0,0],
                   [0,np.cos(theta_x),-np.sin(theta_x)],
                   [0,np.sin(theta_x), np.cos(theta_x)]])

    theta_y = np.radians(y_degrees)
    ry = np.array([[np.cos(theta_y),0,np.sin(theta_y)],
                   [0,1,0],
                   [-np.sin(theta_y),0, np.cos(theta_y)]])

    theta_z = np.radians(z_degrees)
    rz = np.array([[np.cos(theta_z),-np.sin(theta_z),0],
                   [np.sin(theta_z), np.cos(theta_z),0],
                   [0,0,1]])

    r = rx.dot(ry.dot(rz))

    return r


def combine_verts(lst_vert_floats,lst_indices):

    import numpy as np

    # combine the vertices
    vert_floats = np.vstack(lst_vert_floats)

    # combine the indices, which are incremental
    indices = lst_indices[0]
    for index in lst_indices[1:]:

        index[:,[1,3,5]] = index[:,[1,3,5]] + indices[:,[1,3,5]].max() + 1
        index[:,[0,2,4]] = index[:,[0,2,4]] + indices[:,[0,2,4]].max() + 1

        indices = np.vstack([indices,index]).astype(int)

    return vert_floats,indices


def create_beam(cross_section_bottom,cross_section_top):

    import numpy as np


    vert_floats = np.vstack([cross_section_top,cross_section_bottom])


    if cross_section_top.size != cross_section_bottom.size:
        print('Error: corss sections require the same number of vertices')

    sides = int(cross_section_top.size/3)


    # define triangles along sides
    indices = np.empty([0,6])


    for side in range(sides):
        tri1 = (0+side)%sides
        tri2 = (1+side)%sides
        tri3 = sides+side
        tri4 = sides+(side+1)%sides

        base_index = int(indices.size/2)

        indices = np.vstack([indices,
                              [tri1,base_index,tri2,base_index+1,tri3,base_index+2],
                              [tri2,base_index+3,tri4,base_index+4,tri3,base_index+5]
                             ])


    # define triangles at ends
    for side in range(sides):
        bot3 = 0
        bot2 = (1+side)%sides
        bot1 = (2+side)%sides

        top1 = 0 + sides
        top2 = (1+side)%sides + sides
        top3 = (2+side)%sides + sides

        base_index = int(indices.size/2)

        indices = np.vstack([indices,
                              [bot1,base_index,bot2,base_index+1,bot3,base_index+2],
                              [top1,base_index+3,top2,base_index+4,top3,base_index+5]
                             ])



    indices = indices.astype(int)
    #print(indices)

    return vert_floats,indices


def create_regular_polygon(radius=5,sides=8):


    import numpy as np

    angles = np.arange(0,2*np.pi,2*np.pi/sides)

    x = radius*np.sin(angles)
    y = radius*np.cos(angles)

    return x,y


def create_cone(radius_bottom=5,radius_top=4,length=150,sides=8):

    import numpy as np

    # create bottom cross-section
    x,y = create_regular_polygon(radius=radius_bottom,sides=sides)
    z = 0*np.zeros(x.size)
    vert_floats_bot = np.array([x,y,z]).T

    # create top cross-section
    x,y = create_regular_polygon(radius=radius_top,sides=sides)
    z = length*np.ones(x.size)
    vert_floats_top = np.array([x,y,z]).T

    #print(vert_floats)

    vert_floats,indices = create_beam(vert_floats_bot,vert_floats_top)

    return vert_floats,indices


def create_tower(radius_bottom=5,radius_top=4,length=150,sides=8):

    vert_floats,indices = create_cone(radius_bottom=radius_bottom,radius_top=radius_top,length=length,sides=sides)

    door_vert_floats,door_indices = create_cone(radius_bottom=1,radius_top=1,length=2,sides=4)

    door_vert_floats = door_vert_floats.dot(rotation_matrix(x_degrees=0,y_degrees=0,z_degrees=45))

    door_vert_floats[:,1] = door_vert_floats[:,1]+radius_bottom*0.8

    vert_floats,indices = combine_verts([vert_floats,door_vert_floats],[indices,door_indices])

    return vert_floats,indices

def create_cylinder(radius=4,length=150,sides=8):

    import numpy as np

    # create bottom cross-section
    x,y = create_regular_polygon(radius=radius,sides=sides)
    z = 0*np.zeros(x.size)
    vert_floats_bot = np.array([x,y,z]).T

    # create top cross-section
    x,y = create_regular_polygon(radius=radius,sides=sides)
    z = length*np.ones(x.size)
    vert_floats_top = np.array([x,y,z]).T

    #print(vert_floats)

    vert_floats,indices = create_beam(vert_floats_bot,vert_floats_top)

    return vert_floats,indices

def create_aerofoil(chord=10,thickness=2,vertices_top=15):

    # https://en.wikipedia.org/wiki/NACA_airfoil
    # NACA-00xx

    import numpy as np

    t = thickness/chord

    x = np.linspace(0,1,vertices_top)
    x = np.append(x,np.flip(x))
    y = 5*t*(0.2969*x**0.5-0.1260*x-0.3516*x**2+0.2843*x**3-0.1015*x**4)

    y[vertices_top:] = -y[vertices_top:]

    x = x - 0.5
    x = x * chord
    y = y * chord

    return x,y

def create_lofted_body(cross_sections):
    """Verbindet mehrere Querschnitte zu einem geschlossenen Körper.

    Anders als create_beam(), das genau zwei Querschnitte verbindet und an
    beiden Enden eine Kappe setzt, kann diese Funktion beliebig viele Stationen
    aneinanderreihen. Nur der erste und der letzte Querschnitt bekommen eine
    Kappe, dazwischen entsteht durchgehende Mantelfläche - für ein Rotorblatt,
    dessen Tiefe sich über mehrere Stationen ändert.

    Args:
        cross_sections: Liste von (M,3)-Arrays mit je M Punkten in gleicher
            Reihenfolge und gleicher Anzahl.

    Returns:
        (vert_floats, indices) im Format von create_beam().
    """
    import numpy as np

    sections = [np.asarray(cs) for cs in cross_sections]
    points = sections[0].shape[0]
    if any(cs.shape[0] != points for cs in sections):
        raise ValueError('alle Querschnitte brauchen gleich viele Punkte')

    vert_floats = np.vstack(sections)

    triangles = []

    # Mantel: je zwei benachbarte Stationen ergeben einen Ring aus Vierecken.
    # Die Umlaufrichtung muss der von create_beam() entsprechen, sonst zeigen
    # alle Normalen nach innen. Google Earth verwirft solche Flächen per
    # Backface-Culling und vom Rotorblatt bleibt nur die Silhouette - ein
    # Strich. Gegenprobe ist das vorzeichenbehaftete Volumen: es muss positiv
    # sein (Divergenz-Theorem).
    for station in range(len(sections) - 1):
        lower = station * points
        upper = (station + 1) * points
        for side in range(points):
            next_side = (side + 1) % points
            triangles.append((lower + side, upper + side, lower + next_side))
            triangles.append((lower + next_side, upper + side, upper + next_side))

    # Kappen an den beiden Enden, als Fächer um den jeweils ersten Punkt.
    last = (len(sections) - 1) * points
    for side in range(1, points - 1):
        triangles.append((0, side, side + 1))
        triangles.append((last, last + side + 1, last + side))

    # Normalen werden später je Dreieck berechnet, ihr Index ist deshalb
    # fortlaufend: Dreieck k belegt 3k, 3k+1, 3k+2.
    indices = np.array([[a, 3 * k, b, 3 * k + 1, c, 3 * k + 2]
                        for k, (a, b, c) in enumerate(triangles)], dtype=int)

    return vert_floats, indices


# Tiefenverlauf eines modernen Rotorblatts, normiert auf die größte Blatttiefe.
# Stationen als (Anteil der Blattlänge, Anteil der maximalen Tiefe). Die größte
# Tiefe liegt bei rund 20 % der Länge, danach verjüngt sich das Blatt stetig bis
# auf wenige Zentimeter an der Spitze. Der frühere Verlauf war eine Gerade von
# der Wurzel bis zur halben Tiefe an der Spitze - dadurch wirkten die Blätter
# über die ganze Länge wie Balken.
BLADE_PLANFORM = (
    (0.00, 0.55),
    (0.08, 0.85),
    (0.20, 1.00),
    (0.35, 0.82),
    (0.50, 0.66),
    (0.65, 0.52),
    (0.80, 0.37),
    (0.90, 0.26),
    (0.96, 0.17),
    (1.00, 0.06),
)


def blade_sections(length, chord, thickness, twist, planform=BLADE_PLANFORM,
                   station_range=(0.0, 1.0), extra_stations=()):
    """Querschnitte eines Blattabschnitts entlang der Blattlänge.

    Die Verwindung läuft von twist an der Wurzel linear auf 0 an der Spitze -
    so herum wie beim echten Blatt, dessen Profil außen fast in der Rotorebene
    liegt.

    Args:
        station_range: Anteil der Blattlänge, der erzeugt werden soll.
        extra_stations: zusätzliche Stationen (Anteile), damit ein Abschnitt
            exakt an einer gewünschten Trennstelle beginnt oder endet.
    """
    import numpy as np

    fractions = sorted({f for f, _ in planform} | set(extra_stations) | set(station_range))
    fractions = [f for f in fractions if station_range[0] - 1e-9 <= f <= station_range[1] + 1e-9]

    planform_x = [f for f, _ in planform]
    planform_y = [c for _, c in planform]

    sections = []
    for fraction in fractions:
        local_chord = chord * float(np.interp(fraction, planform_x, planform_y))
        local_twist = twist * (1 - fraction)

        x, y = create_aerofoil(chord=local_chord,
                               thickness=thickness * local_chord / chord)
        z = fraction * length * np.ones(x.size)

        section = np.array([x, y, z]).T
        section = section.dot(rotation_matrix(x_degrees=0, y_degrees=0,
                                              z_degrees=local_twist))
        sections.append(section)

    return sections


def create_blade(length=150, rotation=0, chord=10, thickness=2, tip_size=0.5,
                 twist=5, root_length=10, tip_paint_length=6.0):
    """Rotorblatt aus zwei Körpern: Hauptteil und farbig markierte Spitze.

    tip_size wird nicht mehr ausgewertet - der Tiefenverlauf kommt aus
    BLADE_PLANFORM. Das Argument bleibt für Aufrufer erhalten.

    tip_paint_length ist die Länge der Blattspitze in Metern, die als eigener
    Körper entsteht, damit sie ein eigenes Material bekommen kann (rote
    Tageskennzeichnung nach AVV Kennzeichnung von Luftfahrthindernissen).

    Returns:
        (main_verts, main_indices, tip_verts, tip_indices)
    """
    import numpy as np

    split = max(0.0, min(1.0, 1 - tip_paint_length / length)) if length > 0 else 1.0

    def build(station_range):
        sections = blade_sections(length, chord, thickness, twist,
                                  station_range=station_range,
                                  extra_stations=(split,))
        verts, indices = create_lofted_body(sections)
        verts = verts.dot(rotation_matrix(x_degrees=0, y_degrees=0, z_degrees=90))
        verts[:, 2] = verts[:, 2] + root_length
        verts = verts.dot(rotation_matrix(x_degrees=rotation, y_degrees=0, z_degrees=0))
        return verts, indices

    main_verts, main_indices = build((0.0, split))
    tip_verts, tip_indices = build((split, 1.0))

    return main_verts, main_indices, tip_verts, tip_indices

def create_blade_root(radius=5,length=10,rotation=0):

    vert_floats,indices = create_cylinder(radius=radius,length=length,sides=16)

    vert_floats = vert_floats.dot(rotation_matrix(x_degrees=rotation,y_degrees=0,z_degrees=0))


    return vert_floats,indices

def create_hub(radius=5,length=1):


    vert_floats,indices = create_cylinder(radius=radius,length=length,sides=16)

    cone_vert_floats,cone_indices = create_cone(radius_bottom=radius,radius_top=0.75*radius,length=length*0.3,sides=16)

    cone_vert_floats[:,2] = cone_vert_floats[:,2]+length

    vert_floats,indices = combine_verts([vert_floats,cone_vert_floats],[indices,cone_indices])

    vert_floats = vert_floats.dot(rotation_matrix(x_degrees=0,y_degrees=-90,z_degrees=0))

    vert_floats[:,0] = vert_floats[:,0]-2

    return vert_floats,indices

def create_rotor(diameter=100,hub_height=100,overhang=20,chord=10,thickness=5,tip_size=0.2,twist=10,root_length=10,root_diameter=4,tip_paint_length=6.0):


    blade_length=diameter/2-root_length


    vert_floats,indices = create_hub(radius=root_length*0.9,length=root_diameter*1.8)



    root1_vert_floats,root1_indices = create_blade_root(radius=root_diameter/2,length=root_length,rotation=0)
    root2_vert_floats,root2_indices = create_blade_root(radius=root_diameter/2,length=root_length,rotation=120)
    root3_vert_floats,root3_indices = create_blade_root(radius=root_diameter/2,length=root_length,rotation=240)


    vert_floats,indices = combine_verts([vert_floats,root1_vert_floats,root2_vert_floats,root3_vert_floats],
                                        [indices,root1_indices,root2_indices,root3_indices])

    blade_verts = []
    blade_indices = []
    tip_verts = []
    tip_indices = []

    for blade_rotation in (0, 120, 240):
        main_v, main_i, tip_v, tip_i = create_blade(length=blade_length,
                                                    rotation=blade_rotation,
                                                    chord=chord,
                                                    thickness=thickness,
                                                    tip_size=tip_size,
                                                    twist=twist,
                                                    root_length=root_length,
                                                    tip_paint_length=tip_paint_length)
        blade_verts.append(main_v)
        blade_indices.append(main_i)
        tip_verts.append(tip_v)
        tip_indices.append(tip_i)

    vert_floats,indices = combine_verts([vert_floats]+blade_verts,
                                        [indices]+blade_indices)

    # Blattspitzen bleiben eine eigene Geometrie, damit sie in create_turbine()
    # ein anderes Material bekommen können (rote Tageskennzeichnung).
    tip_vert_floats,tip_index_array = combine_verts(tip_verts,tip_indices)

    for arr in (vert_floats, tip_vert_floats):
        arr[:,0] = arr[:,0]+overhang
        arr[:,2] = arr[:,2]+hub_height

    return vert_floats,indices,tip_vert_floats,tip_index_array

def create_nacelle(nacelle_height=3,nacelle_length=20,nacelle_overhang=8,tower_height=95,sides=4):

    nacelle_vert_floats,nacelle_indices = create_cylinder(radius=nacelle_height,length=nacelle_length,sides=4)

    nacelle_vert_floats = nacelle_vert_floats.dot(rotation_matrix(x_degrees=0,y_degrees=0,z_degrees=45))
    nacelle_vert_floats = nacelle_vert_floats.dot(rotation_matrix(x_degrees=0,y_degrees=90,z_degrees=0))

    nacelle_vert_floats[:,0] = nacelle_vert_floats[:,0]+nacelle_overhang
    nacelle_vert_floats[:,2] = nacelle_vert_floats[:,2]+tower_height+nacelle_height/2

    return nacelle_vert_floats,nacelle_indices

def create_turbine(tower_height = 95,
                   tower_bot_diameter = 4,
                   tower_top_diameter = 3,
                   nacelle_height = 3,
                   nacelle_length = 20,
                   nacelle_overhang = 8,
                   rotor_diameter = 150,
                   blade_root_length = 2.5,
                   blade_root_diameter = 2,
                   blade_chord=4,
                   blade_tip_size=0.5,
                   blade_twist=30,
                   blade_tip_paint_length=6.0,
                   tip_color=(1, 1, 1),
                  ):


    hub_height = tower_height+nacelle_height/2
    hub_overhang = nacelle_overhang+2

    blade_thickness=blade_chord/3 # blade thickness


    # create tower
    tower_vert_floats,tower_indices = create_tower(radius_bottom=tower_bot_diameter/2,
                                                   radius_top=tower_top_diameter/2,
                                                   length=tower_height,
                                                   sides=16)


    # create nacelle
    nacelle_vert_floats,nacelle_indices = create_nacelle(nacelle_height=nacelle_height,
                                                         nacelle_length=nacelle_length,
                                                         nacelle_overhang=nacelle_overhang,
                                                         tower_height=tower_height,
                                                         sides=4)


    # create rotor
    rotor_vert_floats,rotor_indices,tip_vert_floats,tip_indices = create_rotor(
                                                   diameter=rotor_diameter,
                                                   hub_height=hub_height,
                                                   overhang=hub_overhang,
                                                   chord=blade_chord,
                                                   thickness=blade_thickness,
                                                   tip_size=blade_tip_size,
                                                   twist=blade_twist,
                                                   root_length=blade_root_length,
                                                   root_diameter=blade_root_diameter,
                                                   tip_paint_length=blade_tip_paint_length)


    # combine objects: erst alles Weiße, dann die Blattspitzen. Die Reihenfolge
    # trägt die Materialzuordnung - die letzten Dreiecke sind die roten.
    body_vert_floats,body_indices = combine_verts([tower_vert_floats,nacelle_vert_floats,rotor_vert_floats],
                                           [tower_indices,nacelle_indices,rotor_indices])

    body_triangles = body_indices.shape[0]

    vert_floats,indices = combine_verts([body_vert_floats,tip_vert_floats],
                                        [body_indices,tip_indices])

    # rotate to match google earth x,y,z
    vert_floats = vert_floats.dot(rotation_matrix(x_degrees=90,y_degrees=0,z_degrees=0))


    # create normals at each vertex based on triangle normals
    normal_floats = np.cross(vert_floats[indices[:,0]]-vert_floats[indices[:,2]],
             vert_floats[indices[:,0]]-vert_floats[indices[:,4]])

    # Auf Einheitslänge bringen. np.cross liefert Vektoren, deren Länge der
    # doppelten Dreiecksfläche entspricht - beim Turm über 250, bei den winzigen
    # Dreiecken der Blattspitze unter 0,1. Google Earth rechnet die Beleuchtung
    # mit diesen Längen, statt sie selbst zu normieren: große Flächen
    # übersteuern zu Weiß, kleine werden schwarz. Genau deshalb waren die
    # Blattspitzen dunkel und der Schattenkontrast so hart.
    lengths = np.linalg.norm(normal_floats, axis=1, keepdims=True)
    normal_floats = normal_floats / np.where(lengths == 0, 1, lengths)

    normal_floats = np.tile(normal_floats,3)


    # create Collada object
    vert_src = collada.source.FloatSource("cubeverts-array", vert_floats.flatten(), ('X', 'Y', 'Z'))
    normal_src = collada.source.FloatSource("cubenormals-array", normal_floats.flatten(), ('X', 'Y', 'Z'))

    mesh = collada.Collada()

    # Materialwerte empirisch in Google Earth Pro ermittelt (Testreihe mit fünf
    # Varianten nebeneinander, siehe CLAUDE.md):
    #   - diffuse MUSS (1,1,1) bleiben. Jeder kleinere Wert - auch 0,9 - lässt
    #     das ganze Modell schwarz erscheinen, nicht etwa etwas dunkler.
    #   - ambient wirkt nicht. Eine Variante mit ambient 0,6 sah exakt aus wie
    #     eine mit ambient 0.
    #   - specular stand früher auf (0,1,0), also grün. Neutral auf 0.
    #   - double_sided NICHT setzen: es zeichnet auch die unbeleuchteten
    #     Rückseiten, die bei den dünnen Blattprofilen die Vorderseite
    #     überdecken. Die Umlaufrichtung stimmt ohnehin (signed_volume).
    effect = collada.material.Effect("effect0", [], "phong",
                                     diffuse=(1, 1, 1),
                                     specular=(0, 0, 0))
    mat = collada.material.Material("material0", "mymaterial", effect)
    mesh.effects.append(effect)
    mesh.materials.append(mat)

    # Zweites Material für die Blattspitzen. Beide Dreiecksmengen teilen sich
    # dieselbe Vertex- und Normalenquelle, unterscheiden sich also nur im
    # Material - deshalb zwei TriangleSets statt zweier Geometrien.
    #
    # tip_color steht auf (1,1,1), die Spitzen sind also weiß wie der Rest.
    # Ein abgesenkter Wert wie (0.75, 0.08, 0.08) kam in Google Earth nicht als
    # Rot an, sondern als Grau - dasselbe Muster wie beim Hauptmaterial, wo
    # jeder Wert unter 1 das Modell schwarz werden ließ. Die Aufteilung der
    # Geometrie bleibt erhalten: sobald ein Farbwert gefunden ist, der in
    # Google Earth durchkommt, genügt es, tip_color zu setzen.
    tip_effect = collada.material.Effect("effect1", [], "phong",
                                         diffuse=tip_color,
                                         specular=(0, 0, 0))
    tip_mat = collada.material.Material("material1", "tipmaterial", tip_effect)
    mesh.effects.append(tip_effect)
    mesh.materials.append(tip_mat)

    geom = collada.geometry.Geometry(mesh, "geometry0", "mycube", [vert_src, normal_src])

    input_list = collada.source.InputList()
    input_list.addInput(0, 'VERTEX', "#cubeverts-array")
    input_list.addInput(1, 'NORMAL', "#cubenormals-array")

    triset = geom.createTriangleSet(indices[:body_triangles].flatten(), input_list, "materialref")
    geom.primitives.append(triset)

    tip_triset = geom.createTriangleSet(indices[body_triangles:].flatten(), input_list, "tipref")
    geom.primitives.append(tip_triset)

    mesh.geometries.append(geom)

    matnode = collada.scene.MaterialNode("materialref", mat, inputs=[])
    tip_matnode = collada.scene.MaterialNode("tipref", tip_mat, inputs=[])
    geomnode = collada.scene.GeometryNode(geom, [matnode, tip_matnode])
    node = collada.scene.Node("node0", children=[geomnode])

    myscene = collada.scene.Scene("myscene", [node])
    mesh.scenes.append(myscene)
    mesh.scene = myscene

    return mesh


def create_zone(zone_height = 95,zone_diameter = 4):
    hub_height = zone_height

    # create zone
    zone_vert_floats,zone_indices = create_tower(radius_bottom=zone_diameter/2,
                                                   radius_top=zone_diameter/2,
                                                   length=zone_height,
                                                   sides=32)




    # combine objects
    vert_floats,indices = combine_verts([zone_vert_floats],[zone_indices])

    # rotate to match google earth x,y,z
    vert_floats = vert_floats.dot(rotation_matrix(x_degrees=90,y_degrees=0,z_degrees=0))


    # create normals at each vertex based on triangle normals
    normal_floats = np.cross(vert_floats[indices[:,0]]-vert_floats[indices[:,2]],
             vert_floats[indices[:,0]]-vert_floats[indices[:,4]])

    # Auf Einheitslänge bringen. np.cross liefert Vektoren, deren Länge der
    # doppelten Dreiecksfläche entspricht - beim Turm über 250, bei den winzigen
    # Dreiecken der Blattspitze unter 0,1. Google Earth rechnet die Beleuchtung
    # mit diesen Längen, statt sie selbst zu normieren: große Flächen
    # übersteuern zu Weiß, kleine werden schwarz. Genau deshalb waren die
    # Blattspitzen dunkel und der Schattenkontrast so hart.
    lengths = np.linalg.norm(normal_floats, axis=1, keepdims=True)
    normal_floats = normal_floats / np.where(lengths == 0, 1, lengths)

    normal_floats = np.tile(normal_floats,3)


    # create Collada object
    vert_src = collada.source.FloatSource("cubeverts-array", vert_floats.flatten(), ('X', 'Y', 'Z'))
    normal_src = collada.source.FloatSource("cubenormals-array", normal_floats.flatten(), ('X', 'Y', 'Z'))

    mesh = collada.Collada()

    effect = collada.material.Effect("effect0", [], "phong",
                                     diffuse=(1, 1, 1),
                                     specular=(0, 0, 0))
    mat = collada.material.Material("material0", "mymaterial", effect)
    mesh.effects.append(effect)
    mesh.materials.append(mat)

    geom = collada.geometry.Geometry(mesh, "geometry0", "mycube", [vert_src, normal_src])

    input_list = collada.source.InputList()
    input_list.addInput(0, 'VERTEX', "#cubeverts-array")
    input_list.addInput(1, 'NORMAL', "#cubenormals-array")

    triset = geom.createTriangleSet(indices.flatten(), input_list, "materialref")
    geom.primitives.append(triset)
    mesh.geometries.append(geom)

    matnode = collada.scene.MaterialNode("materialref", mat, inputs=[])
    geomnode = collada.scene.GeometryNode(geom, [matnode])
    node = collada.scene.Node("node0", children=[geomnode])

    myscene = collada.scene.Scene("myscene", [node])
    mesh.scenes.append(myscene)
    mesh.scene = myscene

    return mesh


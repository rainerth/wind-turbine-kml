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

def create_blade(length=150,rotation=0,chord=10,thickness=2,tip_size=0.5,twist=5,root_length=10):
    
    import numpy as np
    
    # create bottom cross-section
    x,y = create_aerofoil(chord=chord,thickness=thickness)
    z = 0*np.zeros(x.size)
    vert_floats_bot = np.array([x,y,z]).T
    vert_floats_bot = vert_floats_bot.dot(rotation_matrix(x_degrees=0,y_degrees=0,z_degrees=twist))
    
    
    # create top cross-section
    x,y = create_aerofoil(chord=chord,thickness=thickness)
    x = x * tip_size
    y = y * tip_size
    z = length*np.ones(x.size)
    vert_floats_top = np.array([x,y,z]).T
    

    vert_floats,indices = create_beam(vert_floats_bot,vert_floats_top)
    
    vert_floats = vert_floats.dot(rotation_matrix(x_degrees=0,y_degrees=0,z_degrees=90))
    
    vert_floats[:,2] = vert_floats[:,2]+root_length
    
    vert_floats = vert_floats.dot(rotation_matrix(x_degrees=rotation,y_degrees=0,z_degrees=0))
    
    return vert_floats,indices
        
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

def create_rotor(diameter=100,hub_height=100,overhang=20,chord=10,thickness=5,tip_size=0.2,twist=10,root_length=10,root_diameter=4):
    
    
    blade_length=diameter/2-root_length
    
    
    vert_floats,indices = create_hub(radius=root_length*0.9,length=root_diameter*1.8)
    
    
    
    root1_vert_floats,root1_indices = create_blade_root(radius=root_diameter/2,length=root_length,rotation=0)
    root2_vert_floats,root2_indices = create_blade_root(radius=root_diameter/2,length=root_length,rotation=120)
    root3_vert_floats,root3_indices = create_blade_root(radius=root_diameter/2,length=root_length,rotation=240)
    
    
    vert_floats,indices = combine_verts([vert_floats,root1_vert_floats,root2_vert_floats,root3_vert_floats],
                                        [indices,root1_indices,root2_indices,root3_indices])
    
    blade1_vert_floats,blade1_indices = create_blade(length=blade_length,rotation=0,chord=chord,thickness=thickness,tip_size=tip_size,twist=twist,root_length=root_length)
    blade2_vert_floats,blade2_indices = create_blade(length=blade_length,rotation=120,chord=chord,thickness=thickness,tip_size=tip_size,twist=twist,root_length=root_length)
    blade3_vert_floats,blade3_indices = create_blade(length=blade_length,rotation=240,chord=chord,thickness=thickness,tip_size=tip_size,twist=twist,root_length=root_length)
    
    vert_floats,indices = combine_verts([vert_floats,blade1_vert_floats,blade2_vert_floats,blade3_vert_floats],
                                        [indices,blade1_indices,blade2_indices,blade3_indices])
        

    vert_floats = vert_floats.dot(rotation_matrix(x_degrees=0,y_degrees=0,z_degrees=0))
    
    vert_floats[:,0] = vert_floats[:,0]+overhang
    vert_floats[:,2] = vert_floats[:,2]+hub_height
    
     
    return vert_floats,indices    

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
    rotor_vert_floats,rotor_indices = create_rotor(diameter=rotor_diameter,
                                                   hub_height=hub_height,
                                                   overhang=hub_overhang,
                                                   chord=blade_chord,
                                                   thickness=blade_thickness,
                                                   tip_size=blade_tip_size,
                                                   twist=blade_twist,
                                                   root_length=blade_root_length,
                                                   root_diameter=blade_root_diameter)


    # combine objects
    vert_floats,indices = combine_verts([tower_vert_floats,nacelle_vert_floats,rotor_vert_floats],
                                           [tower_indices,nacelle_indices,rotor_indices])

    # rotate to match google earth x,y,z
    vert_floats = vert_floats.dot(rotation_matrix(x_degrees=90,y_degrees=0,z_degrees=0))


    # create normals at each vertex based on triangle normals
    normal_floats = np.cross(vert_floats[indices[:,0]]-vert_floats[indices[:,2]],
             vert_floats[indices[:,0]]-vert_floats[indices[:,4]])

    normal_floats = np.tile(normal_floats,3)


    # create Collada object
    vert_src = collada.source.FloatSource("cubeverts-array", vert_floats.flatten(), ('X', 'Y', 'Z'))
    normal_src = collada.source.FloatSource("cubenormals-array", normal_floats.flatten(), ('X', 'Y', 'Z'))

    mesh = collada.Collada()

    effect = collada.material.Effect("effect0", [], "phong", diffuse=(1,1,1), specular=(0,1,0))
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



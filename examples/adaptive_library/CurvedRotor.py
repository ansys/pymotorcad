
#%%
import bezier
import numpy as np
import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry_drawing import draw_objects_debug
from ansys.motorcad.core.geometry import Arc, Coordinate, EntityList, Line, Region, rt_to_xy

#%%
mc = pymotorcad.MotorCAD(open_new_instance=False)
# mc.load_from_file(r"C:\Consusltancy\Working\Reanult_ampere\M39_Ferrites_v5.mot")
# Disable popup messages
mc.set_variable("MessageDisplayState", 2)
mc.set_variable("VShape_Magnet_ClearanceInner",0)
mc.set_variable("CornerRoundingRadius_Magnets",0)

L1_11=mc.get_region("L1_1Magnet1")
draw_objects_debug(L1_11)
                              
#%%

# Reset geometry to default
mc.reset_adaptive_geometry()



import copy

# %%
def scale_line(region,entity_index,line_length):
    OT1=line_length
    OT1_dxf=region.entities[entity_index].length
    length_ratio=OT1/OT1_dxf
    Xa=region.entities[entity_index].start.x
    Ya=region.entities[entity_index].start.y
    Xb=region.entities[entity_index].end.x
    Yb=region.entities[entity_index].end.y
    s= length_ratio
    Xa1 = Xa*(1+s)/2 + Xb*(1-s)/2
    Ya1 = Ya*(1+s)/2 + Yb*(1-s)/2
    Xb1 = Xb*(1+s)/2 + Xa*(1-s)/2
    Yb1 = Yb*(1+s)/2 + Ya*(1-s)/2
    new_region=copy.deepcopy(region)
    new_start_point=Coordinate(Xa1,Ya1)
    new_end_point=Coordinate(Xb1,Yb1)
    new_region.edit_point(new_region.entities[entity_index].start,new_start_point)
    new_region.edit_point(new_region.entities[entity_index].end,new_end_point)

    return new_region
# %%
left_edge_len=mc.get_adaptive_parameter_value("left_edge_length")
left_edge_index=2
right_edge_len=mc.get_adaptive_parameter_value("right_edge_length")
right_edge_index=0
new_region=scale_line(L1_11,left_edge_index,left_edge_len)
draw_objects_debug([new_region])
new_region=scale_line(new_region,right_edge_index,right_edge_len)
draw_objects_debug([new_region])

#%%
# get the points at the specified distance away from the line (-ve distance)
entity=new_region.entities[1]
point10=entity.start
point20=entity.end
pocket_length=mc.get_adaptive_parameter_value("pocket_length")
point1 = entity.get_coordinate_from_distance(point10,distance=-1*pocket_length)
point2 = entity.get_coordinate_from_distance(point20,distance=-1*pocket_length)
#%%
entity=new_region.entities[3]
point220=entity.start
point110=entity.end
point22 = entity.get_coordinate_from_distance(point220,distance=-1*pocket_length)
point11 = entity.get_coordinate_from_distance(point110,distance=-1*pocket_length)
#%%
# create the region
mag_poc_region_1=Region()      
line1=Line(point2,point20)
line2=Line(point20,point220)
line3=Line(point220,point22)
line4=Line(point22,point2)
mag_poc_region_1.entities=EntityList([line1,line2,line3,line4]) 
draw_objects_debug(mag_poc_region_1)
#%%
mag_poc_region_2=Region()      
line1=Line(point1,point10)
line2=Line(point10,point110)
line3=Line(point110,point11)
line4=Line(point11,point1)
mag_poc_region_2.entities=EntityList([line1,line2,line3,line4]) 
draw_objects_debug(mag_poc_region_2)
#%%
draw_objects_debug([mag_poc_region_1,mag_poc_region_2,new_region])
#%%
def get_rotor_mirror_line():
    rotor_radius = mc.get_variable("RotorDiameter")
    number_poles = mc.get_variable("Pole_Number")
    airgap_centre_x, airgap_centre_y = rt_to_xy(rotor_radius, (360 / number_poles) / 2)

    return Line(Coordinate(0, 0), Coordinate(airgap_centre_x, airgap_centre_y))

new_region_mirror=new_region.mirror(get_rotor_mirror_line())
mag_poc_region_2_mirror=mag_poc_region_2.mirror(get_rotor_mirror_line())
mag_poc_region_1_mirror=mag_poc_region_1.mirror(get_rotor_mirror_line())
draw_objects_debug([mag_poc_region_1_mirror,mag_poc_region_2_mirror,new_region_mirror])

#%%
rt_region=mc.get_region("Rotor")
draw_objects_debug([mag_poc_region_1,mag_poc_region_2,new_region,mag_poc_region_1_mirror,mag_poc_region_2_mirror,new_region_mirror,rt_region])

#%%      
L1_11.replace(new_region)
mc.set_region(L1_11)
L1_12=mc.get_region("L1_1Magnet2")
L1_12.replace(new_region_mirror)
mc.set_region(L1_12)

#%%
# replace the rotor pockets and delete extra rotor pockets
i=0
new_pockets=[mag_poc_region_1,mag_poc_region_2,mag_poc_region_1_mirror,mag_poc_region_2_mirror]
for child_name in rt_region.child_names:
    if "Rotor Pocket" in child_name:
        i=i+1
        pocket_region=mc.get_region(child_name)
        if i>4:
            
            mc.delete_region(pocket_region)
        else:
            pocket_region.replace(new_pockets[i-1])
            mc.set_region(pocket_region)

#%%
    
def line_to_curve(start_point, control_point, end_point):
    nodes = np.asfortranarray([
    [start_point.x, control_point.x, end_point.x],
    [start_point.y, control_point.y  , end_point.y],
    ])
    curve = bezier.Curve(nodes, degree=2)
    samples=np.linspace(0,1,9)
    points_on_curve=curve.evaluate_multi(samples)
    point_list=[]
    for i in range(points_on_curve.shape[1]):
        point_list.append(Coordinate(points_on_curve[0,i],points_on_curve[1,i]))
    line_list=[]
    for i in range(len(point_list)-1):
        line_list.append(Line(point_list[i],point_list[i+1]))
    

    return line_list

#%%

region_curved_line_list=[]
control_top_edge_x=mc.get_adaptive_parameter_value("control_top_edge_x")
control_top_edge_y=mc.get_adaptive_parameter_value("control_top_edge_y")
control_bottom_edge_x=mc.get_adaptive_parameter_value("control_bottom_edge_x")
control_bottom_edge_y=mc.get_adaptive_parameter_value("control_bottom_edge_y")
control_points =[[],Coordinate(control_top_edge_x,control_top_edge_y),[],Coordinate(control_bottom_edge_x,control_bottom_edge_y)]
index_curved_edge=[1,3]
for i, edge in enumerate(L1_11.entities):
    if i in index_curved_edge:
        line_list_curved_L1_11=line_to_curve(L1_11.entities[i].start,control_points[i],L1_11.entities[i].end)
        for line in line_list_curved_L1_11:
            region_curved_line_list.append(line)
    else:
        region_curved_line_list.append(edge)
L1_11.entities=EntityList(region_curved_line_list)
mc.set_region(L1_11)
# %%
draw_objects_debug(L1_11)
#%%
L1_12.replace(L1_11.mirror(get_rotor_mirror_line()))
mc.set_region(L1_12)
draw_objects_debug([rt_region,L1_11,L1_12])
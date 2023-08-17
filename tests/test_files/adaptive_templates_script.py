# Need to import pymotorcad to access Motor-CAD
import ansys.motorcad.core as pymotorcad

# Connect to Motor-CAD
mc = pymotorcad.MotorCAD(open_new_instance=False)

# get default template region from Motor-CAD
region = mc.geometry.get_region("Stator")
# update material and colour
region.material = "M43"
region.colour = (220, 20, 60)
# set region back into Motor-CAD (updates the default stator region)
mc.geometry.set_region(region)

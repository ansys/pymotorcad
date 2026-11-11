"""
.. _ref_force_extraction:

Motor-CAD force extraction example script
=========================================

todo: expand this...

"""

# %%
# Perform required imports
import ansys.motorcad.core as pymotorcad

# %%
# Launch Motor-CAD
mc = pymotorcad.MotorCAD()

# %%
# Disable pop-up messages
mc.set_variable("MessageDisplayState", 2)


# %%
# Load a baseline model - in this case a template.
# For users, this would normally be a baseline model
mc.load_template("e9")

# %%
# Set up the point we want to extract
required_space_order = 8  # Space order required, positive or negative
required_electrical_time_order = 2  # Electrical time order required, should be 0 or positive
operating_point = (
    1  # Which speed point to extract data for (between 1 and the number of calculations run)
)
rotor_slice = 1  # Which rotor slice (if more than one) that we want results from

# %%
# Run the calculation (Assume that it has already been set up as required)
mc.do_multi_force_calculation()

# %%
# How many cycles have been run
electrical_cycles = mc.get_variable("TorqueNumberCycles")

# %%
# Extract max space order that exists in the calculation
mech_force_space_order_max = mc.get_variable("ForceMaxOrder_Space_Stator_OL")

# %%
# Get the indexes to use in querying the force:
# required_time_order should always be 0 or positive. This is the order of
# the number of cycles run, which will be the same as electrical order if
# electrical_cycles = 1
required_time_order = required_electrical_time_order * electrical_cycles

# %%
# Results stored with negative space orders at the end, so apply offset
if required_space_order < 0:
    required_space_order = required_space_order + 2 * mech_force_space_order_max

# %%
# Find the force density using GetMagnetic3DGraphPoint:
# Note the use of _Th1 for the 1st operating point in the name.
_, force_density_result = mc.get_magnetic_3d_graph_point(
    "Fr_Density_Stator_FFT_Amplitude_OL" + "_Th" + str(operating_point),
    rotor_slice,
    required_space_order,
    required_time_order,
)

# %%
# Apply 2x factor due to FFT symmetry, unless 0th time order (mean)
# This is equivalent to showing results with 'Positive time only'
if required_time_order > 0:
    force_density_result = force_density_result * 2

# %%
# Results
# -------
print("Force density: " + str(force_density_result))

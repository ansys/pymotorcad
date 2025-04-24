# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from multiprocessing import current_process

from scipy import io

import ansys.motorcad.core as pymotorcad

unique_file_path = None
mc = None
ref_mot_path = None


# %%
# Define initialisation function
# ------------------------------
# This function is run every time a Motor-CAD instance is opened.


def initialise_motorcad_instances(path):
    # define mc as a separate global variable for each parallel worker/process
    global mc
    global unique_file_path
    global ref_mot_path

    ref_mot_path = path
    # launch Motor-CAD
    print(f"{current_process().name} initialisation starting...")
    mc = pymotorcad.MotorCAD(reuse_parallel_instances=True)

    # load the reference file
    mc.load_from_file(ref_mot_path + ".mot")

    # save a unique file and create a results path for each parallel session
    unique_file_path = f"{ref_mot_path}\\{current_process().name}.mot"
    mc.save_to_file(unique_file_path)
    print(f"{current_process().name} initialisation complete.")


# %%
# Define parallel process function
# --------------------------------
# This function is run by each parallel worker. It loads a duty cycle, runs the transient duty cycle
# calculation in Motor-CAD and saves the file.
# The function returns the transient results as a Python dictionary.
def run_motorcad_duty_cycle(duty_cycle):
    duty_cycle_name = duty_cycle["name"]
    print(f"{current_process().name} running {duty_cycle_name}...")

    # Clear any existing duty cycle and load in the relevant duty cycle from file.
    mc.clear_duty_cycle()
    mc.load_duty_cycle(f"{ref_mot_path}\\{duty_cycle_name}.dat")

    # Run the duty cycle calculation
    mc.do_transient_analysis()
    print(f"{current_process().name} {duty_cycle_name} complete.")

    # Save the MOT file.
    mc.save_to_file(unique_file_path)
    print(f"{current_process().name} file saved to {unique_file_path}")

    # Load the transient duty cycle results as a Python dictionary
    results_path = unique_file_path.replace(".mot", "\\Lab\\MotorLAB_drivecycledata.mat")
    thermal_transient_results = io.loadmat(results_path)

    # Add the duty cycle name, as well as the reference MOT file path and parallel worker name to
    # the dictionary.
    thermal_transient_results["duty_cycle_name"] = duty_cycle_name
    thermal_transient_results["parallel_worker"] = current_process().name
    thermal_transient_results["ref_mot_file"] = ref_mot_path + ".mot"

    # Return the transient duty cycle results dictionary.
    return thermal_transient_results


# %%
# Define function to close Motor-CAD instances
# --------------------------------------------
# This function closes the Motor-CAD instances. It should be called once the processes are complete.
def close_motorcad_instances(dummy_arg):
    print(f"{current_process().name} closing...")
    mc.quit()

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

"""
Running Parallel Motor-CAD Instances
====================================
This script opens and runs multiple Motor-CAD instances to run processes in parallel.
"""
# from scipy import io
# from multiprocessing.pool import ThreadPool as Pool
from multiprocessing import Pool  # , current_process

# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
import os
import shutil

# import sys
import tempfile

# os.environ["PYMOTORCAD_DOCS_BUILD"] = "true"
from dont_include_in_build.parallel_process_functions import (
    close_motorcad_instances,
    initialise_motorcad_instances,
    run_motorcad_duty_cycle,
)
import matplotlib.pyplot as plt

import ansys.motorcad.core as pymotorcad

# %%
# Initial set up
# --------------
# Create empty variables for the Motor-CAD instance and unique file paths.

# mc = None
# unique_file_path = None

# %%
# Open Motor-CAD

if __name__ == "__main__":
    mc_0 = pymotorcad.MotorCAD()
    # %%
    # Disable popup messages
    mc_0.set_variable("MessageDisplayState", 2)

    # %%
    # Load the e10 template
    mc_0.load_template("e10")

    # %%
    # Set up the Duty Cycle calculation in Motor-CAD
    mc_0.set_variable("TransientPointsToPlot", 1)
    mc_0.set_variable("Transient_Number_Cycles", 1)
    mc_0.clear_duty_cycle()
    mc_0.set_variable("Duty_Cycle_Input_Type", 0)  # set to PU
    mc_0.set_variable("Duty_Cycle_Definition", 0)

    # %%
    #  Save file to a temporary folder location.
    working_folder = os.path.join(tempfile.gettempdir(), "advanced_examples")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    ref_mot_name = "e10_IPM_ref"

    os.mkdir(working_folder)
    os.mkdir(working_folder + "/" + ref_mot_name)
    ref_mot_path = working_folder + "/" + ref_mot_name
    mc_0.save_to_file(ref_mot_path + ".mot")

    # %%
    # Create a function for defining a Duty Cycle in Motor-CAD from a Python dictionary.
    def define_duty_cycle(duty_cycle):
        mc_0.set_variable("Duty_Cycle_Num_Periods", duty_cycle["duty_cycle_periods"])
        for i in range(duty_cycle["duty_cycle_periods"]):
            mc_0.set_array_variable("Duty_Cycle_Time", i, duty_cycle["duty_cycle_time"][i])
            mc_0.set_array_variable("Duty_Cycle_Points", i, duty_cycle["duty_cycle_points"][i])
            mc_0.set_array_variable(
                "Duty_Cycle_Torque_Start", i, duty_cycle["duty_cycle_torque"][i]
            )
            mc_0.set_array_variable(
                "Duty_Cycle_Speed_Start", i, duty_cycle["duty_cycle_speed_start"][i]
            )
            mc_0.set_array_variable(
                "Duty_Cycle_Speed_End", i, duty_cycle["duty_cycle_speed_end"][i]
            )
        duty_cycle_name = duty_cycle["name"]
        mc_0.save_duty_cycle(f"{ref_mot_path}\\{duty_cycle_name}.dat")

    # %%
    # Define four separate Duty Cycles based on Torque and Speed definition as Python dictionaries.
    duty_cycle_1 = {
        "name": "duty_cycle_1",
        "duty_cycle_periods": 5,
        "duty_cycle_time": [20, 10, 10, 30, 15],  # 85 s
        "duty_cycle_points": [4, 2, 2, 6, 3],
        "duty_cycle_torque": [0.2, 0.8, 0.5, 1, 0.1],
        "duty_cycle_speed_start": [3000, 3000, 6000, 0, 4000],
        "duty_cycle_speed_end": [3000, 6000, 0, 4000, 3000],
    }

    duty_cycle_2 = {
        "name": "duty_cycle_2",
        "duty_cycle_periods": 5,
        "duty_cycle_time": [10, 30, 5, 20, 20],
        "duty_cycle_points": [2, 6, 1, 4, 4],
        "duty_cycle_torque": [0.1, 0.6, 1, 0.8, 0.2],
        "duty_cycle_speed_start": [500, 1000, 8000, 8000, 800],
        "duty_cycle_speed_end": [1000, 8000, 8000, 800, 500],
    }

    duty_cycle_3 = {
        "name": "duty_cycle_3",
        "duty_cycle_periods": 6,
        "duty_cycle_time": [25, 15, 10, 20, 5, 10],
        "duty_cycle_points": [5, 3, 2, 6, 1, 2],
        "duty_cycle_torque": [0.8, 1, 0.2, 0.5, 1, 0.2],
        "duty_cycle_speed_start": [2000, 2000, 5000, 10000, 10000, 5000],
        "duty_cycle_speed_end": [2000, 5000, 10000, 10000, 5000, 2000],
    }

    duty_cycle_4 = {
        "name": "duty_cycle_4",
        "duty_cycle_periods": 5,
        "duty_cycle_time": [30, 15, 15, 5, 20],
        "duty_cycle_points": [6, 3, 3, 1, 4],
        "duty_cycle_torque": [0.4, 0.9, 0.2, 0.4, 0.6],
        "duty_cycle_speed_start": [0, 4000, 4000, 8000, 2000],
        "duty_cycle_speed_end": [4000, 4000, 8000, 2000, 0],
    }

    # %%
    # Run the ``define_duty_cycle`` function to define the four duty cycles and save these to the
    # working folder.
    duty_cycles = [duty_cycle_1, duty_cycle_2, duty_cycle_3, duty_cycle_4]
    for i in duty_cycles:
        define_duty_cycle(i)

    mc_0.quit()

    # %%
    # Run parallel processes
    # ----------------------
    # Run the parallel duty cycle processes.
    parallel_workers = 4

    # create a worker pool and assign the initialisation function
    p = Pool(
        processes=parallel_workers,
        initializer=initialise_motorcad_instances,
        initargs=[ref_mot_path],
    )

    # Run the calculation. Iterate through inputs. Python handles scheduling,queuing and ordering
    duty_cycle_results = p.map(run_motorcad_duty_cycle, duty_cycles)

    it = p.imap(close_motorcad_instances, range(parallel_workers))
    for i in range(parallel_workers):
        it.next()

    for i in range(len(duty_cycle_results)):
        duty_cycle_result = duty_cycle_results[i]
        time = duty_cycle_result["Time"]
        av_winding_temp = duty_cycle_result["Stator_Winding_Temp_Average"]
        plt.figure(i + 1)
        plt.plot(time, av_winding_temp)
        plt.xlabel("Time [s]")
        plt.ylabel("Average Winding Temperature [°C]")
        plt.show()

# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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
.. _ref_oil_cooling_calib:

Motor-CAD oil cooling calibration example script
================================================

This example shows a calibration workflow for oil spray cooling in Motor-CAD.

"""

from multiprocessing import Pool

# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
# Import ``Pool`` from multiprocessing for controlling multiple Motor-CAD processes in parallel.
import ansys.motorcad.core as pymotorcad


# %%
# Define functions
# ----------------
# Define a function to launch and connect to an instance of Motor-CAD. Create a global ``mc``
# variable to exist as a
# separate global variable in each parallel worker and process.
def open_MotorCAD_instances():
    global mc
    mc = pymotorcad.MotorCAD()
    mc.set_variable("MessageDisplayState", 2)  # Disable popup messages


# %%
# Define a function to close the Motor-CAD instances. You should call this function after the
# processes have been
# completed by the parallel workers.
def close_MotorCAD_instances(dummyarg):
    mc.quit()  # quits each instance of Motor-CAD


# %%
# Define a function for the parallel processes to be carried out by each parallel worker.
def motorcad_process(num):
    mc.load_template("e10")
    mc.show_message(f"I'm worker number {num}!")


# %%
# Run the parallel processes
# --------------------------
# Set up parallel workers and perform optimisation.
#
# Define a boolean to determine whether to use parallel processing. If ``True``, parallel processing
# will be used to run
# processes concurrently in multiple Motor-CAD instances.
# If ``False``, all processes will be run by a single Motor-CAD instance in succession.
use_parallel_processing = False

# %%
# Define a list of processes.
process_num = [1, 2, 3, 4, 5, 6, 7, 8]

# %%
# Define an ``if`` statement that determines whether to use parallel processing.
# To use the Python multiprocessing, it is necessary to use the ``if __name__ == '__main__':`` idiom
# in the main module.
#
# To run the parallel processes:
#
# * Create a process pool object using the ``Pool`` function. Set the number of parallel workers and
# set the
#   ``initializer`` function.
#
# * Use ``startmap`` to call the ``motorcad_process`` function on parallel workers. Use ``zip`` to
# provide the necessary
# arguments.
#
# * Close each Motor-CAD instance when the processes are complete.
#
# If not using parallel processes, run the ``open_MotorCAD_instances`` function, then
# loop through the
# process, calling
# the process function before closing Motor-CAD.

if use_parallel_processing:
    if __name__ == "__main__":
        ParallelWorkers = 4

        p = Pool(processes=ParallelWorkers, initializer=open_MotorCAD_instances)

        # runs calculation, iterating through the list of input vales.
        p.starmap(motorcad_process, zip(process_num))

        it = p.imap(close_MotorCAD_instances, range(ParallelWorkers))
        for i in range(ParallelWorkers):
            it.next()
else:
    open_MotorCAD_instances()

    for num in process_num:
        motorcad_process(num)

    close_MotorCAD_instances(0)

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
Simple multiprocessing example
==============================
This script opens and runs multiple Motor-CAD instances to run processes in parallel.
"""
import multiprocessing

# %%
# Perform required imports
# ------------------------
import time

from dont_include_in_build.counter_functions import counter1, counter2

# %%
# Processes
# ---------
# Code for running single processes and then multiple parallel processes. The processes are timed
# for comparison.
if __name__ == "__main__":
    N = 2 * 10**8
    print("Start processes in series...")
    st = time.time()
    counter1(N)
    counter2(N)
    en = time.time()
    print("time taken = " + str(en - st))

    print("Start processes in parallel...")
    st = time.time()
    p1 = multiprocessing.Process(target=counter1, args=(N,))
    p2 = multiprocessing.Process(target=counter2, args=(N,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
    en = time.time()
    print("time taken = " + str(en - st))

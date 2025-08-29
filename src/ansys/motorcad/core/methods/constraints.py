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

"""Unit containing some exploration of geometric constraints."""
# Geometric constraints are a method by which one can define or refine geometry
# in order to satisfy certain geometric properties, such as tangency of entities,
# angles of lines, etc.
#
# A number of approaches are possible to implement geometric constraints in motorCAD
# The first, most powerful, and extensive option would be to implement a geometric constraint
# solver, one aspect of which is explored below.
# Such a solver would be highly extensive and time-consuming to develop, but would enable a lot of
# powerful and useful techniques, including specifying horizontality, coaxiality, distance, angle,
# or other properties between objects
# The below example shows a function that enforces parallelism between two line entities.
# However, a full system that can solve with respect to several constraints at once would be much
# more extensive, perhaps requiring an iterative and/or numerical approach.

from ansys.motorcad.core.geometry_drawing import draw_objects
from ansys.motorcad.core.geometry_shapes import square


def enforce_parallel(line1, node, line2):
    """Make line1, an entity of node, parallel to line2."""
    for i, entity in enumerate(node.entities):
        if line1 == entity:
            rotation1, rotation2 = (line2.angle - line1.angle) % 180, (
                line1.angle - line2.angle
            ) % 180
            reverse = abs(rotation1) > abs(rotation2)
            if reverse:
                line1.rotate(line1.midpoint, -rotation2)
            else:
                line1.rotate(line1.midpoint, rotation1)
            node.entities[(i - 1) % len(node.entities)].end = line1.start
            node.entities[(i + 1) % len(node.entities)].start = line1.end


reg1 = square(5, 20, 0)
reg2 = square(5, 10, 5)
reg1.name = "square1"
reg1.colour = (255, 255, 255)
reg2.name = "square2"
reg2.colour = (255, 255, 255)

draw_objects([reg1, reg2], draw_points=True, label_regions=True)

enforce_parallel(reg1.entities[0], reg1, reg2.entities[0])

draw_objects([reg1, reg2], draw_points=True, label_regions=True)

reg1 = square(5, 20, 0)
reg2 = square(5, 10, 5)
reg1.name = "square1"
reg1.colour = (255, 255, 255)
reg2.name = "square2"
reg2.colour = (255, 255, 255)

draw_objects([reg1, reg2], draw_points=True, label_regions=True)

enforce_parallel(reg1.entities[-1], reg1, reg2.entities[1])

draw_objects([reg1, reg2], draw_points=True, label_regions=True)


# One constraint solving method might make use of graph-based solving methods,
# including a degrees of freedom or constructive approach.
#
# In the former approach, geometric objects are represented as vertices labeled
# with their degrees of freedom. So in 2D space, a point would have 2, a circle 3, etc.
# Then, constraints are subtracted from the degrees of freedom (for instance, a distance
# constraint removes 1 degree of freedom) and the graph is analyzed for a solution.

# The latter approach is more common, and as such there are more resources as to its use and
# development. In this two-phase method, the first phase consists of generating a graph with,
# again, vertices representing geometric objects and edges the constraints between them. Again,
# vertices are given weights based on the degrees of freedom. However, in this case, the edges
# too are given weights, based on the number of coordinates of its defining vertices that are
# determined by the edge's defining constraint.
# Next, the graph is further analyzed, often by decomposing the graph into tri-connected
# components or other structures which correspond to systems of equations easy to solve.
#
#
#
# Given the current state of pymotorCAD scripting workflow, developing an entire geometric
# constraint solver seems useful, but also extensive and radical. But to implement simpler
# geometric constraints raises a problem, already seen in the above example function.
# Without a full solver, enforcing any geometric constraints at all will result in nonsensical
# or invalid geometry, with unchanged entities connecting to the old entity locations.
# This is because the properties of the defining geometry that we want to preserve, such as
# anticlockwise geometry and adjacent entities with the same ending and starting points need
# to be expressed as geometric constraints and used in a full solver in addition to whatever
# constraints the user wishes to specify. In other words, without a full constraint solver,
# even the very simplest of constraints is difficult to enforce.
#
# One approach to rectify this issue is that seen above, simply changing the ending or starting
# point of the connecting entities in order to make sure geometry is still somewhat valid, or
# just translating or rotating the entities of the region as a whole.
# This approach would likely mean that only one explicit constraint can reliably be enforced
# on a region at a time, as any attempt to enforce a second would often falsify the first.
# This might be an acceptable tradeoff given the time it would take to develop such functions,
# particularly if a list of attempted constraints and their success could be accessed by the user.


# Further expanding on this approach, perhaps constraint enforcement functions might be given
# arguments defining how they reshape a region or regions. For example. in the below function,
# the region can either be deformed or rotated to enforce the parallelism constraint, depending
# on what the user prefers.


def enforce_parallel_2(line1, node, line2, mode):
    """Make line1, an entity of node, parallel to line2."""
    rotation1, rotation2 = (line2.angle - line1.angle) % 180, (line1.angle - line2.angle) % 180
    reverse = abs(rotation1) > abs(rotation2)

    if mode == "deform":
        for i in range(0, len(node.entities)):
            if node.entities[i] == line1:
                if reverse:
                    line1.rotate(line1.midpoint, -rotation2)
                else:
                    line1.rotate(line1.midpoint, rotation1)
                    node.entities[(i - 1) % len(node.entities)].end = line1.start
                    node.entities[(i + 1) % len(node.entities)].start = line1.end
    if mode == "rotate":
        if reverse:
            node.rotate(line1.midpoint, -rotation2)
        else:
            node.rotate(line1.midpoint, rotation1)


reg1 = square(5, 20, 0)
reg2 = square(5, 10, 5)
reg1.name = "square1"
reg1.colour = (255, 255, 255)
reg2.name = "square2"
reg2.colour = (255, 255, 255)

draw_objects([reg1, reg2], draw_points=True, label_regions=True)

enforce_parallel_2(reg1.entities[0], reg1, reg2.entities[0], "deform")

draw_objects([reg1, reg2], draw_points=True, label_regions=True)

reg1 = square(5, 20, 0)
reg2 = square(5, 10, 5)
reg1.name = "square1"
reg1.colour = (255, 255, 255)
reg2.name = "square2"
reg2.colour = (255, 255, 255)

draw_objects([reg1, reg2], draw_points=True, label_regions=True)

enforce_parallel_2(reg1.entities[0], reg1, reg2.entities[0], "rotate")

draw_objects([reg1, reg2], draw_points=True, label_regions=True)

# In all, while a full geometric constraint solver would be both powerful and useful,
# a more limited approach is likely preferable for now. The most promising of these limited
# approaches seems likely to be constraint enforcement functions that modify existing geometry
# to match a single supplied constraint, with options on how exactly that enforcement is to be
# performed.

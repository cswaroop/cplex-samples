#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: admipex2.py
# Version 12.6  
# ---------------------------------------------------------------------------
# Licensed Materials - Property of IBM
# 5725-A06 5725-A29 5724-Y48 5724-Y49 5724-Y54 5724-Y55 5655-Y21
# Copyright IBM Corporation 2009, 2013. All Rights Reserved.
# 
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with
# IBM Corp.
# ---------------------------------------------------------------------------
#
# admipex2.py -  Use the heuristic callback
#                for optimizing a MIP problem
#
# To run this example, the user must specify a problem file.
#
# You can run this example at the command line by
#
#    python admipex2.py <filename>
#
# or within the python interpreter by
#
# >>> import admipex2
#
# The user will be prompted to chose the filename.

import sys
from math import fabs

import cplex
from cplex.callbacks import HeuristicCallback

class RoundDown(HeuristicCallback):

    def __call__(self):
        self.times_called += 1
        feas      = self.get_feasibilities()
        vars = []
        for j in range(len(feas)):
            if feas[j] == self.feasibility_status.feasible:
                vars.append(j)
        self.set_solution([vars, [0.0] * len(vars)])


def admipex2(filename):

    c = cplex.Cplex(filename)
    
    round_down = c.register_callback(RoundDown)
    round_down.times_called = 0
    
    c.parameters.mip.tolerances.mipgap.set(1.0e-6)
    c.parameters.mip.strategy.search.set(c.parameters.mip.strategy.search.values.traditional)

    c.solve()

    solution = c.solution

    # solution.get_status() returns an integer code
    print "Solution status = " , solution.get_status(), ":",
    # the following line prints the corresponding string
    print solution.status[solution.get_status()]
    print "Objective value = " , solution.get_objective_value()
    print
    x = solution.get_values(0, c.variables.get_num()-1)
    for j in range(c.variables.get_num()):
        if fabs(x[j]) > 1.0e-10:
            print "Column %d: Value = %17.10g" % (j, x[j])

    print "RoundDown was called ", round_down.times_called, "times"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: admipex2.py filename"
        print "  filename   Name of a file, with .mps, .lp, or .sav"
        print "             extension, and a possible, additional .gz"
        print "             extension"
        sys.exit(-1)
    admipex2(sys.argv[1])
else:
    prompt = """Enter the path to a file with .mps, .lp, or .sav
extension, and a possible, additional .gz extension:
The path must be entered as a string; e.g. "my_model.mps"\n """
    admipex2(input(prompt))

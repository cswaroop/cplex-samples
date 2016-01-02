#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: admipex3.py
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
# admipex3.py - Using the branch callback for optimizing a MIP 
#               problem with Special Ordered Sets Type 1, with all 
#               the variables binary
#
# To run this example, command line arguments are required:
#
#     python admipex3.py filename
#
#  where
#
#     filename  Name of the file, with .mps, .lp, or .sav
#               extension, and a possible additional .gz 
#               extension.
#
# Example:
#
#     python admipex3.py myexample.mps
#
# You can also run this example within the python interpreter by
#
# >>> import admipex3
#
# The user will be prompted to chose the filename.

from math import floor

import cplex
from cplex.callbacks import BranchCallback

import sys


class SOSBranch(BranchCallback):
    
    def __call__(self):
        bestf = 1e-4
        besti = -1
        bestj = -1
        solvals = self.get_values()
        sosfeas = self.get_SOS_feasibilities()
        for i in range(len(sosfeas)):
            if sosfeas[i] == self.feasibility_status.infeasible:
                sosind = self.cpx.SOS.get_sets(i).ind
                for j in sosind:
                    x = solvals[j]
                    frac = x - floor(x)
                    frac = min(frac, 1-frac)
                    if frac > bestf:
                        bestf = frac
                        besti = i
                        bestj = j

        if bestj >= 0:
            x = self.get_values(bestj)
            self.make_branch(self.get_objective_value(),
                             [(bestj, "U", floor(x))])
            self.make_branch(self.get_objective_value(),
                             [(bestj, "L", floor(x)+1)])


def admipex3(filename):

    from math import fabs

    c = cplex.Cplex(filename)
        
    c.set_log_stream(sys.stdout)
    c.set_results_stream(sys.stdout)

    sos_branch = c.register_callback(SOSBranch)
    sos_branch.cpx = c
        
    c.parameters.mip.strategy.search.set(c.parameters.mip.strategy.search.values.traditional)
    
    c.solve()
        
    solution = c.solution
        
    print "Solution status = " , solution.get_status()
    print "Objective value = " , solution.get_objective_value()
    print
    x = solution.get_values(0, c.variables.get_num()-1)
    for j in range(c.variables.get_num()):
        if fabs(x[j]) > 1.0e-10:
            print "Column %d: Value = %17.10g" % (j, x[j])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: admipex3.py filename"
        print "  filename   Name of a file, with .mps, .lp, or .sav"
        print "             extension, and a possible, additional .gz"
        print "             extension"
        sys.exit(-1)
    admipex3(sys.argv[1])
else:
    prompt = """Enter the path to a file with .mps, .lp, or .sav
extension, and a possible, additional .gz extension:
The path must be entered as a string; e.g. "my_model.mps"\n """
    admipex3(input(prompt))

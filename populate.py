#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: populate.py
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
# populate.py - Reading a MIP problem and generating multiple solutions.
#
# To run this example, command line arguments are required:
#
#    python populate.py <filename> 
# 
# Alternatively, this example can be run from the python interpreter by
# 
# >>> import populate
#
# The user will be prompted to chose the filename.

import cplex
from cplex.exceptions import CplexSolverError
import sys

epszero = 1e-10

def populate(filename):

    c = cplex.Cplex(filename)

    # set the solution pool relative gap parameter to obtain solutions
    # of objective value within 10% of the optimal 
    c.parameters.mip.pool.relgap.set (0.1)
    
    try:
        c.populate_solution_pool()
    except CplexSolverError:
        print "Exception raised during populate"
        return

    print
    # solution.get_status() returns an integer code
    print "Solution status = " , c.solution.get_status(), ":",
    # the following line prints the corresponding string
    print c.solution.status[c.solution.get_status()]

    numcols = c.variables.get_num()

    # Print information about the incumbent
    print
    print "Objective value of the incumbent  = ", \
          c.solution.get_objective_value()
    x = c.solution.get_values()
    for j in range(numcols):
        print "Incumbent: Column %d:  Value = %10f" % (j, x[j])

    # Print information about other solutions
    print
    numsol = c.solution.pool.get_num()
    print "The solution pool contains %d solutions." % numsol

    numsolreplaced = c.solution.pool.get_num_replaced()
    print "%d solutions were removed due to the solution pool relative gap parameter." % numsolreplaced
    
    numsoltotal = numsol + numsolreplaced
    print "In total, %d solutions were generated." % numsoltotal

    meanobjval = c.solution.pool.get_mean_objective_value()
    print "The average objective value of the solutions is %.10g." % meanobjval

    # write out the objective value of each solution and its
    # difference to the incumbent 
    names = c.solution.pool.get_names()
    
    print
    print "Solution        Objective       Number of variables"
    print "                value           that differ compared to"
    print "                                the incumbent"

    for i in range(numsol):        

        objval_i = c.solution.pool.get_objective_value(i)
        
        x_i = c.solution.pool.get_values(i)
        
        # compute the number of variables that differ in solution i
        # and in the incumbent
        numdiff = 0;
        for j in range (numcols):
            if abs (x_i[j] - x[j]) > epszero:
                numdiff = numdiff + 1
        print "%-15s %-10g      %d / %d" % (names[i], objval_i, numdiff, numcols)
 
            
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: populate.py filename"
        print "  filename   Name of a file, with .mps, .lp, or .sav"
        print "             extension, and a possible, additional .gz"
        print "             extension"
        sys.exit(-1)
    populate(sys.argv[1])
else:
    prompt = """Enter the path to a file with .mps, .lp, or .sav
extension, and a possible, additional .gz extension:
The path must be entered as a string; e.g. "my_model.mps"\n """
    fname = input(prompt)
    populate(fname)

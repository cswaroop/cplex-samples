#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: cutstock.py
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
# cutstock.py -- using column generation
#
# Problem Description:
# 
# The cutting stock problem in this example is sometimes known in math
# programming terms as a knapsack problem with reduced costs in the
# objective function. Generally, a cutting stock problem begins with a
# supply of rolls of material of fixed length (the stock). Strips are cut
# from these rolls. All the strips cut from one roll are known together as
# a pattern. The point of this example is to use as few rolls of stock as
# possible to satisfy some specified demand of strips. By convention, it is
# assumed that only one pattern is laid out across the stock; consequently,
# only one dimension (the width) of each roll of stock is important.
#
# To run from the command line, use
#
#    python cutstock.py
#
# To run from within the python interpreter, use
#
# >>> import cutstock

import cplex
from cplex.exceptions import CplexSolverError
from cplex import SparsePair
from inputdata import read_dat_file
import sys

RC_EPS = 1.0e-6

def report1(cut):
    """Print a report about the current solution in the cutting
    optimization problem given by the cut argument.
    """
    
    print
    print "Using " + str(cut.solution.get_objective_value()) + " rolls"
    print
    for v in range(cut.variables.get_num()):
        print "  Cut" + str(v) + " = " + str(cut.solution.get_values(v))
    print
    for c in range(cut.linear_constraints.get_num()):
        print "  Fill" + str(c) + " = " + str(cut.solution.get_dual_values(c))
    print

def report2(pat, use):
    """Print a report about the current solution in the pattern generation
    problem given by the pat argument. The use argument specifies the indices
    of variables that shall appear in the report.
    """
    print
    print "Reduced cost is " + str(pat.solution.get_objective_value())
    print
    if pat.solution.get_objective_value() <= -RC_EPS:
        for v in use:
            print "  Use" + str(v) + " = " + str(pat.solution.get_values(v))
        print

def report3(cut):
    """Print the final report for the current solution in the cutting
    optimization problem given by the cut argument.
    """
    print
    print "Best integer solution uses " + str(cut.solution.get_objective_value()) + " rolls"
    print
    for v in range(cut.variables.get_num()):
        print "  Cut" + str(v) + " = " + str(cut.solution.get_values(v))


if __name__ == "__main__":
    # Input data. If no file is given on the command line then use a
    # default file name. The data read is
    # width  - the width of the the roll,
    # size   - the sie of each strip,
    # amount - the demand for each strip.
    datafile = "data/cutstock.dat"
    if len(sys.argv) < 2:
        print "Default data file : " + datafile
    else:
        datafile = sys.argv[1]
    width, size, amount = read_dat_file(datafile)


    # Setup cutting optimization (master) problem.
    # This is the problem to which columns will be added in the loop
    # below.
    cut = cplex.Cplex()
    cutcons = range(len(amount))   # constraint indices
    cutvars = range(len(size))     # variable indices
    cut.variables.add(obj = [1] * len(cutvars))
    # Add constraints. They have empty left-hand side initially. The
    # left-hand side is filled in the next loop.
    cut.linear_constraints.add(lin_expr = [SparsePair()] * len(cutcons),
                               senses = ["G"] * len(cutcons),
                               rhs = amount)
    for v in cutvars:
        cut.linear_constraints.set_coefficients(v, v, int(width / size[v]))

    # Setup pattern generation (worker) problem.
    # The constraints and variables in this problem always stay the same
    # but the objective function will change during the column generation
    # loop.
    pat = cplex.Cplex();
    use = range(len(size))         # variable indices
    pat.variables.add(types = [pat.variables.type.integer] * len(use))
    # Add a constant 1 to the objective.
    pat.variables.add(obj = [1], lb = [1], ub = [1])
    # Single constraint: total size must not exceed the width.
    totalsize = SparsePair(ind = use, val = size)
    pat.linear_constraints.add(lin_expr = [totalsize],
                               senses = ["L"],
                               rhs = [width])
    pat.objective.set_sense(pat.objective.sense.minimize)

    
    # Column generation procedure
    while True:
        
        # Optimize over current patterns
        cut.solve()
        report1(cut)

        # Find and add new pattern. The objective function of the
        # worker problem is constructed from the dual values of the
        # constraints of the master problem.
        price = map(lambda d: -d, cut.solution.get_dual_values(cutcons))        
        pat.objective.set_linear(zip(use, price))
        pat.solve()
        report2(pat, use)

        # If reduced cost (worker problem objective function value) is
        # non-negative we are optimal. Otherwise we found a new column
        # to be added. Coefficients of the new column are given by the
        # optimal solution vector to the worker problem.
        if pat.solution.get_objective_value() > -RC_EPS:
            break
        newpat = pat.solution.get_values(use)

        # The new pattern constitutes a new variable in the cutting
        # optimization problem. Create that variable and add it to all
        # constraints with the coefficients read from the optimal solution
        # of the pattern generation problem.
        idx = cut.variables.get_num()
        cut.variables.add(obj = [1.0] )
        cut.linear_constraints.set_coefficients(zip(cutcons,
                                                    [idx] * len(use),
                                                    newpat))
        cutvars.append(idx)

    # Perform a final solve on the cutting optimization problem.
    # Turn all variables into integers before doing that.
    cut.variables.set_types(zip(cutvars,
                                [cut.variables.type.integer] * len(cutvars)))
    cut.solve()
    report3(cut)
    print "Solution status = ", cut.solution.get_status()

#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: mipex1.py
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
# mipex1.py - Entering and optimizing a mixed integer programming problem
#             Demonstrates different methods for creating a problem.
#
# The user has to choose the method on the command line:
#
#    python mipex1.y -r     generates the problem by adding rows
#    python mipex1.y -c     generates the problem by adding columns
#    python mipex1.y -n     generates the problem by adding a
#                           list of coefficients
#
# Alternatively, this example can be run from the python interpreter by
# 
# >>> import mipex1
#
# The user will be prompted to chose the method.
#
# The MIP problem solved in this example is:
#
#   Maximize  x1 + 2 x2 + 3 x3 + x4
#   Subject to
#      - x1 +   x2 + x3 + 10 x4 <= 20
#        x1 - 3 x2 + x3         <= 30
#               x2      - 3.5x4  = 0
#   Bounds
#        0 <= x1 <= 40
#        0 <= x2
#        0 <= x3
#        2 <= x4 <= 3
#   Integers
#       x4

import cplex
from cplex.exceptions import CplexError
import sys

# data common to all populateby functions
my_obj      = [1.0, 2.0, 3.0, 1.0]
my_ub       = [40.0, cplex.infinity, cplex.infinity, 3.0]
my_lb       = [0.0, 0.0, 0.0, 2.0]
my_ctype    = "CCCI"
my_colnames = ["x1", "x2", "x3", "x4"]
my_rhs      = [20.0, 30.0, 0.0]
my_rownames = ["r1", "r2", "r3"]
my_sense    = "LLE"

import cplex

def populatebyrow(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.variables.add(obj = my_obj, lb = my_lb, ub = my_ub, types = my_ctype,
                       names = my_colnames)

    rows = [[["x1","x2","x3","x4"],[-1.0, 1.0, 1.0, 10.0]],
            [["x1","x2","x3"],[1.0, -3.0, 1.0]],
            [["x2","x4"],[1.0,-3.5]]]

    prob.linear_constraints.add(lin_expr = rows, senses = my_sense,
                                rhs = my_rhs, names = my_rownames)
    
def populatebycolumn(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)
    
    prob.linear_constraints.add(rhs = my_rhs, senses = my_sense,
                                names = my_rownames)

    c = [[["r1","r2"],[-1.0, 1.0]],
         [["r1","r2","r3"],[1.0, -3.0, 1.0]],
         [["r1","r2"],[1.0, 1.0]],
         [["r1","r3"],[10.0, -3.5]]]
    
    prob.variables.add(obj = my_obj, lb = my_lb, ub = my_ub,
                       names = my_colnames, types = my_ctype, columns = c)

def populatebynonzero(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)
    
    prob.linear_constraints.add(rhs = my_rhs, senses = my_sense,
                                names = my_rownames)
    prob.variables.add(obj = my_obj, lb = my_lb, ub = my_ub, types = my_ctype,
                       names = my_colnames)
    
    rows = [0,0,0,0,1,1,1,2,2]
    cols = [0,1,2,3,0,1,2,1,3]
    vals = [-1.0, 1.0, 1.0, 10.0, 1.0, -3.0, 1.0, 1.0, -3.5]
    
    prob.linear_constraints.set_coefficients(zip(rows, cols, vals))
    
def mipex1(pop_method):

    try:
        my_prob = cplex.Cplex()
        
        if pop_method == "r":
            handle = populatebyrow(my_prob)
        if pop_method == "c":
            handle = populatebycolumn(my_prob)
        if pop_method == "n":
            handle = populatebynonzero(my_prob)
            
        my_prob.solve()
    except CplexError, exc:
        print exc
        return

    print
    # solution.get_status() returns an integer code
    print "Solution status = " , my_prob.solution.get_status(), ":",
    # the following line prints the corresponding string
    print my_prob.solution.status[my_prob.solution.get_status()]
    print "Solution value  = ", my_prob.solution.get_objective_value()

    numcols = my_prob.variables.get_num()
    numrows = my_prob.linear_constraints.get_num()

    slack = my_prob.solution.get_linear_slacks()
    x     = my_prob.solution.get_values()

    for j in range(numrows):
        print "Row %d:  Slack = %10f" % (j, slack[j])
    for j in range(numcols):
        print "Column %d:  Value = %10f" % (j, x[j])


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in  ["-r", "-c", "-n"]:
        print "Usage: mipex1.py -X"
        print "   where X is one of the following options:"
        print "      r          generate problem by row"
        print "      c          generate problem by column"
        print "      n          generate problem by nonzero"
        print " Exiting..."
        sys.exit(-1)
    mipex1(sys.argv[1][1])
else:
    prompt = """Enter the letter indicating how the problem data should be populated:
    r : populate by row
    c : populate by column
    n : populate by nonzero\n ? > """
    r = 'r'
    c = 'c'
    n = 'n'
    mipex1(input(prompt))

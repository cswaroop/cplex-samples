#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: miqpex1.py
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
# miqpex1.py -  Entering and optimizing a MIQP problem.
#
# To run from the command line, use
#
# python miqpex1.py
# 
# To run from within the python interpreter, use
#
# >>> import miqpex1
#

import cplex

def setproblemdata(p):
    p.set_problem_name ("example")

    p.objective.set_sense(p.objective.sense.maximize)

    p.linear_constraints.add(rhs = [20.0, 30.0, 0.0], senses = "LLE")

    obj  = [1.0, 2.0, 3.0, 1.0]
    ub   = [40.0, cplex.infinity, cplex.infinity, 3.0]
    cols = [[[0,1],[-1.0, 1.0]],
            [[0,1,2],[ 1.0,-3.0, 1.0]],
            [[0,1],[ 1.0, 1.0]],
            [[0,2], [ 10.0,-3.5]]]
    
    p.variables.add(obj = obj, ub = ub, columns = cols, 
                    types="CCCI", names = ["x1", "x2", "x3", "x4"])

    qmat = [[[0,1],[-33.0, 6.0]],
            [[0,1,2],[ 6.0,-22.0, 11.5]],
            [[1,2],[ 11.5, -11.0]],
            [[3],[0.0]]]


    p.objective.set_quadratic(qmat)

    
def miqpex1():

    p = cplex.Cplex()
    setproblemdata(p)

    p.solve()

    sol = p.solution

    # solution.get_status() returns an integer code
    print "Solution status = " , sol.get_status(), ":",
    # the following line prints the corresponding string
    print sol.status[sol.get_status()]
    print "Solution value  = ", sol.get_objective_value()

    numrows = p.linear_constraints.get_num()

    for i in range(numrows):
        print "Row %d:  Slack = %10f" % (i, sol.get_linear_slacks(i))

    numcols = p.variables.get_num()

    for j in range(numcols):
        print "Column %d:  Value = %10f" % (j, sol.get_values(j))

    p.write("miqpex1.lp")

miqpex1()

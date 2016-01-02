#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: qpex1.py
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
# qpex1.py -  Entering and optimizing a quadratic programming
#             problem.
#
# To run from the command line, use
#
# python qpex1.py
# 
# To run from within the python interpreter, use
#
# >>> import qpex1
#

import cplex

def setproblemdata(p):
    p.objective.set_sense(p.objective.sense.maximize)

    p.linear_constraints.add(rhs = [20.0, 30.0], senses = "LL")

    obj  = [1.0, 2.0, 3.0]
    ub   = [40.0, cplex.infinity, cplex.infinity]
    cols = [[[0,1],[-1.0, 1.0]],
            [[0,1],[ 1.0,-3.0]],
            [[0,1],[ 1.0, 1.0]]]
    
    p.variables.add(obj = obj, ub = ub, columns = cols,
                    names = ["one", "two", "three"])

    qmat = [[[0,1],[-33.0, 6.0]],
            [[0,1,2],[ 6.0,-22.0, 11.5]],
            [[1,2],[ 11.5, -11.0]]]


    p.objective.set_quadratic(qmat)

    
def qpex1():

    p = cplex.Cplex()
    setproblemdata(p)

    p.solve()

    # solution.get_status() returns an integer code
    print "Solution status = " , p.solution.get_status(), ":",
    # the following line prints the corresponding string
    print p.solution.status[p.solution.get_status()]
    print "Solution value  = ", p.solution.get_objective_value()

    numrows = p.linear_constraints.get_num()

    for i in range(numrows):
        print "Row ", i, ":  ",
        print "Slack = %10f " %  p.solution.get_linear_slacks(i),
        print "Pi = %10f" % p.solution.get_dual_values(i)

    numcols = p.variables.get_num()

    for j in range(numcols):
        print "Column ", j, ":  ",
        print "Value = %10f " % p.solution.get_values(j),
        print "Reduced Cost = %10f" % p.solution.get_reduced_costs(j)

qpex1()

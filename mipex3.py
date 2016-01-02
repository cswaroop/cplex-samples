#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: mipex3.py
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
# mipex3.py - Entering and optimizing a MIP problem with SOS sets
#             and priority orders.  Is a modification of mipex1.py.
#             Note that the problem solved is slightly different than
#             mipex1.py so that the output is interesting.
#
# To run from the command line, use
#
#    python mipex3.py
# 
# To run from within the python interpreter, use
#
# >>> import mipex3

import cplex

def setproblemdata(p):

    p.objective.set_sense(p.objective.sense.maximize)

    p.linear_constraints.add(rhs = [20.0, 30.0, 0.0], senses = "LLE")

    obj  = [1.0, 2.0, 3.0, 1.0]
    lb   = [0.0, 0.0, 0.0, 2.0]
    ub   = [40.0, cplex.infinity, cplex.infinity, 3.0]
    cols = [[[0,1],[-1.0, 1.0]],
            [[0,1,2],[ 1.0,-3.0,1.0]],
            [[0,1],[ 1.0, 1.0]],
            [[0,2],[10.0, -3.5]]]
    
    p.variables.add(obj = obj, lb = lb, ub = ub, columns = cols,
                    types = "CIII", names = ["0", "1", "2", "3"])
    p.SOS.add(type = "1", SOS = [["2","3"], [25.0, 18.0]])

    p.order.set([(1,8,p.order.branch_direction.up),
                 ("3",7,p.order.branch_direction.down)])
    p.order.write("mipex3.ord")

    return
    
def mipex3():

    p = cplex.Cplex()

    p.parameters.preprocessing.presolve.set(p.parameters.preprocessing.presolve.values.off)
    p.parameters.preprocessing.aggregator.set(0)
    p.parameters.mip.interval.set(1)

    setproblemdata(p)

    print
    print "Parameters not at their default value:"
    print "  ", p.parameters.get_changed()
    print
    
    p.solve()

    sol = p.solution

    p.write("mip3.mps")

    print
    # solution.get_status() returns an integer code
    print "Solution status = " , sol.get_status(), ":",
    # the following line prints the corresponding string
    print sol.status[sol.get_status()]
    print "Solution value  = ", sol.get_objective_value()

    numcols = p.variables.get_num()
    numrows = p.linear_constraints.get_num()

    for j in range(numrows):
        print "Row %d:  Slack = %10f" % (j, sol.get_linear_slacks(j))
    for j in range(numcols):
        print "Column %d:  Value = %10f" % (j, sol.get_values(j))


mipex3()

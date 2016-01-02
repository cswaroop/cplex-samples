#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: lpex3.py
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
# lpex3.py - Modifying a previously solved problem.
# 
# We initially set up a network problem and solve it using the Network
# method.  Additional constraints are then added and the Dual Simplex
# method is used to find the new optimum.
#
# To run this example from the command line, use
#
#    python lpex3.py
#
# To run from within the python interpreter, use
#
# >>> import lpex3

import cplex

def lpex3():
    c = cplex.Cplex()
    c.parameters.simplex.display.set(2)
    c.parameters.read.datacheck.set(1)
    c.linear_constraints.add(senses = "EEEEEEE",
                             rhs = [-1.0, 4.0, 1.0, 1.0, -2.0, -2.0, -1.0])
    flow = [[[1, 6], [ 1.0, -1.0]],
            [[2, 6], [ 1.0, -1.0]],
            [[3, 6], [ 1.0, -1.0]],
            [[2, 5], [ 1.0, -1.0]],
            [[3, 5], [ 1.0, -1.0]],
            [[1, 4], [ 1.0, -1.0]],
            [[2, 4], [ 1.0, -1.0]],
            [[0, 1], [-1.0,  1.0]],
            [[0, 2], [-1.0,  1.0]],
            [[0, 3], [ 1.0, -1.0]],
            [[4, 5], [-1.0,  1.0]],
            [[4, 6], [ 1.0, -1.0]]]
    
    # lower bounds are set to their default value of 0.0
    c.variables.add(obj = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                           1.0, 0.0, 0.0, 0.0, 2.0, 2.0],
                    ub  = [50.0] * 12, columns = flow)
    c.parameters.lpmethod.set(c.parameters.lpmethod.values.network)
    c.solve()
    print "After network optimization, objective is ", \
          c.solution.get_objective_value()
    
    cons = [[[10, 11], [2.0, 5.0]],
            [[0, 2, 5], [1.0, 1.0, 1.0]]]
    c.linear_constraints.add(lin_expr = cons, senses = "EE", rhs = [2.0, 3.0])
    c.parameters.lpmethod.set(c.parameters.lpmethod.values.dual)
    c.solve()

    # solution.get_status() returns an integer code
    print "Solution status = " , c.solution.get_status(), ":",
    # the following line prints the corresponding string
    print c.solution.status[c.solution.get_status()]
    print "Solution value:   ", c.solution.get_objective_value()
    print "Solution is:"
    x = c.solution.get_values()
    for j in range(c.variables.get_num()):
        print "x[%d] = %f" % (j, x[j])
    c.write("lpex3.sav")
    
lpex3()

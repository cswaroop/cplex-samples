#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: qcpex1.py
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
# qcpex1.py - Entering and optimizing a quadratically constrained
#             problem.
#
# To run from the command line, use
#
#    python qcpex1.py
# 
# To run from within the python interpreter, use
#
# >>> import qcpex1

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
    Q = cplex.SparseTriple(ind1 = ["one","two","three"], ind2 = [0,1,2],
                           val = [1.0] * 3)
    p.quadratic_constraints.add(rhs = 1.0, quad_expr = Q, name = "Q")

    
def qcpex1():

    p = cplex.Cplex()
    setproblemdata(p)

    p.solve()

    # solution.get_status() returns an integer code
    print "Solution status = " , p.solution.get_status(), ":",
    # the following line prints the corresponding string
    print p.solution.status[p.solution.get_status()]
    print "Solution value  = ", p.solution.get_objective_value()

    numcols = p.variables.get_num()

    for j in range(numcols):
        print "Column %d:  Value = %10f" % (j, p.solution.get_values(j))

    print p.solution.get_linear_slacks(0)

    print
    print "rhs    = ", p.quadratic_constraints.get_rhs("Q")
    print "sense  = ", p.quadratic_constraints.get_senses(0)
    print "[lin]  = ", p.quadratic_constraints.get_linear_components(0,0) # range
    print "[quad] = ", p.quadratic_constraints.get_quadratic_components([0]) # list
    print "[name] = ", p.quadratic_constraints.get_names() # all as a list

    print
    print "Objective function"
    print " qnnz  = ", p.objective.get_num_quadratic_nonzeros()
    print " quad  = ", p.objective.get_quadratic()
    print " lin   = ", p.objective.get_linear()
    print " sense = ", p.objective.get_sense()

    
qcpex1()

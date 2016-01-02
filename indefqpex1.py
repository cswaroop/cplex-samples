#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: indefqpex1.py
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
# indefqpex1.py -  Entering and optimizing an indefinite quadratic
#                  programming problem.
#
# To run from the command line, use
#
# python indefqpex1.py
# 
# To run from within the python interpreter, use
#
# >>> import indefqpex1
#

import cplex

def solve_and_display(p):
    
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


def indefqpex1():

    # This example solves the non-convex quadratic programming problem
    #
    # minimize  (-3 * pow(x,2) - 3 * pow(y,2 )- 1 * x * y)/2
    #
    # subject to:
    #     x + y >= 0
    #    -x + y >= 0
    #   -1 <= x <= 1
    #    0 <= y <= 1
    #
    # This model has local optima at (1, 1), (-1, 1), (- 0.1666667,1) and
    # (0,0) with objective values -3.5, -2.5, -1.4583333333 and 0.0
    # respectively.
    # 
    # After the initial solve, constraints are added to the model to
    # force CPLEX to converge to some of these local optima in turn
    
    p = cplex.Cplex()

    p.variables.add(lb=[-1.0, 0.0], ub=[1.0, 1.0])
    
    p.linear_constraints.add(lin_expr = [[[0, 1], [ 1.0, 1.0]],
                                         [[0, 1], [-1.0, 1.0]]],
                             rhs      = [0.0, 0.0],
                             senses   = ['G', 'G'])

    p.objective.set_quadratic([[[0, 1], [-3.0, -0.5]],
                               [[0, 1], [-0.5, -3.0]]])

    # When a non-convex objective function is present, CPLEX will
    # raise an exception unless the solutiontarget parameter is set to
    # accept first-order optimal solutions
    p.parameters.solutiontarget.set(2)

    # CPLEX may converge to either local optimum 
    solve_and_display(p)

    # Add a constraint that cuts off the solution at (-1, 1)
    p.linear_constraints.add(lin_expr = [[[0], [1.0]]],
                             rhs      = [0.0],
                             senses   = 'G',
                             names    = ["new_constraint"])
    solve_and_display(p)

    # Reverse the sense of the newly added constraint to cut off the
    # solution at (1, 1)
    p.linear_constraints.set_senses("new_constraint", 'L')
    solve_and_display(p)


indefqpex1()

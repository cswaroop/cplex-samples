#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: lpex6.py
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
# lpex6.py - Illustrates that optimal basis can be copied and
#            used to start an optimization.
# 
# To run this example from the command line, use
#
#    python lpex6.py
#
# To run from within the python interpreter, use
#
# >>> import lpex6

import cplex

my_obj      = [1.0, 2.0, 3.0]
my_ub       = [40.0, cplex.infinity, cplex.infinity]
my_colnames = ["x1", "x2", "x3"]
my_rhs      = [20.0, 30.0]
my_rownames = ["c1", "c2"]
my_sense    = "LL"

def populatebycolumn(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)
    
    prob.linear_constraints.add(rhs = my_rhs, senses = my_sense,
                                names = my_rownames)

    c = [[[0,1],[-1.0, 1.0]],
         [["c1",1],[ 1.0,-3.0]],
         [[0,"c2"],[ 1.0, 1.0]]]
    
    prob.variables.add(obj = my_obj, ub = my_ub, names = my_colnames,
                       columns = c)

def lpex6():
    c = cplex.Cplex()
    c.set_problem_name("example")
    populatebycolumn(c)

    b_stat = c.start.status
    c.start.set_basis((b_stat.at_upper_bound, b_stat.basic, b_stat.basic),
                      (b_stat.at_lower_bound, b_stat.at_lower_bound))

    c.solve()

    print
    # solution.get_status() returns an integer code
    print "Solution status = " , c.solution.get_status(), ":",
    # the following line prints the corresponding string
    print c.solution.status[c.solution.get_status()]
    print "Solution value  = ", c.solution.get_objective_value()
    print "Iteration count = ", c.solution.progress.get_num_iterations()
    
    numrows = c.linear_constraints.get_num()
    numcols = c.variables.get_num()

    slack = c.solution.get_linear_slacks()
    pi    = c.solution.get_dual_values()
    x     = c.solution.get_values()
    dj    = c.solution.get_reduced_costs()
    for i in range(numrows):
        print "Row %d:  Slack = %10f  Pi = %10f" % ( i, slack[i], pi[i])
    for j in range(numcols):
        print "Column %d:  Value = %10f Reduced cost = %10f" % (j, x[j], dj[j])

lpex6()

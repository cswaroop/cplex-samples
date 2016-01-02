#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: warehouse.py
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
# warehouse.py -  Given a set of warehouses that each have a
#                 capacity, a cost per unit stored, and a 
#                 minimum usage level, this example find an
#                 assignment of items to warehouses that minimizes
#                 total cost.  The minimum usage levels are
#                 enforced by using semi-integer variables.
#
# To run this example from the command line, use
#
#    python warehouse.py
#
# To run from within the python interpreter, use
#
# >>> import warehouse

from math import fabs
import cplex

# number of warehouses
nbwhouses = 4

# number of loads
nbloads = 31

# cost per warehouse
costs = [1, 2, 4, 6]

# minimum capacity of warehouse if open
caplbs = [2, 3, 5, 7]

# problem variables
assignvars = []
capvars = []

def setupproblem(c):

    c.objective.set_sense(c.objective.sense.minimize)

    # assignment variables: assignvars[i][j] = 1 if load j is assigned to
    #                                            warehouse i
    allassignvars = []
    for i in range(nbwhouses):
        assignvars.append([])
        for j in range(nbloads):
            varname = "assign_"+str(i)+"_"+str(j)
            allassignvars.append(varname)
            assignvars[i].append(varname)
    c.variables.add(names = allassignvars, lb = [0] * len(allassignvars),
                    ub = [1] * len(allassignvars),
                    types = ["B"] * len(allassignvars))

    # capacity of warehouses: capvars[i] = number of loads assigned to
    #                                      warehouse i
    # We can either not use a warehouse (capvars[i] = 0) or use it with at
    # least the specified minimum capacity (capvars[i] >= caplbs[i]). This is
    # modeled by using semi-integer variables (type 'N').
    for i in range(nbwhouses):
        capvarname = "cap_"+str(i)
        capvars.append(capvarname)
    c.variables.add(names = capvars, lb = caplbs, ub = [10] * len(capvars),
                    types = ["N"] * len(capvars), obj = costs)


    # count loads assigned to warehouses:
    #   capvars[i] - sum_j (assignvars[i][j]) = 0
    for i in range(nbwhouses):
        thevars = [capvars[i]]
        thecoefs = [-1]
        for j in range(nbloads):
            thevars.append(assignvars[i][j])
            thecoefs.append(1)
        c.linear_constraints.add(lin_expr =
                                 [cplex.SparsePair(thevars, thecoefs)],
                                 senses = ["E"], rhs = [0])
    
    # Each load must be assigned to exactly one warehouse:
    #    sum_i (assignvars[i][j]) = 1
    for j in range(nbloads):
        thevars = []
        for i in range(nbwhouses):
            thevars.append(assignvars[i][j])
        c.linear_constraints.add(lin_expr =
                                 [cplex.SparsePair(thevars,
                                                   [1] * len(thevars))],
                                 senses = ["E"], rhs = [1])


def warehouse():

    c = cplex.Cplex()

    # Set an overall node limit
    c.parameters.mip.limits.nodes.set(5000)

    setupproblem(c)

    c.solve()

    sol = c.solution

    print
    # solution.get_status() returns an integer code
    print "Solution status = " , sol.get_status(), ":",
    # the following line prints the corresponding string
    print sol.status[sol.get_status()]

    if sol.is_primal_feasible():
        print "Solution value  = ", sol.get_objective_value()
        for i in range(nbwhouses):
            print "Warehouse %d capacity = %d" % (i, sol.get_values(capvars[i]))
            print "  loads:",
            for j in range(nbloads):
                if sol.get_values(assignvars[i][j]) > 0.5:
                    print j,
            print
    else:
        print "No solution available."


warehouse()


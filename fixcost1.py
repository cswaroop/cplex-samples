#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: fixcost1.py
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
# fixcost1.py - A production planning problem with fixed costs 
#
# Problem Description
# -------------------
# 
# A company must produce a product on a set of machines.
# Each machine has limited capacity.
# Producing a product on a machine has both a fixed cost
# and a cost per unit of production.
# 
# Minimize the sum of fixed and variable costs so that the
# company exactly meets demand.
#
# --------------------------------------------------------------------------
# 
# To run this example from the command line, use
#
#    python fixcost1.py
#
# To run from within the python interpreter, use
#
# >>> import fixcost

import cplex

fixed_cost = [1900.0, 820.0, 805.0, 464.0, 3912.00, 556.0]
var_cost   = [15.0,   20.0,  45.0,  64.0,  12.0,    56.0]
capacity   = [100.0,  20.0,  405.0, 264.0, 12.0,    256.0]

demand = 22.0


def fixcost1():
    c = cplex.Cplex()
    n_machines = len(var_cost)
    var_names = ['operate' + str(i) for i in range(n_machines)] + \
                ['use' + str(i) for i in range(n_machines)]
    c.variables.add(obj   = var_cost + fixed_cost,
                    types = "C" * n_machines + "B" * n_machines,
                    names = var_names)
    
    c.linear_constraints.add(lin_expr = [[["operate" + str(i)], [1.0]] \
                                         for i in range(n_machines)],
                             senses = "L" * n_machines,
                             rhs = capacity)
    c.linear_constraints.add(lin_expr = [[["operate" + str(i), "use" + str(i)],
                                          [1.0, -1.0 * capacity[i]]] \
                                         for i in range(n_machines)],
                             senses = "L" * n_machines,
                             rhs = [0.0] * n_machines)
    # if sense is not specified, all linear constraints are taken to be equalities
    c.linear_constraints.add(lin_expr = [[range(n_machines), [1.0] * n_machines]],
                             rhs = [demand])

    c.solve()
    print "Solution status = ", c.solution.get_status()
    print "Obj", c.solution.get_objective_value()
    eps  = c.parameters.mip.tolerances.integrality.get()
    used = c.solution.get_values("use0", "use" + str(n_machines - 1))
    for i in range(n_machines):
        if used[i] > eps:
            print "E", i, "is used for ",
            print c.solution.get_values(i)
    print "--------------------------------------------"

fixcost1()

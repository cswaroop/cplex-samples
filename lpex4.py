#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: lpex4.py
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
# lpex4.py - Illustrating the CPLEX callback functionality.
# 
# This is a modification of lpex1.py, where we use a callback
# function to print the iteration info, rather than have CPLEX
# do it.
#
# To run this example from the command line, use
#
#    python lpex4.py
#
# To run from within the python interpreter, use
#
# >>> import lpex4

import cplex
from cplex.callbacks import SimplexCallback


class MyCallback(SimplexCallback):

    def __call__(self):
        print "CB Iteration ", self.get_num_iterations(), " : ",
        if self.is_primal_feasible():
            print "CB Objective = ", self.get_objective_value()
        else:
            print "CB Infeasibility measure = ", self.get_primal_infeasibility()


def populate_by_column(problem):
    problem.objective.set_sense(problem.objective.sense.maximize)
    problem.linear_constraints.add(rhs = [20.0, 30.0], senses = "LL")

    cols = [[[0,1],[-1.0, 1.0]],
            [[0,1],[ 1.0,-3.0]],
            [[0,1],[ 1.0, 1.0]]]
    
    problem.variables.add(obj = [1.0, 2.0, 3.0],
                          ub = [40.0, cplex.infinity, cplex.infinity],
                          columns = cols)

def lpex4():
    problem = cplex.Cplex()
    populate_by_column(problem)
    problem.parameters.lpmethod.set(problem.parameters.lpmethod.values.primal)
    problem.register_callback(MyCallback)

    problem.solve()

    solution = problem.solution

    # solution.get_status() returns an integer code
    print "Solution status = ", solution.get_status(), ":",
    # the following line prints the corresponding string
    print solution.status[solution.get_status()]
    print "Objective value = ", solution.get_objective_value()
    print
    print "Values          = ", \
          solution.get_values(0, problem.variables.get_num()-1)
    print "Slacks          = ", \
          solution.get_linear_slacks(0, problem.linear_constraints.get_num()-1)
    print "Duals           = ", \
          solution.get_dual_values(0, problem.linear_constraints.get_num()-1)
    print "Reduced Costs   = ", \
          solution.get_reduced_costs(0, problem.variables.get_num()-1)


lpex4()
    


#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: blend.py
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
# blend.py - A blending problem
#
# --------------------------------------------------------------------------
# 
# Goal is to blend four sources to produce an alloy: pure metal, raw
# materials, scrap, and ingots.
# 
# Each source has a cost.
# Each source is made up of elements in different proportions.
# Alloy has minimum and maximum proportion of each element.
# 
# Minimize cost of producing a requested quantity of alloy.
#
# --------------------------------------------------------------------------
# 
# To run this example from the command line, use
#
#    python blend.py
#
# To run from within the python interpreter, use
#
# >>> import blend

import cplex

sources = ["Pure1", "Pure2", "Pure3",
           "Raw1", "Raw2",
           "Scrap1", "Scrap2",
           "Ingots"]

# costs of the sources of metal
costs = [22.0, 10.0, 13.0,
         6.0, 5.0,
         7.0, 8.0,
         9.0]

# amount of alloy requested
alloy = 71.0

# min and max amounts for each element in the alloy
min_spec = [0.05, 0.30, 0.60]
max_spec = [0.10, 0.40, 0.80]

# the entries correspond to Raw1, Raw2, Scrap1, Scrap2, and Ingots respectively
composition = {"Element1": [0.20, 0.01, 0.00, 0.01, 0.10],
               "Element2": [0.05, 0.00, 0.60, 0.00, 0.45],
               "Element3": [0.05, 0.30, 0.40, 0.70, 0.45]}

def blend():
    model = cplex.Cplex()
    model.objective.set_sense(model.objective.sense.minimize)
    model.variables.add(names = sources)
    
    # to model Ingots as an integer variable, uncomment the following line.
    # model.variables.set_types("Ingots", model.variables.type.integer)

    model.variables.set_upper_bounds("Ingots", 100000)
    model.objective.set_linear(zip(sources, costs))
    model.variables.add(names = ["Element1", "Element2", "Element3"],
                        lb = [min * alloy for min in min_spec],
                        ub = [max * alloy for max in max_spec])
    model.linear_constraints.add(lin_expr =
                                 [cplex.SparsePair(ind = ["Element1",
                                                          "Element2",
                                                          "Element3"],
                                                   val = [1.0] * 3)],
                                 senses = ["E"], rhs = [alloy])
    mixed_sources = sources[3:]
    for i in range(1, 4):
        lhs = cplex.SparsePair(["Element" + str(i), "Pure" + str(i)] + mixed_sources,
                               [-1.0, 1.0] + composition["Element" + str(i)])
        model.linear_constraints.add(lin_expr = [lhs], senses = ["E"],
                                     rhs = [0.0])
        
    model.solve()

    print
    print "Solution status: ", model.solution.get_status()
    print "Cost:       ", model.solution.get_objective_value()
    print "Pure metal: "
    for i in range(3):
        print i, ")", model.solution.get_values("Pure" + str(i + 1))
    print "Raw Material:"
    for i in range(2):
        print i, ")", model.solution.get_values("Raw" + str(i + 1))
    print "Raw Material:"
    for i in range(2):
        print i, ")", model.solution.get_values("Scrap" + str(i + 1))
    print "Ingots:"
    print "0) ", model.solution.get_values("Ingots")
    print "Elements:"
    for i in range(3):
        print i, ")", model.solution.get_values("Element" + str(i + 1))
    

blend()

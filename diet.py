#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: diet.py
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
# diet.py -- A diet problem
#
# Problem Description
# -------------------
#
# Mimimize the cost of a diet subject to nutritional constraints.
#
# To run from the command line, use
#
#    python diet.py
#
# To run from within the python interpreter, use
#
# >>> import diet

import cplex
from cplex.exceptions import CplexError
from inputdata import read_dat_file

# a class to store problem data
class ProbData:

    def __init__(self, filename):
        
        # read the data in diet.dat
        self.foodCost, self.foodMin, self.foodMax, self.nutrMin, \
                       self.nutrMax, self.nutrPer = \
                       read_dat_file("../../data/diet.dat")

        # check data consistency
        if len(self.foodCost) != len(self.foodMin) or \
               len(self.foodCost) != len(self.foodMax) or \
               len(self.nutrMin)  != len(self.nutrMax) or \
               len(self.nutrMin)  != len(self.nutrPer):
            print "ERROR: Data file '%s' contains inconsistent data\n" % filename
            raise Exception("data file error")

        for np in self.nutrPer:
            if len(self.foodCost) != len(np):
                print "ERROR: Data file '%s' contains inconsistent data\n" % filename
                raise Exception("data file error")


def populatebyrow(prob, data):

    nFoods = len(data.foodCost)
    nNutrients = len(data.nutrMin)

    # we want to minimize costs
    prob.objective.set_sense(prob.objective.sense.minimize)

    # add variables to decide how much of each type of food to buy
    varnames = ["x"+str(j) for j in range(nFoods)]
    prob.variables.add(obj = data.foodCost,
                       lb = data.foodMin,
                       ub = data.foodMax,
                       names = varnames)

    # add constraints to specify limits for each of the nutrients
    for n in range(nNutrients):
        prob.linear_constraints.add(lin_expr = [[varnames,data.nutrPer[n]]],
                                    senses = ["R"],
                                    rhs = [data.nutrMin[n]],
                                    range_values = [data.nutrMax[n] - data.nutrMin[n]])
    
    
def populatebycolumn(prob, data):
    nFoods = len(data.foodCost)
    nNutrients = len(data.nutrMin)

    # we want to minimize costs
    prob.objective.set_sense(prob.objective.sense.minimize)

    # create empty constraints to be filled later
    rownames = ["r"+str(n) for n in range(nNutrients)]
    prob.linear_constraints.add(senses = ["R" * nNutrients],
                                rhs = data.nutrMin,
                                range_values = [data.nutrMax[n] - data.nutrMin[n]
                                                for n in range(nNutrients)],
                                names = rownames)

    # create columns
    for j in range(nFoods):
        prob.variables.add(obj = [data.foodCost[j]],
                           lb = [data.foodMin[j]],
                           ub = [data.foodMax[j]],
                           columns = [[rownames, [data.nutrPer[n][j]
                                                  for n in range(nNutrients)]]])

    
def diet(pop_method):
    try:
        # read the data in diet.dat
        data = ProbData("../../data/diet.dat")

        # create CPLEX object
        my_prob = cplex.Cplex()

        # populate problem
        if pop_method == "r":
            handle = populatebyrow(my_prob, data)
        if pop_method == "c":
            handle = populatebycolumn(my_prob, data)

        # solve problem
        my_prob.solve()
        
    except CplexError, exc:
        print exc
        return

    numrows = my_prob.linear_constraints.get_num()
    numcols = my_prob.variables.get_num()

    solution = my_prob.solution
    
    # solution.get_status() returns an integer code
    print "Solution status = " , solution.get_status(), ":",
    # the following line prints the corresponding string
    print solution.status[solution.get_status()]
    print "Objective value = " , solution.get_objective_value()
    
    x = solution.get_values(0, my_prob.variables.get_num()-1)
    for j in range(my_prob.variables.get_num()):
        print "Buy %d = %17.10g" % (j, x[j])

import sys

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in  ["-r", "-c"]:
        print "Usage: diet.py -X"
        print "   where X is one of the following options:"
        print "      r          generate problem by row"
        print "      c          generate problem by column"
        print " Exiting..."
        sys.exit(-1)
    diet(sys.argv[1][1])
else:
    prompt = """Enter the letter indicating how the problem data should be populated:
    r : populate by rows
    c : populate by columns\n ? > """
    r = 'r'
    c = 'c'
    diet(input(prompt))


#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: steel.py
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
# steel.py -- a multi period production model
#
# Problem Description:
# 
# This example is an implementation of the model called "steelT.mod" 
# in the AMPL book by Fourer, Gay and Kernighan.
#
# In the AMPL example, a multiperiod production model is given, with data
# for 4 weeks.  In our model we define 5 periods: the time right before
# our observation period starts and the 4 weeks for which we plan. For
# the time before the observation period there is no demand and no
# production can be performed. All costs for this period have already
# been accounted for and can be dropped from the model.
#
# To run this example from the command line, use
#
#    python steel.py
#
# To run from within the python interpreter, use
#
# >>> import steel

import cplex
from cplex.exceptions import CplexSolverError
import sys

# Model data that is independent of the period.
products = range(2)  # The products (from 0 to N-1).
start = [ 10, 0 ]    # starting inventory per product.
icost = [ 2.5, 3 ]   # Inventory cost per unit and product.
prate = [ 200, 140 ] # Production rate per product.
pcost = [ 10, 11 ]   # Production cost per unit and product.

# Model data that depends on the period.
periods = range(5)                        # The periods (from 0 to N-1)
whours = [ 0, 40, 40, 32, 40 ]            # Maximum working time per period
demand = [ [ 0, 6000, 6000, 4000, 6500 ], # Demand for product 0 per period.
           [ 0, 4000, 2500, 3500, 4200 ]  # Demand for product 1 per period.
           ]
revenue = [ [ 0, 25, 26, 27, 27 ], # Revenue per unit and period for product 0.
            [ 0, 30, 35, 37, 39 ]  # Revenue per unit and period for product 1.
            ]


# Turn a two-dimensional array into a one dimensional array.
def flatten(dim2):
    ret = []
    for i in dim2:
        ret.extend(i)
    return ret

# Create and return a two-dimensional array. The first dimension is indexed
# by values from IDX1 and the second dimension by IDX2 (both arguments are
# assumed to be ranges starting at 0).
# The values in the array are subsequent numbers starting at START, i.e.
# the value at cross[i][j] is i * len(IDX2) + j + START.
def cross(idx1, idx2, start):
    ret = []
    for i in idx1:
        ret.append(map(lambda d: d + start, idx2))
        start += len(idx2)
    return ret

if __name__ == "__main__":

    cpx = cplex.Cplex()

    # Create arrays to reference variables. All arrays are indexed
    # by product and period index and have subsequent values that
    # serve as variable indices.
    produce = cross(products, periods, 0)
    inventorize = cross(products, periods, len(products) * len(periods))
    sell = cross(products, periods, 2 * len(products) * len(periods))

    # Add variables with their lower bounds and objective function
    # coefficients. Notice that variables are added carefully so that
    # they are in 1-to-1-correspondance with the indices in the arrays
    # produce, inventorize and sell.

    # Production variables. Each unit produced incurs the respective
    # production cost.
    for p in products:
        cpx.variables.add(obj = [ -pcost[p] ] * len(periods))

    # Invetory variables. Each unit inventorized incurs the respective
    # inventory cost. There is no inventory cost for the first period
    # so we reset this explicitly.
    for p in products:
        cpx.variables.add(obj = [ -icost[p] ] * len(periods))
        cpx.objective.set_linear(inventorize[p][0], 0)

    # Sell variables. Each unit sold returns the respective revenue.
    # As we cannot sell more than the market demand the upper bound
    # for these variables is given by the market demand.
    cpx.variables.add(obj = flatten(revenue), ub = flatten(demand))

    # Our aim is to maximize profit.
    cpx.objective.set_sense(cpx.objective.sense.maximize)

    # Time required for production must satisfy working time limit.
    # The time required to produce one unit of product P is 1/R where
    # R is the production rate for P.
    for period in periods:
        lhs = [map(lambda p: produce[p][period], products),
               map(lambda p: 1.0 / prate[p], products)]
        cpx.linear_constraints.add(lin_expr = [lhs],
                                   senses = ["L"],
                                   rhs = [whours[period]])

    # Balance constraint: For each period and product the amount sold and
    # inventorized must match the amount produced and received from previous
    # period.
    # The first period is special as we have a constant amount (the initial
    # stock) from the previous period.
    for period in periods:
        for product in products:
            if period == 0:
                ind = [ produce[product][period],
                        sell[product][period], inventorize[product][period] ]
                val = [ 1,
                        -1, -1 ]
                cpx.linear_constraints.add(lin_expr = [[ind, val]],
                                           senses = ["E"],
                                           rhs = [-start[product]])
            else:
                ind = [ inventorize[product][period - 1],
                        produce[product][period],
                        sell[product][period], inventorize[product][period] ]
                val = [ 1, 1, -1, -1 ]
                cpx.linear_constraints.add(lin_expr = [[ind, val]],
                                           senses = ["E"],
                                           rhs = [0])

    # Solve the problem. Errors/exceptions will terminate the program.
    cpx.solve()
    print "Solution status = ", cpx.solution.get_status()
    # Dump results.
    print "Total Profit = " + str(cpx.solution.get_objective_value())
    print
    print "\tp" + "\tt" + "\tMake" + "\tInv" + "\tSell"
    for product in products:
        for period in periods:
            print "\t" + str(product) + "\t" + str(period) \
            + "\t" + str(cpx.solution.get_values(produce[product][period])) \
            + "\t" + str(cpx.solution.get_values(inventorize[product][period])) \
            + "\t" + str(cpx.solution.get_values(sell[product][period]))

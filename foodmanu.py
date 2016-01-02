#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: foodmanu.py
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
# A formulation of the food manufacturing problem in H.P. Williams'
# book Model Building in Mathematical Programming.  The formulation
# demonstrates the use indicator constraints and semi-continuous
# variables.
#
#
# To run from the command line, use
#
#    python foodmanu.py
# 
# To run from within the python interpreter, use
#
# >>> import foodmanu

import sys

import cplex

NUMPRODUCTS = 5

VEGOIL1  = 0
VEGOIL2  = 1
OIL1     = 2
OIL2     = 3
OIL3     = 4


NUMMONTHS   = 6


NUMVARS     = 4

BUY         = 0
USE         = 1
STORE       = 2
IS_USED     = 3

cost = [110.0, 120.0, 130.0, 110.0, 115.0, # Cost for January
        130.0, 130.0, 110.0,  90.0, 115.0, # Cost for February
        110.0, 140.0, 130.0, 100.0,  95.0, # Cost for March
        120.0, 110.0, 120.0, 120.0, 125.0, # Cost for April
        100.0, 120.0, 150.0, 110.0, 105.0, # Cost for May
        90.0, 100.0, 140.0,  80.0, 135.0]  # Cost for June

hardness = [8.8, 6.1, 2.0, 4.2, 5.0] # Hardness of each product



def buildmodel(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)
    
    colcnt = NUMVARS*NUMMONTHS*NUMPRODUCTS

    obj     = [0] * colcnt
    lb      = [0] * colcnt
    ub      = [0] * colcnt
    ct      = [0] * colcnt
    rmatind = [0] * colcnt
    rmatval = [0] * colcnt

    ic_dict = {}

    for m in range(NUMMONTHS):
        for p in range(NUMPRODUCTS):

            obj[varindex(m,p,BUY)] = -cost[m*NUMPRODUCTS + p]
            lb[varindex(m,p,BUY)]  = 0.0
            ub[varindex(m,p,BUY)]  = cplex.infinity
            ct[varindex(m,p,BUY)]  = "C"

            obj[varindex(m,p,USE)] = 0.0
            lb[varindex(m,p,USE)]  = 20.0
            ub[varindex(m,p,USE)]  = cplex.infinity
            ct[varindex(m,p,USE)]  = "S"

            obj[varindex(m,p,STORE)] = -5.0
            lb[varindex(m,p,STORE)]  = 0.0
            ub[varindex(m,p,STORE)]  = 1000.0
            ct[varindex(m,p,STORE)]  = "C"

            if m == NUMMONTHS -1:
                lb[varindex (m, p, STORE)] = 500.0
                ub[varindex (m, p, STORE)] = 500.0
                
            obj[varindex (m, p, IS_USED)]   = 0.0
            lb[varindex (m, p, IS_USED)]    = 0.0
            ub[varindex (m, p, IS_USED)]    = 1.0
            ct[varindex (m, p, IS_USED)]    = 'B'
            
    prob.variables.add(obj = obj, lb = lb, ub = ub, types = "".join(ct))

    for m in range(NUMMONTHS):
        for p in range(NUMPRODUCTS):
            ic_dict["lin_expr"]     = cplex.SparsePair(ind = [varindex(m, p, USE)],
                                                       val = [1.0])
            ic_dict["rhs"]          = 0.0
            ic_dict["sense"]        = "L"
            ic_dict["indvar"]       = varindex(m, p, IS_USED)
            ic_dict["complemented"] = 1
            prob.indicator_constraints.add(**ic_dict)

        prob.linear_constraints.add(lin_expr = [[[varindex(m, VEGOIL1, USE),
                                                  varindex(m, VEGOIL2, USE)],
                                                 [1.0, 1.0]]],
                                    senses = "L", rhs = [200.0])
        prob.linear_constraints.add(lin_expr = [[[varindex(m, OIL1, USE),
                                                  varindex(m, OIL2, USE),
                                                  varindex(m, OIL3, USE)],
                                                 [1.0, 1.0, 1.0]]],
                                    senses = "L", rhs = [250.0])
        
        prob.variables.add(obj = [150.0],
                           types = [prob.variables.type.continuous])
        
        last_column = prob.variables.get_num() - 1
        
        for p in range(NUMPRODUCTS):
            rmatind[p] = varindex(m,p,USE)
            rmatval[p] = 1.0
        rmatind[NUMPRODUCTS] = last_column
        rmatval[NUMPRODUCTS] = -1.0
        rm = [[rmatind[:NUMPRODUCTS+1], rmatval[:NUMPRODUCTS+1]]]
        prob.linear_constraints.add(lin_expr = rm, senses = "E", rhs = [0.0])
        
        for p in range(NUMPRODUCTS):
            rmatind[p] = varindex(m,p,USE)
            rmatval[p] = hardness[p]
        rmatind[NUMPRODUCTS] = last_column
        rmatval[NUMPRODUCTS] = -3.0
        prob.linear_constraints.add(lin_expr = [[rmatind[:NUMPRODUCTS+1],
                                                 rmatval[:NUMPRODUCTS+1]]],
                                    senses = "G", rhs = [0.0])
        rmatval[NUMPRODUCTS] = -6.0;
        prob.linear_constraints.add(lin_expr = [[rmatind[:NUMPRODUCTS+1],
                                                 rmatval[:NUMPRODUCTS+1]]],
                                    senses = "L", rhs = [0.0])

        for p in range(NUMPRODUCTS):
            rmatind[p] = varindex(m, p, IS_USED)
            rmatval[p] = 1.0
        prob.linear_constraints.add(lin_expr = [[rmatind[:NUMPRODUCTS],
                                                 rmatval[:NUMPRODUCTS]]],
                                    senses = "L", rhs = [3.0])

        ic_dict["indvar"]       = varindex(m, VEGOIL1, IS_USED)
        ic_dict["rhs"]          = 20.0
        ic_dict["sense"]        = "G"
        ic_dict["complemented"] = 0
        ic_dict["lin_expr"]     = cplex.SparsePair(ind = [varindex(m, OIL3, USE)],
                                                   val = [1.0])
        prob.indicator_constraints.add(**ic_dict)

        ic_dict["indvar"]       = varindex(m, VEGOIL2, IS_USED)
        prob.indicator_constraints.add(**ic_dict)

        for p in range(NUMPRODUCTS):
            ind = []
            val = []
            if m != 0:
                ind.append(varindex(m-1, p, STORE))
                val.append(1.0)
                ind.append(varindex(m, p, BUY))
                val.append(1.0)
                ind.append(varindex(m, p, USE))
                val.append(-1.0)
                ind.append(varindex(m, p, STORE))
                val.append(-1.0)
                rhs = [0.0]
            else:
                ind.append(varindex(m, p, BUY))
                val.append(1.0)
                ind.append(varindex(m, p, USE))
                val.append(-1.0)
                ind.append(varindex(m, p, STORE))
                val.append(-1.0)
                rhs = [-500.0]
            prob.linear_constraints.add(lin_expr = [[ind, val]],
                                        senses = "E", rhs = rhs)


def varindex(m, p, whichvar):
   return m*NUMVARS*NUMPRODUCTS + p*NUMVARS + whichvar


def foodmanu():
    prob = cplex.Cplex()

    # sys.stdout is the default output stream for log and results
    # so these lines may be omitted
    prob.set_results_stream(sys.stdout)
    prob.set_log_stream(sys.stdout)
    
    ic_handle = buildmodel(prob)

    prob.write("foodmanu.lp")

    prob.solve()

    sol = prob.solution
    
    print 
    # solution.get_status() returns an integer code
    print "Solution status = " , sol.get_status(), ":",
    # the following line prints the corresponding string
    print sol.status[sol.get_status()]
    print "Solution value  = ", sol.get_objective_value()

    x = sol.get_values(0, NUMVARS*NUMMONTHS*NUMPRODUCTS - 1)

    for m in range(NUMMONTHS):
        print "Month", m
        print "  . buy   ",
        for p in range(NUMPRODUCTS):
            print "%15.6f" % x[varindex(m,p,BUY)], "\t",
        print
        print "  . use   ",
        for p in range(NUMPRODUCTS):
            print "%15.6f" % x[varindex(m,p,USE)], "\t",
        print
        print "  . store ",
        for p in range(NUMPRODUCTS):
            print "%15.6f" % x[varindex(m,p,STORE)], "\t",
        print
        

foodmanu()

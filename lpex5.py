#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: examples/test/python/lpex5.py
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
# lpex5.py - Demonstrating manipulation of different output streams
#
# To run this example from the command line, use
#
#    python lpex5.py  
#
# Alternatively, this example can be run from the python interpreter by
# 
# >>> import lpex5

import cplex
from cplex.exceptions import CplexError
import sys

# data common to all populateby functions
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
   
    
def lpex5():
    try:
        my_prob = cplex.Cplex()
        
        # messages passed to the results channel will be upcased
        # any function that takes a string and returns a string
        # could be passed in
        screen_output = my_prob.set_results_stream(sys.stdout,
                                                   lambda a: a.upper())
        # equivalent to
        # def my_formatter(str):
        #     return str.upper()
        # my_screen_output = my_prob.add_results_stream(sys.stdout, my_formatter)
    

        # can give a filename instead of a file object
        # in either case, the function is an optional argument
        file_output = my_prob.set_results_stream("results.txt")

        # pass in None to delete the duct
        my_prob.set_results_stream(None)

        # store result stream in file with output manipulation
        my_prob.set_results_stream("results.txt", lambda a:  " RESULT " + a)

        # might as well set other channels
        my_prob.set_warning_stream("warnings.txt", lambda a:  " WARNING " + a)
        my_prob.set_error_stream("errors.txt", lambda a:  " ERROR " + a)       
        my_prob.set_log_stream("log.txt", lambda a:  a + " LOG " )

        handle = populatebycolumn(my_prob)

        my_prob.solve()

    except CplexError, exc:
        print exc
        return

    numrows = my_prob.linear_constraints.get_num()
    numcols = my_prob.variables.get_num()

    print
    print "Solution status = ", my_prob.solution.get_status()
    print "Solution value  = ", my_prob.solution.get_objective_value()
    slack = my_prob.solution.get_linear_slacks()
    pi    = my_prob.solution.get_dual_values()
    x     = my_prob.solution.get_values()
    dj    = my_prob.solution.get_reduced_costs()
    for i in range(numrows):
        print "Row %d:  Slack = %10f  Pi = %10f" % ( i, slack[i], pi[i])
    for j in range(numcols):
        print "Column %d:  Value = %10f Reduced cost = %10f" % (j, x[j], dj[j])

    my_prob.write("lpex5.lp")

lpex5()


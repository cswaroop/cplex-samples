#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: admipex6.py
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
# admipex6.py -  Start the solution of the root relaxation in a
#                MIP model from an existing primal solution with the
#                solve callback.
#
# To run this example, the user must specify a problem file.
#
# You can run this example at the command line by
#
#    python admipex6.py <filename>
#
# or within the python interpreter by
#
# >>> import admipex6
#
# The user will be prompted to chose the filename.

import cplex
from cplex.callbacks import SolveCallback
from cplex.exceptions import CplexError
import sys

epszero = 1e-10

class UserSolve(SolveCallback):

    def __call__(self):
        self.times_called += 1
        # Only use the callback at the root
        if self.times_called == 1:
            self.set_start(cplex.SparsePair(range(self.get_num_cols()),
                                            self.relx)) 
            self.solve(self.method.primal)
            status = self.get_cplex_status()
            self.use_solution()

def admipex6(filename):

    try: 
        c = cplex.Cplex(filename)

        # We transfer a problem with semi-continuous or semi-integer
        # variables to a MIP problem by adding variables and  
        # constraints. So in MIP callbacks, the size of the problem
        # is changed and this example won't work for such problems.

        if (c.variables.get_num_semiinteger() +
            c.variables.get_num_semicontinuous() > 0):
            print "Not for problems with semi-continuous or semi-integer variables."
            sys.exit(-1)

        c.set_log_stream(sys.stdout)
        c.set_results_stream(sys.stdout)

        numcols = c.variables.get_num()

        # solve relaxation 
        
        clone = cplex.Cplex(c)
        clone.set_problem_type(clone.problem_type.LP)
        clone.solve()
        print "Solution status = " , clone.solution.get_status(), ":",
        print "Relaxation objective value = ", \
              clone.solution.get_objective_value()

        relx = clone.solution.get_values()

        for j in range(numcols):
            if abs(relx[j]) > epszero:
                print "Column %d: Relaxation Value = %17.10g" % (j, relx[j])

        # setup the solve callback                
        user_solve = c.register_callback(UserSolve)
        user_solve.times_called = 0
        user_solve.relx = relx

        c.parameters.mip.strategy.search.set(c.parameters.mip.strategy.search.values.traditional)
        c.parameters.mip.display.set(4)

        # solve the original problem
        c.solve()

    except CplexError, exc:
        print exc
        return

    solution = c.solution

    # solution.get_status() returns an integer code
    print "Solution status = " , solution.get_status(), ":",
    # the following line prints the corresponding string
    print solution.status[solution.get_status()]
    print "Objective value = " , solution.get_objective_value()
    print
    x = solution.get_values(0, numcols-1)
    for j in range(numcols):
        if abs(x[j]) > epszero:
            print "Column %d: Value = %17.10g" % (j, x[j])

    print
    print " Iterations = " , c.solution.progress.get_num_iterations()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: admipex6.py filename"
        print "  filename   Name of a file, with .mps, .lp, or .sav"
        print "             extension, and a possible, additional .gz"
        print "             extension"
        sys.exit(-1)
    admipex6(sys.argv[1])
else:
    prompt = """Enter the path to a file with .mps, .lp, or .sav
extension, and a possible, additional .gz extension:
The path must be entered as a string; e.g. "my_model.mps"\n """
    admipex6(input(prompt))

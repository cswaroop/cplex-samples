#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: admipex5.py
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
# admipex5.py --- Solving noswot with user cuts and lazy constraints
#
# Example admipex5.py solves the MIPLIB 3.0 model noswot.mps by adding
# user cuts via a user cut callback during the branch-and-cut process.
#
# Then it modifies the problem by sepcifying a lazy constraint
# generator that tests against one single cut that the original
# optimal solution does not satisfy.
#
# Finally the modified problem is solved again, this time without user
# cuts (but the lazy constraint generator is still active).
#
# You can run this example at the command line by
#
#    python admipex5.py
#
# or within the python interpreter by
#
# >>> import admipex5

import sys

import cplex
from cplex.callbacks import UserCutCallback, LazyConstraintCallback


#  Add the following valid cuts for the noswot model via cut callback:
#
#  cut1: X21 - X22 <= 0
#  cut2: X22 - X23 <= 0
#  cut3: X23 - X24 <= 0
#  cut4: 2.08 X11 + 2.98 X21 + 3.47 X31 + 2.24 X41 + 2.08 X51 
#      + 0.25 W11 + 0.25 W21 + 0.25 W31 + 0.25 W41 + 0.25 W51
#        <= 20.25
#  cut5: 2.08 X12 + 2.98 X22 + 3.47 X32 + 2.24 X42 + 2.08 X52 
#      + 0.25 W12 + 0.25 W22 + 0.25 W32 + 0.25 W42 + 0.25 W52
#        <= 20.25
#  cut6: 2.08 X13 + 2.98 X23 + 3.4722 X33 + 2.24 X43 + 2.08 X53
#      + 0.25 W13 + 0.25 W23 + 0.25 W33 + 0.25 W43 + 0.25 W53
#        <= 20.25
#  cut7: 2.08 X14 + 2.98 X24 + 3.47 X34 + 2.24 X44 + 2.08 X54 
#      + 0.25 W14 + 0.25 W24 + 0.25 W34 + 0.25 W44 + 0.25 W54
#        <= 20.25
#  cut8: 2.08 X15 + 2.98 X25 + 3.47 X35 + 2.24 X45 + 2.08 X55 
#      + 0.25 W15 + 0.25 W25 + 0.25 W35 + 0.25 W45 + 0.25 W55
#        <= 16.25
# 
class MyCut(UserCutCallback):

    def __init__(self, env):
        UserCutCallback.__init__(self, env)
        self.initcuts()
        
    def initcuts(self):
        lhs = []
        rhs = []

        lhs = lhs + [cplex.SparsePair(ind = ["X21", "X22"], val = [1.0, -1.])]
        rhs = rhs + [0.0]
        
        lhs = lhs + [cplex.SparsePair(ind = ["X22", "X23"], val = [1.0, -1.])]
        rhs = rhs + [0.0]
        
        lhs = lhs + [cplex.SparsePair(ind = ["X23", "X24"], val = [1.0, -1.])]
        rhs = rhs + [0.0]
        
        lhs = lhs + [cplex.SparsePair(ind = ["X11", "X21", "X31", "X41", "X51",
                                             "W11", "W21", "W31", "W41", "W51"],
                                      val = [2.08, 2.98, 3.47, 2.24, 2.08,
                                             0.25, 0.25, 0.25, 0.25, 0.25])]
        rhs = rhs + [20.25]

        lhs = lhs + [cplex.SparsePair(ind = ["X12", "X22", "X32", "X42", "X52",
                                             "W12", "W22", "W32", "W42", "W52"],
                                      val = [2.08, 2.98, 3.47, 2.24, 2.08,
                                             0.25, 0.25, 0.25, 0.25, 0.25])]
        rhs = rhs + [20.25]
        
        lhs = lhs + [cplex.SparsePair(ind = ["X13", "X23", "X33", "X43", "X53",
                                             "W13", "W23", "W33", "W43", "W53"],
                                      val = [2.08, 2.98, 3.4722, 2.24, 2.08,
                                             0.25, + 0.25, 0.25, 0.25, 0.25])]
        rhs = rhs + [20.25]

        lhs = lhs + [cplex.SparsePair(ind = ["X14", "X24", "X34", "X44", "X54",
                                             "W14", "W24", "W34", "W44", "W54"],
                                      val = [2.08, 2.98, 3.47, 2.24, 2.08,
                                             0.25, 0.25, 0.25, 0.25, 0.25])]
        rhs = rhs + [20.25]
        
        lhs = lhs + [cplex.SparsePair(ind = ["X15", "X25", "X35", "X45", "X55",
                                             "W15", "W25", "W35", "W45", "W55"],
                                      val = [2.08, 2.98, 3.47, 2.24, 2.08,
                                             0.25, 0.25, 0.25, 0.25, 0.25])]
        rhs = rhs + [16.25]

        self.lhs = lhs
        self.rhs = rhs

    def __call__(self):
        # loop through our list of cuts and check whether they are violated
        lhs = self.lhs
        rhs = self.rhs
        nCuts = len(rhs)
        for i in range(nCuts):
            # calculate activity of cut
            act = 0
            cutlen = len(lhs[i].ind)
            for k in range(cutlen):
                j = lhs[i].ind[k]
                a = lhs[i].val[k]
                act += a*self.get_values(j)

            # check if cut is violated
            if act > rhs[i] + 1e-6:
                self.add(cut = lhs[i], sense = "L", rhs = rhs[i])


#  Add the following constraint to the noswot model via lazy
#  constraint callback; the optimal solution will be cut off:
#
#  lazy_con : W11 + W12 + W13 + W14 + W15 <= 3
#
class MyLazy(LazyConstraintCallback):

    def __call__(self):
        indices = ["W11", "W12", "W13", "W14", "W15"]
        act     = 0.0
        for i in indices:
            act += self.get_values(i)
        if act > 3.01:
            self.add(constraint = cplex.SparsePair(ind = indices, val = [1.0] * 5),
                     sense      = "L",
                     rhs        = 3.0)


def solve_and_report(c):
    # solve problem
    c.solve()

    # solution.get_status() returns an integer code
    print "Solution status = " , c.solution.get_status(), ":",
    # the following line prints the corresponding string
    print c.solution.status[c.solution.get_status()]
    print "Objective value = " , c.solution.get_objective_value()

    # print non-zero solution values
    values = c.solution.get_values()
    for i, x in enumerate(values):
        if abs(x) > 1.e-10:
            print ("Column %3d (%5s):  Value = %17.10g" %
                   (i, c.variables.get_names(i), x))
    
def admipex5():

    c = cplex.Cplex("../../../examples/data/noswot.mps")

    # sys.stdout is the default output stream for log and results
    # so these lines may be omitted
    c.set_log_stream(sys.stdout)
    c.set_results_stream(sys.stdout)

    # need to use traditional branch-and-cut to allow for control callbacks
    c.parameters.mip.strategy.search.set(c.parameters.mip.strategy.search.values.traditional)

    # set node log interval to 1000
    c.parameters.mip.interval.set(1000)

    # the problem will be solved several times, so turn off advanced start

    c.parameters.advance.set(0)
    
    # install the user cut callback
    c.register_callback(MyCut)

    # solve problem with user cuts
    solve_and_report(c)

    # install the lazy constraint callback
    c.register_callback(MyLazy)
    
    # solve problem with user cuts and lazy constraint
    solve_and_report(c)

    # remove the user cut callback
    c.unregister_callback(MyCut)

    # solve problem with lazy constraint
    solve_and_report(c)

    
if __name__ == "__main__":
    if len(sys.argv) != 1:
        print "Usage: admipex5.py "
        sys.exit(-1)
    admipex5()

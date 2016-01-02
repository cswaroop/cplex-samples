#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: admipex4.py
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
# admipex4.py --- Solving noswot by adding user cuts
#
# Examples admipex4.py and admipex5.py both solve the MIPLIB
# 3.0 model noswot.mps by adding user cuts.  admipex4.py adds
# these cuts to the cut table before the branch-and-cut process
# begins, while admipex5.py adds them through the user cut callback
# during the branch-and-cut process
#
# You can run this example at the command line by
#
#    python admipex4.py
#
# or within the python interpreter by
#
# >>> import admipex4

import sys

import cplex

#  Add the following valid cuts for the noswot model as user cuts:
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
def addcuts(c):

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

    c.linear_constraints.advanced.add_user_cuts(lin_expr = lhs,
                                                senses = "LLLLLLLL", rhs = rhs)
    c.parameters.preprocessing.linear.set(0)

    # Alternative approach:  Replace advanced.add_user_cuts()
    # and c.parameters.preprocessing.linear.set(0)
    # by the following add() call.
    #
    # c.linear_constraints.add(lin_expr = lhs, senses = "LLLLLLLL", rhs = rhs)
    #
    # Note that in this example, we're adding a small number
    # of cuts, so it is reasonable (preferable, in fact) to
    # to add them directly to the model.  If you have
    # a large number of cuts, however, they can slow down
    # the linear programming relaxations significantly, so
    # placing them in the user cut table rather than in the
    # model itself will usually be preferable.



def admipex4():

    c = cplex.Cplex("../../../examples/data/noswot.mps")

    # sys.stdout is the default output stream for log and results
    # so these lines may be omitted
    c.set_log_stream(sys.stdout)
    c.set_results_stream(sys.stdout)

    # set node log interval to 1000
    c.parameters.mip.interval.set(1000)

    addcuts(c)
    c.solve()

    # solution.get_status() returns an integer code
    print "Solution status = " , c.solution.get_status(), ":",
    # the following line prints the corresponding string
    print c.solution.status[c.solution.get_status()]
    print "Objective value = " , c.solution.get_objective_value()


if __name__ == "__main__":
    if len(sys.argv) != 1:
        print "Usage: admipex4.py "
        sys.exit(-1)
    admipex4()

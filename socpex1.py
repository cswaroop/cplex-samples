#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: socpex1.py
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
# socpex1.py -- Solve a second order cone program to optimality, fetch
#               the dual values and test that the primal and dual solution
#               vectors returned by CPLEX satisfy the KKT conditions.
#               The problems that this code can handle are second order
#               cone programs in standard form. A second order cone
#               program in standard form is a problem of the following
#               type (c' is the transpose of c):
#                 min c1'x1 + ... + cr'xr
#                   A1 x1 + ... + Ar xr = b
#                   xi in second order cone (SOC)
#               where xi is a vector of length ni. Note that the
#               different xi are orthogonal. The constraint "xi in SOC"
#               for xi=(xi[1], ..., xi[ni]) is
#                   xi[1] >= |(xi[2],...,xi[ni])|
#               where |.| denotes the Euclidean norm. In CPLEX such a
#               constraint is formulated as
#                   -xi[1]^2 + xi[2]^2 + ... + xi[ni]^2 <= 0
#                    xi[1]                              >= 0
#                              xi[2], ..., xi[ni] free
#               Note that if ni = 1 then the second order cone constraint
#               reduces to xi[1] >= 0.

from math import fabs, sqrt
import cplex  as CPX
import sys


# Default tolerance for testing KKT conditions. */
TESTTOL = 1e-9
# Default tolerance for barrier convergence. */
CONVTOL = 1e-9

# Marker for variables that are in a cone constraint but are not the cone
# head variable in that constraint.
NOT_CONE_HEAD = -1
# Marker for variables that are not in any cone constraint.
NOT_IN_CONE = -2

# NOTE: CPLEX does not provide a function to directly get the dual
#       multipliers for second order cone constraints.
#       Example qcpdual.py illustrates how the dual multipliers for a
#       quadratic constraint can be computed from that constraint's slack.
#       However, for SOCP we can do something simpler: we can read those
#       multipliers directly from the dual slacks for the cone head variables.
#       For a second order cone constraint
#         x[1] >= |(x[2], ..., x[n])|
#       the dual multiplier is the dual slack value for x[1].
def getsocpconstrmultipliers(cplex,dslack = None):
    socppi = dict()

    # Compute full dual slack (sum of dual multipliers for bound constraints
    # and per-constraint dual slacks)
    dense = dict(zip(cplex.variables.get_names(),
                     cplex.solution.get_reduced_costs()))
    for n in cplex.quadratic_constraints.get_names():
        v = cplex.solution.get_quadratic_dualslack(n)
        for (var,val) in zip(v.ind, v.val):
            dense[cplex.variables.get_names(var)] += val

    # Find the cone head variables and pick up the dual slacks for them.
    for n in cplex.quadratic_constraints.get_names():
        q = cplex.quadratic_constraints.get_quadratic_components(n)
        for (i1,i2,v) in zip(q.ind1, q.ind2, q.val):
            if v < 0:
                name = cplex.variables.get_names(i1)
                socppi[n] = dense[name]
                break

    if dslack != None:
        dslack.clear()
        for key, value in dense.iteritems():
            dslack[key] = value
            
    return socppi

# Test KKT conditions on the solution.
# The function returns true if the tested KKT conditions are satisfied
# and false otherwise.
def checkkkt(c, cone, tol):
    # Read primal and dual solution information.
    x = dict(zip(c.variables.get_names(), c.solution.get_values()))
    s = dict(zip(c.linear_constraints.get_names(), c.solution.get_linear_slacks()))
    pi = dict(zip(c.linear_constraints.get_names(), c.solution.get_dual_values()))
    dslack = dict()
    for key,value in getsocpconstrmultipliers(c, dslack).iteritems():
        pi[key] = value
    for (q,v) in zip(c.quadratic_constraints.get_names(),
                     c.solution.get_quadratic_slacks(c.quadratic_constraints.get_names())):
        s[q] = v
    
    # Print out the data just fetched.
    print "x      = [",
    for n in c.variables.get_names():
        print " %7.3f" % x[n],
    print " ]"
    print "dslack = [",
    for n in c.variables.get_names():
        print " %7.3f" % dslack[n],
    print " ]"
    print "pi     = [",
    for n in c.linear_constraints.get_names():
        print " %7.3f" % pi[n],
    for n in c.quadratic_constraints.get_names():
        print " %7.3f" % pi[n],
    print " ]"
    print "slack  = [",
    for n in c.linear_constraints.get_names():
        print " %7.3f" % s[n],
    for n in c.quadratic_constraints.get_names():
        print " %7.3f" % s[n],
    print " ]"

    # Test primal feasibility.
    # This example illustrates the use of dual vectors returned by CPLEX
    # to verify dual feasibility, so we do not test primal feasibility
    # here.

    # Test dual feasibility.
    # We must have
    # - for all <= constraints the respective pi value is non-negative,
    # - for all >= constraints the respective pi value is non-positive,
    # - the dslack value for all non-cone variables must be non-negative.
    # Note that we do not support ranged constraints here.
    for n in c.linear_constraints.get_names():
        if c.linear_constraints.get_senses(n) == 'L' and pi[n] < -tol:
            print >>sys.stderr, "Dual multiplier ", pi[n], " for <= constraint ", n, " not feasible."
            return False
        elif c.linear_constraints.get_senses(n) == 'G' and pi[n] > tol:
            print >>sys.stderr, "Dual multiplier ", pi[n], " for >= constraint ", n, " not feasible."
            return False
    for n in c.quadratic_constraints.get_names():
        if c.quadratic_constraints.get_senses(n) == 'L' and pi[n] < -tol:
            print >>sys.stderr, "Dual multiplier ", pi[n], " for <= constraint ", n, " not feasible."
            return False
        elif c.quadratic_constraints.get_senses(n) == 'G' and pi[n] > tol:
            print >>sys.stderr, "Dual multiplier ", pi[n], " for >= constraint ", n, " not feasible."
            return False
    for n in c.variables.get_names():
        if cone[n] == NOT_IN_CONE and dslack[n] < -tol:
            print >>sys.stderr, "Dual multiplier for ", n, " is not feasible: ", dslack[n]
            return False

    # Test complementary slackness.
    # For each constraint either the constraint must have zero slack or
    # the dual multiplier for the constraint must be 0. We must also
    # consider the special case in which a variable is not explicitly
    # contained in a second order cone constraint.
    for n in c.linear_constraints.get_names():
        if fabs(s[n]) > tol and fabs(pi[n]) > tol:
            print >>sys.stderr, "Invalid complementary slackness for ", n, ": ", s[n], " and ", pi[n]
            return False
    for n in c.quadratic_constraints.get_names():
        if fabs(s[n]) > tol and fabs(pi[n]) > tol:
            print >>sys.stderr, "Invalid complementary slackness for ", n, ": ", s[n], " and ", pi[n]
            return False
    for n in c.variables.get_names():
        if cone[n] == NOT_IN_CONE:
            if fabs(x[n]) > tol and fabs(dslack[n]) > tol:
                print >>sys.stderr, "Invalid complementary slackness for ", n, ": ", x[n], " and ", dslack[n]
                return False

    # Test stationarity.
    # We must have
    #  c - g[i]'(X)*pi[i] = 0
    # where c is the objective function, g[i] is the i-th constraint of the
    # problem, g[i]'(x) is the derivate of g[i] with respect to x and X is the
    # optimal solution.
    # We need to distinguish the following cases:
    # - linear constraints g(x) = ax - b. The derivative of such a
    #   constraint is g'(x) = a.
    # - second order constraints g(x[1],...,x[n]) = -x[1] + |(x[2],...,x[n])|
    #   the derivative of such a constraint is
    #     g'(x) = (-1, x[2]/|(x[2],...,x[n])|, ..., x[n]/|(x[2],...,x[n])|
    #   (here |.| denotes the Euclidean norm).
    # - bound constraints g(x) = -x for variables that are not explicitly
    #   contained in any second order cone constraint. The derivative for
    #   such a constraint is g'(x) = -1.
    # Note that it may happen that the derivative of a second order cone
    # constraint is not defined at the optimal solution X (this happens if
    # X=0). In this case we just skip the stationarity test.
    val = dict(zip(c.variables.get_names(), c.objective.get_linear()))

    for n in c.variables.get_names():
        if cone[n] == NOT_IN_CONE:
            val[n] -= dslack[n]

    for n in c.linear_constraints.get_names():
        r = c.linear_constraints.get_rows(n)
        for j in range(0, len(r.ind)):
            nj = c.variables.get_names(r.ind[j])
            val[nj] -= r.val[j] * pi[n]

    for n in c.quadratic_constraints.get_names():
        r = c.quadratic_constraints.get_quadratic_components(n)
        norm = 0
        for j in range(0, len(r.ind1)):
            nj = c.variables.get_names(r.ind1[j])
            if r.val[j] > 0:
                norm += x[nj] * x[nj]
        norm = sqrt(norm)
        if fabs(norm) <= tol:
            # Derivative is not defined. Skip test.
            print >>sys.stderr, "Cannot test stationarity at non-differentiable point."
            return True
        for j in range(0, len(r.ind1)):
            nj = c.variables.get_names(r.ind1[j])
            if r.val[j] < 0:
                val[nj] -= pi[n]
            else:
                val[nj] += pi[n] * x[nj] / norm

    # Now test that all elements in val[] are 0.
    for n in c.variables.get_names():
        if fabs(val[n]) > tol:
            print >>sys.stderr, "Invalid stationarity ", val[n], " for ", n
            return False

    return True

# This function creates the following model:
#   Minimize
#    obj: x1 + x2 + x3 + x4 + x5 + x6
#   Subject To
#    c1: x1 + x2      + x5      = 8
#    c2:           x3 + x5 + x6 = 10
#    q1: [ -x1^2 + x2^2 + x3^2 ] <= 0
#    q2: [ -x4^2 + x5^2 ] <= 0
#   Bounds
#    x2 Free
#    x3 Free
#    x5 Free
#   End
# which is a second order cone program in standard form.
# The function returns objective, variables and constraints in the
# values OBJ, VARS and RNGS.
def createmodel(c, cone):
    # Create variables.
    c.variables.add(names = [ "x1", "x2", "x3", "x4", "x5", "x6" ])
    c.variables.set_lower_bounds([("x2", -CPX.infinity),
                                  ("x3", -CPX.infinity),
                                  ("x5", -CPX.infinity)])

    # Create objective function.
    c.objective.set_linear([("x1", 1), ("x2", 1), ("x3", 1),
                            ("x4", 1), ("x5", 1), ("x6", 1)])

    # Create constraints.
    c.linear_constraints.add(lin_expr = [[["x1", "x2", "x5"], [1, 1, 1]],
                                         [["x3", "x5", "x6"], [1, 1, 1]]],
                             senses = ['E', 'E'],
                             rhs = [8, 10],
                             names = ["c1","c2"])
    c.quadratic_constraints.add(quad_expr = [["x1", "x2", "x3"],
                                             ["x1", "x2", "x3"],
                                             [-1,   1,    1   ]],
                                sense = 'L',
                                rhs = 0,
                                name = "q1")
    c.quadratic_constraints.add(quad_expr = [["x4", "x5"],
                                             ["x4", "x5"],
                                             [-1,   1   ]],
                                sense = 'L',
                                rhs = 0,
                                name = "q2")

    # Set up the cone map.
    cone["x1"] = "q1"
    cone["x2"] = NOT_CONE_HEAD
    cone["x3"] = NOT_CONE_HEAD
    cone["x4"] = "q2"
    cone["x5"] = NOT_CONE_HEAD
    cone["x6"] = NOT_IN_CONE

# Runs the example.
def socpex1():
    c = CPX.Cplex()

    # sys.stdout is the default output stream for log and results
    # so these lines may be omitted
    c.set_log_stream(sys.stdout)
    c.set_results_stream(sys.stdout)

    # Create the model.
    cone = dict()
    createmodel(c, cone)

    # Apply parameter settings.
    c.parameters.barrier.qcpconvergetol.set(CONVTOL)

    # Solve the problem. If we cannot find an _optimal_ solution then
    # there is no point in checking the KKT conditions and we throw an
    # exception.
    c.solve()
    if not c.solution.get_status() == c.solution.status.optimal:
        raise StandardError("Failed to solve problem to optimality")


    # Test the KKT conditions on the solution.
    if not checkkkt(c, cone, TESTTOL):
        print >>sys.stderr, "Testing of KKT conditions failed."
    else:
        print "KKT conditions are satisfied."
        return 0

    return -1

if __name__ == "__main__":
    # Run the example.
    exitcode = socpex1()
    sys.exit(exitcode)

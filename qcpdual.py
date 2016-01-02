#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: qpcdual.py
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
# qcpdual.py - Illustrates how to query and analyze dual values of a QCP.
#

from math import fabs
import cplex
import sys

ZEROTOL = 1e-6

# Problem data
# The data defines the following model:
#   Minimize
#    obj: 3x1 - x2 + 3x3 + 2x4 + x5 + 2x6 + 4x7
#   Subject To
#    c1: x1 + x2 = 4
#    c2: x1 + x3 >= 3
#    c3: x6 + x7 <= 5
#    c4: -x1 + x7 >= -2
#    q1: [ -x1^2 + x2^2 ] <= 0
#    q2: [ 4.25x3^2 -2x3*x4 + 4.25x4^2 - 2x4*x5 + 4x5^2  ] + 2 x1 <= 9.0
#    q3: [ x6^2 - x7^2 ] >= 4
#   Bounds
#     0 <= x1 <= 3
#     x2 Free
#     0 <= x3 <= 0.5
#     x4 Free
#     x5 Free
#     x7 Free
#    End
class Data:
    obj      = [ 3.0, -1.0, 3.0, 2.0, 1.0, 2.0, 4.0 ]
    lb       = [ 0.0, -cplex.infinity, 0.0, -cplex.infinity, -cplex.infinity,
                 0.0, -cplex.infinity ]
    ub       = [ 3, cplex.infinity, 0.5, cplex.infinity, cplex.infinity,
                 cplex.infinity, cplex.infinity]
    cname    = [ "x1", "x2", "x3", "x4", "x5", "x6", "x7" ]
    
    rhs      = [ 4.0, 3.0, 5.0, -2.0 ]
    sense    = "EGLG"
    rows     = [
        [["x1", "x2"],[1.0, 1.0]],
        [["x1", "x3"],[1.0, 1.0]],
        [["x6", "x7"],[1.0, 1.0]],
        [["x1", "x7"],[-1.0, 1.0]]
        ]
    rname    = [ "c1", "c2", "c3", "c4" ]

    qlin     = [ cplex.SparsePair(),
                 cplex.SparsePair(["x1"],[2.0]),
                 cplex.SparsePair()]
    quad     = [ cplex.SparseTriple(["x1","x2"],["x1","x2"],[-1.0,1.0]),
                 cplex.SparseTriple(["x3", "x3", "x4", "x4", "x5"],
                                    ["x3", "x4", "x4", "x5", "x5"],
                                    [4.25, -2.0, 4.25, -2.0, 4.0 ]),
                 cplex.SparseTriple(["x6","x7"],["x6","x7"],[1.0,-1.0])
                 ]
    qsense   = [ 'L', 'L', 'G' ]
    qrhs     = [ 0.0, 9.0, 4.0 ]
    qname    = [ "q1", "q2", "q3" ]

# ###################################################################### #
#                                                                        #
#    C A L C U L A T E   D U A L S   F O R   Q U A D   C O N S T R S     #
#                                                                        #
#    CPLEX does not give us the dual multipliers for quadratic           #
#    constraints directly. This is because they may not be properly      #
#    defined at the cone top and deciding whether we are at the cone     #
#    top or not involves (problem specific) tolerance issues. CPLEX      #
#    instead gives us all the values we need in order to compute the     #
#    dual multipliers if we are not at the cone top.                     #
#                                                                        #
# ###################################################################### #/
    
# Calculate dual multipliers for quadratic constraints from dual
# slack vectors and optimal solution.
# The dual multiplier is the dual slack divided by the derivative evaluated
# at the optimal solution. If the optimal solution is 0 then the derivative
# at this point is not defined (we are at the cone top) and we cannot compute
# a dual multiplier.
# CPLEX the Cplex instance that holds the optimal solution.
# TOL   the tolerance that is used when testing whether we are the cone top.
# Returns a dictionary (indexed by constraint names) with the dual multipliers
# for all quadratic constraints in CPLEX.
def getqconstrmultipliers(cplex,tol):
    qpi = dict()

    x = dict(zip(cplex.variables.get_names(),
                 cplex.solution.get_values()))

    # Helper function to map a variable index to a variable name
    v2name = lambda x: cplex.variables.get_names(x)
    
    for q in cplex.quadratic_constraints.get_names():
        # 'dense' is the dense slack vector
        dense = dict(zip(cplex.variables.get_names(),
                         [0] * cplex.variables.get_num()))
        grad = dict(zip(cplex.variables.get_names(),
                        [0] * cplex.variables.get_num()))
        qdslack = cplex.solution.get_quadratic_dualslack(q)
        for (var,val) in zip(map(v2name, qdslack.ind), qdslack.val):
            dense[var] = val

        # Compute value of derivative at optimal solution.
        # The derivative of a quadratic constraint x^TQx + a^Tx + b <= 0
        # is Q^Tx + Qx + a.
        conetop = True
        quad = cplex.quadratic_constraints.get_quadratic_components(q)
        for (row,col,val) in zip(map(v2name, quad.ind1),
                                 map(v2name, quad.ind2),
                                     quad.val):
            if fabs(x[row]) > tol or fabs(x[col]) > tol:
                conetop = False
            grad[row] += val * x[col]
            grad[col] += val * x[row]
        l = cplex.quadratic_constraints.get_linear_components(q)
        for (var,val) in zip(map(v2name, l.ind), l.val):
            grad[var] += val
            if fabs(x[var]) > tol:
                conetop = False

        if conetop:
            raise Exception("Cannot compute dual multiplier at cone top!")

        # Compute qpi[q] as slack/gradient.
        # We may have several indices to choose from and use the one
        # with largest absolute value in the denominator.
        ok = False
        maxabs = -1.0
        for v in cplex.variables.get_names():
            if fabs(grad[v]) > tol:
                if fabs(grad[v]) > maxabs:
                    qpi[q] = dense[v] / grad[v]
                    maxabs = fabs(grad[v])
                ok = True

        if not ok:
            qpi[q] = 0

    return qpi

def qcpdual():
    # ###################################################################### #
    #                                                                        #
    #    S E T U P   P R O B L E M                                           #
    #                                                                        #
    # ###################################################################### #
    c = cplex.Cplex()
    c.variables.add(obj = Data.obj,
                    lb = Data.lb, ub = Data.ub, names = Data.cname)
    c.linear_constraints.add(lin_expr = Data.rows, senses = Data.sense,
                             rhs = Data.rhs, names = Data.rname)
    for q in range(0, len(Data.qname)):
        c.quadratic_constraints.add(lin_expr = Data.qlin[q],
                                    quad_expr = Data.quad[q],
                                    sense = Data.qsense[q],
                                    rhs = Data.qrhs[q],
                                    name = Data.qname[q])

    # ###################################################################### #
    #                                                                        #
    #    O P T I M I Z E   P R O B L E M                                     #
    #                                                                        #
    # ###################################################################### #
    c.parameters.barrier.qcpconvergetol.set(1e-10)
    c.solve()
    if not c.solution.get_status() == c.solution.status.optimal:
        raise Exception("No optimal solution found")

    # ###################################################################### #
    #                                                                        #
    #    Q U E R Y   S O L U T I O N                                         #
    #                                                                        #
    # ###################################################################### #
    # We store all results in a dictionary so that we can easily access
    # them by name.
    # Optimal solution and slacks for linear and quadratic constraints.
    x = dict(zip(c.variables.get_names(),
                 c.solution.get_values()))
    slack = dict(zip(c.linear_constraints.get_names(),
                     c.solution.get_linear_slacks()))
    qslack = dict(zip(c.quadratic_constraints.get_names(),
                      c.solution.get_quadratic_slacks()))
    # Dual multipliers for constraints.
    cpi = dict(zip(c.variables.get_names(),
                   c.solution.get_reduced_costs()))
    rpi = dict(zip(c.linear_constraints.get_names(),
                   c.solution.get_dual_values()))
    qpi = getqconstrmultipliers(c, ZEROTOL);

    # Some CPLEX functions return results by index instead of by name.
    # Define a function that translates from index to name.
    v2name = lambda x: c.variables.get_names(x)

    # ###################################################################### #
    #                                                                        #
    #    C H E C K   K K T   C O N D I T I O N S                             #
    #                                                                        #
    #    Here we verify that the optimal solution computed by CPLEX (and     #
    #    the qpi[] values computed above) satisfy the KKT conditions.        #
    #                                                                        #
    # ###################################################################### #

    # Primal feasibility: This example is about duals so we skip this test. #

    # Dual feasibility: We must verify
    # - for <= constraints (linear or quadratic) the dual
    #   multiplier is non-positive.
    # - for >= constraints (linear or quadratic) the dual
    #   multiplier is non-negative.
    for r in c.linear_constraints.get_names():
        if c.linear_constraints.get_senses(r) == 'E':
            pass
        elif c.linear_constraints.get_senses(r) == 'R':
            pass
        elif c.linear_constraints.get_senses(r) == 'L':
            if rpi[r] > ZEROTOL:
                raise Exception("Dual feasibility test failed")
        elif c.linear_constraints.get_senses(r) == 'G':
            if rpi[r] < -ZEROTOL:
                raise Exception("Dual feasibility test failed")
    for q in c.quadratic_constraints.get_names():
        if c.quadratic_constraints.get_senses(q) == 'E':
            pass
        elif  c.quadratic_constraints.get_senses(q) == 'L':
            if qpi[q] > ZEROTOL:
                raise Exception("Dual feasibility test failed")
        elif c.quadratic_constraints.get_senses(q) == 'G':
            if qpi[q] < -ZEROTOL:
                raise Exception("Dual feasibility test failed")


    # Complementary slackness.
    # For any constraint the product of primal slack and dual multiplier
    # must be 0.
    for r in c.linear_constraints.get_names():
        if (not c.linear_constraints.get_senses(r) == 'E') and fabs(slack[r] * rpi[r]) > ZEROTOL:
            raise Exception("Complementary slackness test failed")
    for q in c.quadratic_constraints.get_names():
        if (not c.quadratic_constraints.get_senses(q) == 'E') and fabs(qslack[q] * qpi[q]) > ZEROTOL:
            raise Exception("Complementary slackness test failed")
    for j in c.variables.get_names():
        if c.variables.get_upper_bounds(j) < cplex.infinity:
            slk = c.variables.get_upper_bounds(j) - x[j]
            if cpi[j] < -ZEROTOL:
                dual = cpi[j]
            else:
                dual = 0.0
            if fabs(slk * dual) > ZEROTOL:
                raise Exception("Complementary slackness test failed")
        if c.variables.get_lower_bounds(j) > -cplex.infinity:
            slk = x[j] - c.variables.get_lower_bounds(j)
            if cpi[j] > ZEROTOL:
                dual = cpi[j]
            else:
                dual = 0.0
            if fabs(slk * dual) > ZEROTOL:
                raise Exception("Complementary slackness test failed")

    # Stationarity.
    # The difference between objective function and gradient at optimal
    # solution multiplied by dual multipliers must be 0, i.e., for the
    # optimal solution x
    # 0 == c
    #      - sum(r in rows)  r'(x)*rpi[r]
    #      - sum(q in quads) q'(x)*qpi[q]
    #      - sum(c in cols)  b'(x)*cpi[c]
    # where r' and q' are the derivatives of a row or quadratic constraint,
    # x is the optimal solution and rpi[r] and qpi[q] are the dual
    # multipliers for row r and quadratic constraint q.
    # b' is the derivative of a bound constraint and cpi[c] the dual bound
    # multiplier for column c.

    # Objective function
    kktsum = dict(zip(c.variables.get_names(), c.objective.get_linear()))

    # Linear constraints.
    # The derivative of a linear constraint ax - b (<)= 0 is just a.
    for r in c.linear_constraints.get_names():
        row = c.linear_constraints.get_rows(r)
        for (var,val) in zip(map(v2name, row.ind), row.val):
            kktsum[var] -= rpi[r] * val
    # Quadratic constraints.
    # The derivative of a constraint xQx + ax - b <= 0 is
    # Qx + Q'x + a.
    for q in c.quadratic_constraints.get_names():
        lin = c.quadratic_constraints.get_linear_components(q)
        for (var,val) in zip(map(v2name, lin.ind), lin.val):
            kktsum[var] -= qpi[q] * val
        quad = c.quadratic_constraints.get_quadratic_components(q)
        for (row,col,val) in zip(map(v2name, quad.ind1), map(v2name, quad.ind2), quad.val):
            kktsum[row] -= qpi[q] * x[col] * val
            kktsum[col] -= qpi[q] * x[row] * val

    # Bounds.
    # The derivative for lower bounds is -1 and that for upper bounds
    # is 1.
    # CPLEX already returns dj with the appropriate sign so there is
    # no need to distinguish between different bound types here.
    for v in c.variables.get_names():
        kktsum[v] -= cpi[v]

    for v in c.variables.get_names():
        if fabs(kktsum[v]) > ZEROTOL:
            raise Exception("Stationarity test failed");

    # KKT conditions satisfied. Dump out solution and dual values.
    print "Optimal solution satisfies KKT conditions."
    print "   x[] =",
    for n in c.variables.get_names():
        print " %7.3f" % x[n],
    print " ]"
    print "cpi[] = [",
    for n in c.variables.get_names():
        print " %7.3f" % cpi[n],
    print " ]"
    print "rpi[] = [",
    for n in c.linear_constraints.get_names():
        print " %7.3f" % rpi[n],
    print " ]"
    print "qpi[] = [",
    for n in c.quadratic_constraints.get_names():
        print " %7.3f" % qpi[n],
    print " ]"


if __name__ == "__main__":
    # Run the example
    exitcode = qcpdual()
    sys.exit(exitcode)

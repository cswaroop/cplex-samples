#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: distmipex1.py
# Version 12.6  
# ---------------------------------------------------------------------------
# Licensed Materials - Property of IBM
# 5725-A06 5725-A29 5724-Y48 5724-Y49 5724-Y54 5724-Y55 5655-Y21
# Copyright IBM Corporation 2013. All Rights Reserved.
# 
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with
# IBM Corp.
# ---------------------------------------------------------------------------
#
# distmipex1.py - Reading a MIP problem from a file and solving
#                 it via distributed parallel optimization.

import cplex
from cplex.exceptions import CplexError
import sys

# First find the VMC argument
vmconfig = sys.argv[1]

# Now solve the model passed in on the command line
# using distributed parallel MIP optimization.
try:
    # Create CPLEX solver and load model.
    cpx = cplex.Cplex()
    cpx.read(sys.argv[2])

    # Load the virtual machine configuration.
    # This will force solve() to use distributed parallel MIP.
    cpx.read_copy_vmconfig(vmconfig)

    # Solve the model and print some solution information.
    cpx.solve()
    if cpx.solution.is_primal_feasible():
        print "Solution value  = ", cpx.solution.get_objective_value()
    else:
        print "No solution available"
    print "Solution status = " , cpx.solution.get_status()
        
except CplexError, exc:
    print exc
    sys.exit(-1)

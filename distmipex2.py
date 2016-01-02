#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: distmipex2.py
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
# distmipex2.py - Reading a MIP problem from a file and solving
#                 it via distributed parallel optimization using
#                 an informational callback.

import cplex
from cplex.exceptions import CplexError
import sys
from cplex.callbacks import MIPInfoCallback
from math import fabs


class LoggingCallback(MIPInfoCallback):

    def __call__(self):
        newincumbent = 0
        hasincumbent = self.has_incumbent()
        if hasincumbent:
            incobjvalue = self.get_incumbent_objective_value()
            if fabs(self.lastincumbent - incobjvalue) > \
                   1e-5*(1 + fabs(incobjvalue)):
                self.lastincumbent = incobjvalue
                newincumbent = 1

        dettime = self.get_dettime()            
        if dettime >= self.lastdettime + 1000.0 or newincumbent:
            if not newincumbent:
                self.lastdettime = dettime

            walltime = self.get_time()
                
            if hasincumbent:
                incstr = "  Incumbent objective = " + \
                         str(self.get_incumbent_objective_value())
            else:
                incstr = ""
            print "Time = %.2f  Dettime = %.2f  Best objective = %g%s" \
                  % (walltime - self.timestart, dettime - self.dettimestart,
                     self.get_best_objective_value(), incstr)

        if newincumbent:
            incval = self.get_incumbent_values()
            print "New incumbent variable values:", incval


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

    # Turn off CPLEX logging
    cpx.parameters.mip.display.set(0)

    # Install logging info callback
    logging_cb = cpx.register_callback(LoggingCallback)
    logging_cb.lastincumbent = 1e+75
    logging_cb.lastdettime = -1e+75
    logging_cb.timestart = cpx.get_time() 
    logging_cb.dettimestart = cpx.get_dettime()

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

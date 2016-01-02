#!/usr/bin/python
# --------------------------------------------------------------------------
# File: examples/src/python/transport.py
# Version 12.6
# --------------------------------------------------------------------------
# Licensed Materials - Property of IBM
# 5725-A06 5725-A29 5724-Y48 5724-Y49 5724-Y54 5724-Y55 5655-Y21
# Copyright IBM Corporation 2008, 2013. All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
# --------------------------------------------------------------------------
#
# transport.py -   Model piecewise linear cost coefficients with special
#                  ordered sets (SOS). The problem is a simple transportation
#                  model. Set the function argument to 0 for a convex piecewise
#                  linear model and to 1 for a concave piecewise linear model.
#
# The user must choose the model type on the command line:
#
#    python transport.py 0 
#    python transport.py 1  
#
# Alternatively, this example can be run from the python interpreter by
# 
# >>> import transport
#
# The user will be prompted to chose the model type.

import cplex
from cplex.exceptions import CplexError
import sys

def transport(convex):
   try:      
      # The x coordinate of the last break point of pwl
      k = 0
      pwl_x = [[0.0 for a in range(4)] for b in range(n)]
      pwl_y = [[0.0 for a in range(4)] for b in range(n)]

      for i in range(nbSupply):
         for j in range(nbDemand):
            if supply[i] < demand[j]:
               midval = supply[i]
            else:
               midval = demand[j]

            pwl_x[k] = [0.0, 200.0, 400.0, midval]

            if convex == 0:
               pwl_slope = [30.0, 80.0, 130.0]
            else:
               pwl_slope = [120.0, 80.0, 50.0]

            pwl_y[k][0] = 0.0
            pwl_y[k][1] = pwl_x[k][1] * pwl_slope[0]
            pwl_y[k][2] = \
                  pwl_y[k][1] + pwl_slope[1] * (pwl_x[k][2] - pwl_x[k][1])
            pwl_y[k][3] = pwl_y[k][2] + pwl_slope[2] * (midval - pwl_x[k][2])

            k = k + 1
      # Build model
      model = cplex.Cplex()
      model.objective.set_sense(model.objective.sense.minimize)

      # x(varindex(i, j)) is the amount that is shipped from supplier i to
      # recipient j
      model.variables.add(obj = [0.0] * n, lb = [0.0] * n, \
            ub = [cplex.infinity] * n)

      # y(varindex(i, j)) is used to model the PWL cost 
      # associated with this shipment.
      colname_y = ["y" + str(j+1) for j in range(n)]
      model.variables.add(obj = [1.0] * n, lb = [0.0] * n, \
            ub = [cplex.infinity] * n, names = colname_y)

      # Generate colnames for lambdas.
      colname_id = ["lambda_" + str(j+1) for j in range(4*n)]

      # Add columns for lambda.
      model.variables.add(obj = [0.0] * (4 * n), names = colname_id)

      # Supply must meet demand
      for i in range(nbSupply):
         ind = []
         val = []
         for j in range(nbDemand):
            ind.append(varindex(i, j))
            val.append(1.0)

         row = [[ind, val]]
         model.linear_constraints.add(lin_expr = row,\
               senses = "E", rhs = [supply[i]])

      # Demand must meet supply
      for i in range(nbDemand):
         ind = []
         val = []
         for j in range(nbSupply):
            ind.append(varindex(j, i))
            val.append(1.0)

         row = [[ind, val]]
         model.linear_constraints.add(lin_expr = row,\
               senses = "E", rhs = [demand[i]])

      # Add constraints about lambda
      # x = SUM(lambda_i*x_i)
      # y = SUM(lambda_i*y_i)
      # SUM(lambda_i * x_i) = 1
      for i in range(n):
         lambda_ind = range(2*n + i*4, 2*n + i*4 + 4)

         ind = []
         ind[0:4] = lambda_ind
         ind.append(i)
         val = []
         val[0:4] = pwl_x[i]
         val.append(-1)
         row = [[ind, val]]
         model.linear_constraints.add(lin_expr = row, senses = "E", rhs = [0.0])


         ind[4] = n + i         
         val[0:4] = pwl_y[i]
         val.append(-1)
         row = [[ind, val]]
         model.linear_constraints.add(lin_expr = row, senses = "E", rhs = [0.0])

         # SUM(lambda_i * x_i) = 1
         row = [[lambda_ind, [1] * 4]]
         model.linear_constraints.add(lin_expr = row, senses = "E", rhs = [1.0])

         sosind = lambda_ind
         soswt = []
         soswt[0:4] = pwl_x[i]
         soswt[3] = pwl_x[i][3] + 1.0
         s = cplex.SparsePair(ind = sosind, val = soswt)
         model.SOS.add(type = "2", SOS = s)

      # solve model 
      model.solve() 
      model.write('transport.lp')

   except CplexError, exc:
      print exc
      return

   # Display solution
   print "Solution status = ", model.solution.get_status()
   print " -  Solution"
   for i in range(nbSupply):
      print "    ", i, ":",
      for j in range(nbDemand):
         print "\t%6f" % model.solution.get_values(varindex(i, j)),
      print
   print "  Cost =  ", model.solution.get_objective_value()

if __name__ == "__main__":

   if len(sys.argv) < 2:
      print "Specify an argument to choose between convex and concave problems"
      print "Usage: python transport.py <model>"
      print " model = 0 -> convex piecewise linear model"
      print " model = 1 -> concave piecewise linear model [default]"
      convex = 1
   else:
      convex = int(sys.argv[1])
else:
   prompt = """Enter model type:
  model = 0 -> convex piecewise linear model
  model = 1 -> concave piecewise linear model\n"""
   try:
      convex = int(input(prompt))
   except:
      convex = -1
   if convex != 0 and convex != 1:
      convex = 1
      print "invalid input: using concave piecewise linear model"

supply   = [1000.0 ,850.0, 1250.0]
nbSupply = len(supply)
demand   = [900.0, 1200.0, 600.0, 400.0]
nbDemand = len (demand)
n        = nbSupply*nbDemand

def varindex(m, n):
   return m * nbDemand + n

transport(convex)


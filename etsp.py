#!/usr/bin/python
# --------------------------------------------------------------------------
# File: examples/src/python/etsp.py
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
# etsp.py -  Model an earliness-tardiness scheduling problem 
#            with indicator constraints
#
# The user may choose the data file on the command line:
#
#    python etsp.py  ../../data/etsp.dat  
#    python etsp.py 
#
# Alternatively, this example can be run from the python interpreter by
# 
# >>> import etsp 
#
# The user will be prompted to chose the data file.

import cplex
from cplex.exceptions import CplexError
from inputdata import read_dat_file
import sys

def etsp(filename):
   try:      
      # Build model
      model = cplex.Cplex();
      model.objective.set_sense(model.objective.sense.minimize)

      # Add activity start time variables
      nbStart = nbJob * nbResource
      obj = [0.0] * nbStart 
      lb  = [0.0] * nbStart
      ub  = [10000.0] * nbStart
      model.variables.add(obj, lb, ub)    

      # State precedence constraints
      # starttime(i, j) - starttime(i, j-1) >= duration(i, j-1)
      for i in range(nbJob):
         for j in range(1, nbResource):
            ind = [starttime(i, j), starttime(i, j-1)]
            val = [1.0, -1.0]
            row = [[ind, val]]
            model.linear_constraints.add(lin_expr = row, senses = "G", rhs =
                  [duration[i][j-1]])

      # Add indicator variables
      nIndicatorVars = nbResource * nbJob * (nbJob - 1)
      colname_ind = ["ind"+str(j+1) for j in range(nIndicatorVars)]
      obj = [0.0] * nIndicatorVars
      lb  = [0.0] * nIndicatorVars
      ub  = [1.0] * nIndicatorVars
      types = ["B"] * nIndicatorVars
      model.variables.add(obj, lb, ub, types, colname_ind)

      # Add ind1 + ind2 >= 1
      #     ind3 + ind4 >= 1
      #     ind5 + ind6 >= 1
      #     ...
      # constraints
      j = nbStart 
      for i in range(nIndicatorVars / 2):
         ind = [j, j+1]
         val = [1.0, 1.0]
         row = [[ind, val]]
         model.linear_constraints.add(lin_expr = row, senses = "G", rhs = [1])
         j = j + 2

      # Add indicator constraints
      # i1 = 1 <-> c1
      # i2 = 1 <-> c2
      index = 0
      for i in range(nbResource):
         e = nbJob - 1
         for j in range(e):
            activity1 = activityOnAResource[i][j]
            for k in range(j+1, nbJob):
               activity2 = activityOnAResource[i][k]

               ic_dict = {}
               ic_dict["indvar"] = nbStart + index
               ic_dict["lin_expr"] = cplex.SparsePair(
                     ind = [starttime(j,activity1), starttime(k, activity2)], 
                     val = [1.0,-1.0])
               ic_dict["rhs"] = duration[k][activity2]/1.0
               ic_dict["sense"] = "G"
               ic_dict["complemented"] = 0
               # ind(nbStart + index) = 1 -> ...
               # starttime(j, activity1) - starttime(k, activity2) >=
               # duration(k, activity2)
               model.indicator_constraints.add(**ic_dict)

               ic_dict["sense"] = "L"
               ic_dict["complemented"] = 1
               # ind(nbStart + index) = 0 -> ...
               # starttime(j, activity1) - starttime(k, activity2) <=
               # duration(k, activity2)
               model.indicator_constraints.add(**ic_dict)

               ic_dict = {}
               ic_dict["indvar"] = nbStart + index + 1
               ic_dict["lin_expr"] = cplex.SparsePair(ind =[starttime(k,
                  activity2), starttime(j, activity1)], val = [1.0, -1.0])
               ic_dict["rhs"] = duration[j][activity1]/1.0
               ic_dict["sense"] = "G"
               ic_dict["complemented"] = 0
               # ind(nbStart + index) = 1 -> ...
               # starttime(k, activity2) - starttime(j, activity1) >=
               # duration(j, activity1)
               model.indicator_constraints.add(**ic_dict)

               ic_dict["sense"] = "L"
               ic_dict["complemented"] = 1
               # ind(nbStart + index) = 0 -> ...
               # starttime(k, activity2) - starttime(j, activity1) <=
               # duration(j, activity1)
               model.indicator_constraints.add(**ic_dict)

               index = index + 2

      # Add Objective function
      # each job has a cost which contains jobEarlinessCost and
      # jobTardinessCost, and get the index of Earliness variables,
      # Tardiness variables and Endness variables
      indexOfEarlinessVar = \
            range(model.variables.get_num(), model.variables.get_num() + nbJob)
      model.variables.add(obj = jobEarlinessCost)

      indexOfTardinessVar = \
            range(model.variables.get_num(), model.variables.get_num() + nbJob)
      model.variables.add(obj = jobTardinessCost)

      # Add finished time variables
      indexOfEndnessVar = range(model.variables.get_num(),\
            model.variables.get_num() + nbJob)
      model.variables.add(obj = [0.0] * nbJob)

      # Add constraints for each Job
      # indexOfEndnessVar[i] - starttime(i, nbResource) = duration[i][nbResource]
      for i in range(nbJob):
         ind = [indexOfEndnessVar[i], starttime(i, nbResource - 1)]
         val = [1.0, -1.0]
         row = [[ind, val]]
         model.linear_constraints.add(lin_expr = row, senses = "E", rhs =
               [duration[i][nbResource - 1]])

      # Add constraints for each Job
      # jobDueDate[i] = \
      # indexOfEndnessVar[i] + indexOfEarlinessVar[i] - indexOfTardinessVar[i]
      for i in range(nbJob):
         ind = [indexOfEndnessVar[i],
                indexOfEarlinessVar[i],
                indexOfTardinessVar[i]]
         val = [1.0, 1.0, -1.0]
         row = [[ind, val]]
         model.linear_constraints.add(lin_expr = row, senses = "E", rhs =
               [jobDueDate[i]])

      model.parameters.emphasis.mip = 4
      model.solve()
      model.write('etsp.sav')
   except CplexError, exc:
      print exc
      return

# Display solution
   print "Solution status = ", model.solution.get_status()
   print "Optimal Value =  ", model.solution.get_objective_value()

defaultfile = "../../../examples/data/etsp.dat"
   
if __name__ == "__main__":
   # Read in data file. If no file name is given on the command line
   # we use a default file name. The data we read is
   # activityOnAResource -- 
   #                     An array of arrays represents the resources 
   #                     required for each activity of a job
   # duration         -- 
   #                  An array of arrays represents the duration required 
   #                  for each activity of a job.    
   # jobDueDate       -- 
   #                  contains the due date for each job;
   # jobEarlinessCost -- 
   #                  contains the penalty for being too early for each job;
   # jobTardinessCost -- 
   #                  contains the penalty for being too late for each job.

   datafile = defaultfile
   
   if len(sys.argv) < 2:
      print "Default data file : " + datafile
   else:
      datafile = sys.argv[1]

else:
    prompt = """Enter the path to a data file:
The path must be entered as a string; e.g.
"../../../examples/data/etsp.dat".
Enter "" to use the default file.\n"""
    user_file = input(prompt)
    print "hello" + user_file
    if user_file != "":
       datafile = user_file
    else:
       datafile = defaultfile

activityOnAResource, \
duration, \
jobDueDate, \
jobEarlinessCost, \
jobTardinessCost = \
read_dat_file(datafile)

nbJob = len (jobDueDate)
nbResource = len (activityOnAResource[1])

def starttime(job, res):
   return job * nbJob + res 
etsp(datafile)


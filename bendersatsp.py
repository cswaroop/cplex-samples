#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: bendersatsp.py
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
# Example bendersatsp.py solves a flow MILP model for an
# Asymmetric Traveling Salesman Problem (ATSP) instance
# through Benders decomposition.
#
# The arc costs of an ATSP instance are read from an input file.
# The flow MILP model is decomposed into a master ILP and a worker LP.
#
# The master ILP is then solved by adding Benders' cuts during
# the branch-and-cut process via the cut callback classes 
# LazyConstraintCallback and UserCutCallback.
# The cut callbacks add to the master ILP violated Benders' cuts
# that are found by solving the worker LP.
#
# The example allows the user to decide if Benders' cuts have to be separated:
#
# a) Only to separate integer infeasible solutions.
# In this case, Benders' cuts are treated as lazy constraints through the
# class LazyConstraintCallback.
#
# b) Also to separate fractional infeasible solutions.
# In this case, Benders' cuts are treated as lazy constraints through the
# class LazyConstraintCallback.
# In addition, Benders' cuts are also treated as user cuts through the
# class UserCutCallback.
#
# 
# To run this example from the command line, use
#
#    python bendersatsp.py {0|1} [filename]
# where
#     0         Indicates that Benders' cuts are only used as lazy constraints,
#               to separate integer infeasible solutions.
#     1         Indicates that Benders' cuts are also used as user cuts,
#               to separate fractional infeasible solutions.
# 
#     filename  Is the name of the file containing the ATSP instance (arc costs).
#               If filename is not specified, the instance
#               ../../../examples/data/atsp.dat is read
#
#
# ATSP instance defined on a directed graph G = (V, A)
# - V = {0, ..., n-1}, V0 = V \ {0}
# - A = {(i,j) : i in V, j in V, i != j }
# - forall i in V: delta+(i) = {(i,j) in A : j in V}
# - forall i in V: delta-(i) = {(j,i) in A : j in V}
# - c(i,j) = traveling cost associated with (i,j) in A
#
# Flow MILP model
#
# Modeling variables:
# forall (i,j) in A:
#    x(i,j) = 1, if arc (i,j) is selected
#           = 0, otherwise
# forall k in V0, forall (i,j) in A:
#    y(k,i,j) = flow of the commodity k through arc (i,j)
#
# Objective:
# minimize sum((i,j) in A) c(i,j) * x(i,j)
#
# Degree constraints:
# forall i in V: sum((i,j) in delta+(i)) x(i,j) = 1
# forall i in V: sum((j,i) in delta-(i)) x(j,i) = 1
#
# Binary constraints on arc variables:
# forall (i,j) in A: x(i,j) in {0, 1}
#
# Flow constraints:
# forall k in V0, forall i in V:
#    sum((i,j) in delta+(i)) y(k,i,j) - sum((j,i) in delta-(i)) y(k,j,i) = q(k,i)
#    where q(k,i) =  1, if i = 0
#                 = -1, if k == i
#                 =  0, otherwise
#
# Capacity constraints:
# forall k in V0, for all (i,j) in A: y(k,i,j) <= x(i,j)
#
# Nonnegativity of flow variables:
# forall k in V0, for all (i,j) in A: y(k,i,j) >= 0

import sys
from math import fabs
import cplex
from cplex.callbacks import UserCutCallback, LazyConstraintCallback
from cplex.exceptions import CplexError
from inputdata import read_dat_file

# The class BendersLazyConsCallback 
# allows to add Benders' cuts as lazy constraints.
# 
class BendersLazyConsCallback(LazyConstraintCallback):
        
    def __call__(self):    
        x        = self.x
        workerLP = self.workerLP
        numNodes = len(x)
      
        # Get the current x solution
        sol = []
        for i in range(numNodes):
            sol.append([])
            sol[i] = self.get_values(x[i]); 
         
        # Benders' cut separation
        if workerLP.separate(sol, x):
            self.add(constraint = workerLP.cutLhs, sense = "G", rhs = workerLP.cutRhs)


# The class BendersUserCutCallback 
# allows to add Benders' cuts as user cuts.
# 
class BendersUserCutCallback(UserCutCallback):
        
    def __call__(self):  
        x        = self.x
        workerLP = self.workerLP
        numNodes = len(x)

        # Skip the separation if not at the end of the cut loop
        if self.is_after_cut_loop() == False:
            return
  
        # Get the current x solution
        sol = []
        for i in range(numNodes):
            sol.append([])
            sol[i] = self.get_values(x[i]); 
         
        # Benders' cut separation
        if workerLP.separate(sol, x):
            self.add(cut = workerLP.cutLhs, sense = "G", rhs = workerLP.cutRhs)
      

# Data class to read an ATSP instance from an input file 
class ProbData:

    def __init__(self, filename):
        
        # read the data in filename
        self.arcCost = read_dat_file(filename)[0]
        self.numNodes = len(self.arcCost)

        # check data consistency
        for i in range(self.numNodes):
            if len(self.arcCost[i]) != self.numNodes:
                print "ERROR: Data file '%s' contains inconsistent data\n" % filename
                raise Exception("data file error")
            self.arcCost[i][i] = 0.0

   
# This class builds the worker LP (i.e., the dual of flow constraints and
# capacity constraints of the flow MILP) and allows to separate violated
# Benders' cuts.
# 
class WorkerLP:
    
    # The constructor sets up the Cplex instance to solve the worker LP, 
    # and creates the worker LP (i.e., the dual of flow constraints and
    # capacity constraints of the flow MILP)
    #
    # Modeling variables:
    # forall k in V0, i in V:
    #    u(k,i) = dual variable associated with flow constraint (k,i)
    #
    # forall k in V0, forall (i,j) in A:
    #    v(k,i,j) = dual variable associated with capacity constraint (k,i,j)
    #
    # Objective:
    # minimize sum(k in V0) sum((i,j) in A) x(i,j) * v(k,i,j)
    #          - sum(k in V0) u(k,0) + sum(k in V0) u(k,k)
    #
    # Constraints:
    # forall k in V0, forall (i,j) in A: u(k,i) - u(k,j) <= v(k,i,j)
    #
    # Nonnegativity on variables v(k,i,j)
    # forall k in V0, forall (i,j) in A: v(k,i,j) >= 0
    #
    def __init__(self, numNodes): 

        # Set up Cplex instance to solve the worker LP
        cpx = cplex.Cplex()
        cpx.set_results_stream(None)
        cpx.set_log_stream(None) 
         
        # Turn off the presolve reductions and set the CPLEX optimizer
        # to solve the worker LP with primal simplex method.
        cpx.parameters.preprocessing.reduce.set(0) 
        cpx.parameters.lpmethod.set(cpx.parameters.lpmethod.values.primal)
        
        cpx.objective.set_sense(cpx.objective.sense.minimize)
        
        # Create variables v(k,i,j) forall k in V0, (i,j) in A
        # For simplicity, also dummy variables v(k,i,i) are created.
        # Those variables are fixed to 0 and do not contribute to 
        # the constraints.
        v = []
        for k in range(1, numNodes):
            v.append([])
            for i in range(numNodes):
                v[k-1].append([])
                for j in range(numNodes):
                    varName = "v."+str(k)+"."+str(i)+"."+str(j)
                    v[k-1][i].append(cpx.variables.get_num()) 
                    cpx.variables.add(obj = [0.0], 
                                      lb = [0.0], 
                                      ub = [cplex.infinity], 
                                      names = [varName])
                cpx.variables.set_upper_bounds(v[k-1][i][i], 0.0)
                
        # Create variables u(k,i) forall k in V0, i in V     
        u = []
        for k in range(1, numNodes):
            u.append([])
            for i in range(numNodes):
                varName = "u."+str(k)+"."+str(i)
                u[k-1].append(cpx.variables.get_num())
                obj = 0.0
                if i == 0:
                    obj = -1.0
                if i == k:
                    obj = 1.0;
                cpx.variables.add(obj = [obj], 
                                  lb = [-cplex.infinity], 
                                  ub = [cplex.infinity],  
                                  names = [varName])

        # Add constraints:
        # forall k in V0, forall (i,j) in A: u(k,i) - u(k,j) <= v(k,i,j)
        for k in range(1, numNodes):
            for i in range(numNodes):
                for j in range(0, numNodes):
                    if i != j:
                        thevars = []
                        thecoefs = []
                        thevars.append(v[k-1][i][j])
                        thecoefs.append(-1.0)
                        thevars.append(u[k-1][i])
                        thecoefs.append(1.0)
                        thevars.append(u[k-1][j])
                        thecoefs.append(-1.0)
                        cpx.linear_constraints.add(lin_expr = \
                                                   [cplex.SparsePair(thevars, thecoefs)],
                                                   senses = ["L"], rhs = [0.0])
                                                   
        self.cpx      = cpx
        self.v        = v
        self.u        = u
        self.numNodes = numNodes
                                 
      
    # This method separates Benders' cuts violated by the current x solution.
    # Violated cuts are found by solving the worker LP
    #
    def separate(self, xSol, x): 
        cpx              = self.cpx
        u                = self.u
        v                = self.v
        numNodes         = self.numNodes
        violatedCutFound = False
                
        # Update the objective function in the worker LP:
        # minimize sum(k in V0) sum((i,j) in A) x(i,j) * v(k,i,j)
        #          - sum(k in V0) u(k,0) + sum(k in V0) u(k,k)
        thevars = []
        thecoefs = []
        for k in range(1, numNodes):
            for i in range(numNodes):
                for j in range(numNodes):
                    thevars.append(v[k-1][i][j])
                    thecoefs.append(xSol[i][j])    
        cpx.objective.set_linear(zip(thevars, thecoefs))
      
        # Solve the worker LP
        cpx.solve()
      
        # A violated cut is available iff the solution status is unbounded     
        if cpx.solution.get_status() == cpx.solution.status.unbounded:
      
            # Get the violated cut as an unbounded ray of the worker LP
            ray = cpx.solution.advanced.get_ray()
           
            # Compute the cut from the unbounded ray. The cut is:
            # sum((i,j) in A) (sum(k in V0) v(k,i,j)) * x(i,j) >=
            # sum(k in V0) u(k,0) - u(k,k)
            numArcs = numNodes*numNodes
            cutVarsList  = []
            cutCoefsList = []
            for i in range(numNodes):
                for j in range(numNodes):
                    thecoef = 0.0
                    for k in range(1, numNodes):
                        v_k_i_j_index = (k-1)*numArcs + i*numNodes + j
                        if ray[v_k_i_j_index] > 1e-03:
                            thecoef = thecoef + ray[v_k_i_j_index]
                    if thecoef > 1e-03:
                        cutVarsList.append(x[i][j]) 
                        cutCoefsList.append(thecoef)
            cutLhs = cplex.SparsePair(ind = cutVarsList, val = cutCoefsList)
            
            vNumVars = (numNodes-1)*numArcs
            cutRhs = 0.0
            for k in range(1, numNodes):
                u_k_0_index = vNumVars + (k-1)*numNodes
                if fabs(ray[u_k_0_index]) > 1e-03:
                    cutRhs = cutRhs + ray[u_k_0_index]
                u_k_k_index = vNumVars + (k-1)*numNodes + k
                if fabs(ray[u_k_k_index]) > 1e-03:
                    cutRhs = cutRhs - ray[u_k_k_index]
            
            self.cutLhs = cutLhs
            self.cutRhs = cutRhs
            violatedCutFound = True

        return violatedCutFound


# This function creates the master ILP (arc variables x and degree constraints).
#
# Modeling variables:
# forall (i,j) in A:
#    x(i,j) = 1, if arc (i,j) is selected
#           = 0, otherwise
#
# Objective:
# minimize sum((i,j) in A) c(i,j) * x(i,j)
#
# Degree constraints:
# forall i in V: sum((i,j) in delta+(i)) x(i,j) = 1
# forall i in V: sum((j,i) in delta-(i)) x(j,i) = 1
#
# Binary constraints on arc variables:
# forall (i,j) in A: x(i,j) in {0, 1}
#
def createMasterILP(cpx, x, data):

    arcCost   = data.arcCost
    numNodes  = data.numNodes

    cpx.objective.set_sense(cpx.objective.sense.minimize)

    # Create variables x(i,j) for (i,j) in A 
    # For simplicity, also dummy variables x(i,i) are created.
    # Those variables are fixed to 0 and do not partecipate to 
    # the constraints.
    for i in range(numNodes):
        x.append([])
        for j in range(numNodes):
            varName = "x."+str(i)+"."+str(j)
            x[i].append(cpx.variables.get_num())
            cpx.variables.add(obj = [arcCost[i][j]], 
                              lb = [0.0], ub = [1.0], types = ["B"], 
                              names = [varName])
        cpx.variables.set_upper_bounds(x[i][i], 0) 
                                 
    # Add the out degree constraints.
    # forall i in V: sum((i,j) in delta+(i)) x(i,j) = 1
    for i in range(numNodes):
        thevars = []
        thecoefs = []
        for j in range(0, i):
            thevars.append(x[i][j])
            thecoefs.append(1)
        for j in range(i+1, numNodes):
            thevars.append(x[i][j])
            thecoefs.append(1)
        cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(thevars, thecoefs)],
                                   senses = ["E"], rhs = [1.0])
    
    # Add the in degree constraints.
    # forall i in V: sum((j,i) in delta-(i)) x(j,i) = 1
    for i in range(numNodes):
        thevars = []
        thecoefs = []
        for j in range(0, i):
            thevars.append(x[j][i])
            thecoefs.append(1)
        for j in range(i+1, numNodes):
            thevars.append(x[j][i])
            thecoefs.append(1)
        cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(thevars, thecoefs)],
                                   senses = ["E"], rhs = [1.0])

    
def bendersATSP(sepFracSols, filename):
    try:
        print "Benders' cuts separated to cut off: " , 
        if sepFracSols == "1":
            print "Integer and fractional infeasible solutions."
        else:
            print "Only integer infeasible solutions."

        # Read arc costs from data file (17 city problem)
        data = ProbData(filename);

        # Create master ILP
        cpx = cplex.Cplex()
        x = []
        createMasterILP(cpx, x, data)
        numNodes = data.numNodes

        # Create workerLP for Benders' cuts separation 
        workerLP = WorkerLP(numNodes);

        # Set up cplex parameters to use the cut callback for separating Benders' cuts
        cpx.parameters.preprocessing.presolve.set(cpx.parameters.preprocessing.presolve.values.off) 
                                        
        # Set the maximum number of threads to 1. 
        # This instruction is redundant: If MIP control callbacks are registered, 
        # then by default CPLEX uses 1 (one) thread only.
        # Note that the current example may not work properly if more than 1 threads 
        # are used, because the callback functions modify shared global data.
        # We refer the user to the documentation to see how to deal with multi-thread 
        # runs in presence of MIP control callbacks. 
        cpx.parameters.threads.set(1) 

        # Turn on traditional search for use with control callbacks
        cpx.parameters.mip.strategy.search.set(cpx.parameters.mip.strategy.search.values.traditional)
        
        lazyBenders = cpx.register_callback(BendersLazyConsCallback) 
        lazyBenders.x = x
        lazyBenders.workerLP = workerLP 
        if sepFracSols == "1":
            userBenders = cpx.register_callback(BendersUserCutCallback) 
            userBenders.x = x
            userBenders.workerLP = workerLP 
    
        # Solve the model
        cpx.solve()
        
    except CplexError, exc:
        print exc
        return
        
    solution = cpx.solution
    print
    print "Solution status: " , solution.get_status()
    print "Objective value: " , solution.get_objective_value()
        
    if solution.get_status() == solution.status.MIP_optimal:
        # Write out the optimal tour
        succ = [-1] * numNodes
        for i in range(numNodes):
            sol = solution.get_values(x[i])
            for j in range(numNodes):
                if sol[j] > 1e-03:
                    succ[i] = j 
        print "Optimal tour:"
        i = 0
        while succ[i] != 0: 
            print "%d, " % i , 
            i = succ[i]
        print i
    else:
        print "Solution status is not optimal"
        
        
def usage():
    print "Usage:     bendersatsp.py {0|1} [filename]"
    print " 0:        Benders' cuts only used as lazy constraints,"
    print "           to separate integer infeasible solutions."
    print " 1:        Benders' cuts also used as user cuts,"
    print "           to separate fractional infeasible solutions."
    print " filename: ATSP instance file name."
    print "           File ../../../examples/data/atsp.dat used if no name is provided."
   

if __name__ == "__main__":
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        usage()
        sys.exit(-1)
    if sys.argv[1] not in  ["0", "1"]:
        usage()
        sys.exit(-1)
    if len(sys.argv) == 3:
        filename = sys.argv[2]
    else:
        filename = "../../../examples/data/atsp.dat"
    bendersATSP(sys.argv[1][0], filename)


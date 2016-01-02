# facility.py -  Model and solve a facility location problem
#                
# You can run this example at the command line by
#
#    python facility.py
#
# or within the python interpreter by
#
# >>> import facility

import cplex
from cplex.exceptions import CplexSolverError
from inputdata import read_dat_file 
import sys

def facility():
    # Read in data file. If no file name is given on the command line
    # we use a default file name. The data we read is
    # capacity   -- a list/array of facility capacity
    # fixedcost  -- a list/array of facility fixed cost
    # cost       -- a matrix for the costs to serve each client by each facility

    datafile = "data/facility.dat"
    if len(sys.argv) < 2:
        print "Default data file : " + datafile
    else:
        datafile = sys.argv[1]
    capacity, fixedcost, cost = read_dat_file(datafile)

    num_facilities = len(fixedcost)
    num_clients = len(cost)

    # Create a new (empty) model and populate it below.
    model = cplex.Cplex()

    # Create one binary variable for each facility. The variables model 
    # whether each facility is open or not

    model.variables.add(obj = fixedcost, 
                        lb = [0] * num_facilities, 
                        ub = [1] * num_facilities, 
                        types = ["B"] * num_facilities)

    # Create one binary variable for each facility/client pair. The variables
    # model whether a client is served by a facility.
    for c in range(num_clients):
        model.variables.add(obj = cost[c], 
                            lb = [0] * num_facilities, 
                            ub = [1] * num_facilities, 
                            types = ["B"] * num_facilities)

    # Create corresponding indices for later use
    supply = []
    for c in range(num_clients):
        supply.append([])
        for f in range(num_facilities):
            supply[c].append((c+1)*(num_facilities)+f)
    # Equivalently, supply can be defined by list comprehension
    # supply = [[(c + 1) * num_facilities + f
    #            for f in range(num_facilities)] for c in range(num_clients)]
    

    # Each client must be assigned to exactly one location    
    for c in range(num_clients):        
        assignment_constraint = cplex.SparsePair(ind = [supply[c][f] for f in \
                                                        range(num_facilities)],
                                                 val = [1.0] * num_facilities)
        model.linear_constraints.add(lin_expr = [assignment_constraint],                    
                                     senses = ["E"], 
                                     rhs = [1]);
        
    # The number of clients assigned to a facility must be less than the
    # capacity of the facility, and clients must be assigned to an open facility
    for f in range(num_facilities):
        index = [f]
        value = [-capacity[f]]
        for c in range(num_clients):
            index.append(supply[c][f])
            value.append(1.0)
        capacity_constraint = cplex.SparsePair(ind = index, val = value)
        model.linear_constraints.add(lin_expr = [capacity_constraint],                    
                                     senses = ["L"], 
                                     rhs = [0]);

    # Our objective is to minimize cost. Fixed and variable costs 
    # have been set when variables were created.
    model.objective.set_sense(model.objective.sense.minimize)

    # Solve                                                         
    try:
        model.solve()
    except CplexSolverError, e:
        print "Exception raised during solve: " + e
    else:
        solution = model.solution

        # solution.get_status() returns an integer code
        print "Solution status = " , solution.get_status(), ":",
        # the following line prints the corresponding string
        print solution.status[solution.get_status()]
        
        # Display solution.
        print "Total cost = " , solution.get_objective_value()                
                                
        for f in range(num_facilities):
            if (solution.get_values(f) >
                model.parameters.mip.tolerances.integrality.get()):
                print "Facility %d is open and serves the following clients:" % f,
                for c in range(num_clients):
                    if (solution.get_values(supply[c][f]) >
                        model.parameters.mip.tolerances.integrality.get()):
                        print c,
                print

facility()

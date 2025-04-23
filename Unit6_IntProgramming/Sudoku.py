import numpy as np # import numpy package
import pyomo.environ as pyo # import pyomo package

# Data (known cell values)
known = [(1, 2, 4), (1, 4, 9), (1, 9, 7), (2, 1, 1), (2, 2, 9), (2, 4, 6), 
         (2, 9, 4), (3, 1, 5), (3, 8, 1), (4, 2, 8), (4, 5, 3), (4, 8, 7), 
         (5, 1, 2), (5, 6, 4), (5, 7, 5), (5, 9, 8), (6, 4, 5), (7, 8, 2), 
         (8, 7, 3), (8, 8, 4), (9, 2, 7), (9, 6, 6), (9, 9, 1)]

# Create a Concrete model
model = pyo.ConcreteModel()

# Index sets
N = pyo.RangeSet(9)
B = pyo.RangeSet(3)

# Decision variables
model.x = pyo.Var(N,N,N, within=pyo.Binary)

# Objective function
model.obj = pyo.Objective(expr = 0)

# Uniqueness constraints
def unique_rule(model,i,j):
    return sum(model.x[i, j, k] for k in N) == 1

model.unique = pyo.Constraint(N,N, rule=unique_rule)

# Row constraints
def row_rule(model,i,k):
    return sum(model.x[i, j, k] for j in N) == 1

model.row = pyo.Constraint(N,N, rule=row_rule)

# Column constraints
def col_rule(model,j,k):
    return sum(model.x[i, j, k] for i in N) == 1

model.col = pyo.Constraint(N,N, rule=col_rule)

# Block constraints
def block_rule(model,s,t,k):
    return sum(model.x[i, j, k] for i in pyo.RangeSet(3*s-2,3*s) for j in pyo.RangeSet(3*t-2,3*t)) == 1

model.block = pyo.Constraint(B,B,N, rule=block_rule)

# Known cells constraints
def knownCell_rule(model,i,j,k):
    return model.x[i,j,k] == 1

model.knownCell = pyo.Constraint(known, rule=knownCell_rule)

# Solve the model through the GLPK solver
solver = pyo.SolverFactory('glpk')
solver.solve(model)

# In case you are interested in the solution
model.display()

# Print the solution
sol_array = np.zeros((9,9))

for i in N:
    for j in N:
        for k in N:
            if pyo.value(model.x[i,j,k]) == 1:
                sol_array[i-1][j-1] = k

print(sol_array)


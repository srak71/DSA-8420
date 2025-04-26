# Import Python Libraries
import numpy as np
import pyomo.environ as pyo
from pyomo.opt import SolverFactory


"""
known: list fixed cells.
known = [(<row>, <col>, <dig>), (<i>, <j>, <k>), ... , (<row>, <col>, <dig>)].

Replace example values with custom values for personal killer sudoku solution.
"""
known = [(1, 7, 3), (2, 5, 3), (4, 2, 2), (5, 5, 2),
         (6, 7, 6), (7, 6, 1), (8, 3, 5), (8, 9, 2),
         (9, 4, 4), (9, 8, 3)]



"""
cages: list cage group with each cell coordinate.
cages = [[<Cage_Groups>], [(<i>,<j>), (<i>,<j>)], ... , [<Cage_Groups>]].

Replace example values with custom values for personal killer sudoku solution.
"""
cages = [[(1,1)], [(1,2), (1,3), (1,4)], [(1,5), (2,4), (2,5)],
    [(1,6), (2,6)], [(1,7), (1,8), (1,9), (2,8)], [(2,1)],
    [(2,2), (2,3)], [(2,7), (3,6), (3,7)], [(2,9)],
    [(3,1), (4,1)], [(3,2), (4,2), (5,1), (5,2), (6,1)],
    [(3,3), (4,3)], [(3,4), (3,5)], [(3,8), (3,9), (4,8)],
    [(4,4), (4,5)], [(4,6), (5,5), (5,6)], [(4,7), (5,7), (5,8)],
    [(4,9), (5,9)], [(5,3), (6,3)], [(5,4), (6,4), (6,5)],
    [(6,2), (7,2)], [(6,6), (6,7)], [(6,8), (7,7), (7,8)],
    [(6,9), (7,9), (8,9)], [(7,1), (8,1), (8,2)],
    [(7,3), (8,3), (8,4), (9,4)], [(7,4), (7,5), (7,6)],
    [(8,5), (9,5)], [(8,6), (9,6)],
    [(8,7), (8,8), (9,7), (9,8), (9,9)],
    [(9,1), (9,2)], [(9,3)]]



"""
cage_sums: list of cage totals, must match cages order.
cage_sums = [<Int>, ... , <Integer>].

Replace example values with custom values for personal killer sudoku solution.
"""
cage_sums = [9, 14, 11, 14, 18, 2, 12, 11, 6, 10, 17, 12, 13, 20, 9,
    18, 19, 4, 9, 14, 10, 10, 17, 15, 19, 17, 13, 17, 5, 24, 10, 6]


# pyomo model
model = pyo.ConcreteModel()

# sudoku grid
N = pyo.RangeSet(1,9)
# 3by3 block ind  
B = pyo.RangeSet(1,3)

# x[i,j,k]= 1 if i,j == k
model.x = pyo.Var(N,N,N, within= pyo.Binary)
# y[i,j] = digit in cell i,j
model.y = pyo.Var(N, N, within= pyo.Integers, bounds= (1,9))


# no optimizing goal just finding solution
model.obj = pyo.Objective(expr= 0)


# one digit per cell
model.cell_unique = pyo.ConstraintList()
for i in N:
    for j in N:
        model.cell_unique.add(sum(model.x[i,j,k] for k in N)==1)

# one digit occurance in row
model.row_unique = pyo.ConstraintList()
for i in N:
    for k in N:
        model.row_unique.add(sum(model.x[i,j,k] for j in N)==1)

# one dig occurance in col
model.col_unique = pyo.ConstraintList()
for j in N:
    for k in N:
        model.col_unique.add(sum(model.x[i,j,k] for i in N)==1)

# one dig occurance in 3 by 3
model.block_unique = pyo.ConstraintList()
for block_row in range(0,9,3):
    for block_col in range(0,9,3):
        for k in N:
            model.block_unique.add(
                sum(model.x[i+1, j+1, k]
                    for i in range(block_row, block_row + 3)
                    for j in range(block_col, block_col + 3)
                ) == 1)
            
            
# y[i,j]=k only if x[i,j,k]==1
model.link = pyo.ConstraintList()
for i in N:
    for j in N:
        model.link.add(model.y[i,j] == sum(k * model.x[i,j,k] for k in N))


model.known = pyo.ConstraintList()
for i, j, k in known:
    model.known.add(model.x[i,j,k] == 1)


# sum of num in each cage == upper left corner of cage
model.this_cage_sum = pyo.ConstraintList()
for ind, cage in enumerate(cages):
    model.this_cage_sum.add(sum(model.y[i,j] for i,j in cage) == cage_sums[ind])

# cant repeat within cages
model.cage_unique = pyo.ConstraintList()
for cage in cages:
    for k in N:
        model.cage_unique.add(sum(model.x[i,j,k] for i,j in cage) <= 1)
        

# solving with glpk
solver = SolverFactory('glpk')
result = solver.solve(model, tee=True)

# pretty display of solution
sol = np.zeros((9,9), dtype= int)
for i in N:
    for j in N:
        sol[i-1, j-1]= int(pyo.value(model.y[i,j]))

print("Solved Killer Sudoku")
print("=====================")
print(sol)

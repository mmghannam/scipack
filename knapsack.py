from typing import List
from pyscipopt import Model, quicksum

def pricing_solver(sizes: List[int], capacity: int, dual_solution: dict[float], together: set[tuple[int]], apart: set[tuple[int]]):
    # objective function: 1 - sum(dual_value of a constraint * coeff)
    # min 1 - sum(dual_value of a constraint * coeff)
    # 1 + min - sum(dual_value of a constraint * coeff)
    # 1 - max (sum(dual per item))    
    
    model = Model("Pricing Problem")
    model.hideOutput()
    
    x = {}
    for i in range(len(sizes)):
        x[i] = model.addVar(vtype="B", obj=dual_solution[i])
    
    model.addCons(quicksum(sizes[i] * x[i] for i in range(len(sizes))) <= capacity)
    
    for (i, j) in together:
        model.addCons(x[i] == x[j])
    
    for pair in apart:
        model.addCons(x[pair[0]] + x[pair[1]] <= 1)
    
    model.setMaximize()
    
    model.optimize()
    
    min_red_cost = 1 - model.getObjVal()
    pattern = [i for i in range(len(sizes)) if model.getVal(x[i]) > 0.1]
    
    return min_red_cost, pattern


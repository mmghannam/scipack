from typing import Dict, List
from pyscipopt import Model, quicksum, SCIP_PARAMSETTING

from compact import binpacking_compact
from generator import random_bin_packing_instance
from pricer import KnapsackPricer

def extended_binpacking(sizes: List[int], capacity: int):
    model = Model("Extended Binpacking")
    
    model.setPresolve(SCIP_PARAMSETTING.OFF)
    model.setSeparating(SCIP_PARAMSETTING.OFF)
    model.setHeuristics(SCIP_PARAMSETTING.OFF)
    
    x = {}
    # create one item per bin variables
    for i in range(len(sizes)):
        x[i] = model.addVar(vtype="B", name=f"{i}", obj=1)
    
    # add constraints that ensure that each item is packed into exactly one bin
    constraints = {}
    for i in range(len(sizes)):
        constraints[i] = model.addCons(x[i] == 1, modifiable=True)
    
    return model, x, constraints



def pricing_solver(sizes: List[int], capacity: int, dual_solution: dict[float]):
    
    # objective function: 1 - sum(dual_value of a constraint * coeff)
    # min 1 - sum(dual_value of a constraint * coeff)
    # 1 + min - sum(dual_value of a constraint * coeff)
    # 1 - max (sum(dual per item))    
    
    model = Model("Pricing Problem")
    model.hideOutput()
    
    x = {}
    for i in range(len(sizes)):
        x[i] = model.addVar(vtype="B", name=f"X", obj=dual_solution[i])
    
    model.addCons(quicksum(sizes[i] * x[i] for i in range(len(sizes))) <= capacity)
    
    model.setMaximize()
    
    model.optimize()
    
    min_red_cost = 1 - model.getObjVal()
    pattern = [i for i in range(len(sizes)) if model.getVal(x[i]) > 0.1]
    
    return min_red_cost, pattern



if __name__ == "__main__":
    sizes = [1, 2, 3, 4, 5]
    capacity = 10
    
    capacity = 100
    sizes = random_bin_packing_instance(35, capacity)
    
    model, vars, constraints = extended_binpacking(sizes, capacity)
    model.relax()
    
    # generate more variables if needed and resolve 
    # stop when reduced cost is non-negative
    while True:
        model.optimize()
        
        # dual_sol = {cons_id: model.getDualsolLinear(cons) for (cons_id, cons) in constraints.items()}
        dual_sol = {}
        for (cons_id, cons) in constraints.items():
            cons = model.getTransformedCons(cons)
            dual_sol[cons_id] = model.getDualsolLinear(cons)
            
            
        # is_done = any(model.isInfinity(val) for val in dual_sol.values())
        # if is_done: break
        
        print("dual solution", dual_sol)
        min_red_cost, pattern = pricing_solver(sizes, capacity, dual_sol)
        
        print("min_red_cost", min_red_cost)
        print("pattern", pattern)
        
        if min_red_cost >= 0:
            break
        else:
            # add a variable
            model.freeTransform()
            model.setPresolve(SCIP_PARAMSETTING.OFF)
            model.setSeparating(SCIP_PARAMSETTING.OFF)
            model.setHeuristics(SCIP_PARAMSETTING.OFF)
    
            new_var = model.addVar(vtype="C", name=f"{pattern}", obj=1)
            for item in pattern:
                item_constraint = constraints[item]
                model.addConsCoeff(item_constraint, new_var, 1)
                
    
    print("done")
    print("objective value", model.getObjVal())
    for var in model.getVars():
        print(var, model.getVal(var))
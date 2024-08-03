from typing import List
from pyscipopt import Model, quicksum

def binpacking_compact(sizes: List[int], capacity: int) -> Model:
    model = Model("Binpacking")
    n = len(sizes)
    x = {}
    for i in range(n):
        for j in range(n):
            x[i, j] = model.addVar(vtype="B", name=f"x{i}_{j}")
    y = [model.addVar(vtype="B", name=f"y{i}") for i in range(n)]
    
    for i in range(n):
        model.addCons(
            quicksum(x[i, j] for j in range(n)) == 1
        )
        
    for j in range(n):
        model.addCons(
            quicksum(sizes[i] * x[i, j] for i in range(n)) <= capacity * y[j]
        )
        
    model.setObjective(
        quicksum(y[j] for j in range(n)), "minimize"
    )
               
    return model

def test_compact(): 
    sizes = [4, 3, 5, 4, 1, 2, 4]
    capacity = 8
    
    model = binpacking_compact(sizes, capacity)
    model.optimize()
    assert model.getObjVal() == 3    
    
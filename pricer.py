import math
from pyscipopt import Pricer, SCIP_RESULT
from knapsack import pricing_solver

class KnapsackPricer(Pricer):
    def __init__(self, sizes, capacity, constraints, branching_decisions):
        self.sizes = sizes
        self.capacity = capacity
        self.constraints = constraints
        self.branching_decisions = branching_decisions
        self.i = 0
        
    def pricerredcost(self):
        self.i += 1
        
        branching_decisions = self.branching_decisions[self.model.getCurrentNode().getNumber()]
        
        if self.i % 10 == 0:
            print("--lp obj:", self.model.getLPObjVal())
        
        dual_sol = {}
        for (cons_id, cons) in self.constraints.items():
            cons = self.model.getTransformedCons(cons)
            dual_sol[cons_id] = self.model.getDualsolLinear(cons)   
        
        # sum_duals = 0
        # for cons in self.model.getConss():
        #     cons = self.model.getTransformedCons(cons)
        #     print(cons, self.model.getDualsolLinear(cons))
        #     sum_duals += self.model.getDualsolLinear(cons)
        
        
        # offset_from_branching_cons = sum_duals - sum(dual_sol.values())
        # assert(offset_from_branching_cons < 1e-6)            
        
        # print("dual solution", dual_sol)
        min_red_cost, pattern = pricing_solver(self.sizes, self.capacity, dual_sol, branching_decisions["together"], branching_decisions["apart"])
        # print("min_red_cost", min_red_cost)
        # print("pattern", pattern)            
        
        
        bound = - self.model.infinity()                    
        if min_red_cost < 0:
            # add a variable
            new_var = self.model.addVar(vtype="B", name=f"{pattern}", obj=1, pricedVar=True)
            for item in pattern:
                item_constraint = self.constraints[item]
                item_constraint = self.model.getTransformedCons(item_constraint)
                self.model.addConsCoeff(item_constraint, new_var, 1)
        else:
            bound = math.ceil(self.model.getLPObjVal())
        
        
        return {
            'result': SCIP_RESULT.SUCCESS,
            'lowerbound': bound
            }

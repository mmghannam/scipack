from pyscipopt import Branchrule, SCIP_RESULT

class RyanFoster(Branchrule):
    def __init__(self):
        self.branching_decisions = {
            1: {
                "together": set(),
                "apart": set(),
            }
        }
    
    def branchexeclp(self, allowaddcons):
        lpcands, lpcandssol, *_ = self.model.getLPBranchCands()
        
        # find a pair of items to branch on
        pair_var_values = {}
        for (var, val) in zip(lpcands, lpcandssol):
            pattern = eval(var.name.replace("t_", ""))
            for i in pattern:
                for j in pattern:
                    if i != j:
                        if (i, j) not in pair_var_values:
                            pair_var_values[i, j] = val
                        else:
                            pair_var_values[i, j] += val
        
        
        
        fractional_pairs = {pair: val for pair, val in pair_var_values.items() if val > 1e-6 and val < 1.0 - 1e-6}
        
        if len(fractional_pairs) == 0:
            raise Exception("No fractional pairs found")
        

        chosen_pair = max(fractional_pairs, key= lambda x: fractional_pairs[x])
        
                        
        
        
        parent_together = set()
        parent_apart = set()
        
        
        parent = self.model.getCurrentNode().getParent()
        if parent:
            parent_together = set(self.branching_decisions[parent.getNumber()]["together"])
            parent_apart = set(self.branching_decisions[parent.getNumber()]["apart"])
        
                                
        # left subproblem
        # enforce that pair is in the same bin
        left_node = self.model.createChild(0, 0)
        #  - add constraints to the pricing problem
        self.branching_decisions[left_node.getNumber()] = {
            "together": parent_together.union({chosen_pair}),
            "apart": parent_apart
        }
        #  - fix any variable in the current master problem to zero if it visits one item of the pair and not the other.
        # done in the event handler
        
        # right subproblem
        # enforce that pair is in different bins
        #  - add constraints to the pricing problem
        right_node = self.model.createChild(0, 0)
        self.branching_decisions[right_node.getNumber()] = {
            "together": parent_together,
            "apart": parent_apart.union({chosen_pair})
        }
        #  - fix any variable in the current master problem to zero if it visits both items of the pair.
        # done in the event handler
        
        return {"result": SCIP_RESULT.BRANCHED}

from pymoo.core.termination import Termination

class OneSolutionHeuristicTermination(Termination):

    def __init__(self, heu_vals) -> None:
        super().__init__()

        self.heu_vals = heu_vals

    def _do_continue(self, algorithm):
        F = algorithm.opt.get("F")

        valid_sols = []
        i = 0
        for sol in F:
            # for each fitness result collection
            # print(f'{i} = {tuple(sol)}')
            i+=1
            sol_is_valid = True
            for heu_i in range(len(sol)):
                heu_v = sol[heu_i]
                heu_max = self.heu_vals[heu_i]
                if heu_v > heu_max:
                    sol_is_valid = False
                    break
            if sol_is_valid:
                valid_sols.append(sol)
        
        # # PRINT BEST HEURISTIC VAL
        # mostZeros = -1
        # bestSol = None
        # for sol in F:
        #     # for each fitness result collection
        #     # print(f'{i} = {tuple(sol)}')
        #     i+=1
        #     numZeros = 0
        #     for heu_i in range(len(sol)):
        #         heu_v = sol[heu_i]
        #         if heu_v == 0:
        #             numZeros += 1
        #     if numZeros > mostZeros:
        #         bestSol = sol
        #         mostZeros = numZeros
                
        #     if numZeros == mostZeros:
        #         bestSum = sum(bestSol)
        #         curSum = sum(sol)
        #         if curSum < bestSum:
        #             bestSol = sol

        # print(bestSol)

        # print(valid_sols)
        return len(valid_sols) == 0
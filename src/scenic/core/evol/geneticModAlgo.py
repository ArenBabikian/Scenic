
import copy
import time
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.callback import Callback
from pymoo.algorithms.base.genetic import GeneticAlgorithm



def get_genetic_mod_algo(base):

    if isinstance(base, GeneticAlgorithm):
        raise Exception(f'Must be subtype of genetic Algo')

    class GeneticMod(base):
        
        def __init__(self,
                    pop_size=100,
                    n_offsprings=None,
                    restart_time=-1.0,
                    **kwargs):
            """

            Parameters
            ----------
            pop_size : {pop_size}
            sampling : {sampling}
            selection : {selection}
            crossover : {crossover}
            mutation : {mutation}
            eliminate_duplicates : {eliminate_duplicates}
            n_offsprings : {n_offsprings}

            """

            super().__init__(pop_size=pop_size,
                            n_offsprings=n_offsprings,
                            **kwargs)
            self.end_time = None
            self.exec_time = None
            self.restart_time = restart_time
            self.last_restart_time = time.time()
            self.to_restart = False
            self.all_restarts = []


        def _post_advance(self):
            # FROM pymoo.core.algorithm.Algorithm
            # update the current optimum of the algorithm
            self._set_optimum()

            # display the output if defined by the algorithm
            if self.verbose and self.display is not None:
                self.display.do(self.problem, self.evaluator, self, pf=self.pf)

            # if a callback function is provided it is called after each iteration
            if self.callback is not None:
                if isinstance(self.callback, Callback):
                    self.callback.notify(self)
                else:
                    self.callback(self)

            # ADJUSTMENTS
            # TEMP
            # if self.save_history == 'shallow':
            #     raise Exception(f'Shallow history not yet implemented')
            # elif self.save_history == 'deep' or self.save_history == 'shallow':
            if self.save_history == 'deep' or self.save_history == 'shallow':
                _hist, _callback = self.history, self.callback

                self.history, self.callback = None, None
                obj = copy.deepcopy(self)

                self.history, self.callback = _hist, _callback
                self.history.append(obj)

                # ADDED BELOW
                self.end_time = time.time()
                self.exec_time = self.end_time-self.start_time


        def _infill(self):
            # FROM pymoo.core.algorithms.base.genetic.GeneticAlgorithm
            cur_t = time.time()
            t_since_last_restart = cur_t-self.last_restart_time
            self.to_restart = t_since_last_restart > self.restart_time
            if self.restart_time != -1 and self.to_restart:
                self.last_restart_time = time.time()
                t = cur_t - self.start_time
                self.all_restarts.append(t)
                return None
            else:
                return super()._infill()


        def _advance(self, infills=None, **kwargs):
            # FROM pymoo.core.algorithms.base.genetic.GeneticAlgorithm
            if self.restart_time != -1 and self.to_restart:
                self.to_restart = False
                print("RESTARTED")
                infills = self.initialization.do(self.problem, self.pop_size, algorithm=self)
                self.evaluator.eval(self.problem, infills, algorithm=self)
                self.pop = infills
                self._initialize_advance(infills=infills, **kwargs)
            else:
                super()._advance(infills, **kwargs)
    
    return GeneticMod

##################
# MODIFIED CLASSES
##################
NSGA2MOD = get_genetic_mod_algo(NSGA2)
NSGA3MOD = get_genetic_mod_algo(NSGA3)
GAMOD = get_genetic_mod_algo(GA)


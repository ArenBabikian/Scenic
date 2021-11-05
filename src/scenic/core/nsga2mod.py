
import copy
import time
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.callback import Callback


class NSGA2M(NSGA2):
    
    def __init__(self,
                 pop_size=100,
                 n_offsprings=None,
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


    def _post_advance(self):
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

        if self.save_history:
            _hist, _callback = self.history, self.callback

            self.history, self.callback = None, None
            obj = copy.deepcopy(self)

            self.history, self.callback = _hist, _callback
            self.history.append(obj)
            self.end_time = time.time()
            self.exec_time = self.end_time-self.start_time
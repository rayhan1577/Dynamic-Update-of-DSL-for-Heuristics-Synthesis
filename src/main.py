from bus import BottomUpSearch
import os
from dsl import Abs, Max, Min, Minus, Plus, Times

def main():    
    ncpus = int(os.environ.get('SLURM_CPUS_PER_TASK', default = 1))
    
    synthesizer = BottomUpSearch(ncpus)
    
    p, num = synthesizer.synthesize(600,
                                    [Abs, Times, Plus, Minus, Min, Max], 
                                    [0.5, 2], 
                                    ['x', 'y', 'x_goal', 'y_goal'], 
                                    "dao-map/brc000d.map",
                                    50,
                                    50)
     
    if p is not None:
        print(p.toString(), num)
    
if __name__ == "__main__":
    main()    

from algorithms import AStarSketch, AStar, State
from map import Map

class Evaluation():
    def eval_program(self):
        raise Exception('Unimplemented method: toString')
    
    def run_search(self, start, goal, cost_program):
        astar = AStarSketch(self.gridded_map)
        
        cost, expanded_astar = astar.search(start, goal, cost_program)
        
        return cost, expanded_astar

class EvalExpansions(Evaluation):
    def __init__(self, map_name, number_problems):
        self.map_name = map_name
        
        self.gridded_map = Map("brc000d.map")
        
        self.start_states = []
        self.goal_states = []
        
        for _ in range(0, number_problems):
            self.start_states.append(self.gridded_map.random_state())
            self.goal_states.append(self.gridded_map.random_state())
        
    def eval_program(self, program):                
        total_cost = 0
        total_expanded = 0 
        for i in range(len(self.start_states)):
            
            try:
                cost, expanded = self.run_search(self.start_states[i], self.goal_states[i], program)
            except Exception as e:
                print(e)
                return None, None, None, True
            
            total_cost += cost
            total_expanded += expanded
        
        return total_cost/len(self.start_states), total_expanded/len(self.start_states), program, False
        
        

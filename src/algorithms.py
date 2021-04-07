import heapq

class State:
    map_width = 0
    map_height = 0
    
    def __init__(self, x, y, parent=None):
        self._x = x
        self._y = y
        self._g = 0
        self._h = 0
        self._cost = 0
        
        self._parent = parent
        
    def __repr__(self):
        state_str = "[" + str(self._x) + ", " + str(self._y) + "]"
        return state_str
    
    def __lt__(self, other):
        return self._cost < other._cost
    
    def state_hash(self):
        return self._y * State.map_width + self._x
    
    def __eq__(self, other):
        return self._x == other._x and self._y == other._y

    def get_x(self):
        return self._x
    
    def get_y(self):
        return self._y
    
    def get_g(self):
        return self._g
        
    def get_h(self):
        return self._h
    
    def get_cost(self):
        return self._cost
    
    def set_g(self, cost):
        self._g = cost
    
    def set_h(self, h):
        self._h = h
    
    def set_cost(self, cost):
        self._cost = cost

class Search:
    def __init__(self, gridded_map):
        self.map = gridded_map
        self.OPEN = []
        self.CLOSED = {}
    
    def search(self, start, goal):
        raise NotImplementedError()
    
class AStarSketch(Search):
    
    def h_value(self, state):
        dist_x = abs(state.get_x() - self.goal.get_x())
        dist_y = abs(state.get_y() - self.goal.get_y())
        return max(dist_x, dist_y) + 0.5 * min(dist_x, dist_y)
    
    def cost_function(self, state, program):
        env = {}
        env['x'] = state.get_x()
        env['y'] = state.get_y()
        env['x_goal'] = self.goal.get_x()
        env['y_goal'] = self.goal.get_y()
        env['g'] = state.get_g()
        
        return program.interpret(env)

            
    def search(self, start, goal, program):
        self.start = start
        self.goal = goal
        
        self.OPEN.clear()
        self.CLOSED.clear()
        nodes_expanded = 0
        
        start.set_cost(self.cost_function(start, program))
        
        heapq.heappush(self.OPEN, start)
        self.CLOSED[start.state_hash()] = start
        while len(self.OPEN) > 0:
            node = heapq.heappop(self.OPEN)
            nodes_expanded += 1
            if node == goal:
                return node.get_g(), nodes_expanded
            children = self.map.successors(node)
            for child in children:
                hash_value = child.state_hash()
                child.set_cost(child.get_g() + self.cost_function(child, program))
                
                if hash_value in self.CLOSED and self.CLOSED[hash_value].get_cost() > child.get_cost():
                    self.CLOSED[hash_value].set_cost(child.get_cost())
                    self.CLOSED[hash_value].set_g(child.get_g())
                    self.CLOSED[hash_value].set_h(child.get_h())
                    heapq.heapify(self.OPEN)
                
                if hash_value not in self.CLOSED:
                    heapq.heappush(self.OPEN, child)
                    self.CLOSED[hash_value] = child
        return -1, nodes_expanded
    
class AStar(Search):
    
    def h_value(self, state):
        dist_x = abs(state.get_x() - self.goal.get_x())
        dist_y = abs(state.get_y() - self.goal.get_y())
        return max(dist_x, dist_y) + 0.5 * min(dist_x, dist_y)
            
    def search(self, start, goal):
        self.start = start
        self.goal = goal
        
        self.OPEN.clear()
        self.CLOSED.clear()
        nodes_expanded = 0
        
        start.set_h(self.h_value(start))
        start.set_cost(self.h_value(start))
        
        heapq.heappush(self.OPEN, start)
        self.CLOSED[start.state_hash()] = start
        while len(self.OPEN) > 0:
            node = heapq.heappop(self.OPEN)
            nodes_expanded += 1
            if node == goal:
                return node.get_g(), nodes_expanded, node
            children = self.map.successors(node)
            for child in children:
                hash_value = child.state_hash()
                child.set_h(self.h_value(child))
                child.set_cost(child.get_g() + child.get_h())
                
                if hash_value in self.CLOSED and self.CLOSED[hash_value].get_cost() > child.get_cost():
                    self.CLOSED[hash_value].set_cost(child.get_cost())
                    self.CLOSED[hash_value].set_g(child.get_g())
                    self.CLOSED[hash_value].set_h(child.get_h())
                    heapq.heapify(self.OPEN)
                
                if hash_value not in self.CLOSED:
                    heapq.heappush(self.OPEN, child)
                    self.CLOSED[hash_value] = child
        return -1, nodes_expanded, None
    
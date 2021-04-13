import numpy as np
import itertools

class Node:
    def __init__(self):
        self.size = 0
        self.cost = 1
    
    def getSize(self):
        return self.size

    def getCost(self):
        return self.cost
    
    def setCost(self, cost):
        self.cost = cost
    
    def toString(self):
        raise Exception('Unimplemented method: toString')
    
    def interpret(self):
        raise Exception('Unimplemented method: interpret')
            
    @classmethod
    def grow(plist, new_plist):
        pass
    
    @classmethod
    def className(cls):
        return cls.__name__

class VarScalar(Node):
    def __init__(self, name):
        super(VarScalar, self).__init__()
        self.name = name
        self.size = 1
        
    def toString(self):
        return self.name
    
    def interpret(self, env):
        return env[self.name]

class Constant(Node):
    def __init__(self, value):
        super(Constant, self).__init__()
        self.value = value
        self.size = 1
        
    def toString(self):
        return str(self.value)
    
    def interpret(self, env):
        return self.value
    
class Abs(Node):
    def __init__(self, value):
        super(Abs, self).__init__()
        self.value = value
        self.size = self.value.size + 1
        
    def toString(self):
        return "abs(" + self.value.toString() + ")"
    
    def interpret(self, env):
        return abs(self.value.interpret(env))
    
    def grow(plist, size):       
        new_programs = []
        # defines which nodes are accepted in the AST
        accepted_nodes = set([Plus.className(),
                              Times.className(),
                              Minus.className(), 
                              Min.className(),
                              Max.className()])
        
        program_set = plist.get_programs(size - 1)
            
        for t, programs in program_set.items():                
            if t not in accepted_nodes:
                continue
            
            for p in programs:
                abs_p = Abs(p)
                #print(size)
                #print(abs_p.toString())
                new_programs.append(abs_p)

                yield abs_p
                
        return new_programs

class Min(Node):
    def __init__(self, left, right):
        super(Min, self).__init__()
        self.left = left
        self.right = right
        self.size = self.left.size + self.right.size + 1
        
    def toString(self):
        return "min(" + self.left.toString() + ", " + self.right.toString() + ")"
    
    def interpret(self, env):
        v1 = self.left.interpret(env)
        v2 = self.right.interpret(env)
        if v1 > v2:
            return v2
        else:
            return v1
    
    def grow(plist, size):       
        new_programs = []
        # defines which nodes are accepted in the AST
        accepted_nodes = set([Abs.className(),
                              VarScalar.className(),
                              Plus.className(),
                              Times.className(),
                              Minus.className(),
                              Constant.className(),
                              Max.className(),
                              Min.className()])
        
        # generates all combinations of cost of size 2 varying from 1 to size - 1
        combinations = list(itertools.combinations_with_replacement(range(1, size - 1), 2))
        
        for c in combinations:           
            # skip if the cost combination exceeds the limit
            #if c[0] + c[1] + 1 > size:
            #    continue
                    
            # retrive bank of programs with costs c[0], c[1], and c[2]
            program_set1 = plist.get_programs(c[0])
            program_set2 = plist.get_programs(c[1])
                
            for t1, programs1 in program_set1.items():                
                # skip if t1 isn't a node accepted by Lt
                if t1 not in accepted_nodes:
                    continue
                
                for p1 in programs1:                       

                    for t2, programs2 in program_set2.items():                
                        # skip if t1 isn't a node accepted by Lt
                        if t2 not in accepted_nodes:
                            continue
                        
                        for p2 in programs2:
    
                            min_p = Min(p1, p2)
                            new_programs.append(min_p)
            
                            yield min_p
        return new_programs

class Max(Node):
    def __init__(self, left, right):
        super(Max, self).__init__()
        self.left = left
        self.right = right
        self.size = self.left.size + self.right.size + 1
        
    def toString(self):
        return "max(" + self.left.toString() + ", " + self.right.toString() + ")"
    
    def interpret(self, env):
        v1 = self.left.interpret(env)
        v2 = self.right.interpret(env)
        if v1 > v2:
            return v1
        else:
            return v2
    
    def grow(plist, size):       
        new_programs = []
        # defines which nodes are accepted in the AST
        accepted_nodes = set([Abs.className(),
                              VarScalar.className(),
                              Plus.className(),
                              Times.className(),
                              Minus.className(), 
                              Constant.className(),
                              Max.className(),
                              Min.className()])

        # generates all combinations of cost of size 2 varying from 1 to size - 1
        combinations = list(itertools.combinations_with_replacement(range(1, size - 1), 2))

        for c in combinations:           
            # skip if the cost combination exceeds the limit
            #if c[0] + c[1] + 1> size:
            #    continue
                    
            # retrive bank of programs with costs c[0], c[1], and c[2]
            program_set1 = plist.get_programs(c[0])
            program_set2 = plist.get_programs(c[1])
                
            for t1, programs1 in program_set1.items():                
                # skip if t1 isn't a node accepted by Lt
                if t1 not in accepted_nodes:
                    continue
                
                for p1 in programs1:                       

                    for t2, programs2 in program_set2.items():                
                        # skip if t1 isn't a node accepted by Lt
                        if t2 not in accepted_nodes:
                            continue
                        
                        for p2 in programs2:
    
                            max_p = Max(p1, p2)
                            new_programs.append(max_p)
            
                            yield max_p
        return new_programs
    
class Times(Node):
    def __init__(self, left, right):
        super(Times, self).__init__()
        self.left = left
        self.right = right
        self.size = self.left.size + self.right.size + 1
        
    def toString(self):
        return "(" + self.left.toString() + " * " + self.right.toString() + ")"
    
    def interpret(self, env):
        return self.left.interpret(env) * self.right.interpret(env)
    
    def grow(plist, size):       
        new_programs = []
        # defines which nodes are accepted in the AST
        accepted_nodes = set([VarScalar.className(),
                              Plus.className(),
                              Times.className(),
                              Minus.className(), 
                              Constant.className(),
                              Max.className(),
                              Min.className(),
                              Abs.className()])
        
        # generates all combinations of cost of size 2 varying from 1 to size - 1
        combinations = list(itertools.combinations_with_replacement(range(1, size - 1), 2))

        for c in combinations:           
            # skip if the cost combination exceeds the limit
            #if c[0] + c[1] + 1 > size:
            #    continue
                    
            # retrive bank of programs with costs c[0], c[1], and c[2]
            program_set1 = plist.get_programs(c[0])
            program_set2 = plist.get_programs(c[1])
                
            for t1, programs1 in program_set1.items():                
                # skip if t1 isn't a node accepted by Lt
                if t1 not in accepted_nodes:
                    continue
                
                for p1 in programs1:                       

                    for t2, programs2 in program_set2.items():                
                        # skip if t1 isn't a node accepted by Lt
                        if t2 not in accepted_nodes:
                            continue
                        
                        for p2 in programs2:
    
                            times = Times(p1, p2)
                            new_programs.append(times)
            
                            yield times
        return new_programs
    
class Minus(Node):
    def __init__(self, left, right):
        super(Minus, self).__init__()
        self.left = left
        self.right = right
        self.size = self.left.size + self.right.size + 1
        
    def toString(self):
        return "(" + self.left.toString() + " - " + self.right.toString() + ")"
    
    def interpret(self, env):
        return self.left.interpret(env) - self.right.interpret(env)
    
    def grow(plist, size):               
        new_programs = []
        # defines which nodes are accepted in the AST
        accepted_nodes = set([VarScalar.className(), 
                              Constant.className(),
                              Plus.className(),
                              Times.className(),
                              Minus.className(),
                              Max.className(),
                              Min.className(),
                              Abs.className()])
        
        # generates all combinations of cost of size 2 varying from 1 to size - 1
        combinations = list(itertools.combinations_with_replacement(range(1, size - 1), 2))

        for c in combinations:                       
            # skip if the cost combination exceeds the limit
            #if c[0] + c[1] + 1 > size:
            #    continue
                
            # retrive bank of programs with costs c[0], c[1], and c[2]
            program_set1 = plist.get_programs(c[0])
            program_set2 = plist.get_programs(c[1])
                
            for t1, programs1 in program_set1.items():                
                # skip if t1 isn't a node accepted by Lt
                if t1 not in accepted_nodes:
                    continue
                
                for p1 in programs1:                       

                    for t2, programs2 in program_set2.items():                
                        # skip if t1 isn't a node accepted by Lt
                        if t2 not in accepted_nodes:
                            continue
                        
                        for p2 in programs2:
    
                            minus = Minus(p1, p2)
                            new_programs.append(minus)
            
                            yield minus
        return new_programs  

class Plus(Node):
    def __init__(self, left, right):
        super(Plus, self).__init__()
        self.left = left
        self.right = right
        self.size = self.left.size + self.right.size + 1
        
    def toString(self):
        return "(" + self.left.toString() + " + " + self.right.toString() + ")"
    
    def interpret(self, env):
        return self.left.interpret(env) + self.right.interpret(env)
    
    def grow(plist, size):               
        new_programs = []
        # defines which nodes are accepted in the AST
        accepted_nodes = set([VarScalar.className(), 
                              Constant.className(),
                              Plus.className(),
                              Times.className(),
                              Minus.className(),
                              Max.className(),
                              Min.className(),
                              Abs.className()])
        
        # generates all combinations of cost of size 2 varying from 1 to size - 1
        combinations = list(itertools.combinations_with_replacement(range(1, size - 1), 2))

        for c in combinations:                       
            # skip if the cost combination exceeds the limit
            #if c[0] + c[1] + 1 > size:
            #    continue
                
            # retrive bank of programs with costs c[0], c[1], and c[2]
            program_set1 = plist.get_programs(c[0])
            program_set2 = plist.get_programs(c[1])
                
            for t1, programs1 in program_set1.items():                
                # skip if t1 isn't a node accepted by Lt
                if t1 not in accepted_nodes:
                    continue
                
                for p1 in programs1:                       

                    for t2, programs2 in program_set2.items():                
                        # skip if t1 isn't a node accepted by Lt
                        if t2 not in accepted_nodes:
                            continue
                        
                        for p2 in programs2:
    
                            plus = Plus(p1, p2)
                            new_programs.append(plus)
            
                            yield plus
        return new_programs  
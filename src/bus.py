from dsl import *
from evaluation import EvalExpansions
from algorithms import State, AStarSketch, AStar

from concurrent.futures import ProcessPoolExecutor

import os
import math
from map import Map
import time
import random
import numpy as np


class ProgramList():

    def __init__(self):
        self.plist = {}
        self.number_programs = 0

    def insert(self, program):
        if program.size not in self.plist:
            self.plist[program.size] = {}

        if program.className() not in self.plist[program.size]:
            self.plist[program.size][program.className()] = []

        self.plist[program.size][program.className()].append(program)
        self.number_programs += 1

    def init_plist(self, constant_values, variables_list):

        for i in variables_list:
            p = VarScalar(i)
            self.insert(p)

        for i in constant_values:
            constant = Constant(i)
            self.insert(constant)

    def get_programs(self, size):

        if size in self.plist:
            return self.plist[size]
        return {}

    def get_number_programs(self):
        return self.number_programs


def eval_program(n):
    program = n[0]
    pairs_start_goal = n[1]
    #     start_states = n[1]
    #     goal_states = n[2]
    map_name = n[2]

    gridded_map = Map(map_name)

    total_cost = 0
    total_expanded = 0

    for i in range(len(pairs_start_goal)):
        astar = AStarSketch(gridded_map)

        try:
            cost, expanded = astar.search(pairs_start_goal[i][0], pairs_start_goal[i][1], program)
        except Exception as e:
            print('Exception: ', e)
            return None, None, None, True

        total_cost += cost
        total_expanded += expanded

    #     print(program.toString(), total_cost, total_expanded)
    return total_cost, total_expanded, program, False


def eval_program_paths(n):
    program = n[0]
    solution_paths = n[1]
    number_improvs = 0

    total_steps = 0

    for path in solution_paths:
        goal = path[0]
        cost_values = []
        g_costs = []

        total_steps += len(path)

        prev_h = None

        for state in path:
            env = {}
            env['x'] = state.get_x()
            env['y'] = state.get_y()
            #             env['g'] = state.get_g()
            env['x_goal'] = goal.get_x()
            env['y_goal'] = goal.get_y()

            cost_value = program.interpret(env)
            cost_values.append(cost_value)

            if prev_h is None:
                prev_h = cost_value
            else:
                if cost_value > prev_h:
                    number_improvs += 1
                    prev_h = cost_value

            g_costs.append(state.get_g())

    if number_improvs == 0:
        #         cost_program = 1000
        reg_cost_program = 1000

    else:
        #         cost_program = math.ceil(-100 * math.log2(number_improvs/total_steps))

        reg_eval = (number_improvs - total_steps * 0.01 * program.getSize()) / total_steps

        reg_cost_program = 1000
        if reg_eval <= 0:
            reg_cost_program = 1000
        else:
            reg_cost_program = math.ceil(-100 * math.log2(reg_eval))

    #         print(program.toString(), cost_program, reg_cost_program, program.getSize())

    return reg_cost_program, number_improvs * -1, program, False


class BottomUpSearch():

    def __init__(self, ncpus):
        self.ncpus = ncpus
        self.file = open("a.txt", "w")
        self.augment = []
        self.best_expanded_value = math.inf
        self.incumbent_program = None
        self.iteration=0
        self.step=0

    def generate_training_data(self, map_name, number_paths):
        gridded_map = Map(map_name)

        training_data = []

        start_states = []
        goal_states = []
        costs = []
        expanded_values = []

        for _ in range(0, number_paths):

            start = gridded_map.random_state()
            goal = gridded_map.random_state()
            node = None
            cost = None
            expanded = None

            astar = AStar(gridded_map)
            cost, expanded, node = astar.search(start, goal)

            while node is None:
                start = gridded_map.random_state()
                goal = gridded_map.random_state()
                cost, expanded, node = astar.search(start, goal)

            start_states.append(start)
            goal_states.append(goal)
            costs.append(cost)
            expanded_values.append(expanded)

            solution_path = [node]

            while node._parent is not None:
                node = node._parent

                solution_path.append(node)

            training_data.append(solution_path)

        return training_data, tuple(zip(start_states, goal_states)), costs, expanded_values

    def grow(self, operations, size):
        new_programs = []
        for op in operations:
            # print(self.plist.get_number_programs(),size)
            for p in op.grow(self.plist, size):
                        new_programs.append(p)

        return new_programs

    def get_closed_list(self):
        return self.closed_list

    def compute_values_for_equivalence(self, p):
        env = {}
        values = []
        for i in range(len(self.start_states)):
            env['x'] = self.start_states[i].get_x()
            env['y'] = self.start_states[i].get_y()
            env['x_goal'] = self.goal_states[i].get_x()
            env['y_goal'] = self.goal_states[i].get_y()
            env['g'] = self.generated_g_values[i]

            value = p.interpret(env)
            values.append(value)
        return tuple(values)

    def search(self,
               bound,
               operations,
               constant_values,
               variables_list,
               map_name):
        self.closed_list = set()
        self.outputs = set()

        self.plist = ProgramList()
        self.plist.init_plist(constant_values, variables_list)

        #print('Number of programs: ', self.plist.get_number_programs())

        self._variables_list = variables_list



        number_evaluations = 0
        current_size = 0

        while current_size <= bound:

            number_evaluations_bound = 0
            # print("current Size", current_size)
            new_programs = self.grow(operations, current_size)

            if len(new_programs) == 0:
                current_size += 1
                continue

            print( 'Step:', self.step+1, 'Iteration', self.iteration+1 ,'Generated: ', len(new_programs), ' Size: ', current_size)
            self.iteration+=1
            number_evaluations += len(new_programs)
            number_evaluations_bound += len(new_programs)

            time_start = time.time()
            with ProcessPoolExecutor(max_workers=self.ncpus) as executor:
                #                 args = ((p, self.start_states, self.goal_states, map_name) for p in new_programs)
                #                 results = executor.map(eval_program, args)
                args = ((p, self.training_data) for p in new_programs if(p.toString() not in self.closed_list and self.compute_values_for_equivalence(p) not in self.outputs))
                results = executor.map(eval_program_paths, args)
            for result in results:
                cost = result[0]
                expanded = result[1]
                program = result[2]
                error = result[3]
                print(program.toString(),file=self.file)
                self.closed_list.add(program.toString())
                self.outputs.add(self.compute_values_for_equivalence(program))
                #                 print(program.toString(), cost)
                program.setCost(cost)
                self.plist.insert(program)

                if error:
                    print('Program ', program.toString(), ' raised an exception')

                if (expanded < self.best_expanded_value and (
                        isinstance(program, Max) or isinstance(program, Abs) or isinstance(program, Plus))):
                    total_cost, total_expanded, program, error_astar = eval_program_paths((program, self.pairs_start_goal, map_name))
                    self.best_expanded_value = expanded
                    self.incumbent_program = program
                    self.augment.append(program)
                    print("for path based eval")
                    print(self.incumbent_program.toString(), cost, expanded, current_size, total_cost, total_expanded,
                          error_astar)
                    total_cost, total_expanded, program, error_astar = eval_program((program, self.pairs_start_goal, map_name))

                    print('Statistics A* with MD on training data (SKETCH): ', total_cost, total_expanded)
                    #if (isinstance(self.incumbent_program, Max)):
                    #    self.augment.append(Min(incumbent_program.left, incumbent_program.right))
                    if(self.incumbent_program!= None):
                        print("Updating DSL")
                        print("Restarting search")
                        print("Updating DSL", file=self.file)
                        print("Restarting search", file=self.file)
                        self.step+=1
                        self.iteration=0
                        self.plist = ProgramList()
                        self.plist.init_plist(constant_values, variables_list)
                        for z in self.augment:
                            self.plist.insert(z)
                        #self.outputs.clear()
                        #self.closed_list.clear()

            time_end = time.time()
            print('Size: ', current_size,
                  ' Evaluations: ', number_evaluations_bound,
                  ' Total: ', number_evaluations,
                  ' Time: ', time_end - time_start)
            current_size += 1

        return self.incumbent_program, number_evaluations

    def synthesize(self,
                   bound,
                   operations,
                   constant_values,
                   variables_list,
                   map_name,
                   number_states,
                   number_training_paths):

        training_data, pairs_start_goal, costs, expanded = self.generate_training_data(map_name, number_training_paths)

        self.gridded_map = Map(map_name)
        self.training_data = training_data
        self.pairs_start_goal = pairs_start_goal
        self.start_states = []
        self.goal_states = []
        self.generated_g_values = []

        program = Plus(
            Max(
                Abs(Minus(VarScalar('x'), VarScalar('x_goal'))),
                Abs(Minus(VarScalar('y'), VarScalar('y_goal')))
            ),
            Times(
                Constant(0.5),
                Min(
                    Abs(Minus(VarScalar('x'), VarScalar('x_goal'))),
                    Abs(Minus(VarScalar('y'), VarScalar('y_goal'))))))
        #
        #         program_md4 = Plus(
        #                             Abs(Minus(VarScalar('x'), VarScalar('x_goal'))),
        #                             Abs(Minus(VarScalar('y'), VarScalar('y_goal')))
        #                           )

        total_cost, total_expanded, program, error_astar = eval_program((program, self.pairs_start_goal, map_name))

        print('Statistics A* with MD on training data (SKETCH): ', total_cost, total_expanded)
        print(program.toString())

        cost, expanded, program, error = eval_program_paths((program, self.training_data))
        print('Statistics for MD-8: ', cost, expanded, program.toString(), error)

        #         cost, expanded, program, error = eval_program_paths((program_md4, self.training_data))
        #         print('Statistics for MD-4: ', cost, expanded, program.toString(), error)
        # #         eval_program((program, self.start_states, self.goal_states, map_name))
        for _ in range(0, number_states):
            self.start_states.append(self.gridded_map.random_state())
            self.goal_states.append(self.gridded_map.random_state())
            self.generated_g_values.append(random.randint(50, 200))

        solution, evals = self.search(bound,
                                      operations,
                                      constant_values,
                                      variables_list,
                                      map_name)

        return solution, evals
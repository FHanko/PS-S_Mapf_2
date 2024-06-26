import json
import os
import sys
import time

from typing import List, Dict
from ortools.sat.python import cp_model
from state import State
from model import init_model

start_time = time.time()


def solve_initial(state: State):
    # Set infeasible shortest paths. No need for A* for simple cases.
    paths = {}
    for a in range(state.agents):
        current = state.start[a]
        paths[a] = [current]
        while current % state.width != state.end[a] % state.width:
            current += 1 if state.end[a] % state.width > current % state.width else -1
            paths[a].append(current)
        while current // state.height != state.end[a] // state.height:
            current += state.width if state.end[a] // state.height > current // state.height else -state.width
            paths[a].append(current)
    # Extend paths to later get correct obstacles.
    for p in paths:
        while len(paths[p]) < state.time:
            paths[p].append(paths[p][-1])
    # Start lns with infeasible initial state.
    state.paths = paths
    # print(json.dumps(state.paths, default=str))
    lns_step(state)


def lns_step(state: State, iteration: int = 0):
    # For infeasible states the neighbor will make it feasible after some iterations.
    # For feasible states the neighbor will try to improve the solution.
    neighbor = state.neighbor()
    print(f"{neighbor.active_agents} {iteration}")
    model = init_model(neighbor)
    status = model.solve()
    if status[0] == cp_model.OPTIMAL or status[0] == cp_model.FEASIBLE:
        neighbor.paths = model.get_paths()

        # Evaluate sum of cost of neighbor sub problem.
        old_sub_soc = state.get_soc(neighbor.active_agents)
        new_sub_soc = neighbor.get_soc(range(neighbor.agents))
        # If solution improved replace paths.
        if (not state.feasible) or (new_sub_soc < old_sub_soc):
            old_total_soc = state.get_soc(range(state.agents))
            state.merge_paths(neighbor)

            new_total_soc = state.get_soc(range(state.agents))
            if not state.feasible and neighbor.active_agents == set():
                state.feasible = True
                state.time = max([len(l) for i, l in state.paths.items()])
                print(f"Initial solution: \n{str(state.paths)}")
                print(f"Sum of costs: {new_total_soc} at time {time.time() - start_time}")
                if solution_callback(state):
                    return
            elif state.feasible:
                print(f"Sum of costs: {old_total_soc} -> {new_total_soc} at time {time.time() - start_time}")
                if solution_callback(state):
                    return
    else:
        pass
    if iteration_callback(iteration):
        lns_step(state, iteration + 1)


def iteration_callback(iteration: int):
    return True


def solution_callback(state: State):
    return False


if __name__ == "__main__":
    file_name = sys.argv[1]
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            input_data = json.load(f)
            input_state = State(**input_data)
            solve_initial(input_state)
    else:
        print(f"File {os.path.basename(file_name)} not found.")
        exit(1)

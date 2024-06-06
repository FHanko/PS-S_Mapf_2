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
    model = init_model(state)
    status = model.solve_initial()
    if status[0] == cp_model.OPTIMAL or status[0] == cp_model.FEASIBLE:
        print("--- %s seconds ---" % (time.time() - start_time))
        print(f"Initial solution time: {status[1]}")
        print(model.get_paths())
        lns_step(state, model.get_paths())
    else:
        print("Initial state is not feasible")
    pass


def lns_step(state: State, paths: Dict[int, List[int]]):
    neighbor = state.neighbor_random(paths, 4)
    model = init_model(neighbor)
    status = model.solve_optimal()
    if status[0] == cp_model.OPTIMAL or status[0] == cp_model.FEASIBLE:
        p = model.get_paths()
        # Evaluate sum of cost of neighbor sub problem.
        old_part_soc = sum([len(l) for i, l in paths.items() if i in state.active_agents])
        new_part_soc = sum([len(l) for i, l in p.items()])
        # If solution improved replace paths.
        if new_part_soc < old_part_soc:
            old_total_soc = sum([len(l) for i, l in paths.items()])
            c = 0
            for i in state.active_agents:
                paths[i] = p[c]
                c = c + 1
            state.time = max([len(l) for i, l in paths.items()])
            new_total_soc = sum([len(l) for i, l in paths.items()])
            print(f"Sum of costs: {old_total_soc} -> {new_total_soc}")
            print("--- %s seconds ---" % (time.time() - start_time))
    else:
        print('Neighborhood not feasible')

    lns_step(state, paths)


file_name = sys.argv[1]
if os.path.exists(file_name):
    with open(file_name, 'r') as f:
        input_data = json.load(f)
        input_state = State(**input_data)
        solve_initial(input_state)
else:
    print(f"File {os.path.basename(file_name)} not found.")
    exit(1)

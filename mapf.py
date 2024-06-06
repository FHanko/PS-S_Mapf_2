import json
import os
import sys

from typing import List, Dict
from ortools.sat.python import cp_model
from state import State
from model import init_model


def solve_initial(state: State):
    model = init_model(state)
    status = model.solve_initial()
    if status[0] == cp_model.OPTIMAL or status[0] == cp_model.FEASIBLE:
        print(f"Initial solution time: {status[1]}")
        print(model.get_paths())
        lns_step(state, model.get_paths())
    else:
        print("Initial state is not feasible")
    pass


def lns_step(state: State, paths: Dict[int, List[int]]):
    neighbor = state.neighbor_random(paths)
    model = init_model(neighbor)
    status = model.solve_optimal()
    if status[0] == cp_model.OPTIMAL or status[0] == cp_model.FEASIBLE:
        p = model.get_paths()
        old_soc = sum([len(l) for i, l in paths.items() if i in state.active_agents])
        new_soc = sum([len(l) for i, l in p.items()])
        # Solution improved
        if new_soc < old_soc:
            c = 0
            for i in state.active_agents:
                paths[i] = p[c]
                c = c + 1
            print(f'Sum of costs: {old_soc} -> {new_soc}')
            print(paths)
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

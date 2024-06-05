import json
import os
import sys

from ortools.sat.python import cp_model
from state import State
from model import init_model


def solve_initial(state: State):
    model = init_model(state)
    status = model.solve_initial()
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        a = model.get_paths()
        print(a)
    else:
        print("Initial state is not feasible")
    pass


def solve_optimal(state: State):
    model = init_model(state)
    status = model.solve_optimal()
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        a = model.get_paths()
        print(a)
    else:
        print('Neighborhood not feasible')
    pass


def start_lns(state: State):
    solve_initial(state)


file_name = sys.argv[1]
if os.path.exists(file_name):
    with open(file_name, 'r') as f:
        input_data = json.load(f)
        input_state = State(**input_data)
        start_lns(input_state)
else:
    print(f"File {os.path.basename(file_name)} not found.")
    exit(1)

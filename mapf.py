import json
import os
import sys

from ortools.sat.python import cp_model
from model import State
from model import init_model


def solve_initial():
    pass


def solve_optimal(state: State):
    model = init_model(state)
    status = model.solve_optimal()
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        a = model.get_paths()
        print(a)
    else:
        print('INFEASIBLE')
    pass


def start_lns(state: State):
    solve_initial()
    solve_optimal(state)


file_name = sys.argv[1]
if os.path.exists(file_name):
    with open(file_name, 'r') as f:
        input_data = json.load(f)
        input_state = State(**input_data)
        start_lns(input_state)
else:
    print(f"File {os.path.basename(file_name)} not found.")
    exit(1)

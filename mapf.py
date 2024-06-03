import json
import os
import sys

from ortools.sat.python import cp_model
from model import State
from model import init_model


def solve_initial():
    pass


def solve_optimal(state: State):
    solver = cp_model.CpSolver()
    model = init_model(state)
    status = solver.Solve(model[0])
    print(f"status   : {solver.status_name(status)}")
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for a in range(state.agents):
            for t in range(state.time):
                print(f"{a}, {t}: {solver.value(model[1][t, a])}")
        soc = 0
        for a in range(state.agents):
            print(f"cost   : {solver.value(model[2][a])}")
            soc += solver.value(model[2][a])
        print(f"total cost: {soc}")
        print(f"time   : {solver.wall_time}")
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

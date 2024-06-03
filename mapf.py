from ortools.sat.python import cp_model
import json
import os
import sys

file_name = sys.argv[1]


class State:
    def __init__(self, agents, time, width, height, start, end):
        self.agents = agents
        self.time = time
        self.width = width
        self.height = height
        self.start = start
        self.end = end


def init_model(state: State):
    model = cp_model.CpModel()
    pos = {}
    for t in range(state.time):
        for a in range(state.agents):
            pos[t, a] = model.new_int_var(0, state.width * state.height - 1, f"pos_{t}_{a}")
        # No two agents at the same position at the same time.
        model.add_all_different(pos[t, a] for a in range(state.agents))

    # Fix start and end positions.
    for a in range(state.agents):
        model.add(pos[0, a] == state.start[a])
        model.add(pos[state.time - 1, a] == state.end[a])

    # Only allow 1 distance moves.
    x = {}
    y = {}
    for t in range(state.time):
        for a in range(state.agents):
            x[t, a] = model.new_int_var(0, state.width-1, f"x_{t}_{a}")
            y[t, a] = model.new_int_var(0, state.height-1, f"y_{t}_{a}")
            model.add_modulo_equality(x[t, a], pos[t, a], state.width)
            model.add_division_equality(y[t, a], pos[t, a], state.height)

    dx = {}
    dy = {}
    for t in range(state.time-1):
        for a in range(state.agents):
            dx[t, a] = model.new_int_var(0, state.width, f"dx_{t}_{a}")
            dy[t, a] = model.new_int_var(0, state.height, f"dy_{t}_{a}")
            model.add_abs_equality(dx[t, a], x[t, a] - x[t + 1, a])
            model.add_abs_equality(dy[t, a], y[t, a] - y[t + 1, a])
            model.add(dx[t, a] + dy[t, a] <= 1)

    # Set objective

    return model, pos


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
    pass


def start_lns(state: State):
    solve_initial()
    solve_optimal(state)


if os.path.exists(file_name):
    with open(file_name, 'r') as f:
        input_data = json.load(f)
        input_state = State(**input_data)
        start_lns(input_state)
else:
    print(f"File {os.path.basename(file_name)} not found.")
    exit(1)

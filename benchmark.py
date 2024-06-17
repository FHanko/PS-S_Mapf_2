import os
import json
import time

import mapf
from state import State
from model import init_model


current_file = ""
current_start_time = time.time()


def _iteration_callback(iteration: int):
    t = time.time() - current_start_time
    if t > 180 or iteration > 200:
        return False
    else:
        return True


def _solution_callback(state: State):
    t = time.time() - current_start_time
    print(f"\"{current_file}\";{round(t,3)};{state.get_soc(range(state.agents))}")


mapf.iteration_callback = _iteration_callback
mapf.solution_callback = _solution_callback


files = []
for file in os.listdir(f"data"):
    files.append(f"data/{file}")

for c in files:
    current_file = c
    current_start_time = time.time()
    with open(c, 'r') as f:
        input_data = json.load(f)
        input_state = State(**input_data)
        # Compute optimal sum of costs if not already contained in input.
        if input_state.soc == 0:
            input_state.obstacles = [[] for _ in range(input_state.time)]
            model = init_model(input_state)
            model.solve()
            input_state.paths = model.get_paths()
            t = time.time() - current_start_time
            print(f"\"optimal\";\"{current_file}\";{round(t, 3)};{input_state.get_soc(range(input_state.agents))}")
        else:
            print(f"\"optimal\";\"{current_file}\";{input_state.soc_time};{input_state.soc}")
        # mapf.solve_initial(input_state)


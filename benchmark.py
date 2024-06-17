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
for _dir in os.listdir("data"):
    for file in os.listdir(f"data/{_dir}"):
        files.append(f"data/{_dir}/{file}")

while len(files) > 0:
    current = [f for f in files if f.__contains__(files[0].split('/')[-1])]

    for c in current:
        current_file = c
        current_start_time = time.time()
        with open(c, 'r') as f:
            input_data = json.load(f)
            input_state = State(**input_data)
            mapf.solve_initial(input_state)

        files.remove(c)





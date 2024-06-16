import os
import json
from mapf import solve_initial
from state import State

files = []
for _dir in os.listdir("data"):
    for file in os.listdir(f"data/{_dir}"):
        files.append(f"data/{_dir}/{file}")

while len(files) > 0:
    current = [f for f in files if f.__contains__(files[0].split('/')[-1])]

    for c in current:
        with open(c, 'r') as f:
            input_data = json.load(f)
            input_state = State(**input_data)
            solve_initial(input_state)

        files.remove(c)


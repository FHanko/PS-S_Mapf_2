from ortools.sat.python import cp_model


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
            x[t, a] = model.new_int_var(0, state.width - 1, f"x_{t}_{a}")
            y[t, a] = model.new_int_var(0, state.height - 1, f"y_{t}_{a}")
            model.add_modulo_equality(x[t, a], pos[t, a], state.width)
            model.add_division_equality(y[t, a], pos[t, a], state.height)

    for t in range(state.time - 1):
        for a in range(state.agents):
            dx = model.new_int_var(0, state.width, f"dx_{t}_{a}")
            dy = model.new_int_var(0, state.height, f"dy_{t}_{a}")
            model.add_abs_equality(dx, x[t, a] - x[t + 1, a])
            model.add_abs_equality(dy, y[t, a] - y[t + 1, a])
            model.add(dx + dy <= 1)

    # No swapping of agents.
    for t in range(state.time - 1):
        for a in range(state.agents):
            for a2 in range(state.agents):
                atoa2 = model.new_bool_var("")
                a2toa = model.new_bool_var("")
                model.add(pos[t, a] == pos[t + 1, a2]).only_enforce_if(atoa2)
                model.add(pos[t + 1, a] == pos[t, a2]).only_enforce_if(a2toa)
                model.add_at_most_one(atoa2, a2toa)

    # Set the objective.
    at_goal = {}
    for t in range(state.time):
        for a in range(state.agents):
            at_goal[t, a] = model.new_bool_var(f"ag_{t}_{a}")
            model.add(pos[t, a] == state.end[a]).only_enforce_if(at_goal[t, a].Not())
            model.add(pos[t, a] != state.end[a]).only_enforce_if(at_goal[t, a])

    cost = {}
    for a in range(state.agents):
        cost[a] = model.new_int_var(0, state.time, f"cost_{a}")
        model.add(cost[a] == sum([at_goal[t, a] for t in range(state.time)]) + 1)

    soc = model.new_int_var(0, state.time * state.agents, "soc")
    model.add(soc == sum(cost[a] for a in range(state.agents)))
    model.minimize(soc)

    return model, pos, cost

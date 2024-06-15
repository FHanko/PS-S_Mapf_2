from ortools.sat.python import cp_model
from typing import List, Dict

from ortools.sat.python.cp_model import IntVar

from state import State


class Model:
    def __init__(self, model: cp_model.CpModel, pos: dict[tuple[int, int], IntVar],
                 costs: dict[int, IntVar], soc: IntVar, agent_count: int):
        self.model = model
        self.pos = pos
        self.costs = costs
        self.soc = soc
        self.agent_count = agent_count
        self.solver = cp_model.CpSolver()

    def solve(self):
        self.model.minimize(self.soc)
        status = self.solver.Solve(self.model)
        return status, self.solver.wall_time

    def get_paths(self) -> Dict[int, List[int]]:
        paths = {}
        for i in range(self.agent_count):
            # Get path for each agent from solver values
            nodes = [v for (k1, k2), v in self.pos.items() if k2 == i]
            paths[i] = self.solver.values(nodes).array.tolist()
        return paths


def init_model(state: State) -> Model:
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

    # No obstacle collision
    for t in range(state.time):
        for a in range(state.agents):
            if t < len(state.obstacles):
                model.add_linear_expression_in_domain(pos[t, a],
                                                      cp_model.Domain.from_values(
                                                          state.obstacles[t]).complement().intersection_with(
                                                          cp_model.Domain.from_intervals(
                                                              [[0, state.width * state.height - 1]])
                                                      ))

    # Define cost as the objective.
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

    # No moving away from goal.
    for t in range(state.time - 1):
        for a in range(state.agents):
            model.add(pos[t, a] == pos[t + 1, a]).only_enforce_if(at_goal[t, a].Not())

    return Model(model, pos, cost, soc, state.agents)

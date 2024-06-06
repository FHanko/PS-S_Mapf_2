import random
from typing import List, Dict


class State:
    def __init__(self, agents: int, time: int, width: int, height: int,
                 start: List[int], end: List[int], obstacles: List[List[int]]):
        self.agents = agents
        self.time = time
        self.width = width
        self.height = height
        self.start = start
        self.end = end
        self.obstacles = obstacles

    active_agents = []

    def neighbor_random(self, paths: Dict[int, List[int]]):
        # Randomly select active agents.
        active = []
        for i in range(2):
            active.append(random.choice(range(self.agents)))
        active = set(active)
        self.active_agents = active

        # Set inactive agents to obstacles.
        inactive = [i for i in range(self.agents) if i not in active]
        obstacles = []
        for i in range(self.time):
            obstacle_list = []
            for a in inactive:
                if i < len(paths[a]):
                    obstacle_list.append(paths[a][i])
            obstacles.append(obstacle_list)

        neighbor = State(len(set(active)), self.time, self.width, self.height,
                         [self.start[a] for a in active],
                         [self.end[a] for a in active],
                         obstacles)
        return neighbor



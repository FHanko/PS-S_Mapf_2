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

    def neighbor_random(self, paths: Dict[int, List[int]]):
        active = []
        for i in range(1):
            active.append(random.choice(range(self.agents)))
        print(active)
        inactive = [i for i in range(self.agents) if i not in active]
        print(inactive)
        obstacles = []
        for i in range(self.time):
            obstacle_list = []
            for a in inactive:
                obstacle_list.append(paths[a][i])
            obstacles.append(obstacle_list)

        neighbor = State(len(set(active)), self.time, self.width, self.height,
                         [self.start[a] for a in active],
                         [self.end[a] for a in active],
                         obstacles)
        return neighbor



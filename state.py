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
        self.paths = {}
        self.active_agents = set()
        self.feasible = False

    def merge_paths(self, other: 'State'):
        c = 0
        for i in other.active_agents:
            self.paths[i] = other.paths[c]
            c = c + 1

    def get_soc(self, agent_subset):
        return sum([len(l) for i, l in self.paths.items() if i in agent_subset])

    # Turn the paths of inactive agents to a list of obstacles at specific times and return it.
    def get_obstacles(self) -> List[List[int]]:
        inactive = [i for i in range(self.agents) if i not in self.active_agents]
        obstacles = []
        for i in range(self.time):
            obstacle_list = []
            for a in inactive:
                if i < len(self.paths[a]):
                    obstacle_list.append(self.paths[a][i])
            obstacles.append(obstacle_list)
        return obstacles

    def neighbor(self):
        if not self.feasible:
            return self.neighbor_repair()
        else:
            return self.neighbor_random()

    def get_active_from_conflicts(self, max_size):
        for p1 in self.paths:
            for p2 in self.paths:
                for t in range(self.time):
                    if (p1 != p2 and t < len(self.paths[p1]) and t < len(self.paths[p2])
                            and self.paths[p1][t] == self.paths[p2][t]):
                        self.active_agents.add(p1)
                        self.active_agents.add(p2)
            if len(self.active_agents) >= max_size:
                return

    def neighbor_repair(self, neighborhood_size=10):
        neighbor = State(self.agents, self.time, self.width, self.height, self.start, self.end, self.obstacles)
        neighbor.paths = self.paths
        # Select agents with conflicting paths as active agents.
        neighbor.get_active_from_conflicts(neighborhood_size)

        # Set neighbor attributes.
        neighbor.agents = len(neighbor.active_agents)
        neighbor.obstacles = neighbor.get_obstacles()
        neighbor.start = [self.start[a] for a in neighbor.active_agents]
        neighbor.end = [self.end[a] for a in neighbor.active_agents]
        return neighbor

    def neighbor_random(self, neighborhood_size=10):
        neighbor = State(self.agents, self.time, self.width, self.height, self.start, self.end, self.obstacles)
        neighbor.paths = self.paths
        # Randomly select active agents.
        for i in range(neighborhood_size):
            neighbor.active_agents.add(random.choice(range(self.agents)))
        # Set neighbor attributes.
        neighbor.agents = len(neighbor.active_agents)
        neighbor.obstacles = neighbor.get_obstacles()
        neighbor.start = [self.start[a] for a in neighbor.active_agents]
        neighbor.end = [self.end[a] for a in neighbor.active_agents]
        return neighbor

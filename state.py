from typing import List


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

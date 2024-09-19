# NAME(S): [PLACE YOUR NAME(S) HERE]
#
# APPROACH: [WRITE AN OVERVIEW OF YOUR APPROACH HERE.]
#     Please use multiple lines (< ~80-100 char) for you approach write-up.
#     Keep it readable. In other words, don't write
#     the whole damned thing on one super long line.
#
#     In-code comments DO NOT count as a description of
#     of your approach.


"""
So potential approaches:

We could map it all in a 2d array, but that seems costly

We could use a graph to traverse

Question: If agent is at point g, and end is at point Z, how do we find the optimal path from point g to z if it's all relative to a

We need some form of pathfinding algorithm that can find the lowest cost traversal of known paths from g to z by backtracking

Traveling salesman problem?

Dijkstra's algorithm? 
"""

import random
import pprint
import time
import numpy as np


class AI:
    def __init__(self):
        """
        Called once before the sim starts. You may use this function
        to initialize any data or data structures you need.
        """
        self.turn = 0
        self.valid_moves = ["N", "E", "S", "W"]
        self.oppMove = {"N": "S", "E": "W", "S": "N", "W": "E"}
        self.direction_To_Coord = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
        self.coord_To_Direction = {(0, -1): "N", (1, 0): "E", (0, 1): "S", (-1, 0): "W"}

        self.map = {}

        self.traversed = []

        self.position = [1, 1]

        self.visit_queue = []

        self.move_stack = []

    def update_position(self, move):

        dx, dy = self.direction_To_Coord[move]
        self.position = [self.position[0] + dx, self.position[1] + dy]

    def valid_move(self, direction, percepts):
        print("percepts", percepts)
        print("direction", direction)
        print("traversed", self.traversed)
        dx, dy = self.direction_To_Coord[direction]
        new_position = (self.position[0] + dx, self.position[1] + dy)
        if percepts[direction][0] == "w" or new_position in self.traversed:
            return False
        print("new position", new_position)
        return new_position

    def depth_first_search(self, percepts):
        if percepts["X"][0] == "r":
            return "U"
        for move in self.valid_moves:
            if self.valid_move(move, percepts):
                print("valid move")
                self.traversed.append(tuple(self.position))

                self.move_stack.append(self.oppMove[move])

                self.update_position(move)

                return move

            if self.move_stack and move == "W":
                print("backtracking")
                print("traversed", self.traversed)
                self.traversed.append(tuple(self.position))
                backtrack = self.move_stack.pop()

                self.update_position(backtrack)

                return backtrack

        return "N"

    def update(self, percepts):
        """
        PERCEPTS:
        Called each turn. Parameter "percepts" is a dictionary containing
        nine entries with the following keys: X, N, NE, E, SE, S, SW, W, NW.
        Each entry's value is a single character giving the contents of the
        map cell in that direction. X gives the contents of the cell the agent
        is in.

        COMAMND:
        This function must return one of the following commands as a string:
        N, E, S, W, U

        N moves the agent north on the map (i.e. up)
        E moves the agent east
        S moves the agent south
        W moves the agent west
        U uses/activates the contents of the cell if it is useable. For
        example, stairs (o, b, y, p) will not move the agent automatically
        to the corresponding hex. The agent must 'U' the cell once in it
        to be transported.

        The same goes for goal hexes (0, 1, 2, 3, 4, 5, 6, 7, 8, 9).
        """

        """First, let's make it not hit walls"""

        return self.depth_first_search(percepts)


"""
py main.py -w worlds/world -t 100 -d
can use -l log to output to text file
"""

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
        self.direction_To_Coord = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
            "NE": (1, -1),
            "NW": (-1, -1),
            "SE": (1, 1),
            "SW": (-1, 1),
        }
        self.direction_To_Index = {
            "N": 0,
            "E": 1,
            "S": 2,
            "W": 3,
            "NE": 4,
            "NW": 5,
            "SE": 6,
            "SW": 7,
        }
        self.coord_To_Direction = {(0, -1): "N", (1, 0): "E", (0, 1): "S", (-1, 0): "W"}

        self.map = {}

        self.unmarked = {}

        self.traversed = []

        self.position = [1, 1]

        self.visit_queue = []

        self.move_stack = []

    def calculate_position(self, origin, move):
        dx, dy = self.direction_To_Coord[move]
        return [origin[0] + dx, origin[1] + dy]

    def map_location(self, percepts):
        for move in self.valid_moves:
            base_position = self.position
            for i in range(len(percepts[move])):
                base_position = self.calculate_position(base_position, move)
                self.map[tuple(base_position)] = percepts[move][i]
                if (
                    tuple(base_position) not in self.traversed
                    or percepts[move][i] not in "w"
                ):
                    self.unmarked[tuple(base_position)] = percepts[move][i]

    def cull_tiles(self):
        copy_dict = self.unmarked.copy()
        for coord in copy_dict:
            position_list = []
            for i in self.direction_To_Coord.keys():
                if tuple(self.calculate_position(coord, i)) in self.traversed:
                    position_list += ["t"]
                elif (
                    self.map.get(tuple(self.calculate_position(coord, i)), False) == "w"
                ):
                    position_list += ["w"]
                elif (
                    self.map.get(tuple(self.calculate_position(coord, i)), False) == "g"
                ):
                    position_list += ["g"]
                else:
                    position_list += ["u"]
            if len(position_list) == 8:
                check_list = [
                    [["N", "E", "W"], ["SW", "S", "SE"]],
                    [["N", "E", "S"], ["W", "SW", "NW"]],
                    [["E", "S", "W"], ["N", "NE", "NW"]],
                    [["N", "S", "W"], ["E", "NE", "SE"]],
                    [["N", "E"], ["S", "W", "SW"]],
                    [["E", "S"], ["N", "W", "NW"]],
                    [["S", "W"], ["N", "E", "NE"]],
                    [["N", "W"], ["E", "S", "SE"]],
                    [["N"], ["E", "SE", "S", "SW", "W"]],
                    [["E"], ["N", "NW", "W", "SW", "S"]],
                    [["S"], ["E", "NE", "N", "NW", "W"]],
                    [["W"], ["N", "NE", "E", "SE", "S"]],
                ]
                if all(x in ("g") for x in position_list):
                    self.traversed.append(tuple(coord))
                    self.unmarked.pop(tuple(coord))
                    if coord in self.visit_queue:
                        self.visit_queue.remove(coord)
                    break
                else:
                    for i in check_list:
                        if all(
                            position_list[self.direction_To_Index.get(x, False)]
                            in ("t", "w")
                            for x in i[0]
                        ):
                            if all(
                                position_list[self.direction_To_Index.get(x, False)]
                                in ("g")
                                for x in i[1]
                            ) or (
                                tuple(self.calculate_position(coord, i[0][0]))
                                == tuple(self.position)
                                and len(i[0]) == 3
                            ):

                                self.traversed.append(tuple(coord))
                                self.unmarked.pop(tuple(coord))
                                if coord in self.visit_queue:
                                    self.visit_queue.remove(coord)
                                break

    def update_position(self, move):

        dx, dy = self.direction_To_Coord[move]
        self.position = [self.position[0] + dx, self.position[1] + dy]

    def valid_move(self, direction, percepts):
        dx, dy = self.direction_To_Coord[direction]
        new_position = (self.position[0] + dx, self.position[1] + dy)
        if percepts[direction][0] == "w" or new_position in self.traversed:
            return False
        return new_position

    def depth_first_search(self, percepts):
        self.map_location(percepts)
        self.cull_tiles()

        if percepts["X"][0] == "r":
            return "U"
        for move in self.valid_moves:
            if self.valid_move(move, percepts):
                self.traversed.append(tuple(self.position))
                self.move_stack.append(self.oppMove[move])
                self.visit_queue.append(
                    tuple(self.calculate_position(self.position, move))
                )
                self.update_position(move)
                return move

            if self.move_stack and move == "W":
                self.traversed.append(tuple(self.position))
                backtrack = self.move_stack.pop()
                if len(self.visit_queue) > 0:
                    self.visit_queue.pop()
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
        # time.sleep(100000)
        self.turn += 1
        return self.depth_first_search(percepts)


"""
py main.py -w worlds/world -t 100 -d
can use -l log to output to text file
"""

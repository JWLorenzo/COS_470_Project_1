# NAME(S): Jacob Lorenzo and Danila Borodaenko
#
# APPROACH: 
#     The algorithm applied for this project is depth-first search. The agent continuously
#     maintains a record of its movements and what tiles it has explored, prioritizing new
#     movements in the following order: N E S W. Movements that put the agent into a wall
#     are marked invalid, as are movements that go onto already traversed tiles. If no
#     moves are valid, the agent backtracks until a new valid move arises. If the agent
#     sees the goal, it moves directly towards it in order to finish the task faster.
#
#     TODO: find a way to eliminate apparent loops to bypass backtrack (worldB right side)


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
import numpy as np # type: ignore


class AI:
    # initialize agent parameters
    def __init__(self):
        """
        Called once before the sim starts. You may use this function
        to initialize any data or data structures you need.
        """
        # variable to define possible agent movement
        self.valid_moves = ["N", "E", "S", "W"]
        # variable to define opposite movement pairs
        self.oppMove = {"N": "S", "E": "W", "S": "N", "W": "E"}
        # variable to define corresponding movement position adjustment
        self.direction_To_Coord = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
        # unused variable to define corresponding movement position adjustment
        self.coord_To_Direction = {(0, -1): "N", (1, 0): "E", (0, 1): "S", (-1, 0): "W"}

        # variable to record number of actions performed
        self.turn = 0

        # unused variable to record overall map structure
        self.map = {}

        # variable to record tiles that have been traveled to
        self.traversed = []

        # variable to record current tile position
        self.position = [1, 1]

        # unused variable to record desired movements
        self.visit_queue = []

        # variable used to record movement for backtrack traversal
        self.move_stack = []

    # function to change agent position according to chosen movement
    def update_position(self, move):
        # assign movement increments and modify position
        dx, dy = self.direction_To_Coord[move]
        self.position = [self.position[0] + dx, self.position[1] + dy]

    # function to check if desired agent position is valid
    def valid_move(self, direction, percepts):
        #print("percepts", percepts)
        #print("direction", direction)
        #print("traversed", self.traversed)
        # assign movement increments and modify position
        dx, dy = self.direction_To_Coord[direction]
        new_position = (self.position[0] + dx, self.position[1] + dy)
        # check if chosen position is valid and has not been traversed
        if percepts[direction][0] == "w" or new_position in self.traversed:
            return False
        #print("new position", new_position)
        return new_position

    # function to check if agent has gone around a loop TODO
    def loop_check(self):
        # create possible modified positions
        temp_pos = []
        dx, dy = self.direction_To_Coord["N"]
        temp_pos[0] = (self.position[0] + dx, self.position[1] + dy)
        dx, dy = self.direction_To_Coord["E"]
        temp_pos[1] = (self.position[0] + dx, self.position[1] + dy)
        dx, dy = self.direction_To_Coord["S"]
        temp_pos[2] = (self.position[0] + dx, self.position[1] + dy)
        dx, dy = self.direction_To_Coord["W"]
        temp_pos[3] = (self.position[0] + dx, self.position[1] + dy)
        # check where the (possible) loop starts
        for iter, pos in enumerate(self.traversed):
            if pos in temp_pos:
                temp_iter = iter
                break
        # check if the movements form a loop
        for iter, move in enumerate(self.move_stack):
            if iter == temp_iter:
                last_move = move
            elif iter >= temp_iter:
                if self.oppMove[last_move] == move:
                    return False
                last_move = move
        return True

    # function to perform several prior movement removals TODO
    def multi_pop(self, move_stack, position):
        # check where the loop starts
        for iter, move in enumerate(move_stack):
            if move == position:
                temp_len = iter + 1
                break
        # remove prior movements to close the loop
        while len(move_stack) > temp_len:
            self.move_stack.pop()

    # function to perform overall map search algorithm
    def depth_first_search(self, percepts):
        # exit if at goal state
        if percepts["X"][0] == "r":
            return "U"
        
        # move towards goal if it is visible
        # no possible issues of movement validity
        if "r" in percepts["N"]:
            #print("victory approach")
            # record position, record movement complement, and perform movement
            self.traversed.append(tuple(self.position))
            self.move_stack.append(self.oppMove["N"])
            self.update_position("N")
            return "N"
        if "r" in percepts["E"]:
            #print("victory approach")
            # record position, record movement complement, and perform movement
            self.traversed.append(tuple(self.position))
            self.move_stack.append(self.oppMove["E"])
            self.update_position("E")
            return "E"
        if "r" in percepts["S"]:
            #print("victory approach")
            # record position, record movement complement, and perform movement
            self.traversed.append(tuple(self.position))
            self.move_stack.append(self.oppMove["S"])
            self.update_position("S")
            return "S"
        if "r" in percepts["W"]:
            #print("victory approach")
            # record position, record movement complement, and perform movement
            self.traversed.append(tuple(self.position))
            self.move_stack.append(self.oppMove["W"])
            self.update_position("W")
            return "W"
        
        # iterate through possible movements in order: N E S W
        for move in self.valid_moves:
            # check movement validity
            if self.valid_move(move, percepts):
                #print("valid move")
                # record position, record movement complement, and perform movement
                self.traversed.append(tuple(self.position))
                self.move_stack.append(self.oppMove[move])
                self.update_position(move)
                return move

            # check to see if all movements have been attempted
            # if backtrack record exists, attempt movement back
            if self.move_stack and move == "W":
                #print("backtracking")
                #print("traversed", self.traversed)
                # record position, remove prior movement, and perform backtrack
                self.traversed.append(tuple(self.position))
                backtrack = self.move_stack.pop()
                self.update_position(backtrack)
                return backtrack

        # failsafe return statement, agent is permanently stuck
        return "U"

    # function to repeatedly perform agent action
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

        # perform depth-first search based on percepts
        return self.depth_first_search(percepts)


"""
py main.py -w worlds/world -t 100 -d
can use -l log to output to text file
"""

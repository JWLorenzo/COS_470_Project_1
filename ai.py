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
#     TODO: find a way to cull tiles that should not be visited


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

        # variable to record movement for backtrack traversal
        self.move_stack = []

        # variable to record movement for loop determination
        self.move_stack_run = []

        # variable to record maximum number of branches per tile position
        self.branch_num_max = []

        # variable to record number of branches per tile position
        self.branch_num = []

        # variable to track loop traversal status
        self.loop_flag = False

        # variable to track backtrack traversal status
        self.backtrack_flag = False

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
    
    # function to check if desired agent position is valid (loop case) TODO
    def valid_move_loop(self, direction, percepts):
        #print("percepts", percepts)
        #print("direction", direction)
        #print("traversed", self.traversed)
        # assign movement increments and modify position
        dx, dy = self.direction_To_Coord[direction]
        new_position = (self.position[0] + dx, self.position[1] + dy)
        # check if chosen position is valid and has not been traversed
        if percepts[direction][0] == "w":
            return False
        #print("new position", new_position)
        return new_position
    
    # function to record possible branches for each position TODO
    def branch_check(self, percepts):
        temp_branch = 0
        if percepts["N"][0] != "w":
            dx, dy = self.direction_To_Coord["N"]
            new_position = (self.position[0] + dx, self.position[1] + dy)
            temp_branch = temp_branch + 1
            #if new_position not in self.traversed:
            #    temp_branch = temp_branch + 1
        if percepts["E"][0] != "w":
            dx, dy = self.direction_To_Coord["E"]
            new_position = (self.position[0] + dx, self.position[1] + dy)
            temp_branch = temp_branch + 1
            #if new_position not in self.traversed:
            #    temp_branch = temp_branch + 1
        if percepts["S"][0] != "w":
            dx, dy = self.direction_To_Coord["S"]
            new_position = (self.position[0] + dx, self.position[1] + dy)
            temp_branch = temp_branch + 1
            #if new_position not in self.traversed:
            #    temp_branch = temp_branch + 1
        if percepts["W"][0] != "w":
            dx, dy = self.direction_To_Coord["W"]
            new_position = (self.position[0] + dx, self.position[1] + dy)
            temp_branch = temp_branch + 1
            #if new_position not in self.traversed:
            #    temp_branch = temp_branch + 1
        #print(temp_branch)
        return temp_branch
    
    # function to recalculate possible branches for each position
    def branch_recheck(self, percepts):
        for iter, branch in enumerate(self.branch_num_max):
            temp_branch = branch
            dx, dy = self.direction_To_Coord["N"]
            new_position = (self.traversed[iter][0] + dx, self.traversed[iter][1] + dy)
            if new_position in self.traversed:
                temp_branch = temp_branch - 1
            dx, dy = self.direction_To_Coord["E"]
            new_position = (self.traversed[iter][0] + dx, self.traversed[iter][1] + dy)
            if new_position in self.traversed:
                temp_branch = temp_branch - 1
            dx, dy = self.direction_To_Coord["S"]
            new_position = (self.traversed[iter][0] + dx, self.traversed[iter][1] + dy)
            if new_position in self.traversed:
                temp_branch = temp_branch - 1
            dx, dy = self.direction_To_Coord["W"]
            new_position = (self.traversed[iter][0] + dx, self.traversed[iter][1] + dy)
            if new_position in self.traversed:
                temp_branch = temp_branch - 1
            self.branch_num[iter] = temp_branch

    # function to check if agent has gone around a loop TODO
    def loop_check(self, percepts):
        # check possible modified positions
        for move in self.valid_moves:
            #if self.valid_move_loop(move, percepts) and move != self.oppMove[self.move_stack[-1]]:
            if self.valid_move_loop(move, percepts):
                temp_move = move
                break
            if move == "W":
                return [False, False]
        #print(temp_move)
        # assign movement increments and modify position
        dx, dy = self.direction_To_Coord[temp_move]
        new_pos = (self.position[0] + dx, self.position[1] + dy)
        # check where the (possible) loop starts
        for iter, pos in enumerate(self.traversed):
            if pos == new_pos:
                temp_iter = len(self.traversed) - iter
                break
        self.move_stack.append(self.oppMove[temp_move])
        #print(temp_iter)
        #print(len(self.move_stack))
        #print(self.traversed)
        #print(self.move_stack)
        if temp_iter > len(self.move_stack):
            return [False, False]
        # check if the movements form a loop
        # no opposing movement indicates a loop
        temp_len = 0
        first_pos = None
        last_pos = None
        for iter, move in enumerate(self.move_stack):
            if iter == (len(self.move_stack) - temp_iter):
                last_move = move
                first_pos = self.traversed[iter]
                temp_len = temp_len + 1
                #print(last_move)
            elif iter > (len(self.move_stack) - temp_iter):
                if self.oppMove[last_move] == move:
                    self.move_stack.pop()
                    return [False, False]
                last_move = move
                last_pos = self.traversed[iter]
                temp_len = temp_len + 1
                #print(last_move)
        #print(first_pos)
        #print(last_pos)
        if last_pos != None:
            last_pos = (last_pos[0] + dx, last_pos[1] + dy)
            #print(last_pos)
        if first_pos != last_pos:
            self.move_stack.pop()
            return [False, False]
        if temp_len > 1:
            self.move_stack.pop()
            return [temp_move, temp_iter - 1]
        else:
            self.move_stack.pop()
            return [False, False] # 26 13 for worldB loop test - 29 6 for worldB dead end test

    # function to check if agent has gone around a loop TODO
    def loop_check_new(self, percepts):
        # check possible modified positions
        for move in self.valid_moves:
            if self.valid_move_loop(move, percepts):
                temp_move = move
                #print(temp_move)
                N_flag = False
                E_flag = False
                S_flag = False
                W_flag = False
                # assign movement increments and modify position
                dx, dy = self.direction_To_Coord[temp_move]
                new_pos = (self.position[0] + dx, self.position[1] + dy)
                # check where the (possible) loop starts
                for iter, pos in enumerate(self.traversed):
                    if pos == new_pos:
                        temp_iter = len(self.traversed) - iter
                        #print(temp_iter)
                        break
                if temp_iter <= len(self.move_stack_run):
                    self.move_stack_run.append(self.oppMove[temp_move])
                    # check if the movements form a loop
                    # no opposing movement indicates a loop
                    temp_len = 0
                    first_pos = None
                    last_pos = None
                    last_move = None
                    for iter, move_sub in enumerate(self.move_stack_run):
                        #print(last_move)
                        if iter == (len(self.move_stack_run) - temp_iter):
                            #print("equal!")
                            #if self.branch_num[iter] > 2:
                            #    break
                            if (move_sub == "N"):
                                N_flag = True
                            if (move_sub == "E"):
                                E_flag = True
                            if (move_sub == "S"):
                                S_flag = True
                            if (move_sub == "W"):
                                W_flag = True
                            last_move = move_sub
                            first_pos = self.traversed[iter]
                            temp_len = temp_len + 1
                        elif iter > (len(self.move_stack_run) - temp_iter):
                            #print("greater!")
                            if self.oppMove[last_move] == move_sub:
                                #print("oppMove!")
                                #self.move_stack.pop()
                                break
                            if self.branch_num[iter] > 0:
                                #print("branching!")
                                break
                            if (move_sub == "N"):
                                N_flag = True
                            if (move_sub == "E"):
                                E_flag = True
                            if (move_sub == "S"):
                                S_flag = True
                            if (move_sub == "W"):
                                W_flag = True
                            last_move = move_sub
                            last_pos = self.traversed[iter]
                            temp_len = temp_len + 1
                    #print(last_move)
                    #if last_move is None:
                        #print("pop1!")
                        #self.move_stack.pop()
                        #continue
                    #print(first_pos)
                    #print(last_pos)
                    if last_move is not None:
                        #print("final!")
                        #if self.oppMove[last_move] != move:
                        flag_sum = N_flag + E_flag + S_flag + W_flag
                        #print(flag_sum)
                        if temp_len > 1 and flag_sum == 4:
                            if last_pos is not None:
                                last_pos = (last_pos[0] + dx, last_pos[1] + dy)
                                #print(first_pos)
                                #print(last_pos)
                                #print(temp_len)
                                #if first_pos == last_pos and temp_len > 1:
                                if first_pos == last_pos and (temp_iter - 1) < len(self.move_stack):
                                    #print("pop2!")
                                    self.move_stack_run.pop()
                                    return [temp_move, temp_iter - 1]
                    #print("pop3!")
                    self.move_stack_run.pop()
            #print("here!")
            #print(move)
            if move == "W":
                return [False, False]

    # function to perform several prior movement removals TODO
    def multi_pop(self, loop_len):
        # remove prior movements to close the loop
        temp_iter = 0
        while loop_len > temp_iter:
            self.move_stack.pop() 
            #temp_move = self.move_stack.pop()
            #print(temp_move)
            temp_iter = temp_iter + 1

    # function to check goal visibility
    def goal_check(self, percepts):
        if "r" in percepts["N"] or "r" in percepts["E"] or "r" in percepts["S"] or "r" in percepts["W"]:
            return True
        return False
    
    # function to move towards the goal tile
    def goal_approach(self, percepts):
        # move towards goal if it is visible
        # no possible issues of movement validity
        if "r" in percepts["N"]:
            #print("victory approach")
            # record position, record movement complement, and perform movement
            self.traversed.append(tuple(self.position))
            self.branch_num_max.append(self.branch_check(percepts))
            self.branch_num.append(self.branch_check(percepts))
            self.branch_recheck(percepts)
            self.move_stack.append(self.oppMove["N"])
            self.move_stack_run.append(self.oppMove["N"])
            self.update_position("N")
            return "N"
        if "r" in percepts["E"]:
            #print("victory approach")
            # record position, record movement complement, and perform movement
            self.traversed.append(tuple(self.position))
            self.branch_num_max.append(self.branch_check(percepts))
            self.branch_num.append(self.branch_check(percepts))
            self.branch_recheck(percepts)
            self.move_stack.append(self.oppMove["E"])
            self.move_stack_run.append(self.oppMove["E"])
            self.update_position("E")
            return "E"
        if "r" in percepts["S"]:
            #print("victory approach")
            # record position, record movement complement, and perform movement
            self.traversed.append(tuple(self.position))
            self.branch_num_max.append(self.branch_check(percepts))
            self.branch_num.append(self.branch_check(percepts))
            self.branch_recheck(percepts)
            self.move_stack.append(self.oppMove["S"])
            self.move_stack_run.append(self.oppMove["S"])
            self.update_position("S")
            return "S"
        if "r" in percepts["W"]:
            #print("victory approach")
            # record position, record movement complement, and perform movement
            self.traversed.append(tuple(self.position))
            self.branch_num_max.append(self.branch_check(percepts))
            self.branch_num.append(self.branch_check(percepts))
            self.branch_recheck(percepts)
            self.move_stack.append(self.oppMove["W"])
            self.move_stack_run.append(self.oppMove["W"])
            self.update_position("W")
            return "W"
        return False

    # function to perform overall map search algorithm
    def depth_first_search(self, percepts):
        # exit if at goal state
        if percepts["X"][0] == "r":
            return "U"
        
        # move towards goal if it is visible
        if self.goal_check(percepts):
            self.loop_flag = False
            self.backtrack_flag = False
            return self.goal_approach(percepts)
        
        # iterate through possible movements in order: N E S W
        for move in self.valid_moves:
            # check movement validity
            if self.valid_move(move, percepts):
                #print("valid move")
                # record position, record movement complement, and perform movement
                self.traversed.append(tuple(self.position))
                self.branch_num_max.append(self.branch_check(percepts))
                self.branch_num.append(self.branch_check(percepts))
                self.branch_recheck(percepts)
                self.move_stack.append(self.oppMove[move])
                self.move_stack_run.append(self.oppMove[move])
                self.update_position(move)
                self.loop_flag = False
                self.backtrack_flag = False
                return move

            # check to see if all movements have been attempted
            # if backtrack record exists, attempt movement back
            if self.move_stack and move == "W":
                #print("backtracking")
                #print("traversed", self.traversed)
                # check if agent has performed a loop
                #print(self.move_stack)
                self.traversed.append(tuple(self.position))
                self.branch_num_max.append(self.branch_check(percepts))
                self.branch_num.append(self.branch_check(percepts))
                self.branch_recheck(percepts)
                
                #print(self.traversed)
                #print(self.branch_num)
                
                if self.loop_check_new(percepts)[0] != False and self.loop_flag == False and self.backtrack_flag == False:
                # remove loop removal function v
                #if self.loop_check_new(percepts)[0] != False and self.loop_flag == True and self.backtrack_flag == False:
                    #print("loop!")
                    #print(self.move_stack)
                    temp_loop = []
                    temp_loop = self.loop_check_new(percepts)
                    #print(temp_loop)
                    #print(temp_loop)
                    self.multi_pop(temp_loop[1])
                    #self.traversed.append(tuple(self.position))
                    self.update_position(temp_loop[0])
                    #print(self.move_stack)
                    self.move_stack_run.append(self.oppMove[temp_loop[0]])
                    self.loop_flag = True
                    self.backtrack_flag = False
                    return temp_loop[0]
                
                # record position, remove prior movement, and perform backtrack
                #print("backtrack!")
                #print(self.move_stack)
                #self.traversed.append(tuple(self.position))
                backtrack = self.move_stack.pop()
                self.update_position(backtrack)
                self.move_stack_run.append(self.oppMove[backtrack])
                self.loop_flag = False
                self.backtrack_flag = True
                return backtrack

        # failsafe return statement
        self.loop_flag = False
        self.backtrack_flag = False
        return "N"

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

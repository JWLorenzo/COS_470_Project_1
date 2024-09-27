# NAME(S): Jacob Lorenzo and Danila Borodaenko
# ASSIGNMENT: Project 1
# SUBMISSION DATE: 9/27/24
# BENCHMARKS:
#     WORLD A SCORE: 19
#     WORLD B SCORE: 787
#     WORLD C SCORE: 912
# APPROACH:
#     The algorithm applied for this project is depth-first search. The agent continuously
#     maintains a record of its movements and what tiles it has explored, prioritizing new
#     movements in the following order: N E S W. Movements that put the agent into a wall
#     are marked invalid, as are movements that go onto already traversed tiles. If no
#     moves are valid, the agent backtracks until a new valid move arises. If the agent
#     sees the goal, it moves directly towards it in order to finish the task faster. We
#     utilize a pruning algorithm to detect patterns of walls and traversed tiles to eliminate
#     tile candidates to improve traversal path efficiency. In addition, we utilize a loop detection
#     algorithm to determine the most efficient path to exit a loop based on traversed tiles and existing
#     walls. From our observations, it seems that the pruning algorithm takes precedent and can take a route
#     that would be considered less efficient, but falls within the pruning deduction utilized, so therefore
#     the pruning algorithm always takes priority.
#

import time  # Used for testing purposes / map visualization when time.sleep is uncommented


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

        # variable to record number of actions performed
        self.turn = 0

        # unused variable to record overall map structure
        self.map = {}

        # variable used by mapping function to keep track of non-traversed nodes

        self.unmarked = {}

        # variable to record tiles that have been traveled to or pruneed out
        self.traversed = []

        # variable to record tiles that have been traveled to
        self.traversed_loop = []

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

    def calculate_position(self, origin, move):
        dx, dy = self.direction_To_Coord[move]
        return (origin[0] + dx, origin[1] + dy)

    def map_location(self, percepts):
        for move in self.valid_moves:
            base_position = self.position
            for i in range(len(percepts[move])):
                base_position = self.calculate_position(base_position, move)
                self.map[base_position] = percepts[move][i]
                if base_position not in self.traversed or percepts[move][i] != "w":
                    self.unmarked[base_position] = percepts[move][i]

    def update_traversal_maps(self, coord):
        self.traversed.append(coord)
        self.unmarked.pop(coord)
        if coord in self.visit_queue:
            self.visit_queue.remove(coord)

    def prune_tiles(self):

        copy_dict = self.unmarked.copy()
        for coord in copy_dict:
            position_list = []
            for i in self.direction_To_Coord.keys():

                if self.calculate_position(coord, i) in self.traversed:
                    position_list += ["t"]
                elif self.map.get(self.calculate_position(coord, i), False) in (
                    "w",
                    "g",
                ):
                    position_list += [
                        self.map.get(self.calculate_position(coord, i), False)
                    ]
                else:
                    position_list += ["u"]

            if len(position_list) == 8:
                check_list = [
                    [["N", "E", "W", "SE", "SW"], []],
                    [["N", "E", "S", "SW", "NW"], []],
                    [["E", "S", "W", "NE", "NW"], []],
                    [["N", "S", "W", "NE", "SE"], []],
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
                    self.update_traversal_maps(coord)
                    break
                else:
                    for i in check_list:
                        if all(
                            (
                                position_list[self.direction_To_Index.get(x, False)]
                                in ("t", "w")
                            )
                            and (
                                self.calculate_position(coord, x)
                                != tuple(self.position)
                            )
                            for x in i[0]
                        ):
                            if (
                                all(
                                    (
                                        position_list[
                                            self.direction_To_Index.get(x, False)
                                        ]
                                        == "g"
                                    )
                                    and (
                                        self.calculate_position(coord, x)
                                        not in self.traversed
                                    )
                                    and (
                                        self.calculate_position(coord, x)
                                        != tuple(self.position)
                                    )
                                    for x in i[1]
                                )
                            ) or (
                                self.calculate_position(coord, i[0][0])
                                == tuple(self.position)
                                and len(i[0]) in range(3, 8)
                            ):

                                self.update_traversal_maps(coord)
                                break

    # function to change agent position according to chosen movement
    def update_position(self, move):
        # assign movement increments and modify position
        dx, dy = self.direction_To_Coord[move]
        self.position = [self.position[0] + dx, self.position[1] + dy]

    # function to check if desired agent position is valid
    def valid_move(self, direction, percepts):
        # assign movement increments and modify position
        dx, dy = self.direction_To_Coord[direction]
        new_position = (self.position[0] + dx, self.position[1] + dy)
        # check if chosen position is valid and has not been traversed
        if percepts[direction][0] == "w" or new_position in self.traversed:
            return False
        return new_position

    # function to check if desired agent position is valid (loop case) TODO
    def valid_move_loop(self, direction, percepts):
        # assign movement increments and modify position
        dx, dy = self.direction_To_Coord[direction]
        new_position = (self.position[0] + dx, self.position[1] + dy)
        # check if chosen position is valid and has not been traversed
        if percepts[direction][0] == "w":
            return False
        return new_position

    # function to record possible branches for each position TODO
    def branch_check(self, percepts):
        temp_branch = 0
        for move in self.valid_moves:
            if percepts[move][0] != "w":
                new_position = self.calculate_position(self.position, move)
                temp_branch += 1
        return temp_branch

    # function to recalculate possible branches for each position
    def branch_recheck(self, percepts):
        for iter, branch in enumerate(self.branch_num_max):
            temp_branch = branch
            for move in self.valid_moves:
                new_position = self.calculate_position(self.traversed_loop[iter], move)
                if new_position in self.traversed_loop:
                    temp_branch = temp_branch - 1
            self.branch_num[iter] = temp_branch

    # function to check if agent has gone around a loop TODO
    def loop_check(self, percepts):
        # check possible modified positions
        for move in self.valid_moves:
            if self.valid_move_loop(move, percepts):
                temp_move = move
                break
            if move == "W":
                return [False, False]
        # assign movement increments and modify position
        new_pos = self.calculate_position(
            self.position, self.direction_To_Coord[temp_move]
        )

        # check where the (possible) loop starts
        for iter, pos in enumerate(self.traversed):
            if pos == new_pos:
                temp_iter = len(self.traversed) - iter
                break
        self.move_stack.append(self.oppMove[temp_move])
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
            elif iter > (len(self.move_stack) - temp_iter):
                if self.oppMove[last_move] == move:
                    self.move_stack.pop()
                    return [False, False]
                last_move = move
                last_pos = self.traversed[iter]
                temp_len = temp_len + 1
        if last_pos != None:
            last_pos = self.calculate_position(
                last_pos, self.direction_To_Coord[temp_move]
            )
        if first_pos != last_pos:
            self.move_stack.pop()
            return [False, False]
        if temp_len > 1:
            self.move_stack.pop()
            return [temp_move, temp_iter - 1]
        else:
            self.move_stack.pop()
            return [
                False,
                False,
            ]  # 26 13 for worldB loop test - 29 6 for worldB dead end test

    # function to check if agent has gone around a loop TODO
    def loop_check_new(self, percepts):
        temp_move_final = None
        temp_iter_final = None
        # check possible modified positions
        for move in self.valid_moves:
            if self.valid_move_loop(move, percepts):
                temp_move = move
                flag_dict = {
                    "N_flag": False,
                    "E_flag": False,
                    "S_flag": False,
                    "W_Flag": False,
                }
                # assign movement increments and modify position
                dx, dy = self.direction_To_Coord[temp_move]
                new_pos = (self.position[0] + dx, self.position[1] + dy)
                # check where the (possible) loop starts
                for iter, pos in enumerate(self.traversed_loop):
                    if pos == new_pos:
                        temp_iter = len(self.traversed_loop) - iter
                        break
                    else:
                        temp_iter = len(self.move_stack_run) + 1
                if temp_iter <= len(self.move_stack_run):
                    self.move_stack_run.append(self.oppMove[temp_move])
                    # check if the movements form a loop
                    # no opposing movement indicates a loop
                    temp_len = 0
                    first_pos, last_pos, last_move = (None,) * 3
                    for iter, move_sub in enumerate(self.move_stack_run):
                        if iter == (len(self.move_stack_run) - temp_iter):

                            for move in self.valid_moves:
                                if move_sub == move:
                                    flag_dict[move + "_flag"] = True

                            last_move = move_sub
                            first_pos = self.traversed_loop[iter]
                            temp_len = temp_len + 1
                        elif iter > (len(self.move_stack_run) - temp_iter):
                            if self.oppMove[last_move] == move_sub:
                                break
                            if self.branch_num[iter] > 0:
                                break

                            for move in self.valid_moves:
                                if move_sub == move:
                                    flag_dict[move + "_flag"] = True

                            last_move = move_sub
                            last_pos = self.traversed_loop[iter]
                            temp_len = temp_len + 1
                    if last_move is not None:

                        flag_sum = sum(flag_dict.values())

                        if temp_len > 1 and flag_sum == 4:
                            if last_pos is not None:
                                last_pos = (last_pos[0] + dx, last_pos[1] + dy)
                                if first_pos == last_pos and (temp_iter - 1) < len(
                                    self.move_stack
                                ):
                                    if temp_iter_final is None:
                                        temp_iter_final = temp_iter - 1
                                    if temp_move_final is None:
                                        temp_move_final = temp_move
                                    if (temp_iter - 1) > temp_iter_final:
                                        temp_iter_final = temp_iter - 1
                                        temp_move_final = temp_move
                    self.move_stack_run.pop()
        if temp_move_final is not None and temp_iter_final is not None:
            return [temp_move_final, temp_iter_final]
        else:
            return [False, False]

    # function to perform several prior movement removals TODO
    def multi_pop(self, loop_len):
        # remove prior movements to close the loop
        temp_iter = 0
        while loop_len > temp_iter:
            self.move_stack.pop()
            temp_iter = temp_iter + 1

    # function to check goal visibility
    def goal_check(self, percepts):
        if (
            "r" in percepts["N"]
            or "r" in percepts["E"]
            or "r" in percepts["S"]
            or "r" in percepts["W"]
        ):
            return True
        return False

    def goal_approach_iteration(self, percepts, move):
        self.traversed.append(tuple(self.position))
        self.traversed_loop.append(tuple(self.position))
        self.branch_num_max.append(self.branch_check(percepts))
        self.branch_num.append(self.branch_check(percepts))
        self.branch_recheck(percepts)
        self.move_stack.append(self.oppMove[move])
        self.move_stack_run.append(self.oppMove[move])
        self.visit_queue.append(self.calculate_position(self.position, move))
        self.update_position(move)

    # function to move towards the goal tile
    def goal_approach(self, percepts):
        # move towards goal if it is visible
        # no possible issues of movement validity

        for move in self.valid_moves:
            if "r" in percepts[move]:
                self.goal_approach_iteration(percepts, move)
                return move
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
        for move_index in range(len(self.valid_moves)):
            # check movement validity
            if self.valid_move(self.valid_moves[move_index], percepts):
                # record position, record movement complement, and perform movement
                self.goal_approach_iteration(percepts, self.valid_moves[move_index])
                self.loop_flag = False
                self.backtrack_flag = False
                return self.valid_moves[move_index]

            # check to see if all movements have been attempted
            # if backtrack record exists, attempt movement back
            if self.move_stack and move_index == 3:
                self.traversed.append(tuple(self.position))
                self.traversed_loop.append(tuple(self.position))
                self.branch_num_max.append(self.branch_check(percepts))
                self.branch_num.append(self.branch_check(percepts))
                self.branch_recheck(percepts)

                # check if agent has performed a loop
                if (
                    self.loop_check_new(percepts)[0] != False
                    and self.loop_flag == False
                    and self.backtrack_flag == False
                ):
                    # removes loop removal function v
                    temp_loop = []
                    temp_loop = self.loop_check_new(percepts)
                    self.multi_pop(temp_loop[1])
                    self.update_position(temp_loop[0])
                    self.move_stack_run.append(self.oppMove[temp_loop[0]])
                    self.loop_flag = True
                    self.backtrack_flag = False
                    return temp_loop[0]

                # record position, remove prior movement, and perform backtrack
                backtrack = self.move_stack.pop()
                if len(self.visit_queue) > 0:
                    self.visit_queue.pop()
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
        # time.sleep(100000)
        # perform depth-first search based on percepts
        self.map_location(percepts)

        self.prune_tiles()

        return self.depth_first_search(percepts)


"""
py main.py -w worlds/world -t 100 -d
can use -l log to output to text file
"""

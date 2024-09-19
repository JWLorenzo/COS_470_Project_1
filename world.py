import misc

class World:

    VALID_CELLS = [
        'w', 'b', 'o', 'r',
        'g', 'p', 'y', '1',
        '2', '3', '4', '5',
        '6', '7', '8', '9',
        '0'
    ]

    # Cells that are treated as walls.
    WALL_CELLS = ['w']

    # Goal Cells
    GOAL_CELLS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    DIRECTIONS = ['N', 'E', 'S', 'W']

    def __init__(self, world_filename):
        self.world_filename = world_filename
        self.start_x = None
        self.start_y = None
        self.face_dir = None
        self.width = 0
        self.height = 0
        self.world_map = []
        self.doors_closed = True
        self.goals = []

    def load_world(self):
        try:
            with open(self.world_filename, 'r') as f:

                # Parse agent starting location
                startxy = f.readline().strip().split()
                facedir = f.readline().strip()
                
                if len(startxy) != 2:
                    raise misc.InvalidWorldException(
                        f"World {self.world_filename} is missing the xy agent start."
                    )

                if facedir in World.DIRECTIONS:
                    self.face_dir = facedir
                else:
                    raise misc.InvalidWorldException(
                        f"World {self.world_filename} has an invalid starting facing."
                    )

                try:
                    self.start_x = int(startxy[0])
                    self.start_y = int(startxy[1])
                except Exception:
                    raise misc.InvalidWorldException(
                        f"Invalid agent starting cell: {startxy[0]} {startxy[1]}"
                    )

                # Parse the world
                for line in f:
                    line = line.split()
                    row = []
                    for element in line:
                        if element not in World.VALID_CELLS:
                            raise misc.InvalidCellException(
                                f"{element} is not a valid cell type."
                            )
                        row.append(element)
                    self.world_map.append(row)

                self.height = len(self.world_map)
                self.width = len(self.world_map[0])

                # Find all the goals
                self.find_goals()

        except FileNotFoundError:
            print(f"{self.world_filename} was not found.")

    def prettyprint_world(self):
        for row in self.world_map:
            for ele in row:
                print(f"{ele} ",end="")
            print()


    def find_goals(self):
        for row in self.world_map:
            for ele in row:
                if ele in World.GOAL_CELLS:
                    self.goals.append(ele)
        self.goals.sort()

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_startxy(self):
        return (self.start_x, self.start_y)
    
    def get_start_face_dir(self):
        return self.face_dir

    def get_cell(self, x, y):
        return self.world_map[y][x]
    
    def set_cell(self, x, y, flag):
        self.world_map[y][x] = flag

    def is_valid_cell(self, x, y):
        try:
            self.world_map[y][x]
            return True
        except IndexError:
            return False

    def is_cell_enterable(self, x, y):
        if self.is_valid_cell(x, y):
            cell = self.get_cell(x, y)
            return cell not in World.WALL_CELLS
        else:
            return False

    def get_cells_around(self, x, y):
        cells = {}
        cells['N'] = self.get_cell(x, y-1)
        cells['NE'] = self.get_cell(x+1, y-1)
        cells['E'] = self.get_cell(x+1, y)
        cells['SE'] = self.get_cell(x+1, y+1)
        cells['S'] = self.get_cell(x, y+1)
        cells['SW'] = self.get_cell(x-1, y+1)
        cells['W'] = self.get_cell(x-1, y)
        cells['NW'] = self.get_cell(x-1, y-1)
        cells['X'] = self.get_cell(x, y)
        return cells

    def raycast(self, x, y, dx, dy):
        cells = []
        nx = x+dx
        ny = y+dy
        while self.is_valid_cell(nx, ny):
            cells.append(self.get_cell(nx,ny))
            nx = nx+dx
            ny = ny+dy
        return cells

    def prune_raycast(self, cells):
        for i in range(len(cells)):
            if cells[i] in World.WALL_CELLS:
                break
        return cells[:i+1]

    def find_cell(self, flag):
        for y in range(len(self.world_map)):
            for x in range(len(self.world_map[y])):
                cell = self.get_cell(x, y)
                if cell == flag:
                    return (x, y)
        return None

    def swap_all_cells(self, flagA, flagB):
        for y in range(len(self.world_map)):
            for x in range(len(self.world_map[y])):
                cell = self.get_cell(x, y)
                if cell == flagA:
                    self.set_cell(x, y, flagB)

    def check_triggers(self, x, y, cmd):
        if self.is_valid_cell(x, y):
            cell = self.get_cell(x, y)
            
            if cell == "r" and cmd == "U":
                return ["EXIT"]
            elif cell == "b" and cmd == "U":
                nxny = self.find_cell("o")
                if nxny is not None:
                    return ["TELEPORT", nxny[0], nxny[1]]
            elif cell == "o" and cmd == "U":
                nxny = self.find_cell("b")
                if nxny is not None:
                    return ["TELEPORT", nxny[0], nxny[1]]
            elif cell == "y" and cmd == "U":
                nxny = self.find_cell("p")
                if nxny is not None:
                    return ["TELEPORT", nxny[0], nxny[1]]
            elif cell == "p" and cmd == "U":
                nxny = self.find_cell("y")
                if nxny is not None:
                    return ["TELEPORT", nxny[0], nxny[1]]
            elif cell in World.GOAL_CELLS and cmd == "U":
                index = self.goals.index(cell)
                self.swap_all_cells(cell, "g")
                del self.goals[index]
                return ["GOAL_TRIGGERED", len(self.goals), cell]
                
        return ["NONE"]

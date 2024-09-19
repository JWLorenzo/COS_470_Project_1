import world
import ai
import display
import time

DIRECTIONS = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0)
}

FACINGS = ['N', 'E', 'S', 'W']
VALID_COMMANDS = [
    'N', # Move north
    'E', # Move east
    'W', # Move west
    'S', # Move south
    'U' # Teleport/Open Door/Touch Goal
]

POINTS_PER_GOAL = 100

def run_sim(
    the_world, 
    max_turns=None, 
    log=None, 
    use_display=False,
    display_speed=0.5
):

    the_ai = ai.AI()

    agent_x, agent_y = the_world.get_startxy()
    agent_facing = the_world.get_start_face_dir()
    cells_visited = []
    turn = 1
    agent_cmd = "X"
    percepts = {}
    ai_state = 'GOOD'
    points = 1000

    disp = None

    if use_display:
        import display
        disp = display.Display(
            the_world,
            agent_x,
            agent_y
        )

    if use_display:
        disp.update(
            agent_x, agent_y, agent_facing
        )
        time.sleep(display_speed)

    

    run = True
    while run:

        if ai_state != 'GOOD':
            run = False
            write_to_log(
                log,
                f"-----Scenario Finished-----"
            )
            write_to_log(
                log,
                f"FINAL AGENT STATE: {ai_state}"
            )
            continue
        else:
            write_to_log(
                log,
                f"-----Turn {turn}-----"
            )

        # What does the agent see?
        percepts = get_percepts(the_world, agent_x, agent_y, agent_facing)

        # Get agent's command
        agent_cmd = the_ai.update(percepts)

        # LOG ###############################################################
        write_to_log(
            log,
            f"Turn: {turn}"
        )
        write_to_log(
            log,
            f"   Start:    {agent_x},{agent_y}"
        )
        percept_str = ""
        for k, v in percepts.items():
            percept_str += f"({k} {v}) "
        write_to_log(
            log,
            f"   Percepts: {percept_str}"
        )
        write_to_log(
            log,
            f"   Command:  {agent_cmd}"
        )
        # ####################################################################

        # Move the agent
        if validate_agent_cmd(agent_cmd):

            new_agent_x = agent_x
            new_agent_y = agent_y

            match agent_cmd:
                case 'N' | 'E' | 'S' | 'W':
                    dx, dy = DIRECTIONS[agent_cmd]
                    new_agent_x = agent_x + dx
                    new_agent_y = agent_y + dy
                    if the_world.is_cell_enterable(new_agent_x, new_agent_y):
                        agent_x = new_agent_x
                        agent_y = new_agent_y

                
            trigger = the_world.check_triggers(agent_x, agent_y, agent_cmd)
            match trigger[0]:
                case "EXIT":
                    write_to_log(
                        log,
                        f"   Trigger:  Agent has exited the environment."
                    )
                    ai_state = 'EXITED'
                case "TELEPORT":
                    write_to_log(
                        log,
                        f"   Trigger:  Teleported from {the_world.get_cell(agent_x, agent_y)} to {the_world.get_cell(trigger[1], trigger[2])}"
                    )
                    agent_x = trigger[1]
                    agent_y = trigger[2]
                    
                case "DOORS_OPEN":
                    write_to_log(
                        log,
                        f"   Trigger:  Doors opened."
                    )
                case "GOAL_TRIGGERED":
                    # if trigger[1] == 0:
                    #     write_to_log(
                    #         log,
                    #         f"   Trigger:  Goal {trigger[2]}"
                    #     )
                    #     write_to_log(
                    #         log,
                    #         f"   Trigger:  You have completed this map in {turn} turns. SUCCESS"
                    #     )
                    #     run = False
                    # else:
                    points += POINTS_PER_GOAL
                    write_to_log(
                        log,
                        f"   Trigger:  Agent activated goal {trigger[2]}"
                    )
                case "NONE":
                    pass


            write_to_log(
                log,
                f"   End:      {agent_x},{agent_y}"
            )

        else:
            write_to_log(log, f"Invalid command: {agent_cmd}")
            ai_state = 'BAD'
            run = False

        if use_display:
            disp.update(
                agent_x, agent_y, agent_facing
            )
            time.sleep(display_speed)


        if max_turns is not None:
            if turn >= max_turns:
                write_to_log(
                    log,
                    f"---MAX TURNS REACHED---"
                )
                run = False
                continue

        points -= 1
        turn += 1

    write_to_log(
        log,
        f"FINAL SCORE: {points}"
    )

    if use_display:
        disp.quit()

def get_percepts(the_world, agent_x, agent_y, agent_facing):
    # percepts = the_world.get_cells_around(agent_x, agent_y)
    percepts = {'X':[the_world.get_cell(agent_x, agent_y)]}
    for d, v in DIRECTIONS.items():
        dx, dy = v
        ray = the_world.raycast(agent_x, agent_y, dx, dy)
        ray = the_world.prune_raycast(ray)
        percepts[d] = ray

    # percepts = [the_world.get_cell(agent_x, agent_y)]
    # dx, dy = DIRECTIONS[agent_facing]
    # ray = the_world.raycast(
    #     agent_x,
    #     agent_y,
    #     dx, dy
    # )
    # ray = the_world.prune_raycast(ray)
    # percepts += ray
    return percepts


def validate_agent_cmd(cmd):
    return cmd in VALID_COMMANDS

def write_to_log(log, msg):
    if log is not None:
        log.write(f"{msg}\n")
        log.flush()
    else:
        print(msg)

def turn_right(cur_facing):
    match cur_facing:
        case 'N': return 'E'
        case 'E': return 'S'
        case 'S': return 'W'
        case 'W': return 'N'

def turn_left(cur_facing):
    match cur_facing:
        case 'N': return 'W'
        case 'W': return 'S'
        case 'S': return 'E'
        case 'E': return 'N'

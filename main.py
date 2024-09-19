import sys
import world
import misc
import sim

def main():

    world_filename = None
    log_filename = None
    log = None
    max_turns = None
    the_world = None
    use_display = False
    display_speed = 0.5

    args = sys.argv

    if "-w" not in args:
        print("Map argument missing. Run with -h for help.")

    if "-h" in args:
        print("Help")

    i = 1
    while i < len(args):
        try:
            if args[i] == "-w":
                world_filename = args[i+1]
            elif args[i] == "-l":
                log_filename = args[i+1]
            elif args[i] == "-d":
                use_display = True
                try:
                    display_speed = float(args[i+1])
                except:
                    pass
            elif args[i] == "-t":
                try:
                    max_turns = int(args[i+1])
                except TypeError:
                    print(f"max turns must be an int: {args[i+1]}")
        except IndexError:
            print("Incorrect command line arguments. Run with -h for help.")
            return

        i+=1

    if log_filename is not None:
        log = open(log_filename, 'w')
        
    try:
        the_world = world.World(world_filename)
        the_world.load_world()
        sim.run_sim(the_world, max_turns, log, use_display, display_speed)
    except misc.InvalidCellException as e:
        print(e)
    finally:
        if log is not None:
            log.close()



if __name__ == "__main__":
    main()
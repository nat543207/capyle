# Name: Wildfire
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils
import numpy as np
import enum
from collections import namedtuple
from random import random as rand


class Terrain(enum.IntEnum):
    BURNING = 0
    WATER = 1
    SCORCHED = 2
    SCRUBLAND = 3
    CHAPARRAL = 4
    FOREST = 5

wind = None


def transition_function(grid, neighbourstates, neighbourcounts, burning, fuel, ign_prob):
    """
    Function to apply the transition rules
    N. B. `grid` is a reference to a region of data in the caller; you MUST
    return `grid` or things will begin to break in unexpected ways
    """

    # Fire consumes fuel
    fuel[burning] -= 1

    # Determine how the fire has changed
    ignited = (rand() < ign_prob) & ignition_possible(neighbourstates, neighbourcounts)
    scorched = burning & (fuel == 0)
    burning[ignited] = True

    # Any burning cells that have run out of fuel become 'scorched'
    burning[scorched] = False
    ign_prob[scorched] = 0

    # Populate the view based on cell states and return
    grid[burning] = Terrain.BURNING
    grid[scorched] = Terrain.SCORCHED
    return grid


def ignition_possible(neighbourstates, neighbourcounts):
    return (0 < neighbourcounts[int(Terrain.BURNING)])


def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)

    # For some reason calling list(Terrain) breaks everything
    config.states = [v.value for v in Terrain.__members__.values()]
    config.state_colors = [(1,0,0),(0,0,1),(0,0,0),(.5,.7,0),(.2,.5,0),(0,.2,0)]
    config.title = "Wildfire"
    config.wrap = False
    config.dimensions = 2

    #config.grid_dims = (20,20)


    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    # Create grid object using parameters from config + transition function
    data = config.initial_grid.astype(int)
    grid = Grid2D(config,
        (transition_function,
        data == 0, #TODO Enumify
        np.array([-1, 0, 0, 1, 2, 3])[data]
        np.array([0, 0, 0, 1, .7, .4])[data],
        ))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()

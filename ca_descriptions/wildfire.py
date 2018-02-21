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

# Apparently enums don't work with how this program unpickles things.  Sadness.
# So I'll just use constants instead
#from enum import Enum
#class Terrain(Enum):
WATER = 0
SCORCHED = 1
SCRUBLAND = 2
CHAPARRAL = 3
FOREST = 4
BURNING = 5 # Can't be initial state

initial = {
    WATER : (False, 0, 0),
    #SCORCHED : (False, 0, 0),
    SCRUBLAND : (False, 1, 1),
    CHAPARRAL : (False, 1, 2),
    FOREST : (False, 1, 3)
}

vals = None
wind = None

counter = 0

def transition(grid, neighbourstates, neighbourcounts, terraininfo, winddir):
    """
    Function to apply the transition rules
    This *not* named transition_function because our code takes advantage of
    the behavior that is automatically invoked by the engine when the
    transition_function property of a module is a tuple
    """

    global vals
    if vals is None:
        vals = np.empty(grid.shape,
            dtype=[('burning', np.bool_),('burn_prob', np.float_),
                ('fuel', np.int_)])
        tmp = np.vectorize(lambda state: initial[state])(grid)
        vals[:,:]['burning'] = tmp[0]
        vals[:,:]['burn_prob'] = tmp[1]
        vals[:,:]['fuel'] = tmp[2]

    global counter
    vals[counter,counter]['burning'] = True
    counter += 1

    grid[vals[:,:]['burning']] = BURNING

    return grid

transition_function = (transition, vals, wind)

def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "Wildfire"
    config.dimensions = 2
    config.states = (WATER, SCORCHED, BURNING, SCRUBLAND, CHAPARRAL, FOREST)
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0,0,1),(0,0,0),(.5,.7,0),(.2,.5,0),(0,.2,0),(1,0,0)]
    # config.grid_dims = (200,200)

    # ----------------------------------------------------------------------

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
    grid = Grid2D(config, transition_function)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()

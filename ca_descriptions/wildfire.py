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

Terrain = namedtuple('Terrain', ['index', 'burning', 'burn_prob', 'fuel'])
class TerrainType(enum.Enum):
    BURNING = Terrain(0, True, 0, -1)
    WATER = Terrain(1, False, 0, 0)
    SCORCHED = Terrain(2, False, 0, 0)
    SCRUBLAND = Terrain(3, False, .7, 1)
    CHAPARRAL = Terrain(4, False, .5, 2)
    FOREST = Terrain(5, False, .2, 3)
tiles = [v.value.index for v in TerrainType.__members__.values()]

# State used for calculation
state = None

wind = None


def transition_function(grid, neighbourstates, neighbourcounts):
    """
    Function to apply the transition rules
    """
    global state
    global view
    global burning
    global burn_prob
    global fuel

    if state is None:
        state = np.stack(axis=-1, arrays=np.vectorize(
                lambda state: list(TerrainType)[int(state)].value)(grid))

    view = state[:,:,0]
    burning = state[:,:,1].astype(bool) # This is a copy, so insertion semantics don't work correctly on it
    burn_prob = state[:,:,2]
    fuel = state[:,:,3]

    ## Fire consumes fuel
    fuel[burning] -= 1

    ## Any cell that was burning at the beginning of the transition has the
    ## chance to ignite its neighbours
    ignite = (0 < neighbourcounts[TerrainType.BURNING.value.index]) & (rand() < burn_prob)

    # Any burning cells that have run out of fuel become 'scorched'
    scorched = burning & (fuel == 0)

    # Populate the view based on cell states and return
    burning = (burning | ignite) & ~scorched
    state[:,:,1][burning] = True
    state[scorched] = TerrainType.SCORCHED.value
    view[burning] = TerrainType.BURNING.value.index
    return view


def setup(args):
    """Set up the config object used to interact with the GUI"""
    global states
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "Wildfire"
    config.dimensions = 2
    config.states = tiles
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(1,0,0),(0,0,1),(0,0,0),(.5,.7,0),(.2,.5,0),(0,.2,0)]
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

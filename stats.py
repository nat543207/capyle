#! /usr/bin/env python3
import argparse
import numpy as np
import pickle
import sys
from subprocess import call
import pdb
import signal
signal.signal(signal.SIGUSR2, lambda _, __: pdb.set_trace())

default_wind = np.array([.9, 1, .9,
                         .5,    .5,
                         .3, .1,.3])

cclk = np.array([1,  2,  4,
                 0,      7,
                 3,  5,  6])


def simulate(config_file, iterations, wind=default_wind):
    stop_gen = np.zeros((iterations,), dtype=int)

    for s in range(iterations):
        call(['python', 'ca_descriptions/wildfire.py', config_file, '-w', *[str(w) for w in wind]])
        tl = pickle.load(open('temp/timeline.pkl', 'rb'))
        for i, arr in enumerate(tl):
            if 0 in arr[-2:,0:5]:
                stop_gen[s] = i
                break

    avg_stop_gen = np.average(stop_gen)
    sdev_stop_gen = np.std(stop_gen)

    #print(f'Wind: {wind}')
    #print(f'{stop_gen}\n{avg_stop_gen} +/- {sdev_stop_gen}')
    #print('\n-----\n')
    return (avg_stop_gen, sdev_stop_gen)



def simulate_all_winds(config_file, iterations, wind=default_wind):
    for i in range(8):
        simulate(config_file, iterations, wind)
        wind = wind[cclk]



def evolve_water(config_file, iterations, cross_prob=0.3, mut_prob=0.05, pop_size=100, wind=default_wind):
    import math
    import sys
    main_dir_loc = '/home/nat543207/src/remote/capyle/'
    sys.path.append(main_dir_loc)
    sys.path.append(main_dir_loc + 'capyle')
    sys.path.append(main_dir_loc + 'capyle/ca')
    sys.path.append(main_dir_loc + 'capyle/guicomponents')
    from capyle.ca import CAConfig
    def invalid(x, y):
        return ((x <= 6 and y <= 6)
                or (x <= 8 and 43 <= y)
                or (43 <= x and y <= 6))

    def replace_invalid(genome):
        for i in range(len(genome)):
            while invalid(*genome[i]):
                genome[i] = np.random.randint(0, 50, (2,))

    def breed(gen_a, gen_b):
        crs = np.random.random((len(gen_a),))
        pts = np.random.randint(0, 50, (len(gen_a), 2))
        idx = crs < cross_prob
        child_a = gen_a
        child_a[idx] = gen_b[idx]
        child_b = gen_b
        child_b[idx] = gen_a[idx]
        return (child_a, child_b)


    def mutate(genome):
        mut = np.random.random((len(genome),))
        pts = np.random.randint(0, 50, (len(genome), 2))
        idx = mut < mut_prob
        genome[idx] = pts[idx]
        replace_invalid(genome)


    config = pickle.load(open(config_file, 'rb'))
    config.path = '/home/nat543207/src/remote/capyle/temp/config.pkl'
    initial_map = config.initial_grid
    #population = np.random.randint(0, 50, (pop_size, 10, 2))
    #fitness = np.zeros((pop_size,))

    #for p in population:
    #    replace_invalid(p)

    #while True:
    #    for i, genome in enumerate(population):
    #        env = initial_map.copy()
    #        for gene in genome:
    #            env[gene[0], gene[1]] = 1 #WATER
    #        config.initial_grid = env
    #        config.save()
    #        fitness[i] = simulate(config.path, 10, default_wind)[0]

    #    num_selected = math.floor(math.sqrt(len(population)))
    #    best = np.argsort(-fitness)[0:num_selected]
    #    survivors = population[best]

    #    print(survivors)
    #    print(fitness[best])
    #    print('###')
    #    print()
    #    sys.stdout.flush()

    #    population = np.ndarray((len(survivors)**2, 10, 2), dtype=int)
    #    fitness = np.zeros((len(survivors)**2))
    #    for i in range(len(survivors)):
    #        for j in range(i, len(survivors)):
    #            children = breed(survivors[i], survivors[j])
    #            population[num_selected*i+j] = children[0]
    #            population[num_selected*j+i] = children[1]

    #    for p in population:
    #        mutate(p)


    genome = np.array([[i, 15] for i in range(21,31)])

    env = initial_map.copy()
    for gene in genome:
        env[gene[0], gene[1]] = 1 #WATER
    config.initial_grid = env
    config.save()
    print(genome)
    print(simulate(config.path, 500, default_wind))


def run():
    parser = argparse.ArgumentParser(description='Calculate statistics on a CAPyLE cellular automaton')
    parser.add_argument('-f', '--config-file', metavar='CONFIG_FILE', type=str,
            help='Path to .pkl config file', default='./temp/config.pkl')
    parser.add_argument('-n', '--num', metavar='N', dest='num_sims', type=int,
            help='Number of times to run simulation', default=10)
    parser.add_argument('-w', '--wind', metavar='WIND_MODS', dest='wind', nargs=8,
            help='Wind modifiers to use during simulaiton', default=default_wind)
    args = parser.parse_args()

    res = simulate(args.config_file, args.num_sims, args.wind)
    print(f'{res[0]/2} +/- {res[1]} hours to reach within 1km of town ({args.num_sims} simulations run)')
    #evolve_water(args.config_file, args.num_sims, cross_prob=0.4, mut_prob=0.1, pop_size=25)


if __name__ == '__main__':
    run()

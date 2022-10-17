import chromosome
import functools
from time import time
from copy import deepcopy
from random import random

def withtime(f):
    @functools.wraps(f)
    def f_withtime(*args, **kwargs):
        print("Running!")
        start_time = time()
        f_result = f(*args, **kwargs)
        end_time = time()
        print("Wall time: {} seconds".format(str(end_time - start_time)))
        return f_result
    return f_withtime

@withtime
def genetic_algorithm(n_generations, n_population, keep_best, crossover_rate, mutation_rate, verbose = False):
    population = chromosome.generate_population(n_population)
    keep_best = min(n_population, keep_best)
    for gen_idx in range(n_generations):
        new_pop = population[-keep_best:]
        for pop_idx in range(n_population - keep_best):
            p1, p2 = chromosome.select_parents(population)
            if random() < crossover_rate:
                c1, c2 = p1*p2
                child = max(c1, c2)
            else:
                child = deepcopy(p1)
            child.mutation(mutation_rate)
            new_pop.append(child)
        population = sorted(new_pop)
        if verbose:
            print("best distance:", population[-1].distance)
    return population[-1]

best_chromosome = genetic_algorithm(700,  10, 1, 0.25, 0.05)
print(best_chromosome)
chromosome.draw_chromosome(best_chromosome, "chromosome30.jpg")
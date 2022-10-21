import numpy as np
import chromosome
import functools

from time import time
from typing import List
from copy import deepcopy
from random import random
from problem import CVRPProblem


def select_parents(chr_list: List[chromosome.Chromosome]):
    fitness_list = np.array([c.fitness for c in chr_list])
    sum_fitness = sum(fitness_list)
    roulette_rank = fitness_list / sum_fitness
    chosen_parents = np.random.choice(chr_list, 2, False, roulette_rank)
    return chosen_parents


def withtime(f):
    @functools.wraps(f)
    def f_withtime(*args, **kwargs):
        print("Running!")
        start_time = time()
        f_result = f(*args, **kwargs)
        end_time = time()
        time_elapsed = round(end_time - start_time, 3)
        print(f"Wall time: {time_elapsed} seconds")
        return f_result

    return f_withtime


@withtime
def genetic_algorithm(
    n_generations: int,
    n_population: int,
    keep_best: int,
    crossover_rate: float,
    mutation_rate: float,
    problem: CVRPProblem,
    verbose=False,
):
    customer_list = problem.customer_list
    capacity = problem.car_capacity
    depot = problem.depot_node
    population = sorted(
        [
            chromosome.Chromosome.from_node_list(
                customer_list, capacity, depot
            )
            for _ in range(n_population)
        ]
    )
    keep_best = min(n_population, keep_best)
    for gen_idx in range(n_generations):
        new_pop = population[-keep_best:]
        for pop_idx in range(n_population - keep_best):
            p1, p2 = select_parents(population)
            if random() < crossover_rate:
                c1, c2 = p1 * p2
                child = max(c1, c2)
            else:
                child = deepcopy(p1)
            child.mutation(mutation_rate)
            new_pop.append(child)
        population = sorted(new_pop)
        if verbose:
            print("best distance:", population[-1].distance)
    return population[-1]

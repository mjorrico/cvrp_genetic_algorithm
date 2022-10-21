import functools
import chromosome
import numpy as np
import concurrent.futures as parallel

from time import time
from typing import List
from copy import deepcopy
from random import random
from itertools import repeat
from problem import CVRPProblem


def select_parents(chr_list: List[chromosome.Chromosome]):
    fitness_list = np.array([c.fitness for c in chr_list])
    sum_fitness = sum(fitness_list)
    roulette_rank = fitness_list / sum_fitness
    chosen_parents = np.random.choice(chr_list, 2, False, roulette_rank)
    return chosen_parents


def generate_child_parallel(
    old_population, crossover_rate, mutation_rate, n_child
):
    child_list = []
    for child_idx in range(n_child):
        child = generate_child(old_population, crossover_rate, mutation_rate)
        child_list.append(child)
    return child_list


def batch_config_generator(n_generated, n_cores):
    min = int(n_generated / n_cores)
    batch_size_config = [min] * n_cores
    for i in range(n_generated % n_cores):
        batch_size_config[i] += 1
    return batch_size_config


def generate_child(old_population, crossover_rate, mutation_rate):
    p1, p2 = select_parents(old_population)
    if random() < crossover_rate:
        c1, c2 = p1 * p2
        child = max(c1, c2)
    else:
        child = deepcopy(p1)
    child.mutation(mutation_rate)
    return child


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
    n_cores: int = 4,
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
    n_child = n_population - keep_best
    batch_config = batch_config_generator(n_child, n_cores)

    for gen_idx in range(n_generations):
        new_pop = population[-keep_best:]
        with parallel.ProcessPoolExecutor() as executor:
            process_list = [
                executor.submit(
                    generate_child_parallel,
                    population,
                    crossover_rate,
                    mutation_rate,
                    batch_size,
                )
                for batch_size in batch_config
            ]
            for p in parallel.as_completed(process_list):
                new_pop += p.result()
        # for pop_idx in range(n_population - keep_best):
        #     c = generate_child(population, crossover_rate, mutation_rate)
        #     new_pop.append(c)
        population = sorted(new_pop)
        if verbose:
            print("best distance:", population[-1].distance)
        if gen_idx % int(n_generations / 12 + 1) == 0:
            print(f"Progress: {round(gen_idx/n_generations*100)}%")
    return population[-1]

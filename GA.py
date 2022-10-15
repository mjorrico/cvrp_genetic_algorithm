import chromosome
import numpy as np
from time import time
from copy import deepcopy

def genetic_algorithm(n_generations, n_population, keep_best, crossover_rate, mutation_rate):
    population = chromosome.generate_population(n_population)
    keep_best = min(n_population, keep_best)
    for gen_idx in range(n_generations):
        new_pop = population[-keep_best:]
        for pop_idx in range(n_population - keep_best):
            p1, p2 = chromosome.select_parents(population)
            if np.random.random() < crossover_rate:
                c1, c2 = p1*p2
                child = max(c1, c2)
            else:
                child = deepcopy(p1)
            child.mutation(mutation_rate)
            new_pop.append(child)
        population = sorted(new_pop)
        best_distance = 1/population[-1].fitness*1073
        print("best distance:", best_distance)
    return population[-1]

start = time()
best_chromosome = genetic_algorithm(400,  10, 1, 0.5, 0.02)
chromosome.draw_chromosome(best_chromosome, "chromosome1.jpg")
print("Time elapsed: " + str(time() - start))
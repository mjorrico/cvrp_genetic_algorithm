# Made by Group 46
# Our GitHub Repo: https://github.com/mjorrico/cvrp_genetic_algorithm

import cvrp_genetic_algorithm as cvrp_ga
from problem import CVRPProblem

problem_1 = CVRPProblem("data.csv", 100)
best_chromosome = cvrp_ga.genetic_algorithm(500, 20, 2, 0.25, 0.1, problem_1)
print(best_chromosome)
best_chromosome.save_figure()

from module.dep_analysis import get_dep_info
from module.parse import parse
import os.path
import random

my_path = os.path.abspath(os.path.dirname(__file__))
api_info_list = parse(os.path.join(my_path, "../openapi/project.yaml"), 1.0)
matrix, weight_info_list = get_dep_info(api_info_list)
graph = matrix.tolist()

for n in range(len(graph)):
    for m in range(len(graph)):
        if graph[n][m] !=-1 and graph[m][n] != -1:
            k = random.choice(graph[n][m], graph[m][n])
            if graph[n][m] == k:
                graph[n][m] = -1
            else:
                graph[m][n] = -1